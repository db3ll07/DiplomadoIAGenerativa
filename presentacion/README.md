# Presentación

`Proyecto_DemandaBicicletas.pptx` contiene 12 diapositivas editables y notas para explicar el problema, los datos del UCI Machine Learning Repository, el análisis, modelos, resultados, SQL/BI, IA generativa, límites y referencias.

## Presentación interactiva autónoma

`Proyecto_DemandaBicicletas_interactiva.html` es una presentación HTML independiente. Se puede abrir directamente con doble clic en un navegador moderno; no requiere servidor local, conexión a internet ni rutas externas. Incluye los datos resumidos para la gráfica exploratoria y los modelos Random Forest y red neuronal como datos embebidos. La diapositiva 04 permite filtrar y visualizar la demanda por hora o temporada. La diapositiva 08 ejecuta ambas predicciones en el navegador.

Para volver a generar el HTML después de actualizar datos o modelos, abre PowerShell en la raíz del repositorio, instala las dependencias indicadas en `requirements.txt` si hace falta y ejecuta:

```powershell
python scripts/build_interactive_html.py
```

El generador lee los archivos preparados y los modelos guardados en `outputs/metrics/`; escribe únicamente `presentacion/Proyecto_DemandaBicicletas_interactiva.html`. La presentación descargada desde GitHub ya incluye los modelos, así que el usuario final no tiene que ejecutar el generador.

El archivo ya generado puede abrirse en PowerPoint. Para volverlo a crear, se necesita Node.js y Artifact Tool. Define `CODEX_NODE_MODULES` con la ruta a `node_modules` que contiene `@oai/artifact-tool`, abre PowerShell en la raíz del repositorio y ejecuta `node scripts/make_presentation.mjs`. Las rutas de datos y salida se calculan desde la ubicación del repositorio.
