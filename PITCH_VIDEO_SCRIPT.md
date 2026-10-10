# SentinelUPI — 5-Minute Pitch Video Script

**Track**: Razorpay AI Buildathon 2026 — Track 02: AI Risk Manager  
**Project**: SentinelUPI — Scam-Induced Transfer Detector

---

## 🎬 SCENE 1: The Invisible UPI Scam Epidemic (0:00 – 1:00)

**[Visual: Presenter on camera + slides showing official graphics of Ministry of Finance and I4C numbers]**

**Speaker Script**:
> "In FY26 through November, Indians lost **₹805 crore across 10.64 lakh reported cases** of UPI fraud, according to the Ministry of Finance. The RBI's Annual Report highlights a staggering **34% year-on-year increase** in digital payment fraud.
>
> But the most dangerous threat in 2026 isn't stolen PINs or phishing links. It's **panic-induced transfers** — specifically Digital Arrest coercion and AI Voice-Cloning scams. In just the first 5 months of 2026, the Indian Cybercrime Coordination Centre (I4C) recorded **15,215 complaints** of digital arrest and voice cloning. Scammers clone a child's voice claiming an emergency, or impersonate police on video calls for hours.
>
> Here's the catch: once money leaves a UPI account, the **recovery rate is barely 6%**. Pre-transfer anomaly detection — stopping the payment *before* the money leaves — is the only real lever left."

---

## 💳 SCENE 2: Why Razorpay (1:00 – 1:45)

**[Visual: Diagram showing Razorpay PG, Razorpay Route, and Optimizer integration]**

**Speaker Script**:
> "Why is this a Razorpay problem, and not just a public-good issue?
>
> When a victim transfers ₹85,000 under panic through a Razorpay-integrated app or payment link, platform trust is shattered — even if Razorpay wasn't legally at fault.
>
> Undetected panic fraud triggers chargebacks, payment disputes, and merchant churn. By integrating **SentinelUPI into Razorpay AI Risk Manager**, Razorpay gives merchants an intelligent guardrail that preserves user trust, slashes dispute handling costs, and can even freeze mule payouts in **Razorpay Route**."

---

## 💻 SCENE 3: Technical Architecture & Live Product Demo (1:45 – 3:30)

**[Visual: Screen share of SentinelUPI Web Dashboard: Tab 1 (Waterfall), Tab 2 (Mule Graph), and Tab 3 (Dual-Phone Simulator)]**

**Speaker Script**:
> "SentinelUPI evaluates transactions without inspecting private message content. We extract a 20-dimensional non-content behavioral telemetry matrix.
>
> Our model stack combines two engines:
> 1. **Isolation Forest** for tree isolation depth.
> 2. **LSTM Autoencoder** sequence model measuring reconstruction error for behavioral drift: *'This does not look like how this person normally pays.'*
>
> Let's look at the live demo!
>
> In our **Scam Simulator**, selecting the **Digital Arrest Scam** evaluates the telemetry in just **0.36 milliseconds**, outputting an **88/100 Critical Risk Score**.
>
> Our **SHAP Waterfall Engine** maps the exact mathematical trajectory from base risk (10) up to 88, while our **Counterfactual Engine** computes: *'If the call is disconnected and payee verified, risk drops to 18 (Safe Auto-Approve)'*.
>
> On our **Mule Account Graph**, you can see the fund flow across 3 mule layers before cashout, with a single button to **Freeze Razorpay Route Settlements**.
>
> And in our **Dual-Phone Guardrail**, when the victim attempts to pay, the **Trusted Nominee's smartphone receives an instant push alert**. Clicking 'Intercept' immediately cancels the transfer and protects the funds!"

---

## 📊 SCENE 4: Held-Out Metrics & False Positive Analysis (3:30 – 4:15)

**[Visual: Slides showing performance table and ROC-AUC curve]**

**Speaker Script**:
> "We evaluated SentinelUPI on a held-out test set of 2,100 synthetic transaction sequences:
> - **Precision**: 84.4%
> - **Recall**: 92.0%
> - **False Positive Rate**: 0.85% (17 out of 2,000 normal transfers flagged)
> - **ROC-AUC**: 0.965
> - **Inference Latency**: 0.36 ms
>
> What does an **0.85% FPR** mean in practice? Out of 1,000 legitimate UPI transactions, ~8 users encounter step-up verification. If a user is paying a hospital bill late at night while on call with family, a false positive creates friction.
>
> To mitigate this, SentinelUPI uses graduated friction: Medium Risk triggers a zero-delay soft warning banner, while High Risk allows one-click nominee override."

---

## 🛠️ SCENE 5: What Broke During Development & How We Fixed It (4:15 – 5:00)

**[Visual: Slide showing the False Negative Failure Case study diagram]**

**Speaker Script**:
> "Finally, let's talk about **what broke during development**.
>
> In our initial model iteration, we tested a **Micro-Coercion Sharding attack** where scammers coerced victims into transferring small test amounts — ₹500, then ₹1,200 — across 3 hours.
>
> Our model **missed these transactions (False Negative)** because individual transfer amounts had low $Z$-scores ($\approx 0.4\sigma$), bypassing single-transaction thresholds.
>
> **How we fixed it**: We upgraded our sequence feature pipeline to incorporate **rolling 6-hour temporal window aggregation**, accumulating multi-step velocity and total session transfer volume. On re-evaluation, SentinelUPI caught 100% of sharded micro-coercion sequences.
>
> SentinelUPI protects user funds *before* they leave. Thank you!"
