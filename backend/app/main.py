from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.config import get_settings

from app.ml.service import (
    get_ml_service,
    MLService,
)

from app.optimization.service import (
    get_optimization_service,
    OptimizationService,
)

from app.api.schemas.prediction import (
    PredictRequest,
    PredictResponse,
    PersistedPredictRequest,
    PersistedPredictResponse,
    PersistedPredictionItem,
)

from app.api.schemas.optimization import (
    OptimizeRequest,
    OptimizeResponse,
)

from app.db.database import get_db
from app.db import crud

from app.api.schemas.database import (
    OrderDBResponse,
    PredictionDBResponse,
    OrderWithPredictionsResponse,
)
# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Preload ML artifacts when FastAPI starts.
    """

    ml_service = get_ml_service()

    try:
        _ = ml_service.artifacts
        print("ML artifacts loaded successfully.")

    except Exception as e:
        print(
            "Warning: Failed to load ML artifacts "
            f"on startup: {e}"
        )

    yield


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

def create_app() -> FastAPI:

    settings = get_settings()

    app = FastAPI(
        title="SupplyPrescript API",
        version="1.0.0",
        description=(
            "API for late-delivery risk scoring "
            "and prescriptive supply-chain recommendations"
        ),
        lifespan=lifespan,
    )

    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ========================================================
    # HEALTH
    # ========================================================

    @app.get(
        "/health",
        tags=["health"],
    )
    async def health():
        """
        Liveness probe.
        """

        return {
            "status": "ok",
        }

    # ========================================================
    # READY
    # ========================================================

    @app.get(
        "/ready",
        tags=["health"],
    )
    async def ready(
        ml_service: MLService = Depends(
            get_ml_service
        ),
    ):
        """
        Readiness probe.

        Checks whether the trained ML artifacts
        are available.
        """

        if ml_service.is_ready():

            return {
                "status": "ready",
                "models_loaded": (
                    ml_service.available_models()
                ),
                "threshold": ml_service.threshold,
            }

        raise HTTPException(
            status_code=503,
            detail="ML artifacts not loaded",
        )

    # ========================================================
    # STANDARD ML PREDICTION
    #
    # Does NOT write anything to PostgreSQL.
    # ========================================================

    @app.post(
        f"{settings.API_PREFIX}/predict",
        response_model=PredictResponse,
        tags=["predictions"],
    )
    async def predict(
        request: PredictRequest,
        ml_service: MLService = Depends(
            get_ml_service
        ),
    ):
        """
        Run late-delivery prediction.

        This endpoint only performs ML inference.

        It does NOT persist the order or prediction
        to PostgreSQL.
        """

        if not request.orders:

            raise HTTPException(
                status_code=400,
                detail="At least one order is required",
            )

        try:

            predictions = ml_service.predict(
                request.orders
            )

        except ValueError as e:

            raise HTTPException(
                status_code=422,
                detail=str(e),
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Prediction failed: "
                    f"{str(e)}"
                ),
            )

        return PredictResponse(
            request_id=request.request_id,
            predictions=predictions,
            threshold_used=ml_service.threshold,
            prediction_ids=None,
        )

    # ========================================================
    # ORDER + ML PREDICTION + DATABASE PERSISTENCE
    #
    # Flow:
    #
    # API request
    #     ↓
    # orders table
    #     ↓
    # ML inference
    #     ↓
    # ml_predictions table
    #     ↓
    # API response
    # ========================================================

    @app.post(
        f"{settings.API_PREFIX}/orders/predict",
        response_model=PersistedPredictResponse,
        tags=["predictions"],
    )
    def predict_and_persist_order(
        payload: PersistedPredictRequest,
        ml_service: MLService = Depends(
            get_ml_service
        ),
        db: Session = Depends(
            get_db
        ),
    ):
        """
        Store incoming orders, run ML inference,
        and store eligible predictions.

        Current database tables:

        orders
            ↓
        ml_predictions
        """

        if not payload.orders:

            raise HTTPException(
                status_code=400,
                detail="At least one order is required.",
            )

        try:

            # ------------------------------------------------
            # 1. RUN EXISTING TRAINED ML PIPELINE
            # ------------------------------------------------

            predictions = ml_service.predict(
                payload.orders
            )

            persisted_results = []

            # ------------------------------------------------
            # 2. PROCESS EACH ORDER + PREDICTION
            # ------------------------------------------------

            for order_input, prediction in zip(
                payload.orders,
                predictions,
            ):

                # Keep original dataset/API field names.
                order_payload = (
                    order_input.model_dump(
                        by_alias=True
                    )
                )

                # --------------------------------------------
                # 3. STORE ORDER
                # --------------------------------------------

                db_order = crud.insert_order(
                    db,
                    payload=order_payload,
                    source_system="api",
                )

                prediction_id = None

                probability = (
                    prediction.Late_Risk_Probability
                )

                predicted_class = (
                    prediction.Predicted_Late_Risk
                )

                eligible = (
                    prediction.Prediction_Eligible
                )

                exclusion_reason = (
                    prediction.Exclusion_Reason
                )

                # --------------------------------------------
                # 4. STORE ELIGIBLE ML PREDICTION
                # --------------------------------------------
                #
                # Current SQL schema requires:
                #
                # late_risk_probability NOT NULL
                # predicted_late_risk   NOT NULL
                #
                # Therefore excluded/non-predictable rows
                # are kept in orders but are not inserted
                # into ml_predictions.
                # --------------------------------------------

                if (
                    eligible
                    and probability is not None
                    and predicted_class is not None
                ):

                    db_prediction = (
                        crud.insert_ml_prediction(
                            db,
                            order_id=(
                                db_order.order_id
                            ),
                            model_version=(
                                "SupplyPrescript ML V2"
                            ),
                            late_risk_probability=(
                                float(probability)
                            ),
                            predicted_late_risk=(
                                bool(predicted_class)
                            ),
                            prediction_eligible=(
                                bool(eligible)
                            ),
                            exclusion_reason=(
                                exclusion_reason
                            ),
                            threshold_used=(
                                float(
                                    ml_service.threshold
                                )
                            ),
                            ensemble_models_used=[
                                "XGBoost",
                                "LightGBM",
                                "CatBoost",
                            ],
                            request_id=(
                                payload.request_id
                            ),
                        )
                    )

                    prediction_id = (
                        db_prediction.prediction_id
                    )

                # --------------------------------------------
                # 5. BUILD API RESPONSE ITEM
                # --------------------------------------------

                persisted_results.append(
                    PersistedPredictionItem(
                        order_id=(
                            db_order.order_id
                        ),
                        prediction_id=(
                            prediction_id
                        ),
                        Late_Risk_Probability=(
                            probability
                        ),
                        Predicted_Late_Risk=(
                            predicted_class
                        ),
                        Prediction_Eligible=(
                            eligible
                        ),
                        Exclusion_Reason=(
                            exclusion_reason
                        ),
                    )
                )

            # ------------------------------------------------
            # 6. RETURN COMPLETE RESULT
            # ------------------------------------------------

            return PersistedPredictResponse(
                request_id=(
                    payload.request_id
                ),
                predictions=(
                    persisted_results
                ),
                model_version=(
                    "SupplyPrescript ML V2"
                ),
                threshold_used=(
                    float(
                        ml_service.threshold
                    )
                ),
            )

        except ValueError as e:

            raise HTTPException(
                status_code=422,
                detail=str(e),
            )

        except HTTPException:

            raise

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Order prediction failed: "
                    f"{str(e)}"
                ),
            )
    @app.get(
    f"{settings.API_PREFIX}/orders/{{order_id}}",
    response_model=OrderDBResponse,
    tags=["database"],
    )
    def get_order_by_id(
        order_id: int,
        db: Session = Depends(get_db),
    ):
        order = crud.get_order(
            db,
            order_id,
        )

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        return order


    @app.get(
        f"{settings.API_PREFIX}/predictions/{{prediction_id}}",
        response_model=PredictionDBResponse,
        tags=["database"],
    )
    def get_prediction_by_id(
        prediction_id: int,
        db: Session = Depends(get_db),
    ):
        prediction = crud.get_prediction(
            db,
            prediction_id,
        )

        if prediction is None:
            raise HTTPException(
                status_code=404,
                detail="Prediction not found",
            )

        return prediction


    @app.get(
        f"{settings.API_PREFIX}/orders/{{order_id}}/predictions",
        response_model=OrderWithPredictionsResponse,
        tags=["database"],
    )
    def get_order_predictions(
        order_id: int,
        db: Session = Depends(get_db),
    ):
        order = crud.get_order(
            db,
            order_id,
        )

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        predictions = crud.get_predictions_for_order(
            db,
            order_id,
        )

        return {
            "order": order,
            "predictions": predictions,
        }
    # ========================================================
    # OPTIMIZATION
    #
    # Optimization still works, but it is NOT persisted yet
    # because the new supplied DB schema currently contains
    # only orders + ml_predictions.
    # ========================================================

    @app.post(
        f"{settings.API_PREFIX}/optimize",
        response_model=OptimizeResponse,
        tags=["optimization"],
    )
    async def optimize(
        request: OptimizeRequest,
        optimization_service: OptimizationService = Depends(
            get_optimization_service
        ),
    ):
        """
        Run SupplyPrescript intervention optimization.

        Current version returns optimizer recommendations
        without writing them to PostgreSQL.
        """

        if not request.shipments:

            raise HTTPException(
                status_code=400,
                detail=(
                    "At least one shipment "
                    "is required"
                ),
            )

        try:

            (
                status,
                recommendations,
                total_cost,
                total_saving,
            ) = optimization_service.optimize(
                request.shipments,
                request.constraints,
            )

        except ValueError as e:

            raise HTTPException(
                status_code=422,
                detail=str(e),
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Optimization failed: "
                    f"{str(e)}"
                ),
            )

        return OptimizeResponse(
            request_id=request.request_id,
            optimization_status=status,
            total_intervention_cost=(
                total_cost
            ),
            total_expected_saving=(
                total_saving
            ),
            recommendations=(
                recommendations
            ),
            recommendation_ids=None,
        )

    # ========================================================
    # GLOBAL VALUE ERROR HANDLER
    # ========================================================

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request,
        exc,
    ):

        return JSONResponse(
            status_code=422,
            content={
                "detail": str(exc),
            },
        )

    return app


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()