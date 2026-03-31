// ═══════════════════════════════════════════════════════
//  ERAS v4.0 — Shared UI Utilities
// ═══════════════════════════════════════════════════════

// ── TOAST ────────────────────────────────────────────
let _toastTimer;
function toast(type, title, msg) {
  const t  = document.getElementById('toast');
  clearTimeout(_toastTimer);
  t.className = 'toast on ' + type;
  document.getElementById('tt').textContent = title;
  document.getElementById('tm').textContent = msg;
  _toastTimer = setTimeout(() => t.classList.remove('on'), 4000);
}

// ── NOTIFICATIONS ─────────────────────────────────────
function addNotif(cls, icon, title, msg) {
  const nl = document.getElementById('notif-list');
  if (!nl) return;
  const d = document.createElement('div');
  d.className = 'notif ' + cls;
  d.innerHTML = `<div class="notif-icon">${icon}</div>
    <div class="notif-body">
      <div class="notif-title">${title}</div>
      <div class="notif-msg">${msg}</div>
      <div class="notif-time">${nowT()}</div>
    </div>`;
  nl.insertBefore(d, nl.firstChild);
  while (nl.children.length > 8) nl.removeChild(nl.lastChild);
}

// ── VIEW SWITCHER ─────────────────────────────────────
function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('on'));
  document.querySelectorAll('.htab, .sbi').forEach(t => t.classList.remove('on'));
  const v = document.getElementById('view-' + name);
  if (v) v.classList.add('on');
  document.querySelectorAll(`[data-view="${name}"]`).forEach(el => el.classList.add('on'));
  if (name === 'audit') renderAudit && renderAudit();
  if (name === 'res')   renderResources && renderResources();
}

// ── REGION SIDEBAR ────────────────────────────────────
function buildRegList(filter) {
  const list = document.getElementById('reg-list');
  if (!list) return;
  const q = (filter || '').toLowerCase();
  const filtered = DISTRICTS.filter(d => d.name.toLowerCase().includes(q));
  list.innerHTML = filtered.map(d => {
    const r = REGIONS[d.id];
    const sc = {ONLINE:'s-on','LOW RES':'s-lo',FAILED:'s-fa'}[r.status] || 's-on';
    const aP = r.ambulances/r.maxAmbu*100, bP = r.beds/r.maxBeds*100;
    const iP = r.maxIcu ? r.icu/r.maxIcu*100 : 0;
    return `<div class="reg-card" id="rc-${d.id}">
      <div class="rc-top">
        <div class="rc-name">${d.name}</div>
        <div class="rc-status ${sc}" id="rs-${d.id}">${r.status}</div>
      </div>
      <div class="rc-sync" id="rsy-${d.id}">Last sync: just now</div>
      <div>
        <div class="rbar"><div class="rl">🚑</div><div class="rt2"><div class="rf2" id="rb-a-${d.id}" style="width:${aP}%;background:var(--blue)"></div></div><div class="rv" id="rv-a-${d.id}">${r.ambulances}</div></div>
        <div class="rbar"><div class="rl">🏥</div><div class="rt2"><div class="rf2" id="rb-b-${d.id}" style="width:${bP}%;background:var(--teal)"></div></div><div class="rv" id="rv-b-${d.id}">${r.beds}</div></div>
        <div class="rbar"><div class="rl">❤️</div><div class="rt2"><div class="rf2" id="rb-i-${d.id}" style="width:${iP}%;background:var(--purple)"></div></div><div class="rv" id="rv-i-${d.id}">${r.icu}</div></div>
      </div>
    </div>`;
  }).join('');
}

