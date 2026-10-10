# BeforePay — Behavioral Risk Detection for UPI Transfers

[![Live Demo](https://img.shields.io/badge/Demo-Live_on_Render-brightgreen?style=for-the-badge&logo=render)](https://razorpay-jsma.onrender.com/)

> **Track**: Razorpay AI Buildathon 2026 — Track 02: AI Risk Manager  
> Detects the behavioral fingerprint of a scam-induced panic transfer (e.g., "digital arrest" and AI voice-cloning scams) before money leaves, using non-content behavioral anomaly detection, SHAP waterfall explainability, and multi-hop mule ring analysis.

---

## 📚 Document Quick Links
- 🌐 **[Live Deployed App (Render)](https://razorpay-jsma.onrender.com/)**
- 🗺️ **[System Architecture & Data Flow Diagram](ARCHITECTURE.md)**
- 📊 **[Held-Out Benchmark Results](dataset_eval_results.json)**
- ⚡ **[Feature Engineering Pipeline](feature_pipeline.py)**

---

## 1. Problem Context & Citations

- **UPI Fraud Scale**: **₹805 crore lost across 10.64 lakh reported cases** in FY26 through November *(Source: Ministry of Finance)*.
- **Fraud Growth**: **34% year-on-year increase** in digital payment fraud cases *(Source: RBI 2024-25 Annual Report)*.
- **The Irreversibility Problem**: **~6% recovery rate of stolen funds** once money leaves an account — **pre-transfer real-time anomaly detection is the only viable defense lever**.
- **Digital Arrest & AI Voice-Cloning Scams**: **15,215 complaints** in just the first 5 months of 2026 *(Source: Indian Cybercrime Coordination Centre - I4C / Ministry of Home Affairs)*.
- *Source Note*: Primary figures cited from I4C/MHA & Ministry of Finance.

---

## 2. Why Razorpay (Platform Trust & Merchant Retention)

Scam-drained transfers routed through Razorpay-integrated apps and payment links severely damage user trust and merchant reputation, even when Razorpay is not at fault. 
Furthermore, undetected panic fraud surges increase dispute management and chargeback overhead for merchants. Positioning **BeforePay** as a turn-key API guardrail inside **Razorpay AI Risk Manager** protects merchant checkout flows, freezes mule payouts in Razorpay Route, and significantly increases merchant retention.

---

## 3. Key Upgrades & Hackathon Features

1. **Mathematical SHAP Waterfall Trajectory**: Visually proves $R(x) = Base\_Risk + \sum \phi_i$, mapping positive feature risk pushes.
2. **Counterfactual "What-If" Engine**: Calculates actionable step-by-step guidance to make high-risk transactions safe.
3. **Mule Account Ring Network Graph**: Traces rapid multi-layer dissipation ($Victim \rightarrow Mule_1 \rightarrow Mule_2 \rightarrow Cashout$) and triggers Razorpay Route settlement freezes.
4. **Two-Sided Phone Guardrail Simulation**: Side-by-side simulation of Victim Checkout (15-min cooling lock) + Nominee Phone (live push alert with one-click interception).
5. **Merchant Policy Studio & 3-Line Drop-In SDK**: Customizable risk thresholds and official **CERT-In / RBI Forensic Audit Report** downloads.
6. **Live Operations NOC Stream**: Auto-ticking live stream ticker with <0.4ms latency counter.

---

## 4. Model Performance & Evaluation Metrics

Evaluated on a held-out test set of 2,100 synthetic transaction sequences (2,000 normal baseline + 100 injected scam sequences):

| Metric | Held-Out Performance | Description |
| :--- | :---: | :--- |
| **Precision** | **84.4%** | $\frac{92}{92 + 17}$ high confidence on flagged transfers |
| **Recall** | **92.0%** | $\frac{92}{92 + 8}$ catch rate for coercion & voice clone scams |
| **False Positive Rate (FPR)** | **0.85%** | 17 out of 2,000 normal transfers flagged |
| **ROC-AUC** | **0.965** | Strong separation between normal & scam sequences |
| **Avg Detection Latency** | **0.36 ms** | Real-time inline processing before UPI PIN execution |

---

## 5. False-Positive Cost & Friction Analysis

- **Production Impact of 0.85% FPR**: Out of 1,000 legitimate UPI transactions, ~8 users encounter a protective step-up verification.
- **User Disruption**: A false positive on a legitimate urgent payment (e.g., paying a hospital bill late at night while on a phone call with family) risks causing user friction.
- **Mitigation via Graduated Friction**: BeforePay avoids rigid transaction blocking. Medium Risk (30-64) triggers a non-blocking soft warning banner (0-second delay). High Risk (65-84) initiates a 15-minute cooling-off lock with **one-click emergency nominee confirmation override**.

---

## 6. Honest Failure Case Analysis

1. **False Negative (Missed Scam — Low-Amount Micro-Coercion Sharding)**:
   - *Pattern*: Scammer instructs victim to send small test amounts (₹500, ₹1,200) over 3 hours while keeping them on call.
   - *Why Model Missed*: Amount Z-score remained low ($\approx 0.4\sigma$), bypassing single-transaction score thresholds.
   - *Fix / Learning*: Added multi-step temporal window aggregation across rolling 6-hour windows to track cumulative loss velocity.
2. **False Positive (False Alarm — Late-Night Legitimate Used Vehicle Purchase)**:
   - *Pattern*: User buying a used car (₹80,000) late at night while discussing delivery details on a phone call with the seller.
   - *Why Model Flagged*: High Payee Novelty + 7.5$\sigma$ Amount Deviation + Active Phone Call triggered High Risk score (82/100).
   - *Fix / Learning*: Incorporate merchant/VPA trust score verification (distinguishing verified escrow handles from unverified handles).

---

## 7. Quickstart & Local Setup

### Requirements
- Python 3.13 (or Python 3.8+)
- Modern Web Browser (Chrome, Edge, Firefox)

### Run Server & Web Dashboard
```bash
# 1. Start backend server
python server.py
```
Open *https://razorpay-jsma.onrender.com/* in your browser to experience the BeforePay Dashboard!
