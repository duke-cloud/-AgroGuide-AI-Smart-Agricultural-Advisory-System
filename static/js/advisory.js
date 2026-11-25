/* ═══════════════════════════════════════════════════════
   AgroGuide AI — Advisory JS (AJAX calls + UI updates)
═══════════════════════════════════════════════════════ */

const CSRF = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                   getCookie('csrftoken');

function getCookie(name) {
  const val = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function postJSON(url, data) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF() },
    body: JSON.stringify(data),
  }).then(r => r.json());
}

function setLoading(btn, yes) {
  if (yes) {
    btn.dataset.origText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Analyzing…';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.origText || 'Submit';
    btn.disabled = false;
  }
}

function riskClass(r) {
  if (!r) return 'risk-low';
  const l = r.toString().toLowerCase();
  if (l === 'high' || l === '3') return 'risk-high';
  if (l === 'medium' || l === '2') return 'risk-medium';
  return 'risk-low';
}

// ── CROP ADVISORY ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  // ── Crop form ──
  const cropForm = document.getElementById('cropForm');
  if (cropForm) {
    cropForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = this.querySelector('[type=submit]');
      setLoading(btn, true);
      const fd = new FormData(this);
      const data = Object.fromEntries([...fd.entries()].map(([k,v])=>[k, isNaN(v)?v:parseFloat(v)]));
      try {
        const res = await postJSON(window.CROP_URL, data);
        if (res.status === 'ok') renderCropResult(res.result);
      } catch(err) { showToast('Error communicating with server', 'danger'); }
      setLoading(btn, false);
    });
  }

  // ── Fertilizer form ──
  const fertForm = document.getElementById('fertForm');
  if (fertForm) {
    fertForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = this.querySelector('[type=submit]');
      setLoading(btn, true);
      const fd = new FormData(this);
      const data = Object.fromEntries([...fd.entries()].map(([k,v])=>[k, isNaN(v)?v:parseFloat(v)]));
      try {
        const res = await postJSON(window.FERT_URL, data);
        if (res.status === 'ok') renderFertResult(res.result);
      } catch(err) { showToast('Error communicating with server', 'danger'); }
      setLoading(btn, false);
    });
  }

  // ── Yield form ──
  const yieldForm = document.getElementById('yieldForm');
  if (yieldForm) {
    yieldForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = this.querySelector('[type=submit]');
      setLoading(btn, true);
      const fd = new FormData(this);
      const data = Object.fromEntries([...fd.entries()].map(([k,v])=>[k, isNaN(v)?v:parseFloat(v)]));
      data.irrigation = document.getElementById('irrigationCheck')?.checked ? 1 : 0;
      try {
        const res = await postJSON(window.YIELD_URL, data);
        if (res.status === 'ok') renderYieldResult(res.result);
      } catch(err) { showToast('Error communicating with server', 'danger'); }
      setLoading(btn, false);
    });
  }

  // ── Pest form ──
  const pestForm = document.getElementById('pestForm');
  if (pestForm) {
    pestForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = this.querySelector('[type=submit]');
      setLoading(btn, true);
      const fd = new FormData(this);
      const data = Object.fromEntries([...fd.entries()].map(([k,v])=>[k, isNaN(v)?v:parseFloat(v)]));
      try {
        const res = await postJSON(window.PEST_URL, data);
        if (res.status === 'ok') renderPestResult(res.result);
      } catch(err) { showToast('Error communicating with server', 'danger'); }
      setLoading(btn, false);
    });
  }

  // ── Symptom check ──
  const symptomForm = document.getElementById('symptomForm');
  if (symptomForm) {
    symptomForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = this.querySelector('[type=submit]');
      setLoading(btn, true);
      const data = {
        symptoms: document.getElementById('symptomText').value,
        crop:     document.getElementById('symptomCrop').value,
      };
      try {
        const res = await postJSON(window.DISEASE_URL, data);
        if (res.status === 'ok') renderDiagnosis(res.result);
      } catch(err) { showToast('Error communicating with server', 'danger'); }
      setLoading(btn, false);
    });
  }

});

// ── RENDER FUNCTIONS ──────────────────────────────────