function updateRegCard(id) {
  const r = REGIONS[id];
  if (!r) return;
  const sc = {ONLINE:'s-on','LOW RES':'s-lo',FAILED:'s-fa'}[r.status] || 's-on';
  const g = s => document.getElementById(s);
  const aP = r.ambulances/r.maxAmbu*100, bP = r.beds/r.maxBeds*100;
  const iP = r.maxIcu ? r.icu/r.maxIcu*100 : 0;
  if (g(`rs-${id}`))    { g(`rs-${id}`).textContent = r.status; g(`rs-${id}`).className = 'rc-status '+sc; }
  if (g(`rb-a-${id}`))  { g(`rb-a-${id}`).style.width = aP+'%'; g(`rv-a-${id}`).textContent = r.ambulances; }
  if (g(`rb-b-${id}`))  { g(`rb-b-${id}`).style.width = bP+'%'; g(`rv-b-${id}`).textContent = r.beds; }
  if (g(`rb-i-${id}`))  { g(`rb-i-${id}`).style.width = iP+'%'; g(`rv-i-${id}`).textContent = r.icu; }
  if (g(`rsy-${id}`))   g(`rsy-${id}`).textContent = 'Last sync: '+nowT();
}

// ── AUDIT ─────────────────────────────────────────────
function renderAudit(filter) {
  const el = document.getElementById('aud-list');
  if (!el) return;
  const f = filter || 'ALL';
  const logs = f === 'ALL' ? STATE.logs : STATE.logs.filter(l => l.type === f);
  const tc = {ALLOCATION:'tA',FAILOVER:'tF',BORROW:'tB',RECOVERY:'tR',LOGIN:'tL'};
  el.innerHTML = !logs.length
    ? '<div style="color:var(--text3);text-align:center;padding:22px;font-size:10px">No entries yet.</div>'
    : logs.map(l => `<div class="audit-row">
        <div class="at">${l.time}</div>
        <div class="atype ${tc[l.type]||'tA'}">${l.type}</div>
        <div class="amsg">${l.msg}</div>
      </div>`).join('');
}

// ── REPLICATION SYNC FLASH ────────────────────────────
function triggerSync(regId) {
  const sl = document.getElementById('sync-lbl');
  if (sl) { sl.textContent = 'SYNCING…'; setTimeout(() => sl.textContent = 'SYNCED', 900); }
  ['rt1','rt2','rt3'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = nowT(); });
  if (document.getElementById(`rsy-${regId}`))
    document.getElementById(`rsy-${regId}`).textContent = 'Last sync: ' + nowT();
}

// ── UPTIME ────────────────────────────────────────────
function startUptime() {
  setInterval(() => {
    const s  = Math.floor((Date.now() - STATE.uptimeStart)/1000);
    const h  = String(Math.floor(s/3600)).padStart(2,'0');
    const m  = String(Math.floor((s%3600)/60)).padStart(2,'0');
    const ss = String(s%60).padStart(2,'0');
    const el = document.getElementById('uptime');
    if (el) el.textContent = `${h}:${m}:${ss}`;
  }, 1000);
}

// ── HEADER BADGE ──────────────────────────────────────
function applyHeaderBadge(role, username) {
  const roleColors = {admin:'var(--blue)',dispatcher:'var(--teal)',hospital:'var(--green)',ambulance:'var(--amber)',authority:'var(--purple)'};
  const roleLabels = {admin:'Administrator',dispatcher:'Dispatcher',hospital:'Hospital Staff',ambulance:'Ambulance Driver',authority:'Gov. Authority'};
  const rb = document.getElementById('rbadge');
  if (rb) { rb.textContent = (roleLabels[role]||role).toUpperCase(); rb.style.background = (roleColors[role]||'var(--blue)')+'22'; rb.style.color = roleColors[role]||'var(--blue)'; }
  const un = document.getElementById('uname');
  if (un) un.textContent = username;
  document.body.classList.add('role-'+role);
}

// ── SHARED POPULATE HELPERS ───────────────────────────
function populateDistrictSelect(selectId) {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = DISTRICTS.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
}

function populateHospSelect(selectId) {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = HOSPITALS.map(h => `<option value="${h.id}">${h.name}</option>`).join('');
}

function populateAmbuSelect(selectId) {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = AMBULANCES.map(a => `<option value="${a.id}">${a.id} — ${REGIONS[a.region]?.name||a.region}</option>`).join('');
}

