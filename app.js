/* 
  SentinelUPI — Razorpay AI Risk Manager Web App Controller
  Razorpay AI Buildathon 2026 - Track 02: AI Risk Manager
*/

const API_BASE = "http://localhost:8000/api/v1";
let currentScenario = 'DIGITAL_ARREST';
let autoStreamInterval = null;
let currentMuleGraph = null;

// Tab Switching
function switchTab(tabId, event) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  if (event && event.target) {
    event.target.classList.add('active');
  } else {
    const btn = document.querySelector(`button[onclick*="${tabId}"]`);
    if (btn) btn.classList.add('active');
  }

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) {
    targetTab.classList.add('active');
  }

  if (tabId === 'livestream') {
    refreshLiveStream();
  } else if (tabId === 'mule-graph') {
    loadMuleGraph();
  }
}

// Preset Scenario Loader
function loadScenario(type) {
  currentScenario = type;
  document.querySelectorAll('.preset-card').forEach(card => card.classList.remove('active'));
  
  const presetMap = {
    'DIGITAL_ARREST': { card: 'preset-digital-arrest', call: true, paste: true, share: false, amount_z: 8.5, age: 2, hesitation: 6500, payee: 'rbi.verify.mule@cybercell', amount: 85000 },
    'AI_VOICE_CLONE': { card: 'preset-voice-clone', call: true, paste: true, share: false, amount_z: 6.0, age: 5, hesitation: 4500, payee: 'emergency.bail.advocates@icici', amount: 45000 },
    'REMOTE_ACCESS': { card: 'preset-remote-access', call: true, paste: true, share: true, amount_z: 7.0, age: 1, hesitation: 8000, payee: 'refund.desk.agent206@sbi', amount: 38000 },
    'OTP_SHARE': { card: 'preset-otp-share', call: true, paste: true, share: false, amount_z: 1.8, age: 3, hesitation: 800, payee: 'otp.verify.relay_42@paytm', amount: 3500 },
    'KYC_FREEZE_THREAT': { card: 'preset-kyc-freeze', call: true, paste: true, share: false, amount_z: 4.2, age: 4, hesitation: 9500, payee: 'kyc.verify.suspend_18@sbi', amount: 15000 },
    'INVESTMENT_FRAUD': { card: 'preset-investment', call: false, paste: true, share: false, amount_z: 5.5, age: 12, hesitation: 2800, payee: 'invest.profit.returns_fake_99@axis', amount: 25000 },
    'MICRO_COERCION': { card: 'preset-micro-coercion', call: true, paste: false, share: false, amount_z: 0.4, age: 30, hesitation: 1800, payee: 'verification_fee_94@paytm', amount: 1200 },
    'NORMAL': { card: 'preset-normal', call: false, paste: false, share: false, amount_z: 0.2, age: 120, hesitation: 1200, payee: 'merchant_6@icici', amount: 1450 }
  };

  const config = presetMap[type] || presetMap['DIGITAL_ARREST'];
  
  const cardElem = document.getElementById(config.card);
  if (cardElem) cardElem.classList.add('active');

  document.getElementById('input-active-call').checked = config.call;
  document.getElementById('input-pasted-vpa').checked = config.paste;
  document.getElementById('input-screen-share').checked = config.share;
  document.getElementById('input-amount-z').value = config.amount_z;
  document.getElementById('input-payee-age').value = config.age;
  document.getElementById('input-hesitation').value = config.hesitation;

  // Update checkout preview
  const cp = document.getElementById('checkout-payee');
  const ca = document.getElementById('checkout-amount');
  if (cp) cp.innerText = config.payee;
  if (ca) ca.innerText = `₹${config.amount.toLocaleString()}`;

  runEvaluation();
  if (document.getElementById('tab-mule-graph').classList.contains('active')) {
    loadMuleGraph();
  }
}

