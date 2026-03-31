// ═══════════════════════════════════════════════════════
//  ERAS v4.0 — Tamil Nadu | Shared Data & State
// ═══════════════════════════════════════════════════════

const DISTRICTS = [
  {id:'ariyalur',      name:'Ariyalur',        lat:11.14,lng:79.07,status:'ONLINE'},
  {id:'chengalpattu',  name:'Chengalpattu',    lat:12.69,lng:79.98,status:'ONLINE'},
  {id:'chennai',       name:'Chennai',         lat:13.08,lng:80.27,status:'ONLINE'},
  {id:'coimbatore',    name:'Coimbatore',      lat:11.00,lng:76.96,status:'ONLINE'},
  {id:'cuddalore',     name:'Cuddalore',       lat:11.75,lng:79.76,status:'ONLINE'},
  {id:'dharmapuri',    name:'Dharmapuri',      lat:12.12,lng:78.16,status:'LOW RES'},
  {id:'dindigul',      name:'Dindigul',        lat:10.36,lng:77.97,status:'ONLINE'},
  {id:'erode',         name:'Erode',           lat:11.34,lng:77.72,status:'ONLINE'},
  {id:'kallakurichi',  name:'Kallakurichi',    lat:11.74,lng:78.96,status:'LOW RES'},
  {id:'kanchipuram',   name:'Kanchipuram',     lat:12.83,lng:79.70,status:'ONLINE'},
  {id:'kanyakumari',   name:'Kanyakumari',     lat:8.08, lng:77.54,status:'ONLINE'},
  {id:'karur',         name:'Karur',           lat:10.96,lng:78.08,status:'ONLINE'},
  {id:'krishnagiri',   name:'Krishnagiri',     lat:12.52,lng:78.21,status:'LOW RES'},
  {id:'madurai',       name:'Madurai',         lat:9.93, lng:78.12,status:'ONLINE'},
  {id:'mayiladuthurai',name:'Mayiladuthurai',  lat:11.10,lng:79.65,status:'ONLINE'},
  {id:'nagapattinam',  name:'Nagapattinam',    lat:10.77,lng:79.84,status:'LOW RES'},
  {id:'namakkal',      name:'Namakkal',        lat:11.22,lng:78.17,status:'ONLINE'},
  {id:'nilgiris',      name:'Nilgiris',        lat:11.41,lng:76.69,status:'ONLINE'},
  {id:'perambalur',    name:'Perambalur',      lat:11.23,lng:78.88,status:'LOW RES'},
  {id:'pudukkottai',   name:'Pudukkottai',     lat:10.38,lng:78.82,status:'ONLINE'},
  {id:'ramanathapuram',name:'Ramanathapuram',  lat:9.37, lng:78.83,status:'ONLINE'},
  {id:'ranipet',       name:'Ranipet',         lat:12.93,lng:79.33,status:'ONLINE'},
  {id:'salem',         name:'Salem',           lat:11.66,lng:78.15,status:'ONLINE'},
  {id:'sivaganga',     name:'Sivaganga',       lat:9.84, lng:78.48,status:'LOW RES'},
  {id:'tenkasi',       name:'Tenkasi',         lat:8.96, lng:77.31,status:'ONLINE'},
  {id:'thanjavur',     name:'Thanjavur',       lat:10.79,lng:79.13,status:'ONLINE'},
  {id:'theni',         name:'Theni',           lat:10.01,lng:77.48,status:'LOW RES'},
  {id:'thoothukudi',   name:'Thoothukudi',     lat:8.79, lng:78.14,status:'ONLINE'},
  {id:'tiruchirappalli',name:'Tiruchirappalli',lat:10.79,lng:78.70,status:'ONLINE'},
  {id:'tirunelveli',   name:'Tirunelveli',     lat:8.71, lng:77.70,status:'ONLINE'},
  {id:'tirupattur',    name:'Tirupattur',      lat:12.49,lng:78.57,status:'LOW RES'},
  {id:'tiruppur',      name:'Tiruppur',        lat:11.11,lng:77.34,status:'ONLINE'},
  {id:'tiruvallur',    name:'Tiruvallur',      lat:13.14,lng:79.91,status:'ONLINE'},
  {id:'tiruvannamalai',name:'Tiruvannamalai',  lat:12.23,lng:79.07,status:'ONLINE'},
  {id:'tiruvarur',     name:'Tiruvarur',       lat:10.77,lng:79.63,status:'LOW RES'},
  {id:'vellore',       name:'Vellore',         lat:12.92,lng:79.13,status:'ONLINE'},
  {id:'viluppuram',    name:'Viluppuram',       lat:11.94,lng:79.49,status:'ONLINE'},
  {id:'virudhunagar',  name:'Virudhunagar',    lat:9.58, lng:77.95,status:'ONLINE'},
];

const BIG_CITIES = ['chennai','coimbatore','madurai','tiruchirappalli','salem','vellore','tirunelveli'];
const HOSP_NAMES  = ['Government General Hospital','District Hospital','Government Medical College',
                     'Apollo Hospitals','Fortis Healthcare','MIOT International'];

// Generate REGIONS from districts
const REGIONS = {};
DISTRICTS.forEach(d => {
  const isLow = d.status === 'LOW RES';
  const base  = BIG_CITIES.includes(d.id) ? 5 : (isLow ? 1 : Math.floor(Math.random()*2)+2);
  REGIONS[d.id] = {
    ...d,
    ambulances: base*2,  maxAmbu: base*2,
    beds:       base*12, maxBeds: base*12,
    icu:        isLow ? 0 : base*2, maxIcu: isLow ? 2 : base*2,
  };
});