// ── GEOLOCATION ───────────────────────────────────────
function getLocation(onSuccess) {
  toast('ti', 'Getting GPS…', 'Using browser geolocation API');
  if (!navigator.geolocation) { useFallbackLoc(onSuccess); return; }
  navigator.geolocation.getCurrentPosition(
    pos => {
      STATE.locLat = pos.coords.latitude;
      STATE.locLng = pos.coords.longitude;
      const txt = `${STATE.locLat.toFixed(4)}, ${STATE.locLng.toFixed(4)}`;
      toast('ts', 'Location captured', txt);
      addLog('LOGIN', `Live GPS: ${txt}<div class="anode">Source: navigator.geolocation</div>`);
      if (onSuccess) onSuccess(txt);
    },
    () => useFallbackLoc(onSuccess)
  );
}
function useFallbackLoc(onSuccess) {
  STATE.locLat = 13.08; STATE.locLng = 80.27;
  toast('tw', 'Using demo location', 'Chennai coordinates (GPS denied)');
  if (onSuccess) onSuccess('13.0827, 80.2707 (demo)');
}

// ── RESOURCE HELPERS ──────────────────────────────────
function freeAmbulance(id) {
  const a = AMBULANCES.find(x => x.id === id);
  if (a && a.status === 'busy') {
    a.status = 'free';
    const r = REGIONS[a.region];
    r.ambulances = Math.min(r.ambulances+1, r.maxAmbu);
    updateRegCard(a.region);
    toast('ts', id+' freed', 'Ambulance available');
    addLog('RECOVERY', `Ambulance ${id} returned to service<div class="anode">Region: ${r.name}</div>`);
  }
}

function renderResourcesTable() {
  const at = document.getElementById('ambu-tb');
  const ht = document.getElementById('hosp-tb');
  if (at) at.innerHTML = AMBULANCES.slice(0,25).map(a => `
    <tr>
      <td style="font-family:var(--mono);font-size:9px">${a.id}</td>
      <td style="font-size:9px">${REGIONS[a.region]?.name||a.region}</td>
      <td><span class="badge ${a.status==='free'?'bf':'bb'}">${a.status.toUpperCase()}</span></td>
      <td style="font-family:var(--mono);font-size:9px;color:${a.status==='busy'?'var(--red)':'var(--green)'}">${a.status==='busy'?'HIGH':'LOW'}</td>
      <td><button class="btn bs btn-sm" onclick="freeAmbulance('${a.id}');renderResourcesTable();">Free</button></td>
    </tr>`).join('');
  if (ht) ht.innerHTML = HOSPITALS.slice(0,20).map(h => `
    <tr>
      <td style="font-size:10px;font-weight:700">${h.name}</td>
      <td style="font-size:9px;color:var(--text2)">${REGIONS[h.region]?.name||h.region}</td>
      <td style="font-family:var(--mono);font-size:9px;color:${h.beds<5?'var(--red)':'var(--text)'}">${h.beds}/${h.maxBeds}</td>
      <td style="font-family:var(--mono);font-size:9px;color:${h.icu<2?'var(--amber)':'var(--text)'}">${h.icu}/${h.maxIcu}</td>
      <td style="font-family:var(--mono);font-size:9px;color:var(--blue)">${Math.round(Math.max(0,scoreHosp(h,'general',h.lat,h.lng)))}</td>
    </tr>`).join('');
}

