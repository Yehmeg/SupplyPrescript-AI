from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.ml.service import get_ml_service, MLService
from app.api.schemas.prediction import PredictRequest, PredictResponse


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

    @app.get("/health", tags=["health"])
    async def health():
        """Liveness probe - always returns 200 if process is running."""
        return {"status": "ok"}

    @app.get("/ready", tags=["health"])
    async def ready(ml_service: MLService = Depends(get_ml_service)):
        """Readiness probe - checks ML artifacts are loaded."""
        if ml_service.is_ready():
            return {"status": "ready", "models_loaded": ml_service.artifacts.available_models}
        raise HTTPException(status_code=503, detail="ML artifacts not loaded")

    @app.post(f"{settings.API_PREFIX}/predict", response_model=PredictResponse, tags=["predictions"])
    async def predict(
        request: PredictRequest,
        ml_service: MLService = Depends(get_ml_service),
    ):
        """Score late-delivery risk for one or more orders."""
        if not request.orders:
            raise HTTPException(status_code=400, detail="At least one order is required")

        try:
            predictions = ml_service.predict(request.orders)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

        return PredictResponse(
            request_id=request.request_id,
            predictions=predictions,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    return app


app = create_app()