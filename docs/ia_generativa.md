# Componente de IA generativa: asistente de planeación

## Cómo se relaciona con el Diplomado

Esta parte practica el diseño de prompts y el uso de herramientas por un modelo generativo. El modelo de Machine Learning calcula el número estimado de alquileres; el modelo generativo usa ese cálculo para explicarlo con palabras sencillas. Así puedo distinguir la predicción numérica de la explicación en lenguaje natural. El código comentado está en `scripts/demand_agent.py`.

## Uso en el caso

El agente recibe una fecha/hora, clima y contexto de planeación; llama a la herramienta `predict_hour_demand`, que invoca el Random Forest guardado en `outputs/metrics/mejor_modelo.joblib`, y entrega la predicción a un modelo de lenguaje para redactar una recomendación de operación. El agente no decide movimientos de inventario ni ejecuta acciones.

## Prompt de sistema

~~~text
Eres un asistente de planeación de bicicletas compartidas. Resume en español el pronóstico y propone una revisión operativa concreta. Usa únicamente la fecha, hora, clima y predicción que recibes. Distingue una predicción de una certeza. No inventes estaciones, capacidades ni niveles de inventario que el conjunto de datos no contiene. Si la predicción corresponde a una hora de demanda alta, sugiere revisar disponibilidad antes del pico; si es baja, sugiere mantener el monitoreo normal. Responde en tres frases: lectura del pronóstico, acción sugerida y limitación.

Ejemplo 1
Entrada: 08:00, lluvia ligera, 420 alquileres estimados.
Salida: Se esperan alrededor de 420 alquileres a las 08:00. Conviene revisar la disponibilidad antes de la hora pico y considerar que el clima puede cambiar el patrón. Es una estimación de demanda total, no informa cuántas bicicletas hay en cada estación.

Ejemplo 2
Entrada: 02:00, clima despejado, 35 alquileres estimados.
Salida: La demanda estimada para las 02:00 es baja, cercana a 35 alquileres. Puede mantenerse el monitoreo habitual y planear el siguiente turno con la tendencia por hora. El modelo se entrenó con datos históricos de Washington D. C. y no conoce el inventario actual.
~~~

## Control de calidad

- La herramienta consulta el mismo modelo que se evalúa en el proyecto.
- La salida incluye la hora y el volumen estimado, para facilitar la revisión humana.
- El prompt impide inventar información de estaciones: el dataset es agregado por hora.
- Con `OPENAI_API_KEY` y `OPENAI_MODEL` configurados, el script realiza una llamada a la API Responses. Sin credenciales, produce una respuesta local de demostración y lo indica expresamente.
- En PowerShell, define ambas variables en la sesión antes de ejecutar `python scripts/demand_agent.py`. El nombre de modelo debe estar habilitado en tu cuenta de API. La clave no se debe guardar en el código ni subir al repositorio.
- Si falta una sola variable, el script se detiene con un mensaje de configuración. Si la API devuelve un error HTTP o de conexión, lo muestra como error en lugar de presentar la respuesta local como si la hubiera generado el LLM.
- El prompt y una salida de ejemplo se guardan como evidencia en el anexo del reporte.

## Limitación

La demostración usa el volumen agregado del sistema, no pronostica por estación. Para redistribuir bicicletas entre estaciones harían falta datos de inventario y demanda espacial por estación.
