# Guía breve para la defensa

## Guion de 5 minutos

1. **Contexto y decisión (40 s):** el proyecto estima alquileres por hora para apoyar la planeación de revisiones de disponibilidad agregada. No estima inventario ni decisiones por estación.
2. **Datos (40 s):** presentar la fuente, periodo, unidad de análisis y reporte `outputs/metrics/calidad_datos.json`. Explicar que las horas ausentes se mantienen como huecos y no se convierten en demanda cero.
3. **Método (1 min):** explicar el corte cronológico 80/20, los cinco pliegues expansivos comunes y el ajuste que ocurre dentro de cada pliegue. Presentar regresión lineal, árbol, Random Forest, Keras y los dos baselines.
4. **Resultados (1 min):** leer RMSE CV media ± desviación estándar y métricas del holdout en la diapositiva 7. Comparar contra “última hora” y “misma hora de ayer”; una cifra menor de RMSE indica menor error típico con más penalización de errores grandes.
5. **Uso y límites (40 s):** recomendar el pronóstico como señal para priorizar una revisión. Reconocer que los datos son históricos y agregados, y que hacen falta datos recientes e inventario por estación para recomendar redistribuciones.
6. **IA generativa (40 s):** mostrar el agente conectado al predictor y explicar el valor de la llamada real al LLM. La evidencia en vivo requiere configuración manual de credenciales; esa demostración queda pendiente.

## Preguntas que conviene practicar

- **¿Por qué una validación temporal?** Porque la predicción usa el pasado para anticipar periodos posteriores; una partición aleatoria podría mezclar el orden temporal.
- **¿Qué significa que compartan pliegues?** Todos se miden en los mismos bloques de fechas reservadas. La forma de entrenar cada familia sigue siendo distinta: los clásicos ajustan hiperparámetros y RFECV; Keras usa una validación cronológica interna para detener el entrenamiento.
- **¿Qué aportan los baselines?** Indican si los modelos aprendibles mejoran una regla sencilla basada en demanda reciente. El baseline horario requiere que exista el timestamp exacto del lag; si falta, esa observación se excluye sólo para ese baseline.
- **¿Por qué mostrar RMSE y MAE?** MAE es el error absoluto promedio en alquileres; RMSE también está en alquileres, y penaliza más los errores grandes.
- **¿Qué no demuestra el R²?** No significa “porcentaje de predicciones correctas”; describe cuánto de la variación de la respuesta captura el modelo en el conjunto evaluado.
- **¿Puede usarse para decidir movimientos de bicicletas?** No directamente. El conjunto no tiene estación ni inventario; hoy respalda planeación agregada y revisión, no instrucciones de redistribución.
- **¿Por qué el predictor HTML usa Random Forest si Keras obtuvo menor RMSE?** La versión autónoma del HTML serializa el bosque y el agente actual utiliza ese modelo. Keras fue el de menor RMSE en esta evaluación; integrar Keras en el agente o justificar mantener el bosque es una decisión pendiente.
- **¿La IA generativa hace el pronóstico?** El modelo de regresión calcula la cifra. El LLM redacta una explicación a partir de la salida de la herramienta de pronóstico.

## Preparación reproducible

1. Ejecutar `python scripts/prepare_data.py`.
2. Ejecutar `python scripts/train_models.py` y guardar `resultados.json`, `metricas_por_pliegue.csv` y `baselines_prueba.csv`.
3. Ejecutar `python scripts/build_interactive_html.py` y `python scripts/generate_report_assets.py`.
4. Revisar que README, reporte y presentación indiquen los mismos resultados y que ninguna explicación atribuya causalidad a asociaciones descriptivas.
5. Para la demostración generativa real, configurar las variables de entorno localmente y ejecutar el agente durante la defensa. No incluir claves en capturas ni documentos.
