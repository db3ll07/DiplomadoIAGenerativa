"""Funciones compartidas que usan los otros scripts.

Relación con el Diplomado: aquí practico preparación de datos (ETL), limpieza y
creación de variables para Machine Learning. La idea es convertir las dos
versiones de la fuente (UCI y Kaggle) a una misma tabla sencilla.

Este archivo no se ejecuta por sí solo. Los demás scripts lo importan.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "datos" / "raw"
PROCESSED = ROOT / "datos" / "processed"
OUTPUTS = ROOT / "outputs"

FEATURE_COLUMNS = [
    "season", "holiday", "workingday", "weather", "temp", "atemp",
    "humidity", "windspeed", "hour", "dayofweek", "month", "year",
]
CATEGORICAL = [
    "season", "holiday", "workingday", "weather", "hour", "dayofweek", "month", "year",
]
NUMERIC = ["temp", "atemp", "humidity", "windspeed"]


def load_observations() -> pd.DataFrame:
    """Carga la tabla procesada o la transforma desde los archivos originales.

    Primero busca datos/processed/observations.csv. Si todavía no existe,
    intenta usar hour.csv de UCI o train.csv de Kaggle.
    """
    path = PROCESSED / "observations.csv"
    if path.exists():
        df = pd.read_csv(path, parse_dates=["datetime"])
    else:
        raw = RAW / "hour.csv"
        if raw.exists():
            df = _uci_to_common(pd.read_csv(raw))
        elif (RAW / "train.csv").exists():
            df = _kaggle_to_common(pd.read_csv(RAW / "train.csv"))
        else:
            raise FileNotFoundError("No hay datos. Ejecuta python scripts/download_data.py")
    df = df.drop_duplicates(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return add_time_features(df)


def _uci_to_common(df: pd.DataFrame) -> pd.DataFrame:
    """Cambia nombres y unidades de UCI al formato común del proyecto."""
    result = pd.DataFrame({
        "datetime": pd.to_datetime(df["dteday"]) + pd.to_timedelta(df["hr"], unit="h"),
        "season": df["season"], "holiday": df["holiday"], "workingday": df["workingday"],
        "weather": df["weathersit"], "temp": df["temp"] * 41,
        "atemp": df["atemp"] * 50, "humidity": df["hum"] * 100,
        "windspeed": df["windspeed"] * 67, "count": df["cnt"],
    })
    return result


def _kaggle_to_common(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona y acomoda las columnas que necesitamos de Kaggle."""
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    rename = {"count": "count", "weather": "weather", "humidity": "humidity"}
    keep = ["datetime", "season", "holiday", "workingday", "weather", "temp", "atemp", "humidity", "windspeed"]
    result = df[keep].rename(columns=rename)
    if "count" in df:
        result["count"] = df["count"]
    return result


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega hora, día de semana, mes y año a partir de la fecha."""
    df = df.copy()
    dt = pd.to_datetime(df["datetime"])
    df["hour"] = dt.dt.hour
    df["dayofweek"] = dt.dt.dayofweek
    df["month"] = dt.dt.month
    df["year"] = dt.dt.year
    if "count" in df:
        df["count"] = pd.to_numeric(df["count"], errors="coerce")
    return df

