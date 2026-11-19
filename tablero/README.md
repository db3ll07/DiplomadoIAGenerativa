# Tablero Power BI

## Fuente de datos y modelo

Ejecuta `python scripts/build_sqlite.py` y después `python scripts/export_powerbi_source.py`. Power BI Desktop puede importar `datos/processed/powerbi_source.xlsx`; contiene cuatro hojas con tablas limpias. Para no romper rutas al clonar, genera el libro después de clonar en lugar de editar una ruta fija del equipo.

Esquema estrella:

- FactDemand (tabla de hechos por hora) → DimDate por `date_key`.
- FactDemand → DimHour por `hour_key`.
- FactDemand → DimConditions por `conditions_key`.
- Relaciones 1 a muchos, filtro unidireccional desde dimensión a hechos.

## Historia visual

Una página “¿Cuándo conviene redistribuir bicicletas?” con tarjetas para alquileres observados, estimados, MAE y sesgo; líneas de observado vs. estimado por hora; barras por hora del día y temporada; y filtros de fecha, franja horaria y clima. La prueba final debe quedar identificada como ventana histórica de evaluación.

Las medidas propuestas están en `sql/medidas_dax.md`. El modelo y las exportaciones se producen localmente. El PBIX debe refrescarse desde el archivo generado en la clonación activa.
