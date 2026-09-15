# SupplyPrescript Frontend

React + Vite frontend for **SupplyPrescript**, a closed-loop prescriptive analytics system for supply-chain delay risk prediction, optimization, operational decision execution, outcome recording, and ROI analysis.

The frontend is integrated with the SupplyPrescript **FastAPI backend**, **PostgreSQL database**, ML ensemble, and **PuLP/CBC optimization engine**.

---


## Purpose

The frontend provides an interactive operations dashboard for:

- Viewing ML-driven late-delivery risk
- Monitoring backend and model readiness
- Reviewing prescriptive optimization recommendations
- Comparing intervention cost, expected savings, time, and residual risk
- Accepting or rejecting optimizer recommendations
- Executing accepted decisions
- Recording actual operational outcomes
- Comparing predicted and actual costs
- Viewing closed-loop ROI
- Configuring optimizer budgets, capacities, and action availability

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 18.3+ |
| Build Tool | Vite 5.4+ |
| Language | JavaScript / JSX |
| Styling | Plain CSS |
| State | React hooks |
| API Client | Native `fetch` through `src/services/api.js` |
| Backend | FastAPI |
| Database | PostgreSQL |
| ML | XGBoost + LightGBM + CatBoost ensemble |
| Optimization | PuLP + CBC |
| Local Persistence | `localStorage` for frontend workflow references/settings |

---

## Architecture

```text
                     SupplyPrescript

                 ┌───────────────────┐
                 │   React + Vite    │
                 │     Frontend      │
                 └─────────┬─────────┘
                           │
                         HTTP
                           │
                           ▼
                 ┌───────────────────┐
                 │      FastAPI      │
                 │      Backend      │
                 └──────┬─────┬──────┘
                        │     │
                ┌───────┘     └────────┐
                ▼                      ▼
        ┌───────────────┐      ┌───────────────┐
        │  ML Ensemble  │      │   PuLP / CBC  │
        │ XGB/LGBM/Cat  │      │   Optimizer   │
        └───────┬───────┘      └───────┬───────┘
                │                      │
                └──────────┬───────────┘
                           ▼
                 ┌───────────────────┐
                 │    PostgreSQL     │
                 └─────────┬─────────┘
                           │
                           ▼
        Decision → Execution → Outcome → ROI
````

### Architecture Flow

* The React frontend communicates only with the FastAPI backend.
* The frontend does not call the ML models or optimizer directly.
* FastAPI uses the XGBoost, LightGBM, and CatBoost ensemble for prediction.
* FastAPI invokes the PuLP/CBC optimizer for prescriptive recommendations.
* Orders, predictions, optimization runs, recommendations, decisions, outcomes, and ROI data are persisted in PostgreSQL.
* The frontend accesses the workflow through REST API endpoints.

---

## Folder Structure

```text
frontend/
├── index.html
├── package.json
├── package-lock.json
├── README.md
├── .env.example
│
├── src/
│   ├── main.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── components/
│   │   └── ui/
│   │       ├── Accordion.jsx
│   │       ├── Badge.jsx
│   │       ├── Button.jsx
│   │       ├── Card.jsx
│   │       ├── ErrorBoundary.jsx
│   │       ├── Modal.jsx
│   │       ├── Spinner.jsx
│   │       └── Toast.jsx
│   │
│   ├── hooks/
│   │   ├── useDecisionHistory.js
│   │   ├── useLocalStorage.js
│   │   └── useToast.js
│   │
│   ├── data/
│   │   └── mockData.js
│   │
│   ├── utils/
│   │   └── formatters.js
│   │
│   ├── styles.css
│   │
│   └── styles/
│       ├── tokens.css
│       ├── base.css
│       ├── components.css
│       ├── layout.css
│       ├── legacy.css
│       └── integration.css
│
├── dist/                 # Generated production build
└── node_modules/         # Local npm dependencies
```


---

## Environment Configuration

Use `.env.example` as the reference configuration.

```env
VITE_API_ROOT_URL=http://127.0.0.1:8000
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1

