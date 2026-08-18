
import pandas as pd
import numpy as np


def engineer_features(df):
    """
    Create reusable features for SupplyPrescript.

    The same feature-engineering logic can be used
    during model training and later during prediction.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Date features
    # --------------------------------------------------------

    if "order date (DateOrders)" in df.columns:

        date_col = pd.to_datetime(
            df["order date (DateOrders)"],
            errors="coerce"
        )

        df["Order_Year"] = date_col.dt.year
        df["Order_Month"] = date_col.dt.month
        df["Order_Day"] = date_col.dt.day
        df["Order_DayOfWeek"] = date_col.dt.dayofweek

    # --------------------------------------------------------
    # Remove columns that should not be used as features
    # --------------------------------------------------------

    excluded_columns = [
        "Late_delivery_risk",
        "Delivery Status",
        "Days for shipping (real)",
        "shipping date (DateOrders)"
    ]

    df = df.drop(
        columns=[
            col for col in excluded_columns
            if col in df.columns
        ],
        errors="ignore"
    )

    return df


def prepare_features_and_target(df, target="Late_delivery_risk"):
    """
    Separate the final feature matrix and target variable.
    """

    if target not in df.columns:
        raise ValueError(
            f"Target column '{target}' not found."
        )

    X = engineer_features(df)

    y = df[target].astype(int)

    return X, y