// Interactive Real-Time Evaluation
async function runEvaluation() {
  const call = document.getElementById('input-active-call').checked;
  const paste = document.getElementById('input-pasted-vpa').checked;
  const share = document.getElementById('input-screen-share').checked;
  const amountZ = parseFloat(document.getElementById('input-amount-z').value);
  const payeeAge = parseInt(document.getElementById('input-payee-age').value);
  const hesitation = parseInt(document.getElementById('input-hesitation').value);

  // Update slider labels
  const approxAmount = Math.round(amountZ * 10000 + 5000);
  document.getElementById('val-amount-z').innerText = `${amountZ}σ (₹${approxAmount.toLocaleString()})`;
  document.getElementById('val-payee-age').innerText = `${payeeAge} Day${payeeAge > 1 ? 's' : ''} ${payeeAge < 7 ? '(Brand New Mule)' : ''}`;
  document.getElementById('val-hesitation').innerText = `${hesitation} ms ${hesitation > 5000 ? '(Severe Hesitation)' : ''}`;

  const payload = {
    amount: approxAmount,
    telemetry: {
      velocity: { amount_zscore: amountZ, time_since_last_tx_sec: call ? 120 : 3600, hourly_tx_count: call ? 4 : 0, rolling_6hr_vol: approxAmount * 1.1 },
      session: { active_phone_call: call, pasted_payee_vpa: paste, screen_sharing_active: share, hesitation_latency_ms: hesitation },
      payee_novelty: { is_first_time_payee: payeeAge < 30, payee_account_age_days: payeeAge, graph_distance: payeeAge < 10 ? 5 : 1 }
    }
  };

  const t0 = performance.now();
  try {
    const res = await fetch(`${API_BASE}/risk/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const latencyMs = (performance.now() - t0).toFixed(2);
    const latencyEl = document.getElementById('actual-latency-val');
    if (latencyEl) latencyEl.innerText = latencyMs;
    if (res.ok) {
      const data = await res.json();
      updateGaugeAndSHAP(data);
      return;
    }
  } catch (err) {
    const latencyMs = (performance.now() - t0).toFixed(2);
    const latencyEl = document.getElementById('actual-latency-val');
    if (latencyEl) latencyEl.innerText = latencyMs;
    fallbackEvaluation(call, paste, share, amountZ, payeeAge, hesitation);
  }
}

function fallbackEvaluation(call, paste, share, amountZ, payeeAge, hesitation) {
  let score = 10;
  if (call) score += 35;
  if (paste) score += 20;
  if (share) score += 30;
  if (amountZ > 3) score += Math.min(30, amountZ * 3.5);
  if (payeeAge < 7) score += 22;
  if (hesitation > 4000) score += 15;

  score = Math.min(100, Math.round(score));

  let tier = "LOW";
  let action = "AUTO_APPROVE";
  if (score >= 85) { tier = "CRITICAL_PANIC"; action = "HARD_INTERCEPT"; }
  else if (score >= 65) { tier = "HIGH"; action = "COOLING_OFF_LOCK"; }
  else if (score >= 30) { tier = "MEDIUM"; action = "SOFT_WARNING"; }

  const dummyData = {
    composite_risk_score: score,
    risk_tier: tier,
    action: action,
    waterfall_steps: [
      { label: "Base Prior Risk", contribution: 10.0, cumulative: 10.0, type: "base" },
      { label: "Active Phone Call", contribution: call ? 35.0 : 0, cumulative: call ? 45.0 : 10.0, type: "positive" },
      { label: "Unusual Amount Z-Score", contribution: Math.min(25.0, amountZ * 3.0), cumulative: Math.min(70.0, score), type: "positive" },
      { label: "Final Risk Score", contribution: score, cumulative: score, type: "total" }
    ],
    counterfactual: {
      summary: `If user terminates the active phone call and verifies payee, risk drops from ${score} to 18 (LOW - Auto-Approve).`
    },
    xai_explanation: `Flagged with ${score}/100 risk score based on behavioral anomaly inputs.`
  };
  updateGaugeAndSHAP(dummyData);
}

function updateGaugeAndSHAP(data) {
  const scoreVal = document.getElementById('risk-score-val');
  const tierVal = document.getElementById('risk-tier-val');
  const gauge = document.getElementById('risk-gauge');
  const badge = document.getElementById('risk-action-badge');
  const cfText = document.getElementById('counterfactual-text');

  scoreVal.innerText = Math.round(data.composite_risk_score);
  tierVal.innerText = data.risk_tier.replace('_', ' ');

  let colorMap = {
    'LOW': { border: '#10b981', bg: 'rgba(16, 185, 129, 0.2)', label: '✅ Proceed Safely (Auto-Approved)' },
    'MEDIUM': { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.2)', label: '⚠️ Soft Coercion Warning Banner' },
    'HIGH': { border: '#f97316', bg: 'rgba(249, 115, 22, 0.2)', label: '⏳ 15-Min Cooldown & Nominee Alert' },
    'CRITICAL_PANIC': { border: '#ef4444', bg: 'rgba(239, 68, 68, 0.25)', label: '🚨 Panic Transfer Intercepted' }
  };

  const theme = colorMap[data.risk_tier] || colorMap['LOW'];
  gauge.style.borderColor = theme.border;
  gauge.style.boxShadow = `0 0 30px ${theme.bg}`;
  scoreVal.style.color = theme.border;
  tierVal.style.color = theme.border;

  badge.innerText = theme.label;
  badge.className = `risk-badge ${data.risk_tier}`;

  if (cfText && data.counterfactual) {
    cfText.innerText = data.counterfactual.summary;
  }

  // Render SHAP Waterfall Rows
  const wfContainer = document.getElementById('shap-waterfall-container');
  if (wfContainer && data.waterfall_steps) {
    wfContainer.innerHTML = '';
    data.waterfall_steps.forEach(step => {
      const row = document.createElement('div');
      row.className = 'waterfall-row';
      const fillClass = step.type === 'base' ? 'base' : (step.type === 'total' ? 'total' : 'positive');
      row.innerHTML = `
        <span style="color:var(--text-muted); font-size:0.75rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${step.label}</span>
        <div class="wf-bar-wrapper">
          <div class="wf-bar-fill ${fillClass}" style="width: ${Math.min(100, step.cumulative)}%;"></div>
        </div>
        <span style="font-weight:700; text-align:right; color:${step.type === 'total' ? theme.border : '#ffffff'}; font-size:0.75rem;">${step.cumulative}</span>
      `;
      wfContainer.appendChild(row);
    });
  }

  // Update VPA Trust Badge
  const vpaIcon = document.getElementById('vpa-trust-icon');
  const vpaLabel = document.getElementById('vpa-trust-label');
  if (data.payee_trust && vpaLabel) {
    const tier = data.payee_trust.trust_tier;
    const icons = { 'TRUSTED': '🛡️', 'UNKNOWN': '❓', 'WATCHLIST': '🚨' };
    const colors = { 'TRUSTED': '#10b981', 'UNKNOWN': '#94a3b8', 'WATCHLIST': '#ef4444' };
    if (vpaIcon) vpaIcon.innerText = icons[tier] || '❓';
    vpaLabel.innerHTML = `<span style="color:${colors[tier] || '#fff'}; font-weight:700;">[${tier}]</span> ${data.payee_trust.reason || ''}`;
  }

  // Update Localized Guidance Alert Box
  const locBox = document.getElementById('localized-alert-box');
  const locText = document.getElementById('localized-alert-text');
  if (locBox && locText && data.localized_guidance) {
    locText.innerText = data.localized_guidance;
    locBox.style.display = 'block';
  } else if (locBox) {
    locBox.style.display = 'none';
  }

  // Record and Draw Risk Score History
  recordAndDrawScoreHistory(data.composite_risk_score, data.risk_tier);
}

// Session Score History & Sparkline Canvas
const scoreHistory = [];

function recordAndDrawScoreHistory(score, tier) {
  scoreHistory.push({
    score: Math.round(score),
    tier: tier,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  });
  if (scoreHistory.length > 12) scoreHistory.shift();

  const countEl = document.getElementById('score-history-count');
  if (countEl) countEl.innerText = `${scoreHistory.length} evaluation${scoreHistory.length > 1 ? 's' : ''}`;

  const canvas = document.getElementById('score-history-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  // Background subtle grid lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  for (let y = 15; y < h; y += 15) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  if (scoreHistory.length < 2) {
    if (scoreHistory.length === 1) {
      ctx.fillStyle = scoreHistory[0].score >= 65 ? '#ef4444' : (scoreHistory[0].score >= 30 ? '#f59e0b' : '#10b981');
      ctx.beginPath();
      ctx.arc(w / 2, h - (scoreHistory[0].score / 100) * (h - 14) - 7, 4, 0, 2 * Math.PI);
      ctx.fill();
    }
    return;
  }

  const step = (w - 30) / (scoreHistory.length - 1);
  const points = scoreHistory.map((item, i) => {
    const x = 15 + i * step;
    const y = h - 7 - (item.score / 100) * (h - 14);
    return { x, y, ...item };
  });

  // Gradient area
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, 'rgba(51, 149, 255, 0.25)');
  grad.addColorStop(1, 'rgba(51, 149, 255, 0.0)');
  ctx.beginPath();
  ctx.moveTo(points[0].x, h);
  points.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.lineTo(points[points.length - 1].x, h);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Trajectory Line
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  points.forEach(p => ctx.lineTo(p.x, p.y));
  ctx.strokeStyle = '#3395ff';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Dots
  points.forEach((p, idx) => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, idx === points.length - 1 ? 4.5 : 3, 0, 2 * Math.PI);
    let dotColor = p.score >= 65 ? '#ef4444' : (p.score >= 30 ? '#f59e0b' : '#10b981');
    ctx.fillStyle = dotColor;
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1;
    ctx.stroke();

    if (idx === points.length - 1) {
      ctx.font = 'bold 9px JetBrains Mono, monospace';
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${p.score}`, p.x - 6, p.y - 7);
    }
  });
}

