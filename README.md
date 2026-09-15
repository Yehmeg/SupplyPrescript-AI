# SupplyPrescript-AI

**AI-Powered Closed-Loop Supply Chain Decision Support System**

SupplyPrescript is an end-to-end prescriptive analytics platform that identifies supply-chain delivery risk, recommends cost-aware interventions, records operational decisions, captures actual outcomes, and measures decision ROI.

The system combines:

- Machine Learning for late-delivery risk prediction
- Mathematical optimization for intervention selection
- FastAPI for backend orchestration
- PostgreSQL for persistent operational data
- React + Vite for the decision-support dashboard
- Closed-loop outcome and ROI tracking

---

## Project Objective

Traditional supply-chain analytics often stops after predicting that a shipment may be delayed.

SupplyPrescript goes further.

Instead of only answering:

> **"Will this shipment be late?"**

the system also answers:

> **"What should we do about it?"**

and finally:

> **"Did the intervention actually work?"**

This creates a complete closed-loop decision workflow:

```text
Predict
   ↓
Prescribe
   ↓
Decide
   ↓
Execute
   ↓
Measure
   ↓
Evaluate ROI
```

---

# System Architecture

```text
                        SUPPLYPRESCRIPT

                 ┌─────────────────────┐
                 │   React + Vite UI   │
                 │ Decision Dashboard  │
                 └──────────┬──────────┘
                            │
                         REST API
                            │
                            ▼
                 ┌─────────────────────┐
                 │       FastAPI       │
                 │   Backend Service   │
                 └──────┬────────┬─────┘
                        │        │
              ┌─────────┘        └─────────┐
              ▼                            ▼
      ┌─────────────────┐          ┌─────────────────┐
      │   ML Ensemble   │          │   PuLP / CBC    │
      │                 │          │    Optimizer    │
      │ XGBoost         │          │                 │
      │ LightGBM        │          │ Budget          │
      │ CatBoost        │          │ Capacity        │
      └────────┬────────┘          │ Availability    │
               │                   └────────┬────────┘
               │                            │
               └──────────────┬─────────────┘
                              ▼
                    ┌───────────────────┐
                    │    PostgreSQL     │
                    │ Persistent Store  │
                    └─────────┬─────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Closed-Loop Lifecycle   │
                 │                         │
                 │ Decision                │
                 │ Execution               │
                 │ Outcome                 │
                 │ ROI                     │
                 └─────────────────────────┘
```

---

## End-to-End Workflow

### 1. Order Ingestion

Supply-chain order/shipment information is received by the backend.

The backend stores the order and prepares the required ML features.

```text
Order
  ↓
Feature validation
  ↓
ML inference
```

---

### 2. ML Risk Prediction

SupplyPrescript ML V2 uses an ensemble of:

- XGBoost
- LightGBM
- CatBoost

The model predicts the probability that an eligible order will be delivered late.

Example persisted prediction:

```text
Late-risk probability: 0.548798
ML threshold: 0.22
Predicted late risk: true
Model version: SupplyPrescript ML V2
```

The ML system predicts **late-delivery probability**.

It does not directly predict the number of delay days.

---

### 3. Prescriptive Optimization

High-risk predictions can be passed to the optimization engine.

The optimizer uses:

```text
PuLP + CBC Solver
```

It considers:

- Late-delivery probability
- Expected delay penalty
- Intervention cost
- Budget limits
- Action capacities
- Action availability
- Expected residual risk

The optimizer selects the most appropriate intervention according to the objective and constraints.

---

### 4. Decision

The generated recommendation can be:

```text
ACCEPTED
```

or:

```text
REJECTED
```

Accepted recommendations can proceed to execution.

---

### 5. Execution

An accepted intervention is marked as executed.

This provides an operational audit trail linking:

```text
Prediction
    ↓
Recommendation
    ↓
Decision
    ↓
Execution
```

---

### 6. Outcome Recording

After execution, the actual operational result can be recorded.

Examples include:

- Actual intervention cost
- Actual delivery time
- Whether the order was delayed
- Actual delay cost
- Operational notes

---

### 7. ROI Evaluation

SupplyPrescript compares the predicted optimization result with the recorded actual outcome.

The system calculates metrics such as:

- Intervention cost variance
- Optimized cost variance
- Realized savings vs modeled baseline
- Savings variance
- Time variance
- Model-relative realized ROI

> The baseline expected loss is a modeled/counterfactual value. Therefore the displayed realized ROI is **model-relative ROI**, not audited accounting ROI.

