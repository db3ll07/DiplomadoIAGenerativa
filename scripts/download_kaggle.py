"""Descarga los archivos oficiales de la competencia Bike Sharing Demand.

Relación con el Diplomado: adquisición de datos y uso de un dataset público
para practicar Machine Learning. Este script solo descarga: Kaggle requiere
que yo haya iniciado sesión, configurado su API y aceptado sus reglas.
Se ejecuta desde la raíz con: python scripts/download_kaggle.py
"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "datos" / "raw"


def main():
    kaggle = shutil.which("kaggle")
    if not kaggle:
        raise SystemExit(
            "No se encontró Kaggle CLI. Instálalo y configura la API key; inicia sesión y acepta las reglas en Kaggle. "
            "Después vuelve a ejecutar este script. El proyecto ya trae el equivalente público de UCI."
        )
    DEST.mkdir(parents=True, exist_ok=True)
    command = [kaggle, "competitions", "download", "-c", "bike-sharing-demand", "-p", str(DEST), "--force"]
    print("Ejecutando Kaggle CLI para bike-sharing-demand...")
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        raise SystemExit("Kaggle CLI no pudo descargar. Verifica autenticación y aceptación de reglas.")
    print(f"Descarga lista en {DEST.relative_to(ROOT)}. Extrae el ZIP si el CLI no lo hizo.")


if __name__ == "__main__":
    main()

