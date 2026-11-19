# Guía sencilla de los scripts

Esta guía acompaña el código como apuntes para volver a entenderlo. Cada script incluye al inicio qué hace, qué necesita, qué genera y qué tema del Diplomado practica.

## Orden de ejecución

Sigue la sección **Ejecutar el flujo de análisis desde una clonación limpia** del README. El flujo descarga el conjunto de UCI, lo prepara, compara modelos, crea las tablas de SQL/BI, genera el reporte y muestra una demostración del asistente.

## Qué hace cada archivo y qué tema practica

| Archivo | En palabras sencillas | Tema del Diplomado |
|---|---|---|
| `scripts/download_data.py` | Descarga los datos horarios desde UCI. | Fuentes y adquisición de datos. |
| `scripts/common.py` | Da formato común a los datos y crea variables de fecha. Se importa; no se ejecuta directamente. | Limpieza y transformación. |
| `scripts/prepare_data.py` | Limpia, ordena y guarda la tabla que usarán los demás scripts. | Preparación de datos para Machine Learning. |
| `scripts/train_models.py` | Resume los datos, compara modelos, prueba una red neuronal y guarda gráficas. | Estadística, análisis exploratorio, Machine Learning y redes neuronales. |
| `scripts/build_sqlite.py` | Acomoda las observaciones en tablas relacionadas y crea una base local. | SQL, agregación y organización de datos para BI. |
| `scripts/export_powerbi_source.py` | Junta las tablas en un Excel para importarlo en Power BI. No genera un archivo PBIX. | Visualización y comunicación de datos. |
| `scripts/demand_agent.py` | Calcula una estimación y puede pedir a un LLM que la explique. | IA generativa, instrucciones y herramientas. Incluye una respuesta local. |
| `scripts/generate_report_assets.py` | Escribe el artículo y genera su PDF a partir de las métricas. | Interpretación y comunicación de resultados. |
| `scripts/make_presentation.mjs` | Crea las diapositivas y notas para exponer el proyecto. | Comunicación de proyectos de IA. Requiere Node.js y Artifact Tool. |

## Cómo leer los resultados

- `outputs/metrics/comparacion_modelos.csv`: comparación de los modelos clásicos. En RMSE y MAE, un valor menor significa un error menor.
- `outputs/metrics/resultados.json`: métricas, fechas de evaluación y resumen de la prueba estadística.
- `outputs/predictions/holdout_predictions.csv`: valor observado y estimado en el último tramo de tiempo.
- `outputs/figures/`: gráficas para entender la demanda y el desempeño.
- `datos/processed/demand_bikes.sqlite`: base de datos para consultar con SQL.

## Glosario corto

- **Variable objetivo:** lo que quiero estimar; aquí es `count`, total de alquileres en una hora.
- **Predictor:** dato que usa el modelo para estimar, como hora o clima.
- **Entrenar:** mostrar ejemplos históricos al modelo para que encuentre patrones.
- **Prueba:** datos reservados para revisar el modelo con casos que no usó para aprender.
- **Sobreajuste:** cuando el modelo aprende demasiado los ejemplos de entrenamiento y falla con datos nuevos.
- **Red neuronal:** modelo con capas de operaciones que aprende combinaciones de variables; aquí usamos una versión pequeña.
- **Agente:** programa que puede pedir a una herramienta (el predictor) que haga un cálculo y luego redactar una respuesta.

El modelo no conoce el inventario de cada estación. Su predicción ayuda a planear revisiones agregadas, pero no indica qué bicicleta mover ni a dónde.