# ERAS v4.0 — Tamil Nadu Emergency Resource Allocation System
## Distributed Emergency System | 38 Districts | Role-Based Access

---

## 📁 Project Structure

```
ERAS_TamilNadu/
├── index.html              ← Login page (start here)
├── css/
│   └── style.css           ← Shared styles for all pages
├── js/
│   ├── data.js             ← All 38 districts, ambulances, hospitals + allocation engine
│   └── ui.js               ← Shared UI utilities (toast, notifs, charts, sidebar)
└── pages/
    ├── admin.html          ← Admin: full access, all features
    ├── dispatcher.html     ← Dispatcher: create & allocate emergencies
    ├── hospital.html       ← Hospital staff: manage beds, ICU, accept patients
    ├── ambulance.html      ← Ambulance driver: update status, view assignments
    └── authority.html      ← Government: analytics & disaster monitoring only
```

---

## 🚀 How to Run

**Just open `index.html` in any browser — no server needed.**

Or double-click `index.html` directly.

> For the map view (Leaflet.js) to work, you need an internet connection (loads tiles from OpenStreetMap).

---

## 👥 Roles & Access

| Role | Login Page | Features |
|------|-----------|----------|
| **Admin** | admin.html | Full access: emergencies, simulation, fault tolerance, audit, analytics, map |
| **Dispatcher** | dispatcher.html | Create emergencies, smart allocate, view audit |
| **Hospital Staff** | hospital.html | Manage beds/ICU, accept/reject patients, view incoming |
| **Ambulance Driver** | ambulance.html | Update availability, accept/complete assignments, share GPS |
| **Gov. Authority** | authority.html | Analytics only: district stats, disaster monitoring, charts |

**Demo login:** any username + any password → click Login

---

## 🌍 Districts Included (38)

Ariyalur, Chengalpattu, Chennai, Coimbatore, Cuddalore, Dharmapuri, Dindigul, Erode,
Kallakurichi, Kanchipuram, Kanyakumari, Karur, Krishnagiri, Madurai, Mayiladuthurai,
Nagapattinam, Namakkal, Nilgiris, Perambalur, Pudukkottai, Ramanathapuram, Ranipet,
Salem, Sivaganga, Tenkasi, Thanjavur, Theni, Thoothukudi, Tiruchirappalli, Tirunelveli,
Tirupattur, Tiruppur, Tiruvallur, Tiruvannamalai, Tiruvarur, Vellore, Viluppuram, Virudhunagar

---

## 🔧 Key Distributed System Features

| Feature | Implementation |
|---------|---------------|
| **Smart Allocation** | Distance scoring + capacity scoring + ICU bonus |
| **Self-Healing** | Heartbeat detection → auto-failover → auto-recovery |
| **Cross-District Borrow** | Surplus detection → atomic resource transfer |
| **Replication Sync** | Visual sync timestamps on every operation |
| **Priority Queue** | CRITICAL > HIGH > NORMAL scheduling |
| **Audit Trail** | Every decision logged with node + reason |
| **GPS Location** | navigator.geolocation API for live accident location |
| **Map View** | Leaflet.js with all 38 districts + hospitals |
| **Role-Based Security** | JWT simulation, feature restrictions per role |
| **What-if Simulation** | Deep copy engine, 4 scenario types |

---

## 💬 Viva Key Phrases

> "Our system demonstrates distributed coordination across 38 geographically separated Tamil Nadu district nodes with automatic fault tolerance, role-based secure access, and location-based smart allocation."

> "The simulation engine creates a deep copy of the system state, so what-if scenarios run in parallel without affecting live operations — this is a key principle of distributed system evaluation."

> "When a district node fails, the self-healing system detects the missed heartbeats, triggers automatic failover to a backup node, and reassigns pending requests — all within milliseconds, without human intervention."

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (custom), Vanilla JS |
| Maps | Leaflet.js (OpenStreetMap) |
| Charts | Chart.js 4.x |
| Communication | Simulated Raft consensus + JWT tokens |
| Geolocation | navigator.geolocation API |
| Storage | In-memory (sessionStorage for auth) |

---

*ERAS v4.0 — Built for Tamil Nadu | Distributed Systems Project*
