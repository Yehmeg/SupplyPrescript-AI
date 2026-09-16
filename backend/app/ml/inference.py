"""Inference-only SupplyPrescript V2 runtime for the FastAPI backend."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

TARGET = "Late_delivery_risk"
UNKNOWN_CATEGORY = "__UNKNOWN__"
NON_SHIPMENT_STATUSES = ("CANCELED", "SUSPECTED_FRAUD")

REQUIRED_ARTIFACTS = {
    "xgb": "final_xgboost.pkl",
    "lgb": "final_lightgbm.pkl",
    "cat": "final_catboost.pkl",
    "features": "final_features.pkl",
    "categorical": "final_categorical_features.pkl",
    "category_levels": "final_category_levels.pkl",
    "threshold": "final_threshold.pkl",
    "config": "final_ensemble_config.pkl",
}

_ARTIFACT_CACHE: dict[Path, dict[str, Any]] = {}


def missing_model_artifacts(model_dir: Path) -> list[str]:
    return [
        filename
        for filename in REQUIRED_ARTIFACTS.values()
        if not (model_dir / filename).exists()
    ]


def load_artifacts(model_dir: Path) -> dict[str, Any]:
    model_dir = model_dir.resolve()
    if model_dir in _ARTIFACT_CACHE:
        return _ARTIFACT_CACHE[model_dir]

    missing = missing_model_artifacts(model_dir)
    if missing:
        raise FileNotFoundError(
            f"Missing SupplyPrescript V2 artifacts in {model_dir}: {missing}"
        )

    artifacts = {
        key: joblib.load(model_dir / filename)
        for key, filename in REQUIRED_ARTIFACTS.items()
    }

    if float(artifacts["threshold"]) != float(artifacts["config"]["threshold"]):
        raise ValueError("Saved threshold does not match final_ensemble_config.pkl")

    _ARTIFACT_CACHE[model_dir] = artifacts
    return artifacts


def prepare_inference_features(
    new_data: pd.DataFrame,
    artifacts: dict[str, Any],
) -> pd.DataFrame:
    loaded_features = artifacts["features"]
    loaded_categorical = artifacts["categorical"]
    loaded_category_levels = artifacts["category_levels"]
    loaded_config = artifacts["config"]

    data = new_data.copy()

    for col in loaded_config["dropped_columns"]:
        if col in data.columns:
            data = data.drop(columns=[col])

    for forbidden in [TARGET, "_Order_Group_ID"]:
        if forbidden in data.columns:
            data = data.drop(columns=[forbidden])

    missing_features = [c for c in loaded_features if c not in data.columns]
    if missing_features:
        raise ValueError(f"Missing required V2 features: {missing_features}")

    data = data[loaded_features].copy()

    for col in loaded_categorical:
        levels = loaded_category_levels[col]
        known_levels = set(levels)
        data[col] = data[col].astype("object")
        data[col] = data[col].where(data[col].isin(known_levels), UNKNOWN_CATEGORY)
        data[col] = pd.Categorical(data[col], categories=levels)

    return data


def predict_supplyprescript(
    new_data: pd.DataFrame,
    artifacts: dict[str, Any],
) -> pd.DataFrame:
    loaded_config = artifacts["config"]
    loaded_threshold = float(artifacts["threshold"])

    result = pd.DataFrame(
        {
            "Late_Risk_Probability": np.nan,
            "Predicted_Late_Risk": pd.Series(pd.NA, index=new_data.index, dtype="Int64"),
            "Prediction_Eligible": True,
            "Exclusion_Reason": pd.Series(pd.NA, index=new_data.index, dtype="string"),
        },
        index=new_data.index,
    )

    eligible_mask = pd.Series(True, index=new_data.index)

    if "Order Status" in new_data.columns:
        status = new_data["Order Status"].astype("string").str.strip().str.upper()
        excluded_mask = status.isin(
            loaded_config.get("excluded_order_statuses", list(NON_SHIPMENT_STATUSES))
        )
        eligible_mask &= ~excluded_mask
        result.loc[excluded_mask, "Prediction_Eligible"] = False
        result.loc[excluded_mask, "Exclusion_Reason"] = "Non-shipment order status"

    if eligible_mask.any():
        features = prepare_inference_features(new_data.loc[eligible_mask].copy(), artifacts)
        p_xgb = artifacts["xgb"].predict_proba(features)[:, 1]
        p_lgb = artifacts["lgb"].predict_proba(features)[:, 1]
        p_cat = artifacts["cat"].predict_proba(features)[:, 1]
        probability = (p_xgb + p_lgb + p_cat) / 3.0
        prediction = (probability >= loaded_threshold).astype(int)
        result.loc[eligible_mask, "Late_Risk_Probability"] = probability
        result.loc[eligible_mask, "Predicted_Late_Risk"] = prediction

    return result