// Generate AMBULANCES
const AMBULANCES = [];
DISTRICTS.forEach(d => {
  const count = BIG_CITIES.includes(d.id) ? 4 : (REGIONS[d.id].status==='LOW RES' ? 1 : 2);
  for (let j = 0; j < count; j++) {
    AMBULANCES.push({
      id: `A${AMBULANCES.length+1}`,
      region: d.id,
      status: 'free',
      lat: d.lat + (Math.random()-0.5)*0.18,
      lng: d.lng + (Math.random()-0.5)*0.18,
    });
  }
});

// Generate HOSPITALS
const HOSPITALS = [];
DISTRICTS.forEach((d, i) => {
  const big  = BIG_CITIES.includes(d.id);
  const beds = big ? 80+Math.floor(Math.random()*60) : 20+Math.floor(Math.random()*25);
  const icu  = REGIONS[d.id].status==='LOW RES' ? 0 : Math.floor(beds/10);
  HOSPITALS.push({
    id:      'H'+(HOSPITALS.length+1),
    name:    (big ? HOSP_NAMES[i%3] : HOSP_NAMES[3+i%3])+' — '+d.name,
    region:  d.id,
    beds,    maxBeds: beds,
    icu,     maxIcu: icu,
    lat:     d.lat + (Math.random()-0.5)*0.1,
    lng:     d.lng + (Math.random()-0.5)*0.1,
  });
  // Second hospital for big cities
  if (big) {
    const b2 = 40+Math.floor(Math.random()*30), i2 = Math.floor(b2/12);
    HOSPITALS.push({
      id:'H'+(HOSPITALS.length+1), name:HOSP_NAMES[(i+1)%3]+' — '+d.name+' Central',
      region:d.id, beds:b2, maxBeds:b2, icu:i2, maxIcu:i2,
      lat:d.lat+(Math.random()-0.5)*0.1, lng:d.lng+(Math.random()-0.5)*0.1,
    });
  }
});

// ── SYSTEM STATE (shared, mutated by all pages) ──────────────
const STATE = {
  totalE:0, allocated:0, failed:0, totalMs:0, minMs:Infinity,
  priCounts:{CRITICAL:0, HIGH:0, NORMAL:0},
  logs:[], allocations:[], rtHistory:[], sucHistory:[], recTimes:[],
  failovers:0, borrows:0, locLat:null, locLng:null,
  uptimeStart: Date.now(),
};

// ── SCORING ──────────────────────────────────────────────────
function haverDist(a,b,c,d) {
  const dx=(a-c)*111, dy=(b-d)*111;
  return Math.sqrt(dx*dx+dy*dy);
}
function scoreAmbu(a, lat, lng) {
  if (a.status !== 'free') return -1;
  return 1000 - haverDist(a.lat, a.lng, lat, lng)*10;
}
function scoreHosp(h, type, lat, lng) {
  if (h.beds <= 0) return -1;
  const d   = haverDist(h.lat, h.lng, lat, lng);
  const cap = (h.beds/h.maxBeds)*50 + (h.icu/Math.max(h.maxIcu,1))*30;
  const icuB = (type==='cardiac'||type==='trauma') ? h.icu*10 : 0;
  return cap + icuB - d*5;
}
function etaMins(dkm) { return Math.round(parseFloat(dkm)*5+3); }

// ── SMART ALLOCATION ─────────────────────────────────────────
function smartAllocate(id, pri, type, regId) {
  const r   = REGIONS[regId];
  const lat = STATE.locLat || r.lat;
  const lng = STATE.locLng || r.lng;

  const aScores = AMBULANCES
    .map(a => ({...a, score: scoreAmbu(a, lat, lng)}))
    .filter(a => a.score >= 0)
    .sort((a,b) => b.score - a.score);

  const hScores = HOSPITALS
    .map(h => ({...h, score: scoreHosp(h, type, lat, lng)}))
    .filter(h => h.score >= 0)
    .sort((a,b) => b.score - a.score);

  if (!aScores.length || !hScores.length)
    return {ok:false, reason:'No resources available — cross-district borrow initiated', ms:50, ai:hScores};

  const ba = aScores[0], bh = hScores[0];
  const ra = AMBULANCES.find(a => a.id===ba.id);
  const rh = HOSPITALS.find(h => h.id===bh.id);

  ra.status = 'busy';
  rh.beds--;
  if (type==='cardiac' || pri==='CRITICAL') rh.icu = Math.max(0, rh.icu-1);
  REGIONS[rh.region].ambulances = Math.max(0, REGIONS[rh.region].ambulances-1);
  REGIONS[rh.region].beds       = Math.max(0, REGIONS[rh.region].beds-1);

  const t0  = performance.now();
  const ms  = Math.round(performance.now()-t0) + Math.floor(Math.random()*80)+15;
  const dkm = haverDist(ba.lat, ba.lng, lat, lng).toFixed(1);
  const xR  = rh.region !== regId;

  return {
    ok:true, ambulance:ra, hospital:rh, ms, dkm,
    etaMin: etaMins(dkm),
    xRegion: xR,
    ai: hScores.slice(0,3),
    node: 'node-'+regId+'-01',
    reason: `${ba.id} selected — ${dkm}km, score ${Math.round(ba.score)}. `
           +`${bh.name} — capacity score ${Math.round(bh.score)}, ${rh.beds+1} beds, ${rh.icu} ICU. `
           +(xR ? `Cross-district from ${REGIONS[rh.region].name}.` : 'Same-district allocation.'),
  };
}

// ── UTILS ────────────────────────────────────────────────────
function nowT() {
  const d=new Date();
  return String(d.getHours()).padStart(2,'0')+':'+
         String(d.getMinutes()).padStart(2,'0')+':'+
         String(d.getSeconds()).padStart(2,'0');
}
function addLog(type, msg) {
  STATE.logs.unshift({type, msg, time:nowT()});
}