---

# Repository Structure

```text
SupplyPrescript-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── models/
│   ├── tests/
│   ├── .env.example
│   ├── .gitignore
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── data/
│   │   ├── hooks/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   ├── utils/
│   │   └── main.jsx
│   │
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── README.md
│
├── DescriptionDataCoSupplyChain.csv
├── .gitignore
├── LICENSE
└── README.md
```

Generated/local folders such as the following are ignored by Git:

```text
backend/.venv/
backend/.pytest_cache/
backend/.env

frontend/node_modules/
frontend/dist/
frontend/.env
```

---

# Technology Stack

## Frontend

| Technology | Purpose |
|---|---|
| React 18 | User interface |
| Vite 5 | Development/build tooling |
| JavaScript / JSX | Frontend application logic |
| CSS | Styling and dashboard visualization |
| Fetch API | FastAPI communication |
| localStorage | UI workflow references/settings |

---

## Backend

| Technology | Purpose |
|---|---|
| Python 3.11 | Backend runtime |
| FastAPI | REST API |
| Pydantic | Request/response validation |
| SQLAlchemy | Database access |
| psycopg | PostgreSQL driver |
| PostgreSQL | Persistent database |
| pytest | Automated backend testing |

---

## Machine Learning

| Technology | Purpose |
|---|---|
| XGBoost | Ensemble model |
| LightGBM | Ensemble model |
| CatBoost | Ensemble model |
| Pandas | Data handling |
| NumPy | Numerical processing |
| scikit-learn | ML utilities |

---

## Optimization

| Technology | Purpose |
|---|---|
| PuLP | Optimization modeling |
| CBC | Mathematical optimization solver |

---

# Supported Optimization Actions

The current optimizer supports:

| Action ID | Intervention |
|---|---|
| A0 | NO_ACTION |
| A1 | EXPEDITE |
| A2 | PRIORITY_HANDLING |
| A3 | ALTERNATIVE_ROUTE |
| A4 | ALTERNATIVE_HUB |

Example action configuration:

| Action | Cost | Risk Reduction | Time Reduction |
|---|---:|---:|---:|
| NO_ACTION | $0 | 0% | 0 days |
| EXPEDITE | $1,800 | 35% | 2 days |
| PRIORITY_HANDLING | $900 | 20% | 1 day |
| ALTERNATIVE_ROUTE | $1,400 | 28% | 1.5 days |
| ALTERNATIVE_HUB | $2,200 | 40% | 1 day |

---

# PostgreSQL Data Model

The integrated development database contains six primary tables.

## `orders`

Stores submitted orders and prediction eligibility information.

---

## `ml_predictions`

Stores persisted ML inference results.

Key information includes:

- Model version
- Late-risk probability
- Predicted late-risk class
- Threshold
- Prediction eligibility
- Ensemble metadata

---

## `optimization_runs`

Stores optimizer executions.

Example fields include:

- Run ID
- Request ID
- Optimization status
- Total intervention cost
- Total expected saving

---

## `optimization_recommendations`

Stores the intervention selected for each optimized shipment.

Information includes:

- Action
- Late probability
- Risk after intervention
- Action cost
- Expected saving
- Baseline expected loss
- Optimized expected cost
- Predicted time

---

## `recommendation_decisions`

Stores management decisions and execution state.

Examples:

```text
ACCEPTED
REJECTED
PENDING
EXECUTED
```

---

## `optimization_outcomes`

Stores actual results after execution.

Examples include:

- Actual intervention cost
- Actual delivery time
- Actual delayed status
- Actual delay cost
- Actual total cost
- Outcome notes

---

# FastAPI Endpoints

## System

```http
GET /health
GET /ready
```

---

## Prediction

```http
POST /api/v1/predict

POST /api/v1/orders/predict
```

---

## Order / Prediction Reads

```http
GET /api/v1/orders/{order_id}

GET /api/v1/predictions/{prediction_id}

GET /api/v1/orders/{order_id}/predictions
```

---

## Optimization

```http
POST /api/v1/optimize
```

---

## Optimization Reads

```http
GET /api/v1/optimization-runs/{run_id}

GET /api/v1/recommendations/{recommendation_id}

GET /api/v1/optimization-runs/{run_id}/recommendations
```

---

## Recommendation Decisions

```http
POST /api/v1/recommendations/{recommendation_id}/decision
```

---

## Execution