// Mule Account Graph Visualizer
async function loadMuleGraph() {
  try {
    const res = await fetch(`${API_BASE}/mule-graph?scenario=${currentScenario}`);
    if (res.ok) {
      currentMuleGraph = await res.json();
      drawMuleGraph(currentMuleGraph);
    }
  } catch (err) {
    console.error("Mule graph load error:", err);
  }
}

function drawMuleGraph(graphData) {
  const canvas = document.getElementById('muleGraphCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!graphData || !graphData.nodes) return;

  // Draw links
  graphData.links.forEach(link => {
    const sNode = graphData.nodes.find(n => n.id === link.source);
    const tNode = graphData.nodes.find(n => n.id === link.target);
    if (!sNode || !tNode) return;

    ctx.beginPath();
    ctx.moveTo(sNode.x, sNode.y);
    ctx.lineTo(tNode.x, tNode.y);
    ctx.strokeStyle = link.alert ? 'rgba(239, 68, 68, 0.7)' : 'rgba(51, 149, 255, 0.4)';
    ctx.lineWidth = link.alert ? 3 : 1.5;
    ctx.setLineDash(link.alert ? [6, 4] : []);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw edge latency label
    const midX = (sNode.x + tNode.x) / 2;
    const midY = (sNode.y + tNode.y) / 2 - 8;
    ctx.fillStyle = link.alert ? '#fca5a5' : '#94a3b8';
    ctx.font = '10px Plus Jakarta Sans, sans-serif';
    ctx.fillText(`${link.amount} (${link.hop_latency})`, midX - 45, midY);
  });

  // Draw nodes
  graphData.nodes.forEach(node => {
    ctx.beginPath();
    ctx.arc(node.x, node.y, 22, 0, 2 * Math.PI);

    let fillColor = '#1e293b';
    let strokeColor = '#3395ff';
    if (node.type === 'victim') {
      fillColor = '#065f46';
      strokeColor = '#10b981';
    } else if (node.type === 'mule_primary' || node.type === 'mule_hop') {
      fillColor = '#7f1d1d';
      strokeColor = '#ef4444';
    } else if (node.type === 'cashout') {
      fillColor = '#831843';
      strokeColor = '#f43f5e';
    }

    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = strokeColor;
    ctx.stroke();

    // Node icon / text
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 11px Plus Jakarta Sans, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(node.type === 'victim' ? 'Payer' : (node.type === 'cashout' ? 'ATM' : 'Mule'), node.x, node.y + 4);

    // Node sub-label
    ctx.font = '10px Plus Jakarta Sans, sans-serif';
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(node.label, node.x, node.y + 36);

    ctx.font = '9px JetBrains Mono, monospace';
    ctx.fillStyle = node.risk_score > 60 ? '#f87171' : '#34d399';
    ctx.fillText(`Risk: ${node.risk_score}/100 • ${node.account_age}`, node.x, node.y + 49);
  });
}

function freezeMuleSettlement() {
  const statusEl = document.getElementById('route-action-status');
  if (statusEl) {
    statusEl.innerText = "🛑 ROUTE SETTLEMENT FROZEN (₹85,000)";
    statusEl.className = "g-val ruby";
  }
  alert("🛑 Razorpay Route Settlement Freeze Engaged!\nDownstream vendor payouts to identified mule nodes have been locked for 24 hours.");
}

// Dual-Phone Simulation Handlers with Live Countdown
let countdownInterval = null;
let countdownRemainingSec = 15 * 60;

function startCountdown(durationMinutes = 15) {
  stopCountdown();
  countdownRemainingSec = durationMinutes * 60;
  updateCountdownDisplay();
  countdownInterval = setInterval(() => {
    countdownRemainingSec--;
    if (countdownRemainingSec <= 0) {
      stopCountdown();
      cancelCheckout();
      alert('⏳ Cooling-Off period expired safely! Transfer has been automatically cancelled.');
    } else {
      updateCountdownDisplay();
    }
  }, 1000);
}

function stopCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
}