VITE_DEMO_ORDER_ID=1
VITE_DEMO_RUN_ID=1
VITE_DEMO_DECISION_ID=1
```

The demo IDs point to the persisted end-to-end development example.

If the database is reset or reseeded, these IDs may need to be changed.

---

## Prerequisites

* Node.js 18+
* npm
* SupplyPrescript FastAPI backend
* PostgreSQL
* Backend ML model artifacts

---

## Installation

From the repository root:

```powershell
cd frontend
npm install
```

---

## Development Server

```powershell
npm run dev
```

Default frontend URL:

```text
http://localhost:5173
```

Expected backend URL:

```text
http://127.0.0.1:8000
```

---

## Production Build

```powershell
npm run build
```

The production build has been successfully validated using:

```text
Vite 5.4.21
34 modules transformed
Build successful
```

Generated files are written to:

```text
frontend/dist/
```

`dist/` is ignored by Git.

---

## Preview Production Build

```powershell
npm run preview
```

---

# Application Pages

The application currently uses React state-based page switching rather than React Router.

## 1. Dashboard

The Dashboard displays live backend/database information including:

* Order ID
* Order status
* Late-risk probability
* ML classification threshold
* High-risk / low-risk classification
* Optimization run status
* Optimizer recommendation
* Intervention cost
* Expected saving
* Predicted action time
* Residual risk after action
* Relative risk reduction
* Decision workflow progress
* ROI when an outcome exists

Example persisted development record:

```text
Order: #1
Status: COMPLETE

Late Risk: 54.88%
Threshold: 22%

Recommendation: PRIORITY_HANDLING
Action ID: A2
Intervention Cost: $900.00
Predicted Time: 4 days
Risk After Intervention: 43.90%
Expected Saving: $197.60
```

The optimizer is correctly displayed as:

```text
PuLP / CBC
```

---

## 2. Decisions

The Decisions page represents the closed-loop operational decision lifecycle.

The backend persists:

* Recommendation decisions
* Accept/reject status
* Execution status
* Actual operational outcomes
* ROI-related information

Decision writes are no longer simulated.

They are sent through FastAPI and stored in PostgreSQL.

### Local Storage

`localStorage` is still used to retain frontend workflow references because the current backend does not yet expose a general decision-history listing endpoint.

It does **not** replace PostgreSQL persistence.

---

## 3. Decision ROI

The Decision ROI page displays:

* Number of tracked decisions
* Completed outcomes
* Average predicted cost
* Average actual cost
* Predicted vs actual cost comparison
* Selected action
* Realized savings
* Time variance
* Model-relative ROI

### ROI Interpretation

The baseline used by the backend is a modeled expected-loss/counterfactual baseline.

Therefore, the displayed realized ROI should be interpreted as:

```text
Model-relative realized ROI
```

and not as audited financial/accounting ROI.

---

## 4. Constraints

The Constraints page is connected to the real PuLP/CBC optimizer.

Configurable values include:

* Total intervention budget
* Late-delivery penalty
* Baseline delivery time
* Expedite capacity
* Priority-handling capacity
* Alternative-route capacity
* Alternative-hub capacity
* Individual action availability

Running:

```text
Run & Persist Optimization
```

calls the FastAPI optimizer endpoint and persists a new `optimization_runs` record and the corresponding `optimization_recommendations` record.

---

# Closed-Loop Workflow

The implemented application workflow is:

```text
1. Predict
      ↓
2. Prescribe
      ↓
3. Accept / Reject
      ↓
4. Execute
      ↓
5. Record Outcome
      ↓
6. Calculate ROI
```

The Dashboard summarizes the main lifecycle as:

```text
Predict → Prescribe → Execute → Measure
```

---

# Backend API Integration

All frontend API communication is centralized in:

```text
src/services/api.js
```

## Health / Readiness

```http
GET /ready
```

Used for backend and ML-model readiness monitoring.

---

## Orders and Predictions

```http
POST /api/v1/orders/predict

GET /api/v1/orders/{order_id}

GET /api/v1/predictions/{prediction_id}

GET /api/v1/orders/{order_id}/predictions
```

---

## Optimization

```http
POST /api/v1/optimize

GET /api/v1/optimization-runs/{run_id}

GET /api/v1/recommendations/{recommendation_id}

GET /api/v1/optimization-runs/{run_id}/recommendations
```

---

## Decision Lifecycle

```http
POST /api/v1/recommendations/{recommendation_id}/decision

POST /api/v1/decisions/{decision_id}/execute

POST /api/v1/decisions/{decision_id}/outcome

GET /api/v1/decisions/{decision_id}/roi
```

---

# Machine Learning Integration

SupplyPrescript ML V2 uses an ensemble of:

* XGBoost
* LightGBM
* CatBoost

Example validated persisted prediction:

```text
Late-risk probability: 0.548798
Classification threshold: 0.22
Predicted late risk: true
Model version: SupplyPrescript ML V2
```

The ML model predicts:

```text
Probability of late delivery
```

It does **not** directly predict a specific number of delay days.

---

# Optimization Engine

The prescriptive optimization layer uses:

```text
PuLP + CBC Solver
```

Supported intervention actions include:

| Action ID | Action            |
| --------- | ----------------- |
| A0        | NO_ACTION         |
| A1        | EXPEDITE          |
| A2        | PRIORITY_HANDLING |
| A3        | ALTERNATIVE_ROUTE |
| A4        | ALTERNATIVE_HUB   |

The frontend displays recommendations persisted by the actual optimizer.

The original static:

* Air Freight
* Secondary Supplier
* Delay Product Launch

cards are no longer used for the integrated dashboard workflow.

---

# Decision Lifecycle

```text
Optimizer Recommendation
          |
          ├──── Reject
          |
          └──── Accept
                  |
                  ▼
               Execute
                  |
                  ▼
           Record Outcome
                  |
                  ▼
             Calculate ROI
