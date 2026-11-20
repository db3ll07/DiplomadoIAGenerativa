# Presentación

`Proyecto_DemandaBicicletas.pptx` contiene 12 diapositivas editables y notas para explicar el problema, los datos del UCI Machine Learning Repository, el análisis, modelos, resultados, SQL/BI, IA generativa, límites y referencias.

## Presentación interactiva autónoma

`Proyecto_DemandaBicicletas_interactiva.html` es una presentación HTML independiente. Se puede abrir directamente con doble clic en un navegador moderno; no requiere servidor local, conexión a internet ni rutas externas. Incluye los datos resumidos para la gráfica exploratoria y los modelos Random Forest y red neuronal como datos embebidos. La diapositiva 04 permite filtrar y visualizar la demanda por hora o temporada. La diapositiva 08 ejecuta ambas predicciones en el navegador.

Para volver a generar el HTML después de actualizar datos o modelos, abre PowerShell en la raíz del repositorio, instala las dependencias indicadas en `requirements.txt` si hace falta y ejecuta:

```powershell
python scripts/build_interactive_html.py
```

El generador lee los archivos preparados y los modelos guardados en `outputs/metrics/`; escribe únicamente `presentacion/Proyecto_DemandaBicicletas_interactiva.html`. La presentación descargada desde GitHub ya incluye los modelos, así que el usuario final no tiene que ejecutar el generador.

El archivo ya generado puede abrirse en PowerPoint sin instalar herramientas adicionales. Volver a generarlo es opcional y requiere Node.js y el módulo Artifact Tool disponible en una carpeta `node_modules`. El script busca el módulo en `node_modules` en la raíz del repositorio. Si está en otra ubicación, abre PowerShell en la raíz del repositorio, define `ARTIFACT_TOOL_NODE_MODULES` con la ruta a esa carpeta y ejecuta `node scripts/make_presentation.mjs`. Las rutas de datos y salida se calculan desde la ubicación del repositorio.
