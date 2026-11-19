# Pronóstico de demanda de bicicletas

Proyecto final del **Diplomado Liderazgo en la Era de la IA**. El objetivo es estimar el total de alquileres de bicicletas por hora para apoyar la planeación de revisiones operativas. El modelo usa fecha, hora y condiciones meteorológicas. Se excluyen `casual` y `registered` porque suman directamente el objetivo `count` y causarían fuga de información.

## Fuente de datos

Se utiliza el **Bike Sharing Dataset** del [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). El archivo horario `hour.csv` contiene 17,379 observaciones de Washington, D. C., entre 2011 y 2012. El script de descarga guarda el archivo en `datos/raw/`; los datos originales se excluyen de Git.

## Requisitos

- Windows 10/11, PowerShell y Python 3.11 de 64 bits.
- Conexión a internet para descargar el conjunto de datos y las dependencias.
- Espacio para instalar TensorFlow y las demás bibliotecas indicadas en `requirements.txt` (TensorFlow puede requerir una descarga considerable).
- Para regenerar la presentación: Node.js y acceso a `@oai/artifact-tool`; consulta la sección **Presentación y Power BI**. No es requisito del flujo Python.

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

El flujo produce también el artículo Markdown y el PDF con `generate_report_assets.py`. `scripts/common.py` es un módulo compartido que se importa desde otros scripts; no se ejecuta directamente. El orden anterior satisface las dependencias entre entradas y salidas de los scripts Python.

Para abrir el notebook, instala las dependencias anteriores, inicia Jupyter desde la raíz del repositorio y abre `notebooks/01_Analisis_y_modelos.ipynb`:

```powershell
python -m jupyter notebook
```

Si PowerShell impide activar el entorno virtual, ejecuta esta instrucción solo para la ventana actual y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

El agente corre en modo de demostración local sin credenciales. Para usar OpenAI, configura `OPENAI_API_KEY` y `OPENAI_MODEL` en PowerShell y vuelve a ejecutar el script. La clave se lee desde la variable de entorno; no la escribas en el código ni la subas a Git. Este paso no es necesario para el análisis ni para los modelos predictivos.

```powershell
$secureApiKey = Read-Host "Clave API de OpenAI" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $secureApiKey).Password
$env:OPENAI_MODEL = "gpt-6-luna"
python scripts/demand_agent.py
```

El ejemplo usa `gpt-6-luna`; puedes sustituirlo por otro modelo habilitado en tu cuenta que admita llamadas a funciones en la API Responses. Las variables solo permanecen en esa ventana de PowerShell. Si falta una de las dos, el script muestra un error claro; si faltan ambas, usa la demostración local. La llamada usa la API Responses de OpenAI y puede generar cargos según el uso de tu cuenta.

### Archivos que genera el flujo

- `datos/raw/hour.csv`: datos originales descargados desde UCI.
- `datos/processed/observations.csv`: observaciones normalizadas para el proyecto.
- `outputs/metrics/`: comparación de modelos, estadísticas y modelos entrenados.
- `outputs/predictions/`: predicciones del periodo de prueba reservado.
- `outputs/figures/`: gráficas para el reporte y la exposición.
- `datos/processed/demand_bikes.sqlite` y los CSV asociados: tablas para consultas y análisis BI.
- `datos/processed/powerbi_source.xlsx`: libro con las cuatro tablas para importar en Power BI.
- `reportes/Articulo_DemandaBicicletas.md` y `reportes/Reporte_DemandaBicicletas.pdf`: reporte actualizado con las métricas calculadas.

## Presentación y Power BI

La presentación editable de 12 diapositivas está en `presentacion/Proyecto_DemandaBicicletas.pptx`. Para regenerarla se necesita Node.js y el paquete Artifact Tool disponible en el entorno Codex. Define `CODEX_NODE_MODULES` como la carpeta `node_modules` de ese entorno y ejecuta `node scripts/make_presentation.mjs`. La generación de la presentación no es necesaria para correr el flujo Python anterior.

En PowerShell, define la variable para la sesión con `$env:CODEX_NODE_MODULES = 'C:\ruta\al\entorno\node_modules'` antes de ejecutar el comando. Debe existir `@oai/artifact-tool` dentro de esa carpeta. El script también necesita `outputs/metrics/resultados.json`, generado por `train_models.py`; por eso, primero completa el flujo Python.

El Excel para Power BI sí se genera automáticamente. Para completar y guardar el archivo `.pbix`, abre `datos/processed/powerbi_source.xlsx` en Power BI Desktop, relaciona las dimensiones con `FactDemand`, crea las medidas DAX de `sql/medidas_dax.md` y sigue el diseño de `tablero/README.md`. El repositorio aún no incluye un `.pbix` terminado.

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
- Si la red neuronal no se genera, revisa `outputs/metrics/resultados.json`: `train_models.py` captura el error de TensorFlow y aun así guarda los resultados de los modelos clásicos.
- Para regenerar la presentación, confirma que Node.js está disponible (`node --version`), que `CODEX_NODE_MODULES` apunta a la carpeta correcta y que ahí está `@oai/artifact-tool`.
- No borres los archivos de `outputs/metrics/` antes de ejecutar `build_sqlite.py`, porque ahí se encuentra el modelo que usa el asistente.

## Archivos locales excluidos de Git

`.gitignore` excluye el entorno virtual, cachés de Python/Jupyter, archivos temporales y locales, dependencias de Node, el conjunto de datos descargado, tablas y bases SQLite/Excel generadas, y el contenido generado de `outputs/`. Los README de esas carpetas se conservan versionados para explicar cómo recrear los archivos. La base de datos SQLite generada también se retiró del seguimiento de Git; permanece en tu carpeta local y se vuelve a crear con `build_sqlite.py`.
