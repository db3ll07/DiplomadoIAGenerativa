# Pronóstico de demanda de bicicletas

Proyecto final del **Diplomado Liderazgo en la Era de la IA**. El objetivo es estimar el total de alquileres de bicicletas por hora para apoyar la planeación de revisiones operativas. El modelo usa fecha, hora y condiciones meteorológicas. Se excluyen `casual` y `registered` porque suman directamente el objetivo `count` y causarían fuga de información.

## Fuente de datos

Se utiliza el **Bike Sharing Dataset** del [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). El archivo horario `hour.csv` contiene 17,379 observaciones de Washington, D. C., entre 2011 y 2012. El script de descarga guarda el archivo en `datos/raw/`; los datos originales se excluyen de Git.

## Requisitos

- Windows 10/11, PowerShell y Python 3.11 de 64 bits.
- Conexión a internet para descargar el conjunto de datos y las dependencias.
- Espacio para instalar TensorFlow y las demás bibliotecas indicadas en `requirements.txt`.

## Ejecutar el flujo de análisis desde una clonación limpia

Abre PowerShell en la carpeta raíz del repositorio. Ejecuta los comandos en orden. Cada script guarda sus archivos dentro del repositorio usando rutas relativas, por lo que no tienes que editar rutas de tu computadora.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python scripts/download_data.py
python scripts/prepare_data.py
python scripts/train_models.py
python scripts/build_sqlite.py
python scripts/export_powerbi_source.py
python scripts/generate_report_assets.py
python scripts/demand_agent.py
```

Si PowerShell impide activar el entorno virtual, ejecuta esta instrucción solo para la ventana actual y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

El agente corre en modo de demostración local sin credenciales. Para usar un servicio LLM, configura `OPENAI_API_KEY` y `OPENAI_MODEL` en la sesión; esto no es necesario para el análisis ni para los modelos predictivos.

### Archivos que genera el flujo

- `datos/raw/hour.csv`: datos originales descargados desde UCI.
- `datos/processed/observations.csv`: observaciones normalizadas para el proyecto.
- `outputs/metrics/`: comparación de modelos, estadísticas y modelos entrenados.
- `outputs/predictions/`: predicciones del periodo de prueba reservado.
- `outputs/figures/`: gráficas para el reporte y la exposición.
- `datos/processed/demand_bikes.sqlite` y los CSV asociados: tablas para consultas y análisis BI.
- `datos/processed/powerbi_source.xlsx`: libro con las cuatro tablas para importar en Power BI.
- `reportes/Articulo_DemandaBicicletas.md` y `reportes/Reporte_DemandaBicicletas.pdf`: reporte actualizado con las métricas calculadas.

## Consultas SQL y Microsoft Fabric

Para preparar los datos de SQL y BI, ejecuta los scripts en este orden desde la raíz del proyecto:

1. `python scripts/download_data.py`: descarga los datos originales.
2. `python scripts/prepare_data.py`: prepara las observaciones.
3. `python scripts/train_models.py`: entrena los modelos y guarda las predicciones de prueba.
4. `python scripts/build_sqlite.py`: crea `datos/processed/demand_bikes.sqlite` y los cuatro CSV del modelo (`FactDemand.csv`, `DimDate.csv`, `DimHour.csv` y `DimConditions.csv`).
5. En Fabric, crea un Lakehouse, carga esos cuatro CSV y conviértelos en tablas. Después ejecuta, una por una, las consultas de [`sql/queries.sql`](./sql/queries.sql) en el endpoint de análisis SQL del Lakehouse.
6. Crea el modelo semántico a partir de las tablas, configura sus relaciones y agrega las medidas de [`sql/medidas_dax.md`](./sql/medidas_dax.md).
7. Crea las tarjetas y el resto del informe siguiendo [`tablero/README.md`](./tablero/README.md).

El orden de SQL antes de DAX es recomendado para verificar las tablas y documentar las consultas de SQL; no es una dependencia técnica. Los pasos detallados están en [`sql/README.md`](./sql/README.md).

`python scripts/export_powerbi_source.py` es opcional: después de `build_sqlite.py`, genera `datos/processed/powerbi_source.xlsx` para importar las tablas en Power BI Desktop. Para el flujo de Fabric descrito arriba, se usan directamente los cuatro CSV; no hace falta cargar `demand_bikes.sqlite` ni el Excel. El repositorio no incluye un informe `.pbix` terminado.

La presentación editable de 12 diapositivas está en `presentacion/Proyecto_DemandaBicicletas.pptx`. El archivo ya generado se puede abrir en PowerPoint sin instalar herramientas adicionales. Regenerarlo es opcional y requiere Node.js y el módulo Artifact Tool disponible en una carpeta `node_modules`. El script usa por defecto `node_modules` en la raíz del proyecto; si el módulo está en otra ubicación, define `ARTIFACT_TOOL_NODE_MODULES` con la ruta a esa carpeta y ejecuta `node scripts/make_presentation.mjs`. Esto no es necesario para preparar las tablas SQL/BI.

## Proyecto y rúbrica

El proyecto documenta el problema de negocio, origen y preparación de datos, análisis exploratorio, inferencia estadística, comparación de modelos, evaluación temporal, uso de SQL/BI, componente de IA generativa, conclusiones, limitaciones y referencias. El reporte corto y la presentación sirven como productos de comunicación de resultados. `docs/guia_scripts.md` explica cada etapa con lenguaje sencillo y relaciona el código con los temas del Diplomado.

### Decisión y métricas

La decisión que se busca apoyar es cuándo conviene revisar la disponibilidad agregada de bicicletas. Se comparan regresión lineal, árbol de decisión y Random Forest mediante validación cruzada temporal de cinco pliegues. El último 20% cronológico se reserva como prueba final. Se reportan RMSE, MAE y R². Una red densa de Keras se evalúa en ese mismo periodo, con una validación temporal interna para detener el entrenamiento; no se incluyó en la misma validación cruzada de cinco pliegues que los modelos clásicos.

Los resultados son históricos y corresponden a Washington, D. C. El dataset no incluye inventario ni ubicaciones por estación. Por ello, las estimaciones son una señal de planeación y no indican cuántas bicicletas mover ni a qué lugar. La diferencia entre días laborales y no laborales es asociativa y no demuestra causalidad.

## Contenido del repositorio

- `datos/raw/`: conjunto original descargado; excluido de Git.
- `datos/processed/`: observaciones limpias, tablas SQL/BI y libro de Power BI.
- `notebooks/`: análisis exploratorio y comparación de modelos.
- `scripts/`: descarga, preparación, entrenamiento y generación de entregables.
- `sql/`: esquema, consultas y medidas DAX de ejemplo.
- `tablero/`: guía de armado del tablero en Power BI.
- `outputs/`: métricas, predicciones y figuras generadas.
- `reportes/`: artículo en Markdown y PDF.
- `presentacion/`: exposición editable y notas del presentador.
- `docs/guia_scripts.md`: instrucciones de ejecución, explicación de scripts y glosario.
- `docs/ia_generativa.md`: instrucciones y límites del asistente de IA generativa.
- `app/`: reservado; actualmente no se desarrolla una aplicación.

## Solución de problemas

- Si falta `hour.csv`, vuelve a ejecutar `python scripts/download_data.py` y verifica tu conexión a internet.
- Si aparece `ModuleNotFoundError`, activa `.venv` e instala de nuevo con `python -m pip install -r requirements.txt`.
- Si un paso indica que falta un archivo procesado, ejecuta los scripts anteriores en el orden indicado.
- Si TensorFlow no está disponible, reinstala las dependencias con Python 3.11 de 64 bits. El script informa el estado de la red neuronal junto con los resultados de los modelos clásicos.
- No borres los archivos de `outputs/metrics/` antes de ejecutar `build_sqlite.py`, porque ahí se encuentra el modelo que usa el asistente.