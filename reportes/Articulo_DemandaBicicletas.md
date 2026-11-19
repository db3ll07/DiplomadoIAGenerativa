# Pronóstico de demanda de bicicletas por hora

**Proyecto final — Diplomado Liderazgo en la Era de la IA**

**Autoría:** Equipo por definir

## Resumen

El proyecto estima el volumen total de alquileres de bicicletas por hora para apoyar la planeación de una operación de micromovilidad. Se analizaron 17,379 registros horarios del Bike Sharing Dataset de Washington D. C. (2011–2012), obtenido del UCI Machine Learning Repository. Se excluyeron los conteos casuales y registrados porque son componentes directos del objetivo. Se derivaron hora, día de semana, mes y año; se compararon regresión lineal, árbol de decisión y Random Forest con validación cruzada temporal de cinco pliegues. Random Forest obtuvo el menor RMSE medio de validación (93.5 alquileres). En el último 20% cronológico, su RMSE fue 88.7 y R² 0.838. Una red densa de Keras, con parada temprana, alcanzó RMSE 74.7 y R² 0.885 en el mismo periodo. El resultado sugiere que la red mejora la prueba reservada, pero la selección del modelo debe confirmarse con validación temporal equivalente. Se recomienda usar el pronóstico como apoyo para revisar turnos y redistribución, sin extrapolarlo a estaciones individuales ni a otras ciudades.

## 1. Introducción y definición del problema

La operación de un sistema de bicicletas compartidas debe anticipar horas de demanda alta para programar revisiones y redistribuciones. La decisión que se apoya aquí es cuándo conviene revisar la disponibilidad agregada de bicicletas. La unidad de análisis es una hora para todo el sistema; no hay identificadores de estación ni inventario disponible. Por tanto, el proyecto no recomienda cuántas bicicletas mover ni a qué lugar.

El costo de equivocarse es operativo: una subestimación puede dejar menos bicicletas disponibles durante horas concurridas; una sobrestimación puede provocar movimientos de flota innecesarios. El dataset no contiene costos monetarios ni restricciones de capacidad, así que estos costos se describen de forma cualitativa y no se inventa un retorno financiero.

## 2. Estado del arte

La investigación sobre bicicletas compartidas ha usado variables temporales y meteorológicas para predecir demanda y orientar la operación. Fanaee-T y Gama (2014) describen el uso de conocimiento de dominio para etiquetar eventos en datos de alquileres; su trabajo está ligado al conjunto público usado aquí. Nam et al. (2024) estudian pronósticos horarios con estaciones de bicicletas y Random Forest, y resaltan la relevancia de señales temporales y meteorológicas. Feng et al. (2024) desarrollan una red neuronal espaciotemporal para pronosticar demanda de alquileres y devoluciones por estación. Chen et al. (2022) analizan demanda a nivel de comunidad con aprendizaje profundo.

Estos estudios incluyen señales espaciales o secuencias de inventario que el dataset de este proyecto no ofrece. Por eso se utilizan como contexto metodológico, no como una comparación directa de resultados. Para un proyecto inicial se eligen modelos tabulares sencillos y una red densa, que permiten comparar métodos de forma comprensible sin afirmar que resuelven la asignación por estación.

## 3. Datos y análisis exploratorio

La fuente es el Bike Sharing Dataset del UCI Machine Learning Repository. Contiene 17,379 filas horarias del 1 de enero de 2011 al 31 de diciembre de 2012. Se cambiaron nombres de columnas y unidades para facilitar el análisis, se combinaron fecha y hora, y se eliminaron duplicados por fecha/hora. No se observaron valores faltantes en las variables seleccionadas. La evaluación usa un corte cronológico: el último 20% de las observaciones queda reservado para la prueba final.

Las variables predictoras son temporada, feriado, día laboral, categoría meteorológica, temperatura, sensación térmica, humedad, velocidad de viento y características derivadas de fecha/hora. El objetivo `count` representa alquileres totales. Se excluyen `casual` y `registered` porque suman directamente el objetivo y filtrarían la respuesta hacia los predictores.

La demanda media observada fue 189.5 alquileres por hora (IC 95%: 186.8–192.2). La media en días laborales fue 193.2; en días no laborales, 181.4. La diferencia laboral menos no laboral fue 11.8 (IC 95% de Welch: 6.2–17.5; p = 4.25e-05). Es una asociación descriptiva; el contraste no identifica un efecto causal.

## 4. Metodología

Se ordenaron las observaciones por fecha y se reservaron los últimos 3,476 registros (20%) como prueba temporal, desde 2012-08-07 hasta 2012-12-31. Los modelos clásicos se ajustaron y compararon en el primer 80% con validación cruzada de cinco pliegues tipo ventana expansiva (TimeSeriesSplit). Las variables categóricas se codificaron con one-hot; las numéricas se imputaron por mediana y estandarizaron dentro de cada pipeline para evitar fuga entre pliegues.

