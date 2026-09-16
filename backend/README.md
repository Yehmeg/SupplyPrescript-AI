# SupplyPrescript Backend

FastAPI backend for **SupplyPrescript**, an AI-powered closed-loop supply-chain prescriptive analytics platform.

The backend provides the complete workflow from ML late-delivery prediction through mathematical optimization, operational decision execution, actual outcome recording, and ROI analysis.

The current backend integrates:

- FastAPI REST APIs
- SupplyPrescript ML V2
- XGBoost + LightGBM + CatBoost ensemble inference
- PostgreSQL persistence
- SQLAlchemy database access
- PuLP/CBC prescriptive optimization
- Recommendation decision workflow
- Execution tracking
- Actual outcome capture
- Predicted-vs-actual ROI calculation
- Automated backend tests

---

## Purpose

SupplyPrescript does more than predict whether an order may arrive late.

The backend supports the complete closed-loop lifecycle:

```text
Order
  ↓
ML Prediction
  ↓
Optimization
  ↓
Recommendation
  ↓
Accept / Reject
  ↓
Execution
  ↓
Actual Outcome
  ↓
ROI Evaluation
```

The goal is to move from **predictive analytics** to **prescriptive and closed-loop analytics**.

---

# Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| Validation | Pydantic |
| Configuration | Pydantic Settings |
| ORM / Database Access | SQLAlchemy |
| PostgreSQL Driver | psycopg |
| Database | PostgreSQL |
| ML Models | XGBoost, LightGBM, CatBoost |
| Data Processing | Pandas, NumPy |
| ML Utilities | scikit-learn, joblib |
| Optimization | PuLP |
| Solver | CBC |
| Testing | pytest |
| API Testing | FastAPI / Starlette TestClient |

---

# Backend Architecture

```text
                        FastAPI Backend
                              |
          ┌───────────────────┼───────────────────┐
          |                   |                   |
          ▼                   ▼                   ▼
     ML Service         Optimization         Database
          |               Service              Layer
          |                   |                   |
          ▼                   ▼                   ▼
 XGBoost / LightGBM      PuLP / CBC          PostgreSQL
      / CatBoost            Solver
          |                   |
          └──────────┬────────┘
                     ▼
             Closed-Loop Workflow
                     |
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
     Decision     Execution      Outcome
                                     |
                                     ▼
                                    ROI
```

---

# Core Responsibilities

The backend currently handles:

- API health/readiness monitoring
- ML artifact loading
- Order validation
- Prediction eligibility filtering
- Late-risk inference
- Prediction persistence
- Order persistence
- Optimization execution
- Optimization-run persistence
- Recommendation persistence
- Recommendation retrieval
- Human decision capture
- Decision execution
- Actual outcome capture
- ROI calculation
- Predicted-vs-actual comparison

---

# Project Structure

The exact internal file layout may evolve, but the backend is organized around these responsibilities:

```text
backend/
│
├── app/
│   ├── api/
│   │   └── API routes / schemas
│   │
│   ├── db/
│   │   ├── database configuration
│   │   ├── initialization
│   │   └── persistence layer
│   │
│   ├── ml/
│   │   └── ML inference service
│   │
│   ├── optimization/
│   │   └── PuLP/CBC optimization logic
│   │
│   ├── models/
│   │   └── database models
│   │
│   ├── schemas/
│   │   └── request/response schemas
│   │
│   ├── services/
│   │   └── application/business services
│   │
│   └── main.py
│
├── models/
│   └── trained ML artifacts
│
├── tests/
│   ├── test_health.py
│   ├── test_predict.py
│   ├── test_order_prediction.py
│   ├── test_database_reads.py
│   ├── test_optimize_persistence.py
│   ├── test_optimization_reads.py
│   ├── test_decisions.py
│   ├── test_outcomes.py
│   └── test_roi.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# Environment Configuration

Create:

```text
backend/.env
```

using:

```text
backend/.env.example
```

The important database setting follows this format:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

Example development format:

```env
DATABASE_URL=postgresql+psycopg://supplyprescript_app:<PASSWORD>@localhost:5433/supplyprescript
```

Never commit the real `.env` file or database password.

The local development environment currently uses PostgreSQL with the SupplyPrescript application database.

---

# PostgreSQL Data Model

The integrated backend currently uses six primary tables.

## 1. `orders`

Stores persisted order requests.

Typical information includes:

- Order ID
- Order status
- Source system
- Received timestamp

The ML input is processed from the submitted order payload before prediction.

---

## 2. `ml_predictions`

Stores ML inference results associated with persisted orders.

Important information includes:

- Prediction ID
- Order ID
- Model version
- Late-risk probability
- Predicted late-risk classification
- Prediction eligibility
- Classification threshold
- Ensemble models used
- Request ID
- Creation timestamp

Example:

```text
Model version:
SupplyPrescript ML V2

