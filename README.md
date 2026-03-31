<img width="1909" height="891" alt="image" src="https://github.com/user-attachments/assets/0999a7e8-b736-4a23-9ea4-f6d0f3dc21e1" />
<img width="1913" height="900" alt="image" src="https://github.com/user-attachments/assets/0796d2be-5ae0-4bf3-93aa-15b68d9605d8" />
<img width="1902" height="877" alt="image" src="https://github.com/user-attachments/assets/fa1500f2-661f-4818-9949-5907cf1f8053" />
<img width="1916" height="893" alt="image" src="https://github.com/user-attachments/assets/5e9ec349-659d-4c03-9feb-c5e4b2667aab" />
<img width="1912" height="891" alt="image" src="https://github.com/user-attachments/assets/dbd09db9-8ced-406f-a77f-d8df1da178fa" />
<img width="1920" height="877" alt="Screenshot (4400)" src="https://github.com/user-attachments/assets/1c9e7f7c-fd66-468c-90b6-46aaca561dad" />
<img width="1911" height="883" alt="image" src="https://github.com/user-attachments/assets/720baab2-50fe-4b78-9934-50c7d15000e7" />
<img width="1912" height="888" alt="image" src="https://github.com/user-attachments/assets/cc0f40e9-bed3-4784-a28d-84d003e164c0" />
<img width="1911" height="881" alt="image" src="https://github.com/user-attachments/assets/b2beddbe-0056-4901-9078-6131e9815365" />

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

