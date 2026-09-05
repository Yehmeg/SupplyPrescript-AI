# SupplyPrescript Backend

> **Integrated build note (29 Aug 2026):** The backend now contains the V2 inference runtime locally under `app/ml/` and the tested PuLP optimization layer under `app/optimization/`. Copy the eight trained `.pkl` artifacts into `backend/models/` before starting the API.

FastAPI backend for the **SupplyPrescript** closed-loop prescriptive analytics system. Serves ML predictions (late-delivery risk scoring) and will serve prescriptive optimization recommendations, decision write-back, and outcome capture.

---

## Purpose

- **Prediction API** — Score late-delivery risk for incoming orders using the V2 ensemble (XGBoost + LightGBM + CatBoost)
- **Readiness/Health** — Kubernetes-style liveness and readiness probes
- **Future: Optimization API** — Generate prescriptive recommendations from risk probabilities + business constraints
- **Future: Decision/Write-Back API** — Record human approvals, push to ERP/WMS/OMS, capture outcomes for retraining

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI 0.110+ (async, lifespan, dependency injection) |
| Server | Uvicorn 0.29+ (ASGI, workers) |
| Validation | Pydantic 2.6+ (schemas, aliases, config) |
| Settings | Pydantic-Settings 2.2+ (env-file, case-sensitive) |
| ML Inference | `supplyprescript` package (local editable install) — XGBoost, LightGBM, CatBoost, scikit-learn, pandas, joblib |
| Testing | pytest 8+, pytest-asyncio, httpx (AsyncClient) |
| Lint/Type | ruff, mypy (configured in pyproject.toml) |

---

## Folder Structure

```
backend/
├── pyproject.toml             # Project metadata, dependencies, pytest config
├── requirements.txt           # Pip-compatible dependencies
├── README.md                  # This file
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app factory, lifespan, endpoints
│   ├── config.py              # Settings (CORS, model dir, env)
│   ├── api/
│   │   ├── __init__.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── prediction.py  # Pydantic models: OrderInput, PredictRequest, PredictionResponseItem, PredictResponse
│   └── ml/
│       ├── __init__.py
│       └── service.py         # MLService: loads artifacts, calls supplyprescript.inference.predict_supplyprescript
└── tests/
    ├── __init__.py
    ├── conftest.py            # Fixtures: app, async_client, sample_order (32-feature V2 schema)
    ├── test_health.py         # /health (200), /ready (200/503)
    └── test_predict.py        # 7 predict tests: single/multi, validation, CANCELED exclusion, request_id echo
```

---

## Setup

### Prerequisites
- **Python ≥ 3.10** (tested on 3.14)
- **pip ≥ 23**
- **ML artifacts** — `SupplyPrescript_V2/supplyprescript/artifacts/` (9 `.pkl` files) must exist

### Install Dependencies

```bash
cd D:\Axlero\backend

# Option 1: pip (requirements.txt)
pip install -r requirements.txt

# Option 2: pip with editable ML package (recommended for development)
pip install -r requirements.txt
pip install -e ../SupplyPrescript_V2
```

> **Note:** `requirements.txt` lists `supplyprescript` as a commented local install (line 9). Uncomment and run `pip install -e ../SupplyPrescript_V2` to use the local ML package. Otherwise the ML dependencies (xgboost, lightgbm, catboost, etc.) are installed directly.

### Environment Variables (Optional)

Create `.env` in `backend/` if needed:
```ini
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
API_PREFIX=/api/v1
SUPPLYPRESCRIPT_MODEL_DIR=../SupplyPrescript_V2/supplyprescript/artifacts
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Defaults are defined in `app/config.py:Settings` and work without `.env`.

---

## Running the Server

```bash
cd D:\Axlero\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload` enables auto-reload on code changes (dev only)
- Server starts at `http://localhost:8000`
- Lifespan loads ML artifacts on startup (prints warning if load fails)

### Verify Running Server

```bash
# Health check (liveness)
curl http://localhost:8000/health
# → {"status":"ok"}

# Readiness check (models loaded)
curl http://localhost:8000/ready
# → {"status":"ready","models_loaded":["XGBoost","LightGBM","CatBoost"]}

# Interactive API docs
open http://localhost:8000/docs
# or http://localhost:8000/redoc
```