Late-risk probability:
0.548798

Predicted late risk:
true

Threshold:
0.22
```

---

## 3. `optimization_runs`

Stores each persisted optimizer execution.

Information includes:

- Run ID
- Request ID
- Optimization status
- Total intervention cost
- Total expected saving
- Creation timestamp

Example status:

```text
Optimal
```

---

## 4. `optimization_recommendations`

Stores the action selected by the optimizer.

Important fields include:

- Recommendation ID
- Run ID
- Prediction ID
- Shipment ID
- Action ID
- Selected action
- Late-risk probability
- Risk after intervention
- Action cost
- Expected saving
- Predicted time
- Baseline expected loss
- Optimized expected cost

---

## 5. `recommendation_decisions`

Stores the human/operational decision attached to a recommendation.

Examples:

```text
ACCEPTED
REJECTED
```

It also tracks execution status such as:

```text
PENDING
EXECUTED
```

Additional information may include:

- Decision ID
- Recommendation ID
- Decided by
- Decision note
- Decision timestamp

---

## 6. `optimization_outcomes`

Stores actual operational results after an executed intervention.

Information includes:

- Outcome ID
- Decision ID
- Actual intervention cost
- Actual time
- Actual delayed status
- Actual delay cost
- Actual total cost
- Outcome note

These values are used for predicted-vs-actual comparison and ROI analysis.

---

# Database Initialization

The current project uses the backend initialization module to create missing tables.

From the backend directory:

```powershell
python -m app.db.init_db
```

The project currently does not depend on Alembic migrations for the development/demo schema.

Production deployment should introduce a formal migration workflow.

---

# Machine Learning Integration

SupplyPrescript ML V2 uses an ensemble of:

- XGBoost
- LightGBM
- CatBoost

The backend loads trained model artifacts from:

```text
backend/models/
```

---

## ML Service

The ML service exposes prediction logic similar to:

```python
MLService.predict(orders: List[OrderInput])
```

The service:

1. Receives validated Pydantic order inputs.
2. Converts the request into the required inference structure.
3. Applies eligibility logic.
4. Runs the ML ensemble.
5. Returns probability and classification results.
6. Allows eligible results to be persisted by the database-backed API workflow.

---

# ML Input

The V2 inference contract requires the trained feature schema used by the SupplyPrescript models.

The request contains supply-chain/order attributes such as:

- Transaction type
- Scheduled shipment days
- Benefit per order
- Sales/customer values
- Category
- Customer geography
- Customer segment
- Department
- Market
- Order geography
- Discounts
- Product information
- Profit values
- Quantity
- Order date-derived features

`Order Status` is also supported for eligibility filtering.

---

# Prediction Eligibility

Orders with statuses such as:

```text
CANCELED
SUSPECTED_FRAUD
```

are excluded from normal late-risk scoring.

For eligible orders, the model produces:

```text
Late_Risk_Probability
Predicted_Late_Risk
Prediction_Eligible
Exclusion_Reason
```

The classification threshold in the currently validated development model is approximately:

```text
0.22
```

---

# Prediction Interpretation

The ML model predicts:

> **Probability that the order will be delivered late**

It does not directly predict:

> **The exact number of days the order will be delayed**

Any time value shown for an intervention belongs to the optimization/action model rather than the ML late-risk classifier.

---

# Prescriptive Optimization

SupplyPrescript uses:

```text
PuLP + CBC
```

for mathematical optimization.

The optimizer evaluates available intervention actions under business constraints.

---

## Supported Actions

| Action ID | Action |
|---|---|
| A0 | NO_ACTION |
| A1 | EXPEDITE |
| A2 | PRIORITY_HANDLING |
| A3 | ALTERNATIVE_ROUTE |
| A4 | ALTERNATIVE_HUB |

Current development action configuration:

| Action | Cost | Risk Reduction | Time Reduction |
|---|---:|---:|---:|
| NO_ACTION | $0 | 0% | 0 days |
| EXPEDITE | $1,800 | 35% | 2.0 days |
| PRIORITY_HANDLING | $900 | 20% | 1.0 day |
| ALTERNATIVE_ROUTE | $1,400 | 28% | 1.5 days |
| ALTERNATIVE_HUB | $2,200 | 40% | 1.0 day |

---

## Optimization Inputs

The optimization workflow uses values such as:

- Shipment ID
- Late-risk probability
- Late-delivery penalty
- Baseline time
- Intervention availability
- Budget
- Action capacity
- Associated prediction ID

---

## Optimization Objective

The optimizer attempts to select feasible interventions while respecting constraints such as:

```text
Budget
Action capacity
Action availability
```

It compares modeled loss and intervention cost to determine an appropriate recommendation.

---

# Closed-Loop Decision Workflow

The backend implements:

```text
ML Prediction
      ↓