Se compararon regresión lineal, árbol de decisión (profundidad máxima 18) y Random Forest (100 árboles). El criterio de selección fue el menor RMSE medio de validación cruzada. Se reportan RMSE y R²; RMSE expresa el error típico en número de alquileres y R² resume la proporción de variación explicada en esa partición.

La red Keras tuvo capas densas de 64 y 32 unidades, activación ReLU y dropout de 0.15. Se usó una partición temporal interna para validación y EarlyStopping con restauración de los mejores pesos. La comparación en la prueba utiliza el mismo último 20% cronológico. El componente generativo es un agente con prompt acotado y herramienta de pronóstico; requiere clave y modelo LLM configurados para la llamada externa, y ofrece un respaldo local ilustrativo.

## 5. Resultados

Random Forest fue el mejor modelo clásico por RMSE medio de validación cruzada. En la prueba temporal, la red neuronal obtuvo un RMSE menor que Random Forest. Esto no implica que siempre sea superior: la CV comparativa se aplicó a los modelos clásicos, mientras que la red se evaluó con una validación interna para detener el entrenamiento y una prueba externa común. El seguimiento recomendado es incluir la red en la misma validación temporal de cinco pliegues si se amplía el proyecto.

La tabla siguiente reúne los resultados solicitados por la rúbrica. Los valores corresponden a esta división temporal y no deben interpretarse como garantías de desempeño en otro periodo o ciudad.

## 6. Retos, límites y conclusión

El conjunto es histórico (2011–2012), agregado a nivel del sistema y localizado en Washington D. C. No incluye inventario, estaciones, eventos locales ni costos. La evaluación temporal es más realista que una partición aleatoria, pero las condiciones de operación y clima pueden cambiar; el modelo no se probó en datos recientes. Las predicciones negativas se recortan a cero. El componente generativo no debe inventar estaciones ni capacidad y su respuesta requiere revisión humana.

Se recomienda usar el modelo como una señal para planear revisiones horarias, registrar predicción y demanda observada y medir errores por periodo. Antes de desplegarlo, convendría validar con datos actuales de la empresa, incluir inventario por estación y establecer el costo de faltantes frente a redistribuciones innecesarias. El resultado principal es que las variables temporales y meteorológicas permiten una predicción útil en la prueba histórica, pero no bastan para optimizar movimientos concretos.

### Tabla de comparación de modelos

| Modelo | RMSE CV (media ± DE) | RMSE prueba | MAE prueba | R² prueba |
|---|---:|---:|---:|---:|
| Regresión lineal | 108.76 ± 21.64 | 133.82 | 98.69 | 0.632 |
| Árbol de decisión | 109.73 ± 29.25 | 104.74 | 69.02 | 0.774 |
| Random Forest | 93.46 ± 23.31 | 88.71 | 59.74 | 0.838 |
| Red neuronal Keras | — | 74.74 | 53.16 | 0.885 |

## Tablero Power BI y preparación SQL

El repositorio crea una base SQLite y CSV para cargar: FactDemand, DimDate, DimHour y DimConditions. El esquema estrella, uniones y medidas DAX están documentados en `sql/` y `tablero/`. El tablero final debe mostrar observado y pronosticado por hora/mes, MAE, sesgo y segmentación por clima y calendario.

## Anexo: componente generativo

El prompt de sistema y sus ejemplos están en `docs/ia_generativa.md`. La herramienta `predict_hour_demand` consulta el modelo clásico serializado; el LLM resume el pronóstico sin inventar estaciones o inventario. Sin credenciales, el agente usa una respuesta local de demostración.

## Referencias (APA 7)

- Fanaee-T, H., & Gama, J. (2014). Event labeling combining ensemble detectors and background knowledge. Progress in Artificial Intelligence, 2, 113–127. https://doi.org/10.1007/s13748-013-0040-3
- Nam, H., et al. (2024). Framework for hourly demand forecasting of bike-sharing stations: Case study of the four main gate areas in Seoul. International Journal of Urban Sciences, 28(4). https://doi.org/10.1080/12265934.2024.2317198
- Feng, J., Liu, H., Zhou, J., & Zhou, Y. (2024). A spatial-temporal aggregated graph neural network for docked bike-sharing demand forecasting. ACM Transactions on Knowledge Discovery from Data, 18(9), Article 232. https://doi.org/10.1145/3690388
- Chen, J., et al. (2022). Bike-sharing demand prediction at community level under COVID-19 using deep learning. Sensors, 22(3), 1060. https://doi.org/10.3390/s22031060
- UCI Machine Learning Repository. (2013). Bike Sharing Dataset. https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
