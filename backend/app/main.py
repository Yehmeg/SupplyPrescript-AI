from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.ml.service import get_ml_service, MLService
from app.api.schemas.prediction import PredictRequest, PredictResponse
from app.api.schemas.optimization import OptimizeRequest, OptimizeResponse
from app.optimization.service import get_optimization_service, OptimizationService

from app.api.routes.writeback import router as writeback_router

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pre-load ML artifacts
    ml_service = get_ml_service()
    try:
        _ = ml_service.artifacts
    except Exception as e:
        print(f"Warning: Failed to load ML artifacts on startup: {e}")
    yield
    # Shutdown: nothing to clean up for now


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="SupplyPrescript API",
        version="1.0.0",
        description="API for late-delivery risk scoring and prescriptive recommendations",
        lifespan=lifespan,
    )

    # CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Database / write-back routes
    app.include_router(writeback_router)

    @app.get("/health", tags=["health"])
    async def health():
        """Liveness probe - always returns 200 if process is running."""
        return {"status": "ok"}

    @app.get("/ready", tags=["health"])
    async def ready(ml_service: MLService = Depends(get_ml_service)):
        """Readiness probe - checks ML artifacts are loaded."""
        if ml_service.is_ready():
            return {"status": "ready", "models_loaded": ml_service.available_models()}
        raise HTTPException(status_code=503, detail="ML artifacts not loaded")

    @app.post(
        f"{settings.API_PREFIX}/predict",
        response_model=PredictResponse,
        tags=["predictions"],
    )
    async def predict(
        request: PredictRequest,
        ml_service: MLService = Depends(get_ml_service),
        db: Session = Depends(get_db),
    ):
        """
        Score late-delivery risk.

        If shipment_ids are supplied, eligible predictions are also
        persisted to the predictions table.
        """

        if not request.orders:
            raise HTTPException(
                status_code=400,
                detail="At least one order is required",
            )

        if (
            request.shipment_ids is not None
            and len(request.shipment_ids) != len(request.orders)
        ):
            raise HTTPException(
                status_code=400,
                detail="shipment_ids must match the number of orders",
            )

        try:
            predictions = ml_service.predict(request.orders)

            prediction_ids = None

            # --------------------------------------------------
            # Optional database persistence
            # --------------------------------------------------
            if request.shipment_ids is not None:
                prediction_ids = []

                for shipment_id, prediction in zip(
                    request.shipment_ids,
                    predictions,
                ):

                    # Current DB schema requires probability and class.
                    # Excluded orders cannot be stored without inventing
                    # values, so keep their DB id as None.
                    if (
                        not prediction.Prediction_Eligible
                        or prediction.Late_Risk_Probability is None
                        or prediction.Predicted_Late_Risk is None
                    ):
                        prediction_ids.append(None)
                        continue

                    predicted_class = (
                        "delayed"
                        if prediction.Predicted_Late_Risk == 1
                        else "on_time"
                    )

                    db_prediction = crud.insert_prediction(
                        db,
                        shipment_id=shipment_id,
                        risk_probability=(
                            prediction.Late_Risk_Probability
                        ),
                        predicted_class=predicted_class,
                        model_version="SupplyPrescript ML V2",
                        eligibility_status="eligible",
                    )

                    prediction_ids.append(
                        db_prediction.prediction_id
                    )

        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e),
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}",
            )

        return PredictResponse(
            request_id=request.request_id,
            predictions=predictions,
            threshold_used=ml_service.threshold,
            prediction_ids=prediction_ids,
        )

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
        db: Session = Depends(get_db),
    ):
        """
        Optimize interventions.

        If prediction_ids are supplied, selected recommendations are
        also persisted to the recommendations table.
        """

        if not request.shipments:
            raise HTTPException(
                status_code=400,
                detail="At least one shipment is required",
            )

        if (
            request.prediction_ids is not None
            and len(request.prediction_ids) != len(request.shipments)
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "prediction_ids must match "
                    "the number of shipments"
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

            recommendation_ids = None

            # --------------------------------------------------
            # Optional database persistence
            # --------------------------------------------------
            if request.prediction_ids is not None:
                recommendation_ids = []

                # Validate before writing anything.
                for prediction_id, recommendation in zip(
                    request.prediction_ids,
                    recommendations,
                ):
                    if (
                        prediction_id is not None
                        and recommendation.predicted_time_days is None
                    ):
                        raise ValueError(
                            "baseline_time_days is required "
                            "when persisting recommendations"
                        )

                for prediction_id, recommendation in zip(
                    request.prediction_ids,
                    recommendations,
                ):
                    # A missing prediction_id means there is no
                    # persisted prediction to attach to.
                    if prediction_id is None:
                        recommendation_ids.append(None)
                        continue

                    rows = crud.insert_recommendations(
                        db,
                        prediction_id=prediction_id,
                        recommendations=[
                            {
                                "action_id": recommendation.action_id,
                                "action_name": (
                                    recommendation.selected_action
                                ),
                                "predicted_cost": (
                                    recommendation.action_cost
                                ),
                                "predicted_time_days": (
                                    recommendation.predicted_time_days
                                ),
                                "risk_score": (
                                    recommendation.risk_after
                                ),
                                "feasible": True,
                                "reason": None,
                                "rank": 1,
                            }
                        ],
                    )

                    recommendation_ids.append(
                        rows[0].recommendation_id
                    )

        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e),
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Optimization failed: {str(e)}",
            )

        return OptimizeResponse(
            request_id=request.request_id,
            optimization_status=status,
            total_intervention_cost=total_cost,
            total_expected_saving=total_saving,
            recommendations=recommendations,
            recommendation_ids=recommendation_ids,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

    return app


app = create_app()