Optimization Run
      ↓
Recommendation
      ↓
Accept / Reject
      ↓
Execute
      ↓
Record Outcome
      ↓
Calculate ROI
```

---

# FastAPI Endpoints

## Health

### `GET /health`

Liveness endpoint.

Example:

```http
GET /health
```

Used to verify that the FastAPI process is running.

---

## Readiness

### `GET /ready`

Checks backend/model readiness.

The frontend also uses this endpoint to display:

```text
System Online
System Offline
Model readiness
ML threshold
```

---

# Prediction APIs

## `POST /api/v1/predict`

Runs ML inference without the complete database-backed order lifecycle.

Useful for direct inference/testing.

---

## `POST /api/v1/orders/predict`

Database-integrated order prediction workflow.

This endpoint:

```text
Receives Order
    ↓
Persists Order
    ↓
Runs ML Prediction
    ↓
Persists Eligible Prediction
    ↓
Returns Database IDs + Prediction
```

Excluded orders may be persisted without creating an `ml_predictions` row because the prediction table requires a valid probability/classification result.

---

# Order / Prediction Read APIs

## `GET /api/v1/orders/{order_id}`

Returns persisted order metadata.

---

## `GET /api/v1/predictions/{prediction_id}`

Returns a persisted ML prediction.

---

## `GET /api/v1/orders/{order_id}/predictions`

Returns prediction history associated with an order.

The frontend currently uses this endpoint to display the latest prediction for the configured development order.

---

# Optimization API

## `POST /api/v1/optimize`

Runs the real PuLP/CBC optimizer.

The workflow can persist:

```text
optimization_runs
optimization_recommendations
```

and associate recommendations with persisted ML predictions.

---

# Optimization Read APIs

## `GET /api/v1/optimization-runs/{run_id}`

Returns an optimization run.

---

## `GET /api/v1/recommendations/{recommendation_id}`

Returns a persisted recommendation.

---

## `GET /api/v1/optimization-runs/{run_id}/recommendations`

Returns:

- Optimization-run information
- Recommendations associated with that run

The React frontend uses this endpoint to display the optimizer-selected intervention.

---

# Recommendation Decision API

## `POST /api/v1/recommendations/{recommendation_id}/decision`

Records a recommendation decision.

Example accepted decision:

```json
{
  "decision_status": "ACCEPTED",
  "decided_by": "frontend-ui",
  "decision_note": "Accepted from SupplyPrescript dashboard"
}
```

The decision can also be rejected.

---

# Execution API

## `POST /api/v1/decisions/{decision_id}/execute`

Marks an accepted decision as executed.

Typical lifecycle:

```text
ACCEPTED
   ↓
