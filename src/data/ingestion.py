
import pandas as pd


def load_data(file_path):
    """
    Load the raw Supply Chain dataset.

    Parameters
    ----------
    file_path : str
        Path to the raw CSV dataset.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    df = pd.read_csv(file_path)

    return df


def validate_loaded_data(df):
    """
    Perform basic checks after loading the dataset.
    """

    if df.empty:
        raise ValueError("Dataset is empty.")

    if "Late_delivery_risk" not in df.columns:
        raise ValueError("Target column 'Late_delivery_risk' not found.")

    return True