---

## API Endpoints

### `GET /health` — Liveness Probe
**Always returns 200** if process is running. No dependencies checked.

```json
Response 200:
{
  "status": "ok"
}
```

### `GET /ready` — Readiness Probe
Returns **200** if ML artifacts loaded successfully; **503** otherwise.

```json
Response 200:
{
  "status": "ready",
  "models_loaded": ["XGBoost", "LightGBM", "CatBoost"]
}

Response 503:
{
  "detail": "ML artifacts not loaded"
}
```

### `POST /api/v1/predict` — Late-Delivery Risk Scoring
Scores one or more orders using the V2 ensemble.

**Request:**
```json
{
  "request_id": "optional-correlation-id",
  "orders": [
    {
      "Type": "DEBIT",
      "Days for shipment (scheduled)": 4,
      "Benefit per order": 91.25,
      "Sales per customer": 314.64,
      "Category Name": "Sporting Goods",
      "Customer City": "Caguas",
      "Customer Country": "Puerto Rico",
      "Customer Segment": "Consumer",
      "Customer State": "PR",
      "Department Name": "Fitness",
      "Latitude": 18.2514534,
      "Longitude": -66.03705597,
      "Market": "Pacific Asia",
      "Order City": "Bekasi",
      "Order Country": "Indonesia",
      "Order Item Discount": 13.11,
      "Order Item Discount Rate": 0.04,
      "Order Item Product Price": 327.75,
      "Order Item Profit Ratio": 0.29,
      "Order Item Quantity": 1,
      "Sales": 327.75,
      "Order Item Total": 314.64,
      "Order Profit Per Order": 91.25,
      "Order Region": "Southeast Asia",
      "Order State": "Java Occidental",
      "Product Category Id": 73,
      "Product Name": "Smart watch",
      "Product Price": 327.75,
      "Order_Year": 2018,
      "Order_Month": 1,
      "Order_DayOfWeek": 2,
      "Order_Day": 31,
      "Order Status": "COMPLETE"
    }
  ]
}
```

- All **32 features required** (exact V2 schema, see `app/api/schemas/prediction.py:OrderInput`)
- `Order Status` optional — if `CANCELED` or `SUSPECTED_FRAUD` (case-insensitive), row is excluded from scoring
- Field aliases match DataCo column names (spaces, parentheses)

**Response 200:**
```json
{
  "request_id": "optional-correlation-id",
  "predictions": [
    {
      "Late_Risk_Probability": 0.287567,
      "Predicted_Late_Risk": 1,
      "Prediction_Eligible": true,
      "Exclusion_Reason": null
    }
  ],
  "model_version": "SupplyPrescript ML V2",
  "threshold_used": 0.18
}
```

**Error Responses:**
| Status | Condition |
|--------|-----------|
| 400 | `orders` array empty |
| 422 | Missing required field(s) or invalid type |
| 500 | ML inference failure (artifacts missing, preprocessing error) |
| 422 (ValueError) | Preprocessing validation error (e.g., missing features) |

---

## ML V2 Integration

### Model Artifacts (Loaded at Startup)
Located at `../SupplyPrescript_V2/supplyprescript/artifacts/` (configurable via `SUPPLYPRESCRIPT_MODEL_DIR`):

| File | Purpose |
|------|---------|
| `final_xgboost.pkl` | XGBoost classifier (may be corrupted — graceful degradation) |
| `final_lightgbm.pkl` | LightGBM classifier |
| `final_catboost.pkl` | CatBoost classifier |
| `final_features.pkl` | List of 32 feature names (exact training order) |
| `final_categorical_features.pkl` | List of 13 categorical feature names |
| `final_category_levels.pkl` | Dict: categorical feature → allowed categories (includes `__UNKNOWN__`) |
| `final_threshold.pkl` | Classification threshold (float, expected 0.18) |
| `final_ensemble_config.pkl` | Dict: models, method, weights, dropped columns |
| `baseline_preprocessor.pkl` | Legacy preprocessor (not used by V2 ensemble; sklearn version mismatch warning) |