EXECUTED
```

---

# Outcome API

## `POST /api/v1/decisions/{decision_id}/outcome`

Records the actual result of an executed intervention.

Example payload:

```json
{
  "actual_intervention_cost": 850.0,
  "actual_time_days": 3.8,
  "actual_delayed": false,
  "actual_delay_cost": 0.0,
  "outcome_note": "Outcome recorded for end-to-end validation"
}
```

The development outcome used during validation was simulated test/demo data.

---

# ROI API

## `GET /api/v1/decisions/{decision_id}/roi`

Returns predicted-vs-actual metrics for a completed decision.

The response can contain:

- Selected action
- Baseline expected loss
- Predicted action cost
- Optimized expected cost
- Predicted expected saving
- Predicted time
- Actual intervention cost
- Actual delay cost
- Actual total cost
- Actual time
- Actual delayed status
- Intervention cost variance
- Optimized cost variance
- Realized savings vs baseline
- Savings variance
- Time variance
- Realized ROI percentage

---

# ROI Interpretation

The backend uses:

```text
baseline_expected_loss
```

as a modeled expected/counterfactual loss.

It is not an observed transaction representing what definitely would have occurred without intervention.

Therefore:

```text
realized_roi_percent
```

should be interpreted as:

> **Model-relative realized ROI**

rather than audited accounting ROI.

---

# Current Persisted Development Example

The development database contains a validated closed-loop chain:

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

Example prediction:

```text
Order Status:
COMPLETE

Late-risk probability:
54.8798%

Threshold:
22%

Predicted late risk:
true
```

Example optimization result:

```text
Action:
PRIORITY_HANDLING

Action ID:
A2

Action cost:
$900.00

Risk before:
54.8798%

Risk after:
43.9038%

Expected saving:
$197.60

Predicted time:
4 days
```

The associated outcome was created for end-to-end development validation and is not real production evidence.

---

# Setup

## Prerequisites

Recommended:

```text
Python 3.11
PostgreSQL
pip
```

The project has been validated using Python 3.11.

---

## 1. Open the Backend

From the repository:

```powershell
cd D:\SupplyPrescript-AI-team\SupplyPrescript-AI\backend
```

---

## 2. Create Virtual Environment

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

## 4. Configure PostgreSQL

Create the SupplyPrescript PostgreSQL database and application role appropriate for your environment.

Then configure:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql+psycopg://supplyprescript_app:<PASSWORD>@localhost:5433/supplyprescript
```

Use the values appropriate for your own PostgreSQL installation.

---

## 5. Initialize Database

```powershell
python -m app.db.init_db
```

This creates missing tables required by the application.

---

## 6. Start FastAPI

```powershell
uvicorn app.main:app --reload
```

Default API:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Frontend CORS

The development backend permits the React/Vite frontend origins used locally, including:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Production deployments should use explicit production origins rather than broad CORS rules.

---

# Testing

Run the complete backend test suite from:

```text
backend/
```

using:

```powershell
pytest -q
```

Latest validated result:

```text
46 passed, 34 warnings
```

The warnings are currently non-blocking dependency/deprecation warnings related primarily to testing/client libraries and PuLP behavior.

---

# Test Coverage Areas

The backend test suite currently covers major areas including:

| Test Area | Purpose |
|---|---|
| Health / Readiness | API process and ML readiness |
| Prediction | ML inference and validation |
| Order Prediction | Database-backed prediction workflow |
| Database Reads | Order/prediction retrieval |
| Optimization Persistence | Persisted PuLP results |
| Optimization Reads | Run/recommendation retrieval |
| Decisions | Accept/reject workflow |
| Outcomes | Actual outcome persistence |
| ROI | Predicted-vs-actual ROI calculation |

Current test files include:

```text
test_health.py
test_predict.py
test_order_prediction.py
test_database_reads.py
test_optimize_persistence.py
test_optimization_reads.py
test_decisions.py
test_outcomes.py
test_roi.py
```

---

# Current Backend Status

| Component | Status |
|---|---|
| FastAPI Application | ✅ Complete |
| Health Endpoint | ✅ Complete |
| Readiness Endpoint | ✅ Complete |
| ML V2 Integration | ✅ Complete |
| XGBoost | ✅ Integrated |
| LightGBM | ✅ Integrated |
| CatBoost | ✅ Integrated |
| Prediction API | ✅ Complete |
| Order Persistence | ✅ Complete |
| Prediction Persistence | ✅ Complete |
| PostgreSQL Integration | ✅ Complete |
| Database Read APIs | ✅ Complete |
| PuLP/CBC Optimizer | ✅ Complete |
| Optimization Persistence | ✅ Complete |
| Recommendation Read APIs | ✅ Complete |
| Recommendation Accept/Reject | ✅ Complete |
| Decision Execution | ✅ Complete |
| Outcome Capture | ✅ Complete |
| ROI Calculation | ✅ Complete |
| Backend Automated Tests | ✅ 46 Passing |
| Authentication | ❌ Not implemented |
| Authorization / RBAC | ❌ Not implemented |
| General Decision History Endpoint | ⚠️ Future enhancement |
| Alembic Migration Workflow | ❌ Not implemented |
| Production Monitoring | ❌ Not implemented |
| CI/CD | ❌ Not configured |

