# Distributed Emergency Resource Allocation System
## Tamil Nadu | 38 Districts | Role-Based Access | Fault Tolerance | Smart Allocation

A distributed, REST-based system for managing emergency resource allocation across all **38 districts of Tamil Nadu**. It provides role-based access control, intelligent resource dispatch, and fault-tolerant distributed operation.

---

## Features

| Feature | Details |
|---|---|
| **38 Districts** | Complete coverage of all Tamil Nadu districts with geo-coordinates, population, and resource inventory |
| **Role-Based Access** | 5 roles: Admin, State Coordinator, District Manager, Field Officer, Viewer |
| **Smart Allocation** | Priority × proximity × availability scoring algorithm |
| **Fault Tolerance** | Node registry, circuit breaker, data replication, health monitor with failover |
| **REST API** | Flask-based JSON API with JWT authentication |

---

## Architecture

```
src/
├── app.py              # Flask REST API — all endpoints
├── auth.py             # RBAC: roles, permissions, JWT, decorators
├── allocation.py       # Smart allocation engine
├── districts.py        # Tamil Nadu 38-district dataset
├── models.py           # Data models & in-memory store
└── fault_tolerance.py  # Node registry, circuit breaker, replication, health monitor

tests/
├── test_api.py         # API integration tests
├── test_auth.py        # RBAC & JWT tests
├── test_allocation.py  # Allocation engine tests
├── test_districts.py   # District data tests
└── test_fault_tolerance.py  # Fault tolerance tests
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python -m src.app

# Run tests
python -m pytest tests/ -v
```

---

## Tamil Nadu Districts (38)

| # | District | HQ | District ID |
|---|---|---|---|
| 1 | Ariyalur | Ariyalur | TN-AR |
| 2 | Chengalpattu | Chengalpattu | TN-CGL |
| 3 | Chennai | Chennai | TN-CHE |
| 4 | Coimbatore | Coimbatore | TN-CBE |
| 5 | Cuddalore | Cuddalore | TN-CUD |
| 6 | Dharmapuri | Dharmapuri | TN-DHP |
| 7 | Dindigul | Dindigul | TN-DGL |
| 8 | Erode | Erode | TN-ERD |
| 9 | Kallakurichi | Kallakurichi | TN-KLK |
| 10 | Kancheepuram | Kancheepuram | TN-KPM |
| 11 | Kanyakumari | Nagercoil | TN-KNY |
| 12 | Karur | Karur | TN-KRR |
| 13 | Krishnagiri | Krishnagiri | TN-KRG |
| 14 | Madurai | Madurai | TN-MDU |
| 15 | Mayiladuthurai | Mayiladuthurai | TN-MYD |
| 16 | Nagapattinam | Nagapattinam | TN-NGP |
| 17 | Namakkal | Namakkal | TN-NMK |
| 18 | Nilgiris | Ooty | TN-NLG |
| 19 | Perambalur | Perambalur | TN-PRM |
| 20 | Pudukkottai | Pudukkottai | TN-PDK |
| 21 | Ramanathapuram | Ramanathapuram | TN-RMN |
| 22 | Ranipet | Ranipet | TN-RNP |
| 23 | Salem | Salem | TN-SLM |
| 24 | Sivaganga | Sivaganga | TN-SVG |
| 25 | Tenkasi | Tenkasi | TN-TNK |
| 26 | Thanjavur | Thanjavur | TN-TNJ |
| 27 | Theni | Theni | TN-THN |
| 28 | Thoothukudi | Thoothukudi | TN-TUT |
| 29 | Tiruchirappalli | Tiruchirappalli | TN-TRY |
| 30 | Tirunelveli | Tirunelveli | TN-TNV |
| 31 | Tirupattur | Tirupattur | TN-TPT |
| 32 | Tiruppur | Tiruppur | TN-TPR |
| 33 | Tiruvallur | Tiruvallur | TN-TVL |
| 34 | Tiruvannamalai | Tiruvannamalai | TN-TVN |
| 35 | Tiruvarur | Tiruvarur | TN-TVR |
| 36 | Vellore | Vellore | TN-VLR |
| 37 | Villupuram | Villupuram | TN-VPM |
| 38 | Virudhunagar | Virudhunagar | TN-VDN |

---

## Role-Based Access Control

| Role | Incidents | Allocations | Districts | Users | System |
|---|---|---|---|---|---|
| **Admin** | CRUD | CRUD | R/W | Manage | Admin |
| **State Coordinator** | CRUD | CRUD | R/W | — | — |
| **District Manager** | CRU | CRU | R | — | — |
| **Field Officer** | CRU | R | R | — | — |
| **Viewer** | R | R | R | — | — |

### Default Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@123` | Admin |
| `state_coordinator` | `State@123` | State Coordinator |
| `dm_chennai` | `District@123` | District Manager (Chennai) |
| `fo_chennai` | `Field@123` | Field Officer (Chennai) |
| `viewer` | `Viewer@123` | Viewer |

---

## API Endpoints

### Authentication
```
POST /api/auth/login          # Get JWT token
GET  /api/auth/me             # Get current user info
```

### Districts
```
GET /api/districts            # List all 38 districts with live resources
GET /api/districts/<id>       # Get single district detail
```

### Incidents
```
GET    /api/incidents                       # List incidents (scoped by role)
POST   /api/incidents                       # Create incident (+ optional auto_allocate)
GET    /api/incidents/<id>                  # Get incident detail
PUT    /api/incidents/<id>                  # Update incident
DELETE /api/incidents/<id>                  # Delete incident
```

### Resource Allocation
```
POST /api/incidents/<id>/allocate           # Auto-allocate resources for incident
GET  /api/incidents/<id>/allocations        # Get allocation summary for incident
GET  /api/allocations                       # List allocations (filterable)
POST /api/allocations/<id>/release          # Return resources to source district
```

### System & Fault Tolerance (Admin only)
```
GET  /api/system/health                     # Cluster health report
GET  /api/system/nodes                      # List all nodes and status
POST /api/system/nodes/<id>/heartbeat       # Record node heartbeat
POST /api/system/nodes/<id>/failover        # Trigger manual failover
```

---

## Smart Allocation Algorithm

Resources are allocated using a weighted scoring function:

```
score = availability_ratio × 0.6 + proximity_score × 0.4
```

Where:
- **availability_ratio** = available resources / total inventory (after 20% reserve)
- **proximity_score** = 1 / (1 + distance_km / 100)

Districts are ranked by score and resources are drawn greedily until the need is met or all candidates within 600 km are exhausted.

---

## Fault Tolerance Components

| Component | Description |
|---|---|
| **NodeRegistry** | Tracks health of all system nodes; marks DEGRADED after 1 failure, UNREACHABLE after 3 |
| **CircuitBreaker** | Opens after N failures, probes in HALF_OPEN after timeout, resets on success |
| **ReplicationManager** | Replicates data snapshots to healthy replica nodes |
| **HealthMonitor** | Background thread that checks heartbeats and triggers failover callbacks |
