"""
BeforePay — Cumulative Loss Velocity Cache
---------------------------------------------
Razorpay AI Risk Manager — Track 02: AI Risk Manager

Maintains a rolling 6-hour per-user transaction history in-memory.
Computes cross-transaction behavioral features that the stateless
FeatureEngineeringPipeline cannot see.

Closes the documented False Negative case:
  Micro-coercion sharding: scammer instructs victim to send ₹500–₹1,500
  test amounts over 3 hours. Single-transaction scores stay LOW (<30).
  The velocity cache detects the cumulative pattern and sets
  `rapid_multi_tx_flag = True`, boosting the composite score.
"""

import threading
from datetime import datetime, timedelta
from typing import Optional


class VelocityCache:
    """
    Thread-safe, per-user rolling 6-hour velocity tracker.

    Each entry stored per user:
        (timestamp: datetime, amount: float, payee_vpa: str)

    Usage:
        cache = VelocityCache()
        cache.record(user_id="cust_synth_0001", amount=1200.0,
                     payee_vpa="verification_fee_94@paytm")
        features = cache.get_velocity_features("cust_synth_0001")
    """

    WINDOW_HOURS = 6
    RAPID_TX_WINDOW_MINUTES = 120   # 2-hour window for rapid multi-tx detection
    RAPID_TX_COUNT_THRESHOLD = 3    # ≥3 transactions to NEW payees in 2 hours = flag

    def __init__(self):
        self._lock = threading.Lock()
        # { user_id → [(datetime, amount, payee_vpa), ...] }
        self._store: dict[str, list[tuple]] = {}

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def record(
        self,
        user_id: str,
        amount: float,
        payee_vpa: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Records a transaction for a user and prunes entries older than 6 hours.
        Call this AFTER a transaction is evaluated (even if it passed).
        """
        if not user_id:
            return
        ts = timestamp or datetime.now()
        with self._lock:
            if user_id not in self._store:
                self._store[user_id] = []
            self._store[user_id].append((ts, float(amount), str(payee_vpa)))
            self._prune(user_id, ts)

    def get_velocity_features(self, user_id: str) -> dict:
        """
        Returns cross-transaction velocity features for a user, computed from
        the rolling 6-hour window. Returns safe defaults if no history exists.

        Return keys:
            cumulative_6hr_amount       float — total INR transferred in last 6h
            tx_count_6hr                int   — number of transactions in last 6h
            unique_new_payees_2hr       int   — distinct payees in last 2h
            rapid_multi_tx_flag         bool  — True if ≥3 tx to new payees in 2h
            avg_tx_interval_sec         float — mean gap between transactions
            cumulative_norm             float — normalized [0,1] relative to 1L limit
        """
        now = datetime.now()
        cutoff_6hr = now - timedelta(hours=self.WINDOW_HOURS)
        cutoff_2hr = now - timedelta(minutes=self.RAPID_TX_WINDOW_MINUTES)

        with self._lock:
            entries = self._store.get(user_id, [])

        entries_6hr = [(ts, amt, vpa) for ts, amt, vpa in entries if ts >= cutoff_6hr]
        entries_2hr = [(ts, amt, vpa) for ts, amt, vpa in entries if ts >= cutoff_2hr]

        cumulative_6hr_amount = sum(amt for _, amt, _ in entries_6hr)
        tx_count_6hr = len(entries_6hr)

        unique_new_payees_2hr = len(set(vpa for _, _, vpa in entries_2hr))
        rapid_multi_tx_flag = (
            tx_count_6hr >= self.RAPID_TX_COUNT_THRESHOLD
            and unique_new_payees_2hr >= self.RAPID_TX_COUNT_THRESHOLD
        )

        # Average interval between consecutive transactions
        if tx_count_6hr >= 2:
            sorted_entries = sorted(entries_6hr, key=lambda e: e[0])
            intervals = [
                (sorted_entries[i+1][0] - sorted_entries[i][0]).total_seconds()
                for i in range(len(sorted_entries) - 1)
            ]
            avg_tx_interval_sec = sum(intervals) / len(intervals)
        else:
            avg_tx_interval_sec = 3600.0  # default: 1 hour

        # Normalize cumulative amount against ₹1L UPI daily limit
        cumulative_norm = min(1.0, cumulative_6hr_amount / 100_000.0)

        return {
            "cumulative_6hr_amount": round(cumulative_6hr_amount, 2),
            "tx_count_6hr": tx_count_6hr,
            "unique_new_payees_2hr": unique_new_payees_2hr,
            "rapid_multi_tx_flag": rapid_multi_tx_flag,
            "avg_tx_interval_sec": round(avg_tx_interval_sec, 1),
            "cumulative_norm": round(cumulative_norm, 4),
        }

    def clear_user(self, user_id: str) -> None:
        """Clears history for a specific user (e.g., after a cooling-off lock expires)."""
        with self._lock:
            self._store.pop(user_id, None)

    def size(self) -> int:
        """Returns total number of tracked users."""
        with self._lock:
            return len(self._store)

    # ──────────────────────────────────────────────
    # Internal
    # ──────────────────────────────────────────────

    def _prune(self, user_id: str, now: datetime) -> None:
        """Removes entries older than 6 hours. Must be called under lock."""
        cutoff = now - timedelta(hours=self.WINDOW_HOURS)
        self._store[user_id] = [
            (ts, amt, vpa)
            for ts, amt, vpa in self._store[user_id]
            if ts >= cutoff
        ]


# Module-level singleton
_cache_instance: VelocityCache | None = None


def get_cache() -> VelocityCache:
    """Returns the module-level singleton VelocityCache."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = VelocityCache()
    return _cache_instance


if __name__ == "__main__":
    from datetime import timedelta

    cache = VelocityCache()
    user = "cust_synth_0001"

    print("=== Velocity Cache — Micro-Coercion Detection Demo ===\n")
    now = datetime.now()

    # Simulate 4 small transfers to different new payees over 90 minutes
    transfers = [
        (now - timedelta(minutes=85), 500.0,  "verification_fee_01@paytm"),
        (now - timedelta(minutes=60), 1200.0, "verification_fee_02@paytm"),
        (now - timedelta(minutes=35), 800.0,  "verification_fee_03@phonepe"),
        (now - timedelta(minutes=10), 1500.0, "verification_fee_04@paytm"),
    ]

    for ts, amt, vpa in transfers:
        cache.record(user, amt, vpa, timestamp=ts)
        feats = cache.get_velocity_features(user)
        flag = "🚨 RAPID_MULTI_TX" if feats["rapid_multi_tx_flag"] else "✅ Normal"
        print(f"  After ₹{amt:.0f} to {vpa.split('@')[0]}: "
              f"cumulative=₹{feats['cumulative_6hr_amount']:.0f}, "
              f"tx_count={feats['tx_count_6hr']}, "
              f"unique_payees_2hr={feats['unique_new_payees_2hr']} → {flag}")
