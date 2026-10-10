# SentinelUPI — Technical Architecture & System Data Flow

**Track**: Razorpay AI Buildathon 2026 — Track 02: AI Risk Manager  
**Project**: SentinelUPI — Scam-Induced Transfer Behavioral Detector

---

## 1. High-Level Data Flow Diagram (Mermaid)

```mermaid
graph TD
    subgraph Client_Telemetry["📱 Client Session Telemetry (Non-Content)"]
        A1["Active Phone Call Status & Duration"]
        A2["Clipboard Pasted Payee VPA"]
        A3["Screen Share / Remote Desktop Active"]
        A4["PIN Entry Hesitation Latency (ms)"]
        A5["App Switch Frequency (WhatsApp ↔ UPI)"]
    end

    subgraph Transaction_Context["💳 Razorpay PG & Route Context"]
        B1["Transfer Amount & Log-Normal Z-Score"]
        B2["Payee Account Age & Novelty Index"]
        B3["Payee Graph Distance (1 to 5)"]
        B4["6-Hour Rolling Cumulative Volume"]
        B5["Mule Account Ring Network Hop Velocity"]
    end

    subgraph Feature_Pipeline["⚡ 20D Feature Pipeline (feature_pipeline.py)"]
        C1["Log-Normal Z-Score & Trigonometric Hour Embeddings"]
    end

    subgraph Dual_ML_Stack["🧠 Dual Anomaly Detection Stack"]
        D1["Isolation Forest (Tree Isolation Path Length)"]
        D2["LSTM Autoencoder (Sequence Behavioral Drift MSE)"]
    end

    subgraph XAI_Layer["🔍 SHAP Explainability & Counterfactual Layer"]
        E1["Shapley Additive Value Attribution (phi_i)"]
        E2["Mathematical Waterfall Trajectory: Base + sum(phi_i)"]
        E3["Counterfactual What-If Remediation Analysis"]
    end

    subgraph Intervention_Engine["🛡️ Graduated Protective Interventions (Razorpay PG)"]
        F1{"Composite Risk Score (0-100)"}
        G1["LOW (0-29): Auto-Approve Payment"]
        G2["MEDIUM (30-64): Soft Coercion Warning Banner"]
        G3["HIGH (65-84): 15-Min Cooling Off & Nominee Push Alert"]
        G4["CRITICAL (85-100): Hard Intercept & Razorpay Route Payout Freeze"]
    end

    A1 & A2 & A3 & A4 & A5 --> C1
    B1 & B2 & B3 & B4 & B5 --> C1

    C1 --> D1
    C1 --> D2

    D1 -->|Isolation Score| F1
    D2 -->|Reconstruction MSE| F1

    F1 --> E1
    E1 --> E2
    E1 --> E3

    F1 -->|Score < 30| G1
    F1 -->|30 <= Score < 65| G2
    F1 -->|65 <= Score < 85| G3
    F1 -->|Score >= 85| G4
```

---

## 2. Razorpay Guardrail Architecture & Payout Defense

```
+-------------------------------------------------------------------------------+
|                    Client Session & Transaction Telemetry                     |
|  [ Active Call ]  [ Screen Share ]  [ Pasted VPA ]  [ Hesitation Latency ]    |
+--------------------------------──────┬----------------------------------------+
                                       │
                                       ▼
+-------------------------------------------------------------------------------+
|               Feature Engineering Pipeline (feature_pipeline.py)              |
|  Normalizes 20 non-content behavioral telemetry features into [0, 1]          |
+--------------------------------──────┬----------------------------------------+
                                       │
          ┌────────────────────────────┴────────────────────────────┐
          ▼                                                         ▼
+-------------------------------------+   +-------------------------------------+
|      Isolation Forest Baseline      |   |       LSTM Autoencoder Model        |
|    (Tree isolation path length)     |   |    (Sequence reconstruction MSE)    |
+----------------─┬───────────────────+   +----------------─┬───────────────────+
                  └─────────────────────┬───────────────────┘
                                        ▼
+-------------------------------------------------------------------------------+
|            SHAP Explainability & What-If Layer (shap_explainability.py)       |
|  • Mathematical Waterfall: Base Risk (10.0) + sum(phi_i) -> Final Score       |
|  • Counterfactual Remediation: "If call ends & payee verified, risk -> 18"    |
+--------------------------------──────┬----------------------------------------+
                                       │
                                       ▼
+-------------------------------------------------------------------------------+
|                     Razorpay AI Risk Manager Interventions                    |
|  • LOW (0-29): Auto-Approve                                                   |
|  • MEDIUM (30-64): Soft Phone-Call Warning Banner                             |
|  • HIGH (65-84): 15-Min Cooling Off & Emergency Nominee Push Alert            |
|  • CRITICAL (85-100): Hard Intercept & Razorpay Route Settlement Freeze       |
+-------------------------------------------------------------------------------+
```

---

## 3. Defense-Only Framing

SentinelUPI operates exclusively as an inline guardrail within Razorpay AI Risk Manager to detect, intercept, and mitigate panic coercion fraud. No evasion methodologies or exploitation techniques are demonstrated.