function renderCropResult(r) {
  const el = document.getElementById('cropResult');
  if (!el) return;
  const probBars = r.top3_crops.map(c => {
    const pct = r.probabilities[c] || 0;
    return `<div class="mb-8">
      <div class="d-flex justify-between align-center mb-4">
        <span style="text-transform:capitalize;font-weight:600">${c}</span>
        <span class="text-muted">${pct}%</span>
      </div>
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" style="width:${Math.max(pct,3)}%;background:var(--primary-lt)"></div>
      </div>
    </div>`;
  }).join('');

  const plantMsgs = (r.planting_advice?.messages || [])
    .map(m => `<div class="alert alert-${r.planting_advice.urgency || 'info'}">${m}</div>`).join('');

  el.innerHTML = `
    <div class="result-primary mb-16">
      <div class="rp-label">🌾 PRIMARY RECOMMENDATION</div>
      <div class="rp-value">${r.primary_crop}</div>
      <div class="rp-sub">Best match for your current soil & climate</div>
    </div>
    <div class="card mb-16">
      <div class="card-title">📊 Crop Probability Scores</div>
      ${probBars}
    </div>
    <div class="card">
      <div class="card-title">📅 Planting Advisory</div>
      ${plantMsgs}
    </div>`;
  el.classList.remove('d-none');
  el.scrollIntoView({behavior:'smooth', block:'nearest'});
}

function renderFertResult(r) {
  const el = document.getElementById('fertResult');
  if (!el) return;
  const recs = (r.rule_recommendations || []).map(rec => `
    <div class="fert-rec">
      <div class="fr-name">📦 ${rec.product}</div>
      <div class="fr-meta">
        <span>Rate: <strong>${rec.rate_per_ha}</strong></span>
        <span>Total: <strong>${rec.total}</strong></span>
        <span>Timing: <strong>${rec.timing}</strong></span>
      </div>
      <div class="fr-reason">${rec.reason}</div>
    </div>`).join('');
  el.innerHTML = `
    <div class="card mb-16" style="background:#f0faf4;border-color:#b2dfdb">
      <div class="card-title" style="color:var(--success)">🤖 ML Recommendation</div>
      <div style="font-size:18px;font-weight:700;color:var(--primary)">${r.ml_recommendation}</div>
      <div class="text-muted mt-4">Model confidence: ${r.ml_confidence}%</div>
    </div>
    <div class="card mb-16">
      <div class="card-title">📋 Detailed Application Plan</div>
      ${recs}
    </div>
    <div class="card">
      <div class="card-title">💡 Typical Full Program</div>
      <div style="font-size:13px;color:var(--text)">${r.typical_program}</div>
    </div>`;
  el.classList.remove('d-none');
  el.scrollIntoView({behavior:'smooth', block:'nearest'});
}

function renderYieldResult(r) {
  const el = document.getElementById('yieldResult');
  if (!el) return;
  const rev = Number(r.est_revenue_ngn).toLocaleString();
  el.innerHTML = `
    <div class="result-primary mb-16">
      <div class="rp-label">📊 PREDICTED YIELD</div>
      <div class="rp-value" style="font-size:44px">${r.yield_per_ha}</div>
      <div class="rp-sub">tons per hectare · Total: ${r.total_yield} tons for ${r.area} ha</div>
    </div>
    <div class="result-row mb-16">
      <div class="result-item">
        <div class="ri-label">Est. Revenue</div>
        <div class="ri-value text-success">₦${rev}</div>
      </div>
      <div class="result-item">
        <div class="ri-label">Price Per Ton</div>
        <div class="ri-value">₦${Number(r.price_per_ton).toLocaleString()}</div>
      </div>
    </div>
    <div id="yieldChartCard" class="card">
      <div class="card-title">📈 Scenario Comparison</div>
      <canvas id="yieldChart" height="120"></canvas>
    </div>`;
  el.classList.remove('d-none');
  el.scrollIntoView({behavior:'smooth', block:'nearest'});
  // draw chart
  setTimeout(() => drawYieldChart(r.yield_per_ha), 50);
}