### Inference Pipeline (`supplyprescript.inference.predict_supplyprescript`)
1. **Eligibility filter** — Drop rows with `Order Status` ∈ {CANCELED, SUSPECTED_FRAUD}
2. **Preprocessing** — Drop `Shipping Mode`, `Order Status`; validate 32 features present; reorder to training order; encode categoricals as `pd.Categorical` with saved levels (unseen → `__UNKNOWN__`)
3. **Ensemble prediction** — Average `predict_proba` from available models (equal weight)
4. **Threshold** — Apply saved threshold (0.18) → binary `Predicted_Late_Risk`
5. **Output** — DataFrame with `Late_Risk_Probability`, `Predicted_Late_Risk`, `Prediction_Eligible`, `Exclusion_Reason`

### Backend Integration (`app/ml/service.py:MLService`)
- Singleton `MLService` loads artifacts once via `get_artifacts(model_dir)`
- `predict(orders: List[OrderInput])` → converts to DataFrame, calls `predict_supplyprescript`, maps result to `PredictionResponseItem` list
- `is_ready()` → checks artifacts loaded and ≥1 model available

---

## Testing

```bash
cd D:\Axlero\backend
python -m pytest tests/ -v
```

### Test Suite (9 tests, all passing)
| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_health.py` | 2 | `/health` (200), `/ready` (200 or 503) |
| `test_predict.py` | 7 | Single/multi predict, empty orders (400), missing field (422), CANCELED exclusion, case-insensitive status, request_id echo |

### Test Fixtures (`conftest.py`)
- `app` — `create_app()` session-scoped
- `async_client` — `AsyncClient(ASGITransport(app), base_url="http://test")`
- `sample_order` — Valid 32-feature order dict (matches V2 schema exactly)

---

## Current Backend Status

| Component | Status |
|-----------|--------|
| **FastAPI App** | ✅ Complete — lifespan, CORS, error handlers |
| **Health Endpoints** | ✅ Complete — `/health`, `/ready` |
| **Predict Endpoint** | ✅ Complete — validation, ML integration, 32-feature schema |
| **ML Service** | ✅ Complete — artifact loading, ensemble inference, eligibility |
| **Pydantic Schemas** | ✅ Complete — request/response with aliases |
| **Configuration** | ✅ Complete — env-file, CORS, model dir |
| **Unit Tests** | ✅ Complete — 9/9 passing |
| **Lint/Type Config** | ✅ Complete — ruff, mypy in pyproject.toml |
| **Database Layer** | ❌ **Pending** — no SQLAlchemy, no models, no migrations |
| **Optimization Layer** | ❌ **Pending** — no SciPy solver, no recommendation generation |
| **Decision/Write-Back API** | ❌ **Pending** — no approve/override/writeback endpoints |
| **Outcome Capture** | ❌ **Pending** — no outcome ingestion endpoint |
| **Authentication** | ❌ Not implemented (AUTH_ENABLED=False in config) |
| **Observability** | ❌ No structured logging, metrics, tracing |

---

## Database Integration (Pending)

### Required for Phase 2+
Per `../README.md` (Sections 5.1, 10, 12) and `../SupplyPrescript_README.md`, the database must store:

| Entity | Purpose |
|--------|---------|
| `orders` | Raw input orders (32 features + metadata) |
| `ml_predictions` | Model outputs (probability, binary risk, eligibility, threshold, model version) |
| `optimization_runs` | Solver cycles (config snapshot, solver status, timestamps) |
| `recommendations` | Prescriptive options per order (action, cost, net benefit, constraints, rationale) |
| `decisions` | Human approvals/rejections/overrides (actor, reason, timestamp) |
| `write_backs` | ERP/WMS/OMS API calls (idempotency key, retry state, response) |
| `outcomes` | Realized actuals (late Y/N, actual cost, intervention executed) for retraining |

### Backend → DB Interface (To Be Implemented)
```python
# In predict endpoint (after ML inference)
await db.create_order(order_data)
await db.create_ml_prediction(prediction_data)

# In future optimize endpoint
run_id = await db.create_optimization_run(config_snapshot)
for rec in recommendations:
    await db.create_recommendation(run_id, rec)

# In future approve/override endpoint
await db.create_decision(recommendation_id, decision, reason, actor_id)

# In future write-back endpoint
await db.create_writeback(recommendation_id, system, payload, idem_key)
await db.update_writeback_status(writeback_id, status, response)