function updateCountdownDisplay() {
  const m = Math.floor(countdownRemainingSec / 60);
  const s = countdownRemainingSec % 60;
  const timeStr = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  const victimEl = document.getElementById('victim-countdown');
  const nomineeEl = document.getElementById('nominee-countdown');
  if (victimEl) victimEl.innerText = timeStr;
  if (nomineeEl) nomineeEl.innerText = timeStr;
}

function triggerCheckoutAlert() {
  document.getElementById('checkout-normal-state').style.display = 'none';
  document.getElementById('checkout-alert-state').style.display = 'block';
  document.getElementById('checkout-secured-state').style.display = 'none';

  // Trigger alert state on nominee phone
  document.getElementById('nominee-idle-state').style.display = 'none';
  document.getElementById('nominee-alert-state').style.display = 'block';

  // Start live 15-min countdown
  startCountdown(15);
}

function cancelCheckout() {
  stopCountdown();
  document.getElementById('checkout-alert-state').style.display = 'none';
  document.getElementById('checkout-normal-state').style.display = 'block';
  document.getElementById('nominee-alert-state').style.display = 'none';
  document.getElementById('nominee-idle-state').style.display = 'block';
  alert('🛡️ Transfer Cancelled! Funds saved from potential scam loss.');
}

function nomineeIntercept() {
  stopCountdown();
  document.getElementById('nominee-alert-state').style.display = 'none';
  document.getElementById('nominee-idle-state').style.display = 'block';

  document.getElementById('checkout-alert-state').style.display = 'none';
  document.getElementById('checkout-secured-state').style.display = 'block';
}

