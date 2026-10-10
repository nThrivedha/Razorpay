"""
BeforePay — Feature Engineering Pipeline
-------------------------------------------
Extracts non-content behavioral telemetry features from transaction payloads:
1. Transaction Velocity Features
2. Payee Novelty Features
3. Amount Deviation Features (Log-Normal Z-Score)
4. Time-Pattern / Temporal Deviation Features
5. Session Behavioral Proxy Features
6. [NEW] VPA Trust Score (vpa_trust_registry)
7. [NEW] Cross-Transaction Velocity Features (velocity_cache)
"""

import math
from datetime import datetime
from vpa_trust_registry import get_registry

class FeatureEngineeringPipeline:
    def __init__(self):
        self._trust_registry = get_registry()
        self.feature_names = [
            # Velocity
            "time_since_last_tx_norm",
            "hourly_tx_frequency_ratio",
            "rolling_6hr_accumulated_volume_norm",
            # Payee Novelty
            "is_first_time_payee",
            "payee_account_age_inverse",
            "payee_graph_distance_norm",
            "beneficiary_addition_recency_norm",
            # Amount Deviation
            "amount_log_zscore",
            "amount_to_historical_max_ratio",
            "upi_limit_proximity_ratio",
            # Temporal Pattern Deviation
            "hour_sin_embedding",
            "hour_cos_embedding",
            "is_outside_habitual_window",
            "late_night_window_flag",
            # Session Proxy
            "active_call_indicator",
            "active_call_duration_norm",
            "clipboard_pasted_vpa",
            "screen_share_active",
            "app_switch_frequency_norm",
            "hesitation_latency_norm",
            # [NEW] VPA Trust Score
            "payee_vpa_trust_score",
            # [NEW] Cross-Transaction Velocity (from velocity_cache)
            "cumulative_6hr_loss_norm",
            "rapid_multi_tx_flag",
            "avg_tx_interval_norm",
        ]

    def extract(self, tx_payload, velocity_features: dict | None = None):
        """
        Processes transaction JSON payload and returns a dictionary of named features
        and a normalized 24-dimensional feature vector.

        Args:
            tx_payload: Raw transaction dict from Razorpay / synthetic client.
            velocity_features: Optional dict from VelocityCache.get_velocity_features().
                               Pass this from ml_models.py after recording the transaction.
        """
        telemetry = tx_payload.get("telemetry", {})
        vel = telemetry.get("velocity", {})
        nov = telemetry.get("payee_novelty", {})
        ses = telemetry.get("session", {})
        tmp = telemetry.get("temporal", {})
        amount = float(tx_payload.get("amount", 0.0))
        payer = tx_payload.get("payer", {})
        
        # User baseline stats (defaults if unpopulated)
        mean_spend = float(payer.get("historical_mean_spend", 1500.0))
        std_spend = float(payer.get("historical_std_spend", 800.0))
        max_spend = float(payer.get("historical_max_spend", 15000.0))

        # ----------------------------------------------------
        # 1. TRANSACTION VELOCITY FEATURES
        # ----------------------------------------------------
        time_gap_sec = float(vel.get("time_since_last_tx_sec", 3600.0))
        # Logarithmic normalization of time gap: 1.0 for rapid (<60s), 0.0 for >24h
        time_since_last_tx_norm = max(0.0, min(1.0, 1.0 - math.log10(max(1.0, time_gap_sec) / 60.0 + 1.0) / 3.0))

        hourly_count = float(vel.get("hourly_tx_count", 0.0))
        baseline_hourly = float(vel.get("baseline_hourly_tx_rate", 0.3))
        hourly_tx_frequency_ratio = min(5.0, hourly_count / (baseline_hourly + 1e-3)) / 5.0

        accum_6hr_vol = float(vel.get("rolling_6hr_vol", amount))
        rolling_6hr_accumulated_volume_norm = min(5.0, accum_6hr_vol / (mean_spend * 3.0 + 1e-3)) / 5.0

        # ----------------------------------------------------
        # 2. PAYEE NOVELTY FEATURES
        # ----------------------------------------------------
        is_first_time_payee = 1.0 if nov.get("is_first_time_payee", False) else 0.0

        payee_age_days = float(nov.get("payee_account_age_days", 180.0))
        # 1.0 if brand new (0 days), 0.0 if >= 90 days old
        payee_account_age_inverse = max(0.0, 1.0 - (payee_age_days / 90.0))

        graph_dist = float(nov.get("graph_distance", 1.0))
        payee_graph_distance_norm = min(1.0, (graph_dist - 1.0) / 4.0)  # 0.0 (direct) to 1.0 (distant/unknown)

        added_mins = float(nov.get("beneficiary_added_minutes_ago", 1440.0))
        # 1.0 if added < 5 mins ago, 0.0 if added > 24 hours ago
        beneficiary_addition_recency_norm = max(0.0, 1.0 - math.log10(max(1.0, added_mins) / 5.0 + 1.0) / 2.5)

        # ----------------------------------------------------
        # 3. AMOUNT DEVIATION FEATURES (LOG-NORMAL Z-SCORE)
        # ----------------------------------------------------
        # Log-normal distribution transformation Z-score
        safe_amount = max(1.0, amount)
        safe_mean = max(1.0, mean_spend)
        log_amount = math.log(safe_amount)
        log_mean = math.log(safe_mean)
        log_std = max(0.2, std_spend / (mean_spend + 1e-5))

        raw_log_zscore = (log_amount - log_mean) / log_std
        amount_log_zscore = min(10.0, max(-3.0, raw_log_zscore)) / 10.0  # scaled 0.0 to 1.0

        amount_to_historical_max_ratio = min(5.0, amount / (max_spend + 1e-3)) / 5.0

        # UPI maximum per-transaction limit = ₹1,00,000
        upi_limit_proximity_ratio = min(1.0, amount / 100000.0)

        # ----------------------------------------------------
        # 4. TEMPORAL PATTERN DEVIATION FEATURES
        # ----------------------------------------------------
        hour_of_day = float(tmp.get("hour_of_day", datetime.now().hour))
        hour_rad = (2.0 * math.pi * hour_of_day) / 24.0
        hour_sin_embedding = round(math.sin(hour_rad), 4)
        hour_cos_embedding = round(math.cos(hour_rad), 4)

        is_outside_habitual_window = 1.0 if tmp.get("is_outside_habitual_hours", False) else 0.0
        late_night_window_flag = 1.0 if (23.0 <= hour_of_day or hour_of_day <= 5.0) else 0.0

        # ----------------------------------------------------
        # 5. SESSION BEHAVIORAL PROXY FEATURES
        # ----------------------------------------------------
        active_call_indicator = 1.0 if ses.get("active_phone_call", False) else 0.0
        call_mins = float(ses.get("call_duration_minutes", 0.0))
        active_call_duration_norm = min(1.0, call_mins / 120.0)

        clipboard_pasted_vpa = 1.0 if ses.get("pasted_payee_vpa", False) else 0.0
        screen_share_active = 1.0 if ses.get("screen_sharing_active", False) else 0.0

        app_switches = float(ses.get("app_switch_count_last_2min", 0.0))
        app_switch_frequency_norm = min(1.0, app_switches / 8.0)

        hesitation_ms = float(ses.get("hesitation_latency_ms", 1500.0))
        hesitation_latency_norm = min(1.0, max(0.0, (hesitation_ms - 1000.0) / 10000.0))

        # -------------------------------------------------------
        # 6. VPA TRUST SCORE (payee reputation registry)
        # -------------------------------------------------------
        payee_vpa_str = tx_payload.get("payee", {}).get("vpa", "")
        trust_result = self._trust_registry.lookup(payee_vpa_str)
        # TRUSTED=0.0, UNKNOWN=0.5, WATCHLIST=1.0
        payee_vpa_trust_score = trust_result["trust_score"]

        # -------------------------------------------------------
        # 7. CROSS-TRANSACTION VELOCITY FEATURES (from cache)
        # -------------------------------------------------------
        if velocity_features:
            cumulative_6hr_loss_norm = float(velocity_features.get("cumulative_norm", 0.0))
            rapid_multi_tx_flag = 1.0 if velocity_features.get("rapid_multi_tx_flag", False) else 0.0
            avg_interval = float(velocity_features.get("avg_tx_interval_sec", 3600.0))
        else:
            # Fall back to single-tx velocity telemetry from the payload
            cumulative_6hr_loss_norm = min(1.0, float(vel.get("rolling_6hr_vol", amount)) / 100_000.0)
            rapid_multi_tx_flag = 0.0
            avg_interval = time_gap_sec

        # Normalize interval: 1.0 for very rapid (<60s), 0.0 for ≥1h
        avg_tx_interval_norm = max(0.0, min(1.0, 1.0 - math.log10(max(1.0, avg_interval / 60.0) + 1.0) / 3.0))

        # Vector assembly (24D)
        vector = [
            time_since_last_tx_norm,
            hourly_tx_frequency_ratio,
            rolling_6hr_accumulated_volume_norm,
            is_first_time_payee,
            payee_account_age_inverse,
            payee_graph_distance_norm,
            beneficiary_addition_recency_norm,
            amount_log_zscore,
            amount_to_historical_max_ratio,
            upi_limit_proximity_ratio,
            hour_sin_embedding,
            hour_cos_embedding,
            is_outside_habitual_window,
            late_night_window_flag,
            active_call_indicator,
            active_call_duration_norm,
            clipboard_pasted_vpa,
            screen_share_active,
            app_switch_frequency_norm,
            hesitation_latency_norm,
            payee_vpa_trust_score,
            cumulative_6hr_loss_norm,
            rapid_multi_tx_flag,
            avg_tx_interval_norm,
        ]

        named_features = dict(zip(self.feature_names, vector))

        return {
            "feature_names": self.feature_names,
            "feature_vector": vector,
            "named_features": named_features,
            "payee_trust": trust_result,
            "raw_metrics": {
                "amount_zscore_sigma": round(raw_log_zscore, 2),
                "time_gap_seconds": time_gap_sec,
                "payee_account_age_days": payee_age_days,
                "active_call_duration_mins": call_mins,
                "payee_vpa_trust_tier": trust_result["trust_tier"],
            }
        }

if __name__ == "__main__":
    pipeline = FeatureEngineeringPipeline()
    sample_tx = {
        "amount": 85000,
        "payer": {"historical_mean_spend": 2500, "historical_std_spend": 1200, "historical_max_spend": 15000},
        "telemetry": {
            "velocity": {"time_since_last_tx_sec": 45, "hourly_tx_count": 5, "rolling_6hr_vol": 92000},
            "payee_novelty": {"is_first_time_payee": True, "payee_account_age_days": 2, "graph_distance": 5, "beneficiary_added_minutes_ago": 3},
            "session": {"active_phone_call": True, "call_duration_minutes": 110, "pasted_payee_vpa": True, "screen_sharing_active": False, "hesitation_latency_ms": 7500},
            "temporal": {"hour_of_day": 23, "is_outside_habitual_hours": True}
        }
    }
    extracted = pipeline.extract(sample_tx)
    print("--- Extracted Behavioral Feature Vector (20 Dimensions) ---")
    print(f"Vector Length: {len(extracted['feature_vector'])}")
    print("Raw Metrics:", extracted["raw_metrics"])
    print("\nNamed Features Sample:")
    for k, v in list(extracted["named_features"].items())[:8]:
        print(f"  - {k}: {v}")
