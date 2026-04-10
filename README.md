<img width="1916" height="884" alt="image" src="https://github.com/user-attachments/assets/a6434df8-aca7-4f12-a201-864123646878" />
<img width="1915" height="885" alt="image" src="https://github.com/user-attachments/assets/797d8141-ada1-4ab3-bfd4-cb7f138a0756" />
<img width="1910" height="883" alt="image" src="https://github.com/user-attachments/assets/7996193a-739d-4805-9a58-ffce6099270c" />
<img width="1915" height="905" alt="image" src="https://github.com/user-attachments/assets/ce111449-56d3-4e65-b286-190ad5af102c" />
<img width="1913" height="886" alt="image" src="https://github.com/user-attachments/assets/bb584f3b-a314-4e8e-a3fc-81dac35dad80" />
<img width="1919" height="891" alt="image" src="https://github.com/user-attachments/assets/2f01ac74-c579-40b9-9874-1c9853aef2c0" />
<img width="1918" height="900" alt="image" src="https://github.com/user-attachments/assets/d3b08e96-0950-4c2c-becf-4ee3d9e3d436" />
<img width="1913" height="896" alt="image" src="https://github.com/user-attachments/assets/d20dd39d-d4cb-4005-a126-f8418ca1d5b1" />
<img width="1917" height="883" alt="image" src="https://github.com/user-attachments/assets/42c97c44-4957-4d9a-b8f2-fcd4811d0b3d" />
<img width="1918" height="892" alt="image" src="https://github.com/user-attachments/assets/558e2980-c007-445c-951c-aea848db9909" />
<img width="1913" height="886" alt="image" src="https://github.com/user-attachments/assets/fc3b7976-074c-4357-8679-1557e71d37d0" />
<img width="1913" height="894" alt="image" src="https://github.com/user-attachments/assets/cd2ded8a-9fec-4361-a878-860c3d37f30b" />

# 🚑 Distributed Emergency Resource Allocation System
## ERAS v4.0 — Tamil Nadu | 38 Districts

## Project Overview
An intelligent self-healing distributed emergency resource allocation system built for Tamil Nadu covering all 38 districts. Demonstrates real-world distributed system concepts including fault tolerance, replication, load balancing, and cross-region coordination.

## Key Features
- Smart Allocation using distance, capacity and ICU scoring algorithm
- Self-Healing system that auto-detects node failure and recovers in under 500ms
- Cross-District Resource Borrowing between districts automatically
- All 38 Tamil Nadu districts as distributed nodes
- Role-Based Access for Admin, Dispatcher, Hospital, Ambulance and Authority
- What-if Simulation Engine with deep copy and 4 scenario types
- Live GPS location capture via browser API
- Interactive canvas-based district map
- Real-time analytics charts with no CDN dependency
- Complete audit trail logging every decision with node and reason

## Role-Based Access
Admin has full access to all features. Dispatcher can create and allocate emergencies. Hospital staff manage beds, ICU and accept patients. Ambulance drivers update availability and accept assignments. Government Authority gets analytics and disaster monitoring in read-only mode.

## Tamil Nadu Districts
All 38 districts are included as distributed nodes: Ariyalur, Chengalpattu, Chennai, Coimbatore, Cuddalore, Dharmapuri, Dindigul, Erode, Kallakurichi, Kanchipuram, Kanyakumari, Karur, Krishnagiri, Madurai, Mayiladuthurai, Nagapattinam, Namakkal, Nilgiris, Perambalur, Pudukkottai, Ramanathapuram, Ranipet, Salem, Sivaganga, Tenkasi, Thanjavur, Theni, Thoothukudi, Tiruchirappalli, Tirunelveli, Tirupattur, Tiruppur, Tiruvallur, Tiruvannamalai, Tiruvarur, Vellore, Viluppuram and Virudhunagar.

## Distributed System Concepts Applied
Fault tolerance is implemented through heartbeat detection, auto-failover and self-healing. Load balancing uses a priority queue with smart scoring across nodes. Replication is demonstrated through Raft consensus simulation with sync timestamps. Message passing handles async event coordination between nodes. Cross-district resource borrowing shows distributed coordination. Priority scheduling follows CRITICAL then HIGH then NORMAL order.

## Project Structure
The project contains index.html as the login page, css/style.css for shared styles, js/data.js for all 38 districts and the allocation engine, and js/ui.js for shared UI utilities. The pages folder contains admin.html for the full access dashboard, dispatcher.html for emergency creation, hospital.html for bed and ICU management, ambulance.html for driver availability, authority.html for government analytics and map.html for the interactive district map.

## 👥 Roles & Access

| Role | Login Page | Features |
|------|-----------|----------|
| **Admin** | admin.html | Full access: emergencies, simulation, fault tolerance, audit, analytics, map |
| **Dispatcher** | dispatcher.html | Create emergencies, smart allocate, view audit |
| **Hospital Staff** | hospital.html | Manage beds/ICU, accept/reject patients, view incoming |
| **Ambulance Driver** | ambulance.html | Update availability, accept/complete assignments, share GPS |
| **Gov. Authority** | authority.html | Analytics only: district stats, disaster monitoring, charts |

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

## Key Phrases

> "My system demonstrates distributed coordination across 38 geographically separated Tamil Nadu district nodes with automatic fault tolerance, role-based secure access, and location-based smart allocation."

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