---

# Current Read-API Limitation

The backend currently exposes the individual decision lifecycle operations required for the project but does not provide a general endpoint such as:

```http
GET /api/v1/decisions
```

It also does not currently expose a generic recommendation-to-decision read endpoint.

Because of this, the React frontend keeps returned workflow references in browser `localStorage` for UI continuity.

This does not replace backend persistence.

The actual database records remain stored in PostgreSQL.

---

# Error Handling

The backend provides validation/error handling across the main workflow.

Examples include:

- Invalid request payloads
- Missing ML fields
- Prediction eligibility
- ML inference failures
- Missing database records
- Invalid recommendation transitions
- Duplicate/invalid decisions
- Optimizer errors
- Outcome lifecycle validation
- ROI availability validation

FastAPI/Pydantic validation is also used to reject malformed API requests.

---

# Security

The current system is intended for development, academic demonstration, and project evaluation.

Do not commit:

```text
.env
.venv/
__pycache__/
.pytest_cache/
```

Never commit:

- PostgreSQL passwords
- API secrets
- Credentials
- Production tokens
- Private environment configuration

Use:

```text
.env.example
```

to document required configuration without exposing secrets.

---

# Known Limitations

The current implementation is functionally complete for the project/demo scope but is not a production-hardened platform.

Not yet implemented:

- Authentication
- Role-based authorization
- Production secret management
- General decision-history endpoint
- Full user/audit identity management
- Alembic migration workflow
- Production-grade structured logging
- Metrics/tracing
- Container orchestration
- CI/CD pipeline
- Production deployment automation
- Model drift monitoring
- Scheduled model evaluation
- External ERP/WMS/OMS integration

---

# Future Improvements

Potential backend improvements include:

1. Add JWT/OAuth authentication
2. Add role-based access control
3. Add decision-history/list APIs
4. Add recommendation-to-decision read APIs
5. Add outcome read/list APIs
6. Add pagination/filtering
7. Introduce Alembic migrations
8. Add structured logging
9. Add Prometheus/OpenTelemetry monitoring
10. Add GitHub Actions CI/CD
11. Add Docker/Docker Compose
12. Add production PostgreSQL configuration
13. Add multi-order optimization workflows
14. Add model-performance monitoring
15. Add model-drift detection
16. Add ERP/WMS/OMS connectors
17. Add asynchronous job processing where needed

---

# Related Documentation

Main project documentation:

```text
../README.md
```

Frontend documentation:

```text
../frontend/README.md
```

Frontend API service:

```text
../frontend/src/services/api.js
```

---

# Final Validation

The integrated backend has been validated through:

```text
FastAPI:
Operational

ML Ensemble:
XGBoost + LightGBM + CatBoost working

PostgreSQL:
Persistence verified

Optimizer:
PuLP/CBC optimal solution verified

Closed Loop:
Prediction
→ Optimization
→ Recommendation
→ Decision
→ Execution
→ Outcome
→ ROI

Tests:
46 passed

Frontend Integration:
Verified

Git:
Working tree clean
```

---

# Summary

SupplyPrescript Backend implements an end-to-end transition from predictive analytics into prescriptive and closed-loop decision support.

```text
Supply Chain Order
       ↓
Feature Validation
       ↓
ML Risk Prediction
       ↓
PostgreSQL Persistence
       ↓
PuLP/CBC Optimization
       ↓
Recommended Intervention
       ↓
Human Decision
       ↓
Execution
       ↓
Actual Outcome
       ↓
ROI Evaluation
```

The backend core is functionally complete for the current academic/demo scope.

Remaining work is primarily production hardening, authentication, migrations, expanded read APIs, observability, CI/CD, and deployment.