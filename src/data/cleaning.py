import pandas as pd
import numpy as np


def remove_duplicates(df):
    """Remove duplicate rows."""
    return df.drop_duplicates().copy()


def handle_missing_values(df):
    """Handle missing values in the dataset."""

    df = df.copy()

    # Remove Customer Zipcode because it contains missing values
    if "Customer Zipcode" in df.columns:
        df = df.drop(columns=["Customer Zipcode"])

    return df


def remove_infinite_values(df):
    """Replace infinite values with NaN and remove affected rows."""

    df = df.copy()

    df = df.replace([np.inf, -np.inf], np.nan)

    return df


def clean_data(df):
    """
    Complete data-cleaning pipeline.

    Steps:
    1. Remove duplicates
    2. Handle missing values
    3. Remove infinite values
    """

    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = remove_infinite_values(df)

    return df
