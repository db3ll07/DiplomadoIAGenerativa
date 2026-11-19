# Guía sencilla de los scripts

Esta guía acompaña el código como si fueran apuntes para volver a entenderlo después. Cada script también incluye al inicio una explicación breve de su propósito, lo que necesita, lo que genera y su relación con el Diplomado.

## Orden recomendado

Abre una terminal en la carpeta principal del repositorio. Los comandos siguientes usan rutas relativas; sirven aunque el repositorio se clone en otra carpeta.

```powershell
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/prepare_data.py
python scripts/train_models.py
python scripts/build_sqlite.py
python scripts/export_powerbi_source.py
python scripts/generate_report_assets.py
```

Si ya tienes el archivo original de Kaggle y configuraste su API, puedes usar `python scripts/download_kaggle.py` en lugar de descargar el respaldo de UCI. En este proyecto se usa UCI como fuente pública equivalente.

## Qué hace cada archivo y qué tema practica

| Archivo | En palabras sencillas | Tema del Diplomado que practica |
|---|---|---|
| `scripts/download_data.py` | Descarga los datos horarios de UCI. | Fuentes y adquisición de datos. |
| `scripts/download_kaggle.py` | Intenta bajar los archivos oficiales de Kaggle, si la cuenta está configurada. | Datasets públicos y preparación de un ejercicio de ML. |
| `scripts/common.py` | Comparte funciones para encontrar archivos y dar el mismo formato a UCI y Kaggle. | Limpieza, transformación y preparación de datos. Se importa; no se corre directamente. |
| `scripts/prepare_data.py` | Limpia y guarda una tabla lista para analizar, además de una división de referencia estilo Kaggle. | Preparación de datos y separación entrenamiento/prueba. |
| `scripts/train_models.py` | Resume los datos, compara predictores, prueba una red neuronal y dibuja gráficas. | Estadística, análisis exploratorio, ML supervisado, evaluación y redes neuronales. |
| `scripts/build_sqlite.py` | Acomoda datos y estimaciones en tablas relacionadas y crea una base local. | SQL, agregación y organización analítica para BI. |
| `scripts/export_powerbi_source.py` | Junta las tablas en un Excel para importarlas en Power BI. | Visualización y comunicación de datos. No crea un archivo PBIX. |
| `scripts/demand_agent.py` | Calcula una estimación y puede pedir a un LLM que la explique. | IA generativa, instrucciones y herramientas. Tiene respuesta local si no hay API. |
| `scripts/generate_report_assets.py` | Escribe el artículo y genera su PDF a partir de las métricas. | Interpretación, comunicación y documentación de resultados. |
| `scripts/make_presentation.mjs` | Construye las diapositivas y notas para exponer el proyecto. | Comunicación de resultados de IA. Usa JavaScript y Artifact Tool. |

## Cómo leer los resultados

- `outputs/metrics/comparacion_modelos.csv`: tabla para comparar los modelos clásicos. En RMSE y MAE, un número menor significa un error promedio menor.
- `outputs/metrics/resultados.json`: resumen de métricas, intervalos y fechas de evaluación.
- `outputs/predictions/holdout_predictions.csv`: resultado observado y estimado en el último tramo de tiempo.
- `outputs/figures/`: gráficas para ayudar a interpretar la demanda y la predicción.
- `datos/processed/demand_bikes.sqlite`: base de datos con tablas que se pueden consultar con SQL.

El modelo no conoce el inventario de cada estación. Por eso su estimación es una señal para planear revisiones a nivel agregado; no indica qué bicicleta mover ni a dónde.

## Glosario corto

- **Variable objetivo:** el valor que quiero estimar; aquí es `count`, el total de alquileres en una hora.
- **Predictor:** dato que doy al modelo para que estime el objetivo, como la hora o el clima.
- **Entrenar:** mostrar ejemplos históricos al modelo para que encuentre patrones.
- **Prueba:** datos guardados para revisar qué tan bien funciona el modelo con casos que no usó al aprender.
- **Sobreajuste:** cuando el modelo aprende demasiado los ejemplos de entrenamiento y luego falla con datos nuevos.
- **Red neuronal:** modelo con capas de operaciones que aprende combinaciones de variables; en este ejercicio se usa una versión pequeña.
- **Agente:** programa que puede pedir a una herramienta (el predictor) que haga un cálculo y luego redactar una respuesta.

## Cambios sencillos que puedo probar

Para explorar el proyecto sin reescribirlo, puedo cambiar la fecha y condiciones del ejemplo al final de `scripts/demand_agent.py`, o revisar en `scripts/train_models.py` las opciones del Árbol y Random Forest. Después puedo ejecutar otra vez el script de entrenamiento y comparar las métricas. Si cambio el orden de los datos o las variables, debo anotar el cambio porque la comparación podría dejar de ser equivalente.