```http
POST /api/v1/decisions/{decision_id}/execute
```

---

## Outcome

```http
POST /api/v1/decisions/{decision_id}/outcome
```

---

## ROI

```http
GET /api/v1/decisions/{decision_id}/roi
```

---

# Frontend Application

The React dashboard contains four main views.

## Dashboard

Displays:

- Order information
- ML late-risk prediction
- ML threshold
- Optimization status
- Selected recommendation
- Intervention cost
- Expected saving
- Risk after action
- Predicted time
- Closed-loop progress
- ROI when available

---

## Decisions

Displays the operational decision lifecycle and predicted/actual cost information.

---

## Decision ROI

Displays:

- Decisions tracked
- Completed outcomes
- Predicted vs actual cost
- Realized savings
- Time variance
- Model-relative ROI

---

## Constraints

Allows configuration of optimizer inputs such as:

- Budget
- Late-delivery penalty
- Baseline delivery time
- Action capacities
- Action availability

The frontend can execute and persist a new optimization run through the real FastAPI backend.

---

# Current Demonstration Record

The local development database contains a validated end-to-end example:

```text
Order #1
   ↓
Prediction #1
   ↓
Optimization Run #1
   ↓
Recommendation #1
   ↓
Decision #1
   ↓
Outcome #1
   ↓
ROI
```

Example values:

```text
Order status:
COMPLETE

Late-risk probability:
54.88%

ML threshold:
22%

Selected action:
PRIORITY_HANDLING

Action ID:
A2

Action cost:
$900.00

Risk before:
54.88%

Risk after:
43.90%

Predicted time:
4 days

Expected saving:
$197.60
```

A simulated outcome was used to verify the complete development workflow.

The resulting example ROI is therefore demonstration data and must not be presented as real production financial performance.

---

# Backend Setup

## 1. Open Backend

```powershell
cd D:\SupplyPrescript-AI-team\SupplyPrescript-AI\backend
```

---

## 2. Create Virtual Environment

Python 3.11 is recommended.

```powershell
py -3.11 -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Configure Environment

Create:

```text
backend/.env
```

using:

```text
backend/.env.example
```

Example database URL format:

```env
DATABASE_URL=postgresql+psycopg://supplyprescript_app:<PASSWORD>@localhost:5433/supplyprescript
```

Never commit the real `.env` file or database password.

---

## 5. Initialize Database Tables

```powershell
python -m app.db.init_db
```

---

## 6. Start FastAPI

```powershell
uvicorn app.main:app --reload
```

Default backend:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open another terminal.

```powershell
cd D:\SupplyPrescript-AI-team\SupplyPrescript-AI\frontend
```

Install dependencies:

```powershell
npm install
```

Start development server:

```powershell
npm run dev
```

Default frontend:

```text
http://localhost:5173
```

---

## Frontend Environment

Reference:

```text
frontend/.env.example
```

Current example:

```env
VITE_API_ROOT_URL=http://127.0.0.1:8000
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1

VITE_DEMO_ORDER_ID=1
VITE_DEMO_RUN_ID=1
VITE_DEMO_DECISION_ID=1
```

The IDs are development/demo references and may need to change after resetting or reseeding PostgreSQL.

---

# Running the Complete Application

Use two terminals.

## Terminal 1 — Backend

```powershell
cd D:\SupplyPrescript-AI-team\SupplyPrescript-AI\backend

.\.venv\Scripts\Activate.ps1

uvicorn app.main:app --reload
```

---

## Terminal 2 — Frontend

```powershell
cd D:\SupplyPrescript-AI-team\SupplyPrescript-AI\frontend

