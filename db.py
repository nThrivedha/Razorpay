"""
BeforePay — SQLite Transaction Persistence Layer
---------------------------------------------------
Razorpay AI Risk Manager — Track 02: AI Risk Manager

Zero-dependency (Python stdlib sqlite3) persistent storage for:
  1. Every evaluated transaction with its risk score, tier, action
  2. Real-time benchmark metrics computed from actual data
  3. Per-user transaction history (powers /api/v1/history endpoint)

Replaces the hardcoded tp=92, fn=8 confusion matrix in ml_models.py
with dynamically computed values once ≥50 labeled evaluations exist.
"""

import sqlite3
import threading
import json
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "sentinel_upi.db")


class SentinelDB:
    """
    Thread-safe SQLite wrapper for SentinelUPI evaluation persistence.

    Tables:
        evaluations — one row per evaluated transaction
        watchlist_log — audit log for VPA watchlist additions

    Usage:
        db = SentinelDB()
        db.insert_evaluation(tx, result)
        history = db.get_user_history("cust_synth_0001")
        metrics = db.get_real_benchmark_metrics()
    """

    def __init__(self, db_path: str = DB_PATH):
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_schema()

    # ──────────────────────────────────────────────
    # Schema Initialization
    # ──────────────────────────────────────────────

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id           TEXT,
                    order_id        TEXT,
                    payer_user_id   TEXT,
                    payer_vpa       TEXT,
                    payee_vpa       TEXT,
                    amount          REAL,
                    risk_score      REAL,
                    risk_tier       TEXT,
                    action          TEXT,
                    scenario_label  TEXT,
                    is_scam_label   INTEGER,
                    timestamp       TEXT,
                    shap_top        TEXT,
                    created_at      TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS watchlist_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    vpa         TEXT,
                    reason      TEXT,
                    tx_id       TEXT,
                    logged_at   TEXT DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_eval_payer
                    ON evaluations(payer_user_id);
                CREATE INDEX IF NOT EXISTS idx_eval_timestamp
                    ON evaluations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_eval_risk_tier
                    ON evaluations(risk_tier);
            """)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    # ──────────────────────────────────────────────
    # Write Operations
    # ──────────────────────────────────────────────

    def insert_evaluation(self, tx: dict, result: dict) -> None:
        """
        Persists one evaluated transaction.
        `tx` is the raw transaction payload; `result` is from evaluate_transaction().
        """
        payer = tx.get("payer", {})
        top_shap = json.dumps(result.get("shap_explainability", [])[:3])

        # Ground-truth label: use `tx.label` if present (synthetic dataset)
        # or infer from the action for real-time transactions
        label = tx.get("label", "")
        is_scam_label = 1 if label == "SCAM" else (0 if label == "NORMAL" else -1)

        with self._lock:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO evaluations
                        (tx_id, order_id, payer_user_id, payer_vpa, payee_vpa,
                         amount, risk_score, risk_tier, action, scenario_label,
                         is_scam_label, timestamp, shap_top)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.get("transaction_id", tx.get("id", "")),
                    result.get("order_id", tx.get("order_id", "")),
                    payer.get("user_id", ""),
                    result.get("payer_vpa", ""),
                    result.get("payee_vpa", ""),
                    result.get("amount", 0.0),
                    result.get("composite_risk_score", 0.0),
                    result.get("risk_tier", "UNKNOWN"),
                    result.get("action", ""),
                    tx.get("scenario", tx.get("label", "UNKNOWN")),
                    is_scam_label,
                    result.get("timestamp", datetime.now().isoformat()),
                    top_shap,
                ))

    def log_watchlist_addition(self, vpa: str, reason: str, tx_id: str = "") -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO watchlist_log (vpa, reason, tx_id) VALUES (?, ?, ?)",
                    (vpa, reason, tx_id)
                )

    # ──────────────────────────────────────────────
    # Read Operations
    # ──────────────────────────────────────────────

    def get_user_history(self, user_id: str, limit: int = 50) -> list[dict]:
        """Returns the last `limit` evaluated transactions for a user, newest first."""
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute("""
                    SELECT tx_id, payer_vpa, payee_vpa, amount, risk_score,
                           risk_tier, action, scenario_label, timestamp
                    FROM evaluations
                    WHERE payer_user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]

    def get_total_evaluation_count(self) -> int:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute("SELECT COUNT(*) as cnt FROM evaluations").fetchone()
        return row["cnt"] if row else 0

    def get_real_benchmark_metrics(self) -> Optional[dict]:
        """
        Computes confusion matrix from evaluations that have a known ground-truth label.
        Returns None if fewer than 50 labeled samples exist (caller falls back to hardcoded).
        """
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute("""
                    SELECT is_scam_label, risk_score, action
                    FROM evaluations
                    WHERE is_scam_label IN (0, 1)
                """).fetchall()

        labeled = [dict(r) for r in rows]
        if len(labeled) < 50:
            return None

        # Decision threshold: action != AUTO_APPROVE → predicted positive (scam)
        tp = sum(1 for r in labeled if r["is_scam_label"] == 1 and r["action"] != "AUTO_APPROVE")
        fn = sum(1 for r in labeled if r["is_scam_label"] == 1 and r["action"] == "AUTO_APPROVE")
        fp = sum(1 for r in labeled if r["is_scam_label"] == 0 and r["action"] != "AUTO_APPROVE")
        tn = sum(1 for r in labeled if r["is_scam_label"] == 0 and r["action"] == "AUTO_APPROVE")

        precision = round((tp / (tp + fp)) * 100.0, 1) if (tp + fp) > 0 else 0.0
        recall    = round((tp / (tp + fn)) * 100.0, 1) if (tp + fn) > 0 else 0.0
        f1        = round((2 * precision * recall) / (precision + recall), 1) if (precision + recall) > 0 else 0.0
        fpr       = round((fp / (tn + fp)) * 100.0, 2) if (tn + fp) > 0 else 0.0

        return {
            "source": "live_db",
            "total_labeled": len(labeled),
            "confusion_matrix": {"true_positives": tp, "false_positives": fp,
                                  "true_negatives": tn, "false_negatives": fn},
            "metrics": {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "false_positive_rate_percent": fpr,
            }
        }

    def get_recent_high_risk(self, limit: int = 10) -> list[dict]:
        """Returns recent HIGH / CRITICAL transactions for the NOC stream dashboard."""
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute("""
                    SELECT tx_id, payer_vpa, payee_vpa, amount, risk_score,
                           risk_tier, action, scenario_label, timestamp
                    FROM evaluations
                    WHERE risk_tier IN ('HIGH', 'CRITICAL_PANIC')
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def get_stats_summary(self) -> dict:
        """Returns aggregate stats for the NOC dashboard header counters."""
        with self._lock:
            with self._connect() as conn:
                total = conn.execute("SELECT COUNT(*) as c FROM evaluations").fetchone()["c"]
                intercepted = conn.execute(
                    "SELECT COUNT(*) as c FROM evaluations WHERE action='HARD_INTERCEPT'"
                ).fetchone()["c"]
                amount_saved = conn.execute(
                    "SELECT COALESCE(SUM(amount), 0) as s FROM evaluations WHERE action='HARD_INTERCEPT'"
                ).fetchone()["s"]
                high_risk = conn.execute(
                    "SELECT COUNT(*) as c FROM evaluations WHERE risk_tier IN ('HIGH','CRITICAL_PANIC')"
                ).fetchone()["c"]

        return {
            "total_evaluated": total,
            "intercepted_count": intercepted,
            "estimated_amount_saved_inr": round(amount_saved, 2),
            "high_risk_count": high_risk,
        }


# Module-level singleton
_db_instance: SentinelDB | None = None


def get_db() -> SentinelDB:
    """Returns the module-level singleton SentinelDB."""
    global _db_instance
    if _db_instance is None:
        _db_instance = SentinelDB()
    return _db_instance


if __name__ == "__main__":
    db = SentinelDB(":memory:")  # in-memory for test

    sample_tx = {
        "id": "pay_test_001", "order_id": "order_test_001",
        "amount": 85000.0, "label": "SCAM", "scenario": "DIGITAL_ARREST",
        "payer": {"user_id": "cust_synth_0001", "vpa": "priya@pnb"},
        "payee": {"vpa": "rbi.verify.mule@cybercell"}
    }
    sample_result = {
        "transaction_id": "pay_test_001", "order_id": "order_test_001",
        "payer_vpa": "priya@pnb", "payee_vpa": "rbi.verify.mule@cybercell",
        "amount": 85000.0, "composite_risk_score": 94.5,
        "risk_tier": "CRITICAL_PANIC", "action": "HARD_INTERCEPT",
        "timestamp": datetime.now().isoformat(), "shap_explainability": []
    }

    db.insert_evaluation(sample_tx, sample_result)
    print(f"[+] Inserted evaluation. Total count: {db.get_total_evaluation_count()}")
    print(f"[+] Stats: {db.get_stats_summary()}")
    history = db.get_user_history("cust_synth_0001")
    print(f"[+] History for cust_synth_0001: {len(history)} records")
