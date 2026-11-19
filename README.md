# Pronóstico de demanda de bicicletas

Proyecto final del Diplomado Liderazgo en la Era de la IA. Estima el número de alquileres de bicicletas por hora para apoyar la planeación operativa. El análisis usa las variables de fecha/hora y clima, y excluye `casual` y `registered` porque suman directamente el objetivo `count` y producirían fuga de información.

## Estado de la fuente

La competencia oficial de Kaggle requiere autenticarse y aceptar sus reglas. En esta sesión el navegador no estaba autenticado, por lo que no se automatizó el inicio de sesión. El conjunto público original de UCI (Bike Sharing Dataset, archivo `hour.csv`) es el respaldo local; contiene las etiquetas completas y permite recrear el corte de Kaggle por día del mes. Para bajar el conjunto oficial cuando la cuenta esté autenticada y las reglas ya estén aceptadas:

```powershell
python scripts/download_kaggle.py
```

Fuente oficial de Kaggle: <https://www.kaggle.com/competitions/bike-sharing-demand/data>. Fuente equivalente pública: <https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>.

## Reproducir desde una clonación

Los scripts resuelven las rutas desde la ubicación de `scripts/`, por lo que no dependen de la carpeta donde se clonó el repositorio. Desde la raíz del repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/prepare_data.py
python scripts/train_models.py
python scripts/build_sqlite.py
python scripts/export_powerbi_source.py
python scripts/generate_report_assets.py
```

Los notebooks se deben abrir con el directorio de trabajo en la raíz del repositorio. No se requieren rutas absolutas de la computadora.

## Contenido

- `datos/raw/`: archivo original descargado. Está excluido de Git; revisa la licencia/reglas antes de redistribuirlo.
- `datos/processed/`: datos limpios y tablas dimensión/facto exportadas.
- `notebooks/`: análisis exploratorio, estadística, modelos y comparación.
- `scripts/`: descarga, preparación, entrenamiento, SQL y generación de artefactos.
- `docs/guia_scripts.md`: explicación sencilla de cada script y los conceptos que practica.
- `sql/`: esquema estrella, consultas y medidas DAX de referencia.
- `tablero/`: archivo Power BI, instrucciones y medidas DAX.
- `reportes/`: artículo corto y reporte PDF.
- `presentacion/`: presentación editable de 12 diapositivas y guion en notas.
- `app/`: actualmente no usada; no se desarrolla una aplicación web.

## Decisión y métricas

Decisión: con el pronóstico horario, ¿cuándo debe la operación revisar o redistribuir bicicletas? Se comparan una regresión lineal, un árbol de decisión y un Random Forest con validación cruzada temporal. Se reportan RMSE y R². El último tramo cronológico queda reservado como prueba. La recomendación es de planeación, no una promesa de demanda futura; el conjunto es histórico y de Washington D. C.

## Componente generativo

El prompt con ejemplos y un agente de demostración que usa la herramienta del modelo se describen en `docs/ia_generativa.md` y `scripts/demand_agent.py`. La conexión a un servicio LLM requiere una clave y un nombre de modelo configurados por el usuario; no es necesaria para entrenar ni evaluar los modelos.

## Limitación de Power BI

El entorno tiene Power BI Desktop instalado, pero el PBIX final requiere construir y revisar un modelo tabular en la aplicación. La especificación del esquema estrella, consultas y DAX está en `tablero/`. El tablero Power BI es un requisito de entrega para completar en Desktop; el material analítico y las tablas para cargar se generan con rutas relativas.
