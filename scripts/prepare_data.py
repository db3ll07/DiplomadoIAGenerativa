"""Prepara una tabla limpia y archivos de entrenamiento/prueba estilo Kaggle.

Relación con el Diplomado: preparación de datos para Machine Learning. Practico
normalizar columnas, ordenar por fecha y separar datos. Una separación es como
un ejercicio de evaluación, no sustituye la prueba cronológica principal que
se realiza en train_models.py. La etiqueta de UCI se conserva para poder medir
qué tan cerca quedan las predicciones del resultado real.

Entrada: datos/raw/hour.csv o datos/raw/train.csv.
Salida: varios CSV en datos/processed/.
Comando desde la raíz: python scripts/prepare_data.py
"""
from pathlib import Path
import pandas as pd
from common import ROOT, RAW, PROCESSED, _uci_to_common, _kaggle_to_common


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    uci_file = RAW / "hour.csv"
    kaggle_train = RAW / "train.csv"
    if uci_file.exists():
        original = pd.read_csv(uci_file)
        df = _uci_to_common(original)
        df = df.sort_values("datetime").reset_index(drop=True)
        # En esta recreación, uso días 1–19 para entrenar, como en la competencia.
        source_train = df[df["datetime"].dt.day <= 19].copy()
        source_test = df[df["datetime"].dt.day >= 20].copy()
        source_train.to_csv(PROCESSED / "kaggle_style_train.csv", index=False)
        source_test.drop(columns=["count"]).to_csv(PROCESSED / "kaggle_style_test.csv", index=False)
        # UCI sí trae la respuesta del conjunto de prueba; la guardo para medir error.
        df.to_csv(PROCESSED / "observations.csv", index=False)
        source_test[["datetime", "count"]].to_csv(PROCESSED / "kaggle_style_test_labels.csv", index=False)
        source = "UCI Bike Sharing Dataset (fuente equivalente)"
    elif kaggle_train.exists():
        df = _kaggle_to_common(pd.read_csv(kaggle_train))
        df = df.sort_values("datetime").reset_index(drop=True)
        df.to_csv(PROCESSED / "observations.csv", index=False)
        source = "Kaggle Bike Sharing Demand"
    else:
        raise FileNotFoundError("No se encontró hour.csv ni train.csv en datos/raw. Ejecuta scripts/download_data.py")
    print(f"Fuente: {source}")
    print(f"Observaciones: {len(df):,}; columnas: {len(df.columns)}")
    print(f"Rango: {df.datetime.min()} a {df.datetime.max()}")
    print(f"Archivo procesado: {(PROCESSED / 'observations.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()