# In future outcome endpoint
await db.create_outcome(order_id, actual_late, actual_cost, ...)
```

### DB → Backend Interface (To Be Implemented)
```python
# For Retool/React queues
await db.get_pending_recommendations(cycle_id)
await db.get_recommendation_detail(recommendation_id)

# For retraining pipeline (Airflow)
await db.get_training_data(lookback_days=90)

# For monitoring
await db.get_model_performance(model_version, date_range)
```

---

## Optimization Integration (Pending)

### Required Endpoints (Phase 2)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/optimize` | POST | Input: shipment risk + constraints → Output: ranked recommendations |
| `/api/v1/recommendations` | GET | List pending recommendations for review queue |
| `/api/v1/recommendations/{id}` | GET | Full detail (order, ML prediction, optimization inputs/outputs) |
| `/api/v1/recommendations/{id}/approve` | POST | Record approval, trigger write-back |
| `/api/v1/recommendations/{id}/override` | POST | Record override (requires `reason`), trigger write-back |
| `/api/v1/writeback/{system}` | POST | Internal: push to ERP/WMS/OMS (idempotent, retry with backoff) |
| `/api/v1/constraints` | GET/PUT | Business rules (budget, inventory, SLA) |
| `/api/v1/roi` | GET | Predicted vs actual cost, outcome rates |
| `/api/v1/outcomes` | POST | Ingest realized outcomes from source systems |

### Optimization Inputs (Per Requirements)
- `Risk Probability` (from ML)
- `Intervention Cost` (per action type)
- `Late-Delivery Penalty` (per order/SKU/customer)
- `Available Capacity` (intervention slots per cycle)
- `SLA Constraints` (service level target, e.g., 0.95)

---

## Frontend Integration (Pending)

### Current Frontend (`../frontend/`)
- React + Vite app running on `http://localhost:5173`
- **Fully mock-driven** — no live API calls
- CORS configured in `backend/app/config.py` for `localhost:5173`

### Integration Plan
1. **Replace mock data** with API service layer in frontend
2. **Connect Dashboard** → `GET /api/v1/shipments/{id}/risk` + `POST /api/v1/optimize`
3. **Connect Decisions** → `GET /api/v1/decisions`, `POST /api/v1/decisions`
4. **Connect Analytics** → `GET /api/v1/roi`
5. **Connect Settings** → `GET/PUT /api/v1/constraints`
6. **Add auth context** for `actor_id` on decisions
7. **Add WebSocket/SSE** for real-time recommendation updates (optional)

---

## Development Commands

```bash
# Run server with reload
uvicorn app.main:app --reload --port 8000

# Run tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Lint (ruff)
ruff check app/ tests/

# Type check (mypy)
mypy app/

# Format (ruff)
ruff format app/ tests/
```

---

## Related Repositories

- **Frontend** — `../frontend/` (React + Vite, analyst/executive dashboard)
- **ML Package** — `../SupplyPrescript_V2/supplyprescript/` (inference, preprocessing, artifacts)
- **Documentation** — `../README.md`, `../SupplyPrescript_README.md`, `../README_ML_BRANCH.md`
- **Team Execution Plan** — `../IceStream_SupplyPrescript_Team_Execution_Plan.docx`

---

## License

Proprietary — internal use only. See `../README.md` Section 17.
---

## Optimization API — Integrated

The tested PuLP optimization module is now exposed through:

`POST /api/v1/optimize`

The endpoint accepts already-scored shipment risk plus business constraints. This keeps the existing `/api/v1/predict` ML endpoint unchanged and cleanly separates prediction from prescriptive optimization.

Example request:

```json
{
  "request_id": "cycle-001",
  "shipments": [
    {
      "shipment_id": "S001",
      "late_probability": 0.407488,
      "late_penalty": 15000,
      "expedite_available": true,
      "priority_available": true,
      "route_available": true,
      "hub_available": false
    }
  ],
  "constraints": {
    "total_budget": 10000,
    "expedite_capacity": 1,
    "priority_capacity": 1,
    "route_capacity": 1,
    "hub_capacity": 1
  }
}
```

The response contains solver status, total intervention cost, total expected saving, and one selected action per eligible shipment.