npm run dev
```

Then open:

```text
http://localhost:5173
```

---

# Testing

## Backend Tests

From:

```text
backend/
```

run:

```powershell
pytest -q
```

Latest validated result:

```text
46 passed, 34 warnings
```

The current warnings are non-blocking dependency/deprecation warnings.

---

## Frontend Build Validation

From:

```text
frontend/
```

run:

```powershell
npm run build
```

Latest validated build:

```text
vite v5.4.21
34 modules transformed
Build successful
```

---

# Project Status

| Component | Status |
|---|---|
| ML Pipeline | ✅ Complete |
| XGBoost Model | ✅ Complete |
| LightGBM Model | ✅ Complete |
| CatBoost Model | ✅ Complete |
| Ensemble Inference | ✅ Complete |
| Prediction Persistence | ✅ Complete |
| PostgreSQL Integration | ✅ Complete |
| PuLP/CBC Optimizer | ✅ Complete |
| Optimization Persistence | ✅ Complete |
| Recommendation Read APIs | ✅ Complete |
| Decision Accept/Reject | ✅ Complete |
| Decision Execution | ✅ Complete |
| Outcome Recording | ✅ Complete |
| ROI Calculation | ✅ Complete |
| React Dashboard | ✅ Complete |
| Backend Status Monitoring | ✅ Complete |
| Frontend Production Build | ✅ Passing |
| Backend Automated Tests | ✅ 46 Passing |
| Authentication / Authorization | ❌ Not implemented |
| General Decision History Read API | ⚠️ Future Enhancement |
| Frontend Automated Tests | ❌ Not configured |
| WebSocket / SSE Live Updates | ❌ Not implemented |
| CI/CD | ❌ Not configured |
| Production Deployment | ❌ Not configured |

---

# Current Backend Limitation

The current backend provides individual decision lifecycle operations but does not yet expose a general endpoint such as:

```http
GET /api/v1/decisions
```

or a general recommendation-to-decision lookup endpoint.

Because of this, the React frontend retains returned workflow references in `localStorage` for UI continuity.

This does not replace PostgreSQL persistence.

Decision, execution, and outcome writes are still stored by the backend.

---

# Error Handling and Reliability

Implemented safeguards include:

- Pydantic request validation
- Database persistence validation
- Prediction eligibility handling
- Optimizer feasibility handling
- API error propagation
- React Error Boundary
- Toast notifications
- Loading states
- Backend-offline state
- Budget validation
- Empty recommendation handling

---

# Git and Security

The repository ignores local/generated files including:

```text
backend/.env
backend/.venv/
backend/.pytest_cache/

frontend/.env
frontend/node_modules/
frontend/dist/
```

Files such as these are safe to commit:

```text
backend/.env.example
frontend/.env.example

backend/requirements.txt

frontend/package.json
frontend/package-lock.json

backend/app/
backend/tests/
frontend/src/
```

Never commit:

- Passwords
- Database credentials
- API secrets
- Real `.env` files

---

# Current Git Development Branch

Current integrated development work has been performed on:

```text
feature/backend-db-integration
```

The branch contains the completed backend closed-loop workflow and frontend integration.

---

# Known Limitations

The current version is designed for project/demo use rather than production deployment.

Not yet implemented:

- User authentication
- Role-based access control
- Production secret management
- General decision-history pagination
- Full audit/user identity model
- WebSocket/SSE updates
- Frontend automated testing
- Production migrations workflow
- CI/CD pipeline
- Production monitoring
- Production deployment

---

# Future Improvements

Potential extensions include:

1. Authentication and role-based authorization
2. Decision and outcome list/read APIs
3. Alembic database migrations
4. Automated frontend testing with Vitest/Playwright
5. CI/CD using GitHub Actions
6. Production containerization
7. Docker Compose deployment
8. Monitoring and structured logging
9. Multi-order optimization dashboard
10. Historical recommendation analytics
11. Model drift monitoring
12. Scheduled model evaluation
13. Real-time event ingestion
14. WebSocket/SSE dashboard updates
15. Production cloud deployment

---

# Documentation

Detailed backend documentation:

```text
backend/README.md
```

Detailed frontend documentation:

```text
frontend/README.md
```

---

# Final Validation

The integrated project has successfully passed:

```text
Backend:
46 passed

Frontend:
Production Vite build successful

Database:
PostgreSQL persistence verified

ML:
Ensemble inference verified

Optimization:
PuLP/CBC optimal solution verified

Closed Loop:
Prediction
→ Recommendation
→ Decision
→ Execution
→ Outcome
→ ROI

Git:
Working tree clean
```

---

# Summary

SupplyPrescript implements the complete transition from **predictive analytics** to **prescriptive and closed-loop analytics**.

```text
Raw Supply Chain Data
        ↓
Feature Processing
        ↓
ML Risk Prediction
        ↓
Prescriptive Optimization
        ↓
Management Decision
        ↓
Operational Execution
        ↓
Actual Outcome
        ↓
ROI Evaluation
```

Instead of stopping at a delay-risk prediction, SupplyPrescript provides an actionable recommendation and tracks whether the selected intervention produced the expected operational result.

The core project implementation is functionally complete for the current academic/demo scope.

---

## License

See the repository's [`LICENSE`](LICENSE) file for licensing information.