function renderPestResult(r) {
  const el = document.getElementById('pestResult');
  if (!el) return;
  const riskHtml = (r.risks || []).map(risk => `
    <div class="risk-item ${riskClass(risk.risk_label)}">
      <div class="risk-header">
        <span class="risk-name">${risk.pest}</span>
        <span class="badge badge-${risk.risk_label?.toLowerCase()}">${risk.risk_label} Risk</span>
      </div>
      <div class="risk-action">🔸 <strong>Action:</strong> ${risk.action}</div>
      <div class="risk-prev">🛡️ <strong>Prevention:</strong> ${risk.prevention}</div>
    </div>`).join('');
  const wAdv = (r.weather_advisories || []).map(a =>
    `<div class="alert alert-${a.level}">${a.icon} ${a.msg}</div>`).join('');
  el.innerHTML = `
    <div class="card mb-16">
      <div class="card-title">🚨 Pest & Disease Risk Assessment</div>
      ${riskHtml}
    </div>
    <div class="card">
      <div class="card-title">🌤️ Weather-Based Advisories</div>
      ${wAdv}
    </div>`;
  el.classList.remove('d-none');
  el.scrollIntoView({behavior:'smooth', block:'nearest'});
}

function renderDiagnosis(r) {
  const el = document.getElementById('diagnosisResult');
  if (!el) return;
  const sev = r.severity?.toLowerCase();
  const cls = sev === 'high' ? 'danger' : sev === 'medium' ? 'warning' : 'success';
  el.innerHTML = `
    <div class="alert alert-${cls}" style="flex-direction:column;align-items:flex-start">
      <div style="font-weight:700;font-size:15px;margin-bottom:8px">🔬 Diagnosis: ${r.diagnosis}</div>
      <div class="mb-8"><strong>Severity:</strong> ${r.severity}</div>
      <div><strong>Treatment:</strong> ${r.treatment}</div>
    </div>`;
  el.classList.remove('d-none');
}

// ── CHART.JS HELPERS ──────────────────────────────────
function drawYieldChart(baseYield) {
  const ctx = document.getElementById('yieldChart');
  if (!ctx || !window.Chart) return;
  const yph = parseFloat(baseYield);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Poor Conditions', 'Current Estimate', 'Optimal Conditions'],
      datasets: [{
        label: 'Yield (t/ha)',
        data: [(yph*0.55).toFixed(2), yph, (yph*1.35).toFixed(2)],
        backgroundColor: ['#f5b8b8','#2d6a4f','#52b788'],
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true, plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, title: { display:true, text:'tons/ha' } } }
    }
  });
}

function drawNPKChart(N, P, K, optN, optP, optK) {
  const ctx = document.getElementById('npkChart');
  if (!ctx || !window.Chart) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
      datasets: [
        { label:'Current', data:[N,P,K], backgroundColor:'#2d6a4f', borderRadius:5 },
        { label:'Optimal', data:[optN,optP,optK], backgroundColor:'#e8b84b', borderRadius:5 },
      ]
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero:true, title:{display:true,text:'mg/kg'} } },
    }
  });
}

function drawForecastChart(forecast) {
  const ctx = document.getElementById('forecastChart');
  if (!ctx || !window.Chart || !forecast) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: forecast.map(f => f.date || f.day),
      datasets: [
        { type:'line', label:'High °C', data:forecast.map(f=>f.high), borderColor:'#d4851a', backgroundColor:'transparent', tension:.4, yAxisID:'y1' },
        { type:'bar',  label:'Rain mm', data:forecast.map(f=>f.rain), backgroundColor:'rgba(41,128,185,.45)', borderRadius:4, yAxisID:'y' },
      ]
    },
    options: {
      responsive:true,
      scales: {
        y:  { beginAtZero:true, title:{display:true,text:'Rainfall (mm)'} },
        y1: { position:'right', title:{display:true,text:'Temp (°C)'}, grid:{drawOnChartArea:false} },
      }
    }
  });
}

// ── TOAST NOTIFICATION ────────────────────────────────
function showToast(msg, type='info') {
  const t = document.createElement('div');
  t.className = `alert alert-${type}`;
  t.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;min-width:280px;box-shadow:0 4px 16px rgba(0,0,0,.15)';
  t.innerHTML = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}
