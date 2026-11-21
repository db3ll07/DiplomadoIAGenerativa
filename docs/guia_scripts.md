# Guía sencilla de los scripts

Esta guía acompaña el código como apuntes para volver a entenderlo. Cada script incluye al inicio qué hace, qué necesita, qué genera y qué tema del Diplomado practica.

## Orden de ejecución

Para regenerar todos los resultados, sigue la sección **Ejecutar el flujo de análisis desde una clonación limpia** del [README principal](../README.md). El flujo descarga el conjunto de UCI, lo prepara, compara modelos, crea las tablas de SQL/BI, genera el reporte y muestra una demostración del asistente.

### Orden específico para SQL y Microsoft Fabric

1. Ejecuta `python scripts/download_data.py` para descargar los datos.
2. Ejecuta `python scripts/prepare_data.py` para crear las observaciones limpias.
3. Ejecuta `python scripts/train_models.py` para guardar las predicciones del periodo de prueba. El script ajusta obligatoriamente los hiperparámetros de cada modelo usando validación temporal y guarda los mejores valores en `outputs/metrics/comparacion_modelos.csv`.
4. Ejecuta `python scripts/build_sqlite.py`. Este paso crea la base local `datos/processed/demand_bikes.sqlite` y los cuatro CSV (`FactDemand.csv`, `DimDate.csv`, `DimHour.csv` y `DimConditions.csv`) que se cargan en el Lakehouse. Para comparar pronósticos, incluye este paso después del entrenamiento.
5. En Fabric, carga los cuatro CSV al Lakehouse y usa **Cargar en tablas** para convertirlos en tablas. No cargues el archivo SQLite para este flujo.
6. Ejecuta las consultas de [`sql/queries.sql`](../sql/queries.sql) en el endpoint de análisis SQL del Lakehouse, una por una.
7. Crea el modelo semántico y sus relaciones; después agrega las medidas DAX siguiendo [`sql/medidas_dax.md`](../sql/medidas_dax.md).
8. Crea el informe y las tarjetas siguiendo [`tablero/README.md`](../tablero/README.md).

El script `python scripts/export_powerbi_source.py` es opcional para este flujo: genera un Excel para importar en Power BI Desktop y debe ejecutarse después de `build_sqlite.py`. Las consultas SQL son una verificación recomendada antes de DAX, pero no son una dependencia técnica de las medidas.

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