function nomineeApprove() {
  stopCountdown();
  document.getElementById('nominee-alert-state').style.display = 'none';
  document.getElementById('nominee-idle-state').style.display = 'block';
  document.getElementById('checkout-alert-state').style.display = 'none';
  document.getElementById('checkout-normal-state').style.display = 'block';
  alert('✅ Payment Approved by Designated Nominee Ananya Sharma. Processing transfer.');
}

// Live Stream Fetcher & Auto Ticker
async function refreshLiveStream() {
  const tbody = document.getElementById('stream-table-body');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:1.5rem; color:var(--text-muted);">Fetching live Razorpay AI risk stream...</td></tr>';

  try {
    const res = await fetch(`${API_BASE}/stream`);
    if (res.ok) {
      const data = await res.json();
      tbody.innerHTML = '';
      data.forEach(tx => {
        const ev = tx.evaluation || {};
        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="font-family:JetBrains Mono, monospace; color:var(--primary-light); font-size:0.8rem;">${tx.id}</td>
          <td>${tx.payer.name}</td>
          <td style="font-family:JetBrains Mono, monospace; font-size:0.75rem;">${tx.payee.vpa}</td>
          <td style="font-weight:700;">₹${tx.amount.toLocaleString()}</td>
          <td style="font-size:0.75rem; color:var(--text-muted);">
            ${tx.telemetry.session.active_phone_call ? '📞 Active Call | ' : ''}
            ${tx.telemetry.session.pasted_payee_vpa ? '📋 Pasted VPA | ' : ''}
            Age: ${tx.telemetry.payee_novelty.payee_account_age_days}d
          </td>
          <td><strong style="font-size:0.95rem;">${Math.round(ev.composite_risk_score || 10)}</strong>/100</td>
          <td><span class="risk-badge ${ev.risk_tier || 'LOW'}">${ev.action_label || 'Auto-Approve'}</span></td>
        `;
        tbody.appendChild(row);
      });
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:1.5rem; color:var(--risk-critical);">Stream server disconnected. Run `python server.py`.</td></tr>';
  }
}

function toggleAutoStream(isActive) {
  if (isActive) {
    autoStreamInterval = setInterval(() => {
      refreshLiveStream();
    }, 2500);
  } else if (autoStreamInterval) {
    clearInterval(autoStreamInterval);
    autoStreamInterval = null;
  }
}

// Policy Studio Updates
function updatePolicyUI() {
  const soft = document.getElementById('policy-soft').value;
  const cooling = document.getElementById('policy-cooling').value;
  const hard = document.getElementById('policy-hard').value;
  const dur = document.getElementById('policy-duration').value;

  document.getElementById('val-policy-soft').innerText = `${soft} / 100`;
  document.getElementById('val-policy-cooling').innerText = `${cooling} / 100`;
  document.getElementById('val-policy-hard').innerText = `${hard} / 100`;
  document.getElementById('val-policy-duration').innerText = `${dur} Minutes`;
}

async function saveMerchantPolicy() {
  const payload = {
    soft_warning_threshold: parseFloat(document.getElementById('policy-soft').value),
    cooling_off_threshold: parseFloat(document.getElementById('policy-cooling').value),
    hard_stop_threshold: parseFloat(document.getElementById('policy-hard').value),
    cooling_off_duration_minutes: parseInt(document.getElementById('policy-duration').value)
  };

  try {
    const res = await fetch(`${API_BASE}/policy/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert('💾 Merchant Guardrail Policy Saved Successfully!\nReal-time thresholds updated across all active Razorpay checkout links.');
    }
  } catch (err) {
    alert('Policy updated locally.');
  }
}

// Download CERT-In / RBI Forensic Audit Report
async function downloadForensicAuditReport() {
  try {
    const res = await fetch(`${API_BASE}/incident/audit-report?scenario=${currentScenario}`);
    if (res.ok) {
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CERTIN_RBI_Incident_Audit_${data.report_id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      alert(`📑 Official Forensic Audit Report [${data.report_id}] generated and downloaded!`);
    }
  } catch (err) {
    alert('Report generator error.');
  }
}

// Print / Export Forensic Audit as Formatted PDF
async function printAuditPDF() {
  try {
    const res = await fetch(`${API_BASE}/incident/audit-report?scenario=${currentScenario}`);
    if (!res.ok) throw new Error("Could not fetch incident audit report");
    const data = await res.json();
    const pw = window.open('', '_blank');
    pw.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>CERT-In Incident Report - ${data.report_id}</title>
        <style>
          body { font-family: 'Segoe UI', Tahoma, sans-serif; padding: 2rem; color: #1e293b; line-height: 1.6; max-width: 800px; margin: 0 auto; }
          .hdr { border-bottom: 2px solid #0284c7; padding-bottom: 1rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; }
          .hdr h1 { font-size: 1.35rem; margin: 0; color: #0f172a; }
          .badge { background: #fee2e2; color: #b91c1c; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: bold; font-size: 0.78rem; }
          .sec { margin-bottom: 1.5rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 1rem; }
          .sec h3 { margin-top: 0; font-size: 0.95rem; color: #0284c7; border-bottom: 1px solid #cbd5e1; padding-bottom: 0.4rem; }
          table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
          th, td { padding: 0.45rem; border-bottom: 1px solid #e2e8f0; text-align: left; }
          th { color: #64748b; width: 35%; }
          ul { font-size: 0.82rem; margin: 0; padding-left: 1.2rem; }
          .sig { font-family: monospace; font-size: 0.72rem; word-break: break-all; color: #475569; }
          @media print { body { padding: 0; } }
        </style>
      </head>
      <body>
        <div class="hdr">
          <div>
            <h1>Official CERT-In & RBI Forensic Incident Report</h1>
            <div style="font-size:0.82rem; color:#64748b;">Compliance Standard: ${data.compliance_standard}</div>
          </div>
          <div style="text-align:right;">
            <span class="badge">CONFIDENTIAL / RESTRICTED</span>
            <div style="font-size:0.8rem; color:#64748b; margin-top:0.3rem;">ID: ${data.report_id}</div>
          </div>
        </div>
        <div class="sec">
          <h3>1. Transaction Forensics & Guardrail Verdict</h3>
          <table>
            <tr><th>Generated At</th><td>${data.generated_at}</td></tr>
            <tr><th>Merchant Account</th><td>${data.merchant_account}</td></tr>
            <tr><th>Transaction ID</th><td>${data.transaction_forensics.transaction_id}</td></tr>
            <tr><th>Transfer Amount</th><td><strong>${data.transaction_forensics.amount}</strong></td></tr>
            <tr><th>Payer VPA</th><td>${data.transaction_forensics.payer_vpa}</td></tr>
            <tr><th>Payee VPA</th><td>${data.transaction_forensics.payee_vpa}</td></tr>
            <tr><th>Composite Risk Score</th><td>${data.transaction_forensics.composite_risk_score}</td></tr>
            <tr><th>Verdict</th><td><strong>${data.transaction_forensics.guardrail_verdict}</strong></td></tr>
          </table>
        </div>
        <div class="sec">
          <h3>2. Remediation & Enforcement Actions Taken</h3>
          <ul>${data.remediation_actions_taken.map(a => `<li>${a}</li>`).join('')}</ul>
        </div>
        <div class="sec">
          <h3>3. Cryptographic Guardrail Signature</h3>
          <div class="sig">${data.cryptographic_guardrail_signature}</div>
        </div>
        <script>window.onload = function() { window.print(); };</script>
      </body>
      </html>
    `);
    pw.document.close();
  } catch (err) {
    alert('PDF generation error: ' + err.message);
  }
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
  loadScenario('DIGITAL_ARREST');
});