// ── SIMULATION ENGINE ─────────────────────────────────
function runSimulation(type, onDone) {
  const labels = {mass:'Mass Accident — 50 Cases',hosp:'Hospital Offline',low:'Resource Exhaustion',peak:'Peak Hour — 20 Cases'};
  const counts = {mass:50,hosp:10,low:8,peak:20};
  const n = counts[type];
  const simA = JSON.parse(JSON.stringify(AMBULANCES));
  const simH = JSON.parse(JSON.stringify(HOSPITALS));
  let alloc=0,fail=0,det=[],totMs=0;
  if (type==='hosp') { const h=simH.find(x=>x.id==='H1'); if(h){h.beds=0;h.icu=0;} }
  if (type==='low')  { simA.forEach(a=>a.status='busy'); }
  const pris=['CRITICAL','CRITICAL','HIGH','HIGH','NORMAL','NORMAL','NORMAL'];
  for (let i=0;i<n;i++) {
    const a=simA.find(x=>x.status==='free'), h=simH.find(x=>x.beds>0);
    const ms=Math.floor(Math.random()*200)+20;
    const pr=pris[i%pris.length];
    if (a&&h){a.status='busy';h.beds--;alloc++;totMs+=ms;if(det.length<6)det.push({id:`SIM-${i+1}`,s:'allocated',pr,ms});}
    else {
      if(type==='low'&&i<3){alloc++;totMs+=ms+180;if(det.length<6)det.push({id:`SIM-${i+1}`,s:'borrowed+allocated',pr,ms:ms+180});}
      else{fail++;if(det.length<6)det.push({id:`SIM-${i+1}`,s:'failed',pr,ms:0});}
    }
  }
  const pct=Math.round(alloc/(alloc+fail)*100);
  const avgMs=alloc>0?Math.round(totMs/alloc):0;
  addLog('ALLOCATION',`Sim: <strong>${labels[type]}</strong> — ${alloc}/${alloc+fail} (${pct}%) | Avg ${avgMs}ms<div class="anode">Parallel threads | Deep copy | Live data unchanged</div>`);
  if (onDone) onDone({alloc,fail,pct,avgMs,det,label:labels[type]});
}

function simResultHTML(r) {
  return `<div style="border-top:1px solid var(--border);padding-top:12px;margin-top:6px">
    <div style="font-size:12px;font-weight:700;margin-bottom:10px">📊 ${r.label}</div>
    <div class="three" style="margin-bottom:12px">
      <div style="background:var(--bg3);border-radius:7px;padding:9px;text-align:center"><div style="font-family:var(--mono);font-size:18px;font-weight:600">${r.alloc+r.fail}</div><div style="font-size:8px;color:var(--text2)">SIMULATED</div></div>
      <div style="background:var(--green2);border:1px solid rgba(16,217,160,0.2);border-radius:7px;padding:9px;text-align:center"><div style="font-family:var(--mono);font-size:18px;font-weight:600;color:var(--green)">${r.alloc}</div><div style="font-size:8px;color:var(--text2)">ALLOCATED</div></div>
      <div style="background:var(--red2);border:1px solid rgba(255,69,96,0.2);border-radius:7px;padding:9px;text-align:center"><div style="font-family:var(--mono);font-size:18px;font-weight:600;color:var(--red)">${r.fail}</div><div style="font-size:8px;color:var(--text2)">FAILED</div></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:4px"><span style="color:var(--text2)">Success rate</span><span style="font-family:var(--mono);color:${r.pct>70?'var(--green)':r.pct>40?'var(--amber)':'var(--red)'}">${r.pct}%</span></div>
    <div style="height:5px;background:var(--bg4);border-radius:3px;margin-bottom:10px;overflow:hidden"><div style="height:100%;width:${r.pct}%;border-radius:3px;background:${r.pct>70?'var(--green)':r.pct>40?'var(--amber)':'var(--red)'};transition:width 1s ease"></div></div>
    <div style="font-size:9px;color:var(--text2);margin-bottom:8px">Avg: <strong style="color:var(--text)">${r.avgMs}ms</strong></div>
    ${r.det.map(d=>`<div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid var(--border);font-size:9px;align-items:center"><span style="font-family:var(--mono);color:var(--text3);min-width:52px">${d.id}</span><span class="badge b${d.pr[0].toLowerCase()}">${d.pr}</span><span style="color:${d.s.includes('fail')?'var(--red)':'var(--green)'};flex:1">${d.s}</span>${d.ms?`<span style="font-family:var(--mono);color:var(--text3)">${d.ms}ms</span>`:''}</div>`).join('')}
  </div>`;
}
