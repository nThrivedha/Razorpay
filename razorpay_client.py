"""
SentinelUPI — Razorpay Test-Mode API Synthetic Generator & Mule Network Graph
-------------------------------------------------------------------------------
Razorpay AI Risk Manager — Track 02: AI Risk Manager
Simulates:
1. Razorpay PG Orders, Payments, and Payout Guardrail Telemetry.
2. Multi-hop Mule Account Ring Network Flow Analysis (Hop Velocity & Payout Freeze).
3. 3-Line Razorpay Drop-In SDK Wrapper (`RazorpayGuardrailSDK`).
"""

import json
import random
import time
import math
from datetime import datetime, timedelta

class RazorpayGuardrailSDK:
    """
    Simulated 3-Line Drop-In SDK Wrapper for Razorpay Payment Gateway & Route.
    Usage:
        guardrail = RazorpayGuardrailSDK(api_key="rzp_live_xxx", api_secret="yyy")
        decision = guardrail.inspect_payment(order_id="order_123", telemetry=client_telemetry)
        if decision["action"] == "COOLING_OFF_LOCK":
            guardrail.trigger_nominee_alert(user_id="cust_001")
    """
    def __init__(self, api_key="rzp_live_sentinel", api_secret="sec_buildathon_2026"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.version = "2.4.0-sentinel"

    def inspect_payment(self, payment_payload, risk_engine):
        """Inspects incoming Razorpay payment via SentinelUPI Risk Engine."""
        return risk_engine.evaluate_transaction(payment_payload)

class RazorpaySyntheticClient:
    def __init__(self, seed=42):
        random.seed(seed)
        self.users = self._generate_user_profiles(500)
        self.sdk = RazorpayGuardrailSDK()
        
    def _generate_user_profiles(self, count):
        """Generates realistic synthetic user profiles with log-normal spending patterns."""
        users = {}
        first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Sneha", "Aditya", "Meera", "Karan", "Pooja",
                       "Rahul", "Divya", "Amit", "Kavya", "Siddharth", "Neha", "Arjun", "Ritu", "Rajesh", "Sunita"]
        last_names = ["Sharma", "Verma", "Patel", "Gupta", "Rao", "Nair", "Reddy", "Singh", "Joshi", "Kumar",
                       "Deshmukh", "Iyer", "Chopra", "Mehta", "Mukherjee", "Bhat", "Pillai", "Das", "Saxena", "Yadav"]
        
        banks = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "PNB", "INDUSIND"]
        
        for i in range(1, count + 1):
            user_id = f"cust_synth_{i:04d}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            bank = random.choice(banks)
            vpa = f"{name.lower().replace(' ', '')}{random.randint(10,99)}@{bank.lower()}"
            
            # Historical spending characteristics (log-normal distribution params)
            mean_spend = random.uniform(200, 3500)  # avg transaction amount in INR
            std_spend = mean_spend * random.uniform(0.3, 0.7)
            
            start_hour = random.randint(7, 10)
            end_hour = random.randint(21, 23)
            
            known_payees = [
                f"merchant_{j}@{random.choice(banks).lower()}" for j in range(random.randint(3, 12))
            ] + [f"friend_{j}@{random.choice(banks).lower()}" for j in range(random.randint(2, 6))]
            
            users[user_id] = {
                "user_id": user_id,
                "name": name,
                "vpa": vpa,
                "bank": bank,
                "mean_spend": mean_spend,
                "std_spend": std_spend,
                "active_hours": (start_hour, end_hour),
                "known_payees": known_payees,
                "account_created_days_ago": random.randint(180, 1200),
                "nominee_name": f"{random.choice(first_names)} {name.split()[1]} (Nominee)",
                "nominee_phone": f"+91 98{random.randint(10000000, 99999999)}"
            }
        return users

    def generate_normal_transaction(self, user_id, timestamp=None):
        """Generates a normal user transaction payload aligned with baseline user habits."""
        user = self.users.get(user_id, list(self.users.values())[0])
        if timestamp is None:
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 10000))

        amount = max(50.0, round(random.lognormvariate(math.log(user["mean_spend"]), 0.4), 2))
        
        is_known_payee = random.random() < 0.95
        if is_known_payee:
            payee_vpa = random.choice(user["known_payees"])
            payee_age_days = random.randint(30, 500)
            payee_graph_distance = 1
        else:
            payee_vpa = f"new_merchant_{random.randint(100,999)}@{user['bank'].lower()}"
            payee_age_days = random.randint(10, 180)
            payee_graph_distance = 2

        time_since_last_tx = random.randint(1800, 86400 * 3)
        hourly_tx_count = random.randint(0, 2)
        
        session_telemetry = {
            "active_phone_call": False,
            "call_duration_minutes": 0,
            "screen_sharing_active": False,
            "pasted_payee_vpa": False,
            "app_switch_count_last_2min": random.randint(0, 1),
            "typing_speed_wpm": random.randint(35, 65),
            "hesitation_latency_ms": random.randint(800, 2500)
        }
        
        payee_novelty = {
            "is_first_time_payee": not is_known_payee,
            "payee_account_age_days": payee_age_days,
            "graph_distance": payee_graph_distance,
            "beneficiary_added_minutes_ago": random.randint(120, 10000) if is_known_payee else random.randint(15, 1440)
        }
        
        amount_zscore = round((amount - user["mean_spend"]) / (user["std_spend"] + 1e-5), 2)
        
        return {
            "id": f"pay_norm_{random.randint(100000, 999999)}",
            "entity": "payment",
            "amount": amount,
            "currency": "INR",
            "status": "authorized",
            "order_id": f"order_synth_{random.randint(10000, 99999)}",
            "method": "upi",
            "payer": {
                "user_id": user["user_id"],
                "vpa": user["vpa"],
                "name": user["name"],
                "nominee_name": user.get("nominee_name"),
                "nominee_phone": user.get("nominee_phone"),
                "historical_mean_spend": user["mean_spend"],
                "historical_std_spend": user["std_spend"],
                "historical_max_spend": user["mean_spend"] * 4.5
            },
            "payee": {
                "vpa": payee_vpa,
                "name": payee_vpa.split('@')[0].replace('_', ' ').title()
            },
            "timestamp": timestamp.isoformat(),
            "telemetry": {
                "velocity": {
                    "time_since_last_tx_sec": time_since_last_tx,
                    "hourly_tx_count": hourly_tx_count,
                    "amount_zscore": amount_zscore,
                    "rolling_6hr_vol": amount
                },
                "payee_novelty": payee_novelty,
                "session": session_telemetry,
                "temporal": {
                    "hour_of_day": timestamp.hour,
                    "day_of_week": timestamp.weekday(),
                    "is_outside_habitual_hours": not (user["active_hours"][0] <= timestamp.hour <= user["active_hours"][1])
                }
            },
            "label": "NORMAL"
        }

    def generate_scam_transaction(self, user_id, scenario_type="DIGITAL_ARREST"):
        """Generates a synthetic scam-induced panic transfer sequence."""
        user = self.users.get(user_id)
        if not isinstance(user, dict):
            user = list(self.users.values())[0]
        timestamp = datetime.now()
        
        if scenario_type == "DIGITAL_ARREST":
            amount = round(user["mean_spend"] * random.uniform(8.0, 25.0), 2)
            amount = min(98500.0, max(45000.0, amount))
            payee_vpa = f"rbi.verify.mule_{random.randint(10,99)}@cybercell"
            
            session_telemetry = {
                "active_phone_call": True,
                "call_duration_minutes": random.randint(45, 180),
                "screen_sharing_active": random.choice([True, False]),
                "pasted_payee_vpa": True,
                "app_switch_count_last_2min": random.randint(4, 9),
                "typing_speed_wpm": random.randint(85, 120),
                "hesitation_latency_ms": random.randint(4500, 12000)
            }
            
            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(1, 3),
                "graph_distance": 5,
                "beneficiary_added_minutes_ago": random.randint(1, 4)
            }
            
            time_since_last_tx = random.randint(40, 180)
            hourly_tx_count = random.randint(3, 7)
            
        elif scenario_type == "AI_VOICE_CLONE":
            amount = round(user["mean_spend"] * random.uniform(5.0, 15.0), 2)
            amount = max(35000.0, amount)
            payee_vpa = f"emergency.bail.advocates@{random.choice(['icici', 'axis'])}"
            
            session_telemetry = {
                "active_phone_call": True,
                "call_duration_minutes": random.randint(3, 12),
                "screen_sharing_active": False,
                "pasted_payee_vpa": True,
                "app_switch_count_last_2min": random.randint(3, 6),
                "typing_speed_wpm": random.randint(90, 140),
                "hesitation_latency_ms": random.randint(3000, 8000)
            }
            
            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(2, 7),
                "graph_distance": 4,
                "beneficiary_added_minutes_ago": random.randint(2, 8)
            }
            
            time_since_last_tx = random.randint(60, 300)
            hourly_tx_count = random.randint(2, 4)

        elif scenario_type == "REMOTE_ACCESS":
            amount = round(user["mean_spend"] * random.uniform(6.0, 18.0), 2)
            payee_vpa = f"refund.desk.agent{random.randint(100,999)}@sbi"
            
            session_telemetry = {
                "active_phone_call": True,
                "call_duration_minutes": random.randint(15, 45),
                "screen_sharing_active": True,
                "pasted_payee_vpa": True,
                "app_switch_count_last_2min": random.randint(5, 12),
                "typing_speed_wpm": random.randint(20, 40),
                "hesitation_latency_ms": random.randint(6000, 15000)
            }
            
            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(1, 5),
                "graph_distance": 5,
                "beneficiary_added_minutes_ago": random.randint(1, 5)
            }
            
            time_since_last_tx = random.randint(30, 120)
            hourly_tx_count = random.randint(3, 6)

        elif scenario_type == "OTP_SHARE":
            # Victim verbally reading OTP to scammer on call → rapid small transfers
            amount = round(random.uniform(1000.0, 8000.0), 2)
            payee_vpa = f"otp.verify.relay_{random.randint(10,99)}@{random.choice(['paytm', 'phonepe'])}"

            session_telemetry = {
                "active_phone_call": True,
                "call_duration_minutes": random.randint(5, 20),
                "screen_sharing_active": False,
                "pasted_payee_vpa": True,
                # Very low hesitation — victim follows instructions with confidence
                "app_switch_count_last_2min": random.randint(3, 7),
                "typing_speed_wpm": random.randint(70, 110),
                "hesitation_latency_ms": random.randint(600, 1500)
            }

            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(1, 10),
                "graph_distance": 4,
                "beneficiary_added_minutes_ago": random.randint(1, 6)
            }

            time_since_last_tx = random.randint(120, 600)
            hourly_tx_count = random.randint(2, 5)

        elif scenario_type == "KYC_FREEZE_THREAT":
            # Fake bank helpline: "Your account will be suspended unless you transfer to verify"
            amount = round(user["mean_spend"] * random.uniform(3.0, 10.0), 2)
            amount = min(50000.0, max(8000.0, amount))
            payee_vpa = f"kyc.verify.suspend_{random.randint(10,99)}@{random.choice(['sbi', 'hdfc', 'icici'])}"

            session_telemetry = {
                "active_phone_call": True,
                "call_duration_minutes": random.randint(8, 30),
                "screen_sharing_active": random.choice([False, False, True]),
                "pasted_payee_vpa": True,
                # High hesitation — victim is nervous about account suspension threat
                "app_switch_count_last_2min": random.randint(2, 5),
                "typing_speed_wpm": random.randint(30, 55),
                "hesitation_latency_ms": random.randint(5000, 14000)
            }

            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(1, 7),
                "graph_distance": 5,
                "beneficiary_added_minutes_ago": random.randint(1, 8)
            }

            time_since_last_tx = random.randint(60, 300)
            hourly_tx_count = random.randint(1, 3)

        elif scenario_type == "INVESTMENT_FRAUD":
            # Social media seeded: victim voluntarily sends repeated transfers to "investment platform"
            # No active call — victim is not under direct coercion during transfer
            amount = round(user["mean_spend"] * random.uniform(4.0, 12.0), 2)
            amount = min(80000.0, max(10000.0, amount))
            payee_vpa = f"invest.profit.{random.choice(['groww', 'zerodha', 'returns'])}_fake_{random.randint(10,99)}@axis"

            session_telemetry = {
                "active_phone_call": False,         # No call — social engineering happened earlier
                "call_duration_minutes": 0,
                "screen_sharing_active": False,
                "pasted_payee_vpa": True,           # VPA sent via WhatsApp link
                "app_switch_count_last_2min": random.randint(5, 10),  # WhatsApp ↔ UPI switching
                "typing_speed_wpm": random.randint(40, 65),
                "hesitation_latency_ms": random.randint(1500, 4000)
            }

            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(3, 20),
                "graph_distance": 4,
                "beneficiary_added_minutes_ago": random.randint(5, 30)
            }

            time_since_last_tx = random.randint(600, 3600)
            hourly_tx_count = random.randint(1, 2)

        else: # MICRO_COERCION
            amount = round(random.uniform(500.0, 1800.0), 2)
            payee_vpa = f"verification_fee_{random.randint(10,99)}@paytm"
            
            session_telemetry = {
                "active_phone_call": True,
                "call_duration_minutes": random.randint(20, 60),
                "screen_sharing_active": False,
                "pasted_payee_vpa": False,
                "app_switch_count_last_2min": random.randint(1, 3),
                "typing_speed_wpm": random.randint(40, 60),
                "hesitation_latency_ms": random.randint(1200, 2800)
            }
            
            payee_novelty = {
                "is_first_time_payee": True,
                "payee_account_age_days": random.randint(15, 60),
                "graph_distance": 3,
                "beneficiary_added_minutes_ago": random.randint(10, 30)
            }
            
            time_since_last_tx = random.randint(300, 1800)
            hourly_tx_count = random.randint(1, 2)

        amount_zscore = round((amount - user["mean_spend"]) / (user["std_spend"] + 1e-5), 2)

        return {
            "id": f"pay_scam_{random.randint(100000, 999999)}",
            "entity": "payment",
            "amount": amount,
            "currency": "INR",
            "status": "authorized",
            "order_id": f"order_scam_{random.randint(10000, 99999)}",
            "method": "upi",
            "payer": {
                "user_id": user["user_id"],
                "vpa": user["vpa"],
                "name": user["name"],
                "nominee_name": user.get("nominee_name"),
                "nominee_phone": user.get("nominee_phone"),
                "historical_mean_spend": user["mean_spend"],
                "historical_std_spend": user["std_spend"],
                "historical_max_spend": user["mean_spend"] * 4.5
            },
            "payee": {
                "vpa": payee_vpa,
                "name": payee_vpa.split('@')[0].replace('.', ' ').title()
            },
            "timestamp": timestamp.isoformat(),
            "telemetry": {
                "velocity": {
                    "time_since_last_tx_sec": time_since_last_tx,
                    "hourly_tx_count": hourly_tx_count,
                    "amount_zscore": amount_zscore,
                    "rolling_6hr_vol": amount * 1.1
                },
                "payee_novelty": payee_novelty,
                "session": session_telemetry,
                "temporal": {
                    "hour_of_day": timestamp.hour,
                    "day_of_week": timestamp.weekday(),
                    "is_outside_habitual_hours": random.choice([True, False])
                }
            },
            "label": "SCAM",
            "scenario": scenario_type
        }

    def generate_mule_network_graph(self, scam_tx=None):
        """
        Generates an interactive multi-hop mule account network graph
        demonstrating rapid dissipation across Razorpay Route escrow layers.
        """
        if scam_tx is None:
            scam_tx = self.generate_scam_transaction("cust_synth_0001", "DIGITAL_ARREST")

        payer_name = scam_tx.get("payer", {}).get("name", "Priya Sharma")
        amount = scam_tx.get("amount", 85000.0)

        nodes = [
            {
                "id": "node_payer",
                "label": f"{payer_name} (Victim)",
                "type": "victim",
                "vpa": scam_tx.get("payer", {}).get("vpa", "victim@pnb"),
                "bank": "PNB Bank",
                "account_age": "3.2 Years",
                "risk_score": 5,
                "status": "SOURCE_COERCED",
                "x": 60,
                "y": 200
            },
            {
                "id": "node_mule_1",
                "label": "Mule Layer 1 (CBI Fake Handle)",
                "type": "mule_primary",
                "vpa": scam_tx.get("payee", {}).get("vpa", "rbi.verify.mule@cybercell"),
                "bank": "CyberCell Escrow (Mule)",
                "account_age": "2 Days Old",
                "risk_score": 96,
                "status": "FLAGGED_INTERCEPTED",
                "x": 240,
                "y": 120
            },
            {
                "id": "node_mule_2a",
                "label": "Mule Layer 2A (Crypto Shard)",
                "type": "mule_hop",
                "vpa": "crypto.escrow.relay@axis",
                "bank": "Axis Bank",
                "account_age": "4 Days Old",
                "risk_score": 92,
                "status": "FROZEN_GUARDRAIL",
                "x": 440,
                "y": 80
            },
            {
                "id": "node_mule_2b",
                "label": "Mule Layer 2B (P2P Split)",
                "type": "mule_hop",
                "vpa": "fast.settle.p2p@kotak",
                "bank": "Kotak Bank",
                "account_age": "1 Day Old",
                "risk_score": 89,
                "status": "FROZEN_GUARDRAIL",
                "x": 440,
                "y": 240
            },
            {
                "id": "node_cashout",
                "label": "Off-Ramp Cashout (ATM / USDT Hub)",
                "type": "cashout",
                "vpa": "offramp.cashout.terminal@dubai",
                "bank": "International USDT Relay",
                "account_age": "N/A",
                "risk_score": 99,
                "status": "PREVENTED_BY_SENTINEL",
                "x": 650,
                "y": 160
            }
        ]

        links = [
            {
                "source": "node_payer",
                "target": "node_mule_1",
                "amount": f"₹{amount:,.2f}",
                "hop_latency": "T+0s (Coerced Checkout)",
                "alert": True,
                "status": "BLOCKED"
            },
            {
                "source": "node_mule_1",
                "target": "node_mule_2a",
                "amount": f"₹{round(amount * 0.55):,.2f}",
                "hop_latency": "T+42s (Rapid Relay)",
                "alert": True,
                "status": "PREVENTED"
            },
            {
                "source": "node_mule_1",
                "target": "node_mule_2b",
                "amount": f"₹{round(amount * 0.45):,.2f}",
                "hop_latency": "T+55s (Rapid Relay)",
                "alert": True,
                "status": "PREVENTED"
            },
            {
                "source": "node_mule_2a",
                "target": "node_cashout",
                "amount": f"₹{round(amount * 0.55):,.2f}",
                "hop_latency": "T+110s (Cashout Attempt)",
                "alert": True,
                "status": "PREVENTED"
            },
            {
                "source": "node_mule_2b",
                "target": "node_cashout",
                "amount": f"₹{round(amount * 0.45):,.2f}",
                "hop_latency": "T+135s (Cashout Attempt)",
                "alert": True,
                "status": "PREVENTED"
            }
        ]

        return {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "source_amount": amount,
            "estimated_time_to_cashout_sec": 135,
            "route_guardrail_action": "RAZORPAY_ROUTE_SETTLEMENT_HOLD",
            "nodes": nodes,
            "links": links,
            "protection_summary": f"SentinelUPI intercepted ₹{amount:,.2f} at Hop 1 (T+0s), preventing multi-layer dissipation across 3 mule accounts before final cashout."
        }

    def generate_dataset(self, normal_count=10000, scam_count=500):
        """Generates synthetic dataset of normal and scam transactions."""
        dataset = []
        user_ids = list(self.users.keys())
        
        for _ in range(normal_count):
            u_id = random.choice(user_ids)
            dataset.append(self.generate_normal_transaction(u_id))
            
        scam_types = ["DIGITAL_ARREST", "AI_VOICE_CLONE", "REMOTE_ACCESS", "MICRO_COERCION",
                      "OTP_SHARE", "KYC_FREEZE_THREAT", "INVESTMENT_FRAUD"]
        for _ in range(scam_count):
            u_id = random.choice(user_ids)
            s_type = random.choice(scam_types)
            dataset.append(self.generate_scam_transaction(u_id, scenario_type=s_type))
            
        random.shuffle(dataset)
        return dataset

if __name__ == "__main__":
    client = RazorpaySyntheticClient()
    mule_graph = client.generate_mule_network_graph()
    print("--- Mule Network Flow Graph Generated ---")
    print(f"Nodes: {mule_graph['total_nodes']} | Links: {mule_graph['total_links']}")
    print(mule_graph["protection_summary"])
