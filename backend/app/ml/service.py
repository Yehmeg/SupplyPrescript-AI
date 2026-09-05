import pandas as pd
from typing import List

from app.ml.inference import load_artifacts, predict_supplyprescript
from app.api.schemas.prediction import OrderInput, PredictionResponseItem
from app.config import get_model_dir


class MLService:
    def __init__(self):
        self._artifacts = None
        self._model_dir = get_model_dir()

    @property
    def artifacts(self):
        if self._artifacts is None:
            self._artifacts = load_artifacts(self._model_dir)
        return self._artifacts

    @property
    def threshold(self) -> float:
        return float(self.artifacts["threshold"])

    def predict(self, orders: List[OrderInput]) -> List[PredictionResponseItem]:
        df = pd.DataFrame([o.model_dump(by_alias=True) for o in orders])
        result_df = predict_supplyprescript(df, artifacts=self.artifacts)

        return [
            PredictionResponseItem(
                Late_Risk_Probability=(
                    float(row["Late_Risk_Probability"])
                    if pd.notna(row["Late_Risk_Probability"])
                    else None
                ),
                Predicted_Late_Risk=(
                    int(row["Predicted_Late_Risk"])
                    if pd.notna(row["Predicted_Late_Risk"])
                    else None
                ),
                Prediction_Eligible=bool(row["Prediction_Eligible"]),
                Exclusion_Reason=(
                    str(row["Exclusion_Reason"])
                    if pd.notna(row["Exclusion_Reason"])
                    else None
                ),
            )
            for _, row in result_df.iterrows()
        ]

    def is_ready(self) -> bool:
        try:
            artifacts = self.artifacts
            return all(k in artifacts for k in ("xgb", "lgb", "cat"))
        except Exception:
            return False

    def available_models(self) -> list[str]:
        if not self.is_ready():
            return []
        return ["XGBoost", "LightGBM", "CatBoost"]


_ml_service: MLService | None = None


def get_ml_service() -> MLService:
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service
