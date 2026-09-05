import pandas as pd


REQUIRED_COLUMNS = [
    "shipment_id",
    "late_probability",
    "late_penalty",
    "expedite_available",
    "priority_available",
    "route_available",
    "hub_available"
]


def validate_optimization_input(
    shipments: pd.DataFrame
) -> None:

    # -----------------------------
    # Required columns
    # -----------------------------

    missing_columns = [
        col
        for col in REQUIRED_COLUMNS
        if col not in shipments.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # -----------------------------
    # Empty input
    # -----------------------------

    if shipments.empty:
        raise ValueError(
            "No shipments available for optimization."
        )

    # -----------------------------
    # Duplicate shipment IDs
    # -----------------------------

    if shipments["shipment_id"].duplicated().any():

        duplicates = (
            shipments.loc[
                shipments["shipment_id"].duplicated(),
                "shipment_id"
            ]
            .tolist()
        )

        raise ValueError(
            f"Duplicate shipment IDs found: {duplicates}"
        )

    # -----------------------------
    # Probability validation
    # -----------------------------

    invalid_probability = shipments[
        (shipments["late_probability"] < 0)
        |
        (shipments["late_probability"] > 1)
        |
        (shipments["late_probability"].isna())
    ]

    if not invalid_probability.empty:

        raise ValueError(
            "late_probability must be between 0 and 1."
        )

    # -----------------------------
    # Penalty validation
    # -----------------------------

    invalid_penalty = shipments[
        (shipments["late_penalty"] < 0)
        |
        (shipments["late_penalty"].isna())
    ]

    if not invalid_penalty.empty:

        raise ValueError(
            "late_penalty must be zero or positive."
        )

    # -----------------------------
    # Availability validation
    # -----------------------------

    availability_columns = [
        "expedite_available",
        "priority_available",
        "route_available",
        "hub_available"
    ]

    for column in availability_columns:

        invalid_values = ~shipments[column].isin(
            [0, 1, True, False]
        )

        if invalid_values.any():

            raise ValueError(
                f"{column} must contain only 0/1 values."
            )