```

Decision, execution, and outcome operations are sent to FastAPI and persisted in PostgreSQL.

---

# Backend Read-API Limitation

The current backend does not yet expose a general endpoint such as:

```http
GET /api/v1/decisions
```

or a generic endpoint for discovering the decision attached to any recommendation.

Because of this, the frontend stores returned workflow references in browser `localStorage` for UI continuity.

The underlying operational records remain persisted in PostgreSQL.

A future enhancement should add decision/outcome list/read APIs and remove this frontend dependency.

---

# System Monitoring

The frontend periodically calls:

```http
GET /ready
```

and shows:

* System Online
* System Offline
* Model loaded status
* Current ML threshold

This is backend readiness polling.

It is **not** WebSocket or SSE streaming.

---

# Error Handling

The frontend includes:

* API error handling
* Toast notifications
* React Error Boundary
* Loading states
* Backend-offline state
* Empty recommendation handling
* Budget validation
* Optimizer execution status

---

# Current Validation

## Backend

Latest validated backend test result:

```text
46 passed, 34 warnings
```

The warnings are currently non-blocking dependency/deprecation warnings.

## Frontend

Production build:

```powershell
npm run build
```

Latest result:

```text
34 modules transformed
Build successful
```

## Git

The integrated repository was verified with:

```text
nothing to commit, working tree clean
```

---

# Current Project Status

| Area                           | Status                |
| ------------------------------ | --------------------- |
| UI / UX                        | ✅ Complete            |
| Vite Production Build          | ✅ Passing             |
| FastAPI Integration            | ✅ Complete            |
| PostgreSQL Integration         | ✅ Complete            |
| ML Prediction Display          | ✅ Complete            |
| XGBoost / LightGBM / CatBoost  | ✅ Complete            |
| PuLP / CBC Optimization        | ✅ Complete            |
| Recommendation Display         | ✅ Complete            |
| Accept / Reject Workflow       | ✅ Complete            |
| Decision Execution             | ✅ Complete            |
| Outcome Recording              | ✅ Complete            |
| ROI Calculation / Display      | ✅ Complete            |
| Backend Readiness Monitoring   | ✅ Complete            |
| Authentication / Authorization | ❌ Not implemented     |
| General Decision History API   | ⚠️ Future enhancement |
| Frontend Automated Tests       | ❌ Not configured      |
| WebSocket / SSE Updates        | ❌ Not implemented     |
| CI/CD                          | ❌ Not configured      |

---

# Demo Data

The local development database currently contains a persisted end-to-end demonstration chain:

```text
Order #1
Prediction #1
Optimization Run #1
Recommendation #1
Decision #1
Outcome #1
```

The recorded outcome used during end-to-end validation was **simulated test/demo data**.

It should not be presented as real operational production evidence.

---

# Git Ignore

Do not commit:

```text
node_modules/
dist/
.env
```

Commit:

```text
.env.example
package.json
package-lock.json
src/
README.md
```

---

# Contributor Notes

* The frontend currently uses JavaScript/JSX rather than TypeScript.
* React Router is not currently used.
* The four main views are switched using React state.
* Charts are implemented using lightweight CSS.
* Several original reusable UI components remain available.
* Some legacy/mock utility files remain in the source tree but are no longer the primary data source.
* Authentication is intentionally outside the current project/demo scope.

---

# Related Components

Backend:

```text
../backend/
```

Backend documentation:

```text
../backend/README.md
```

Main repository documentation:

```text
../README.md
```

---

# Summary

SupplyPrescript has progressed from an offline mock frontend into an integrated closed-loop prescriptive analytics application:

```text
React
   ↓
FastAPI
   ↓
ML Ensemble
   ↓
PuLP / CBC
   ↓
PostgreSQL
   ↓
Decision
   ↓
Execution
   ↓
Outcome
   ↓
ROI
```

The frontend implementation is functionally complete for the current project/demo scope.

Remaining work is primarily production hardening, authentication, expanded backend read APIs, frontend test automation, CI/CD, and deployment.

````
