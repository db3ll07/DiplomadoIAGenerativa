# Medidas DAX sugeridas para Power BI

Crear relaciones uno a muchos desde dimensiones hacia FactDemand: DimDate[date_key] → FactDemand[date_key], DimHour[hour_key] → FactDemand[hour_key], DimConditions[conditions_key] → FactDemand[conditions_key]. Mantener filtro en una dirección desde cada dimensión.

~~~DAX
Alquileres observados = SUM(FactDemand[actual_demand])

Alquileres pronosticados = SUM(FactDemand[predicted_classical])

Horas con pronostico =
COUNTROWS(FILTER(FactDemand, NOT ISBLANK(FactDemand[predicted_classical])))

Error absoluto medio =
AVERAGEX(
    FILTER(FactDemand, NOT ISBLANK(FactDemand[predicted_classical])),
    ABS(FactDemand[actual_demand] - FactDemand[predicted_classical])
)

Sesgo del pronostico =
AVERAGEX(
    FILTER(FactDemand, NOT ISBLANK(FactDemand[predicted_classical])),
    FactDemand[predicted_classical] - FactDemand[actual_demand]
)

Demanda pico = MAXX(VALUES(DimHour[hour_label]), [Alquileres observados])

Cambio vs hora anterior =
VAR HoraActual = MAX(DimHour[hour_key])
VAR DemandaAnterior =
    CALCULATE([Alquileres observados], FILTER(ALL(DimHour), DimHour[hour_key] = HoraActual - 1))
RETURN [Alquileres observados] - DemandaAnterior
~~~

Visuales propuestos: tarjetas de alquileres observados, pronosticados, MAE y horas de pico; líneas por hora con observado y estimado; barras por temporada y día laboral; segmentadores de fecha, clima y franja horaria. La página debe titularse “¿Cuándo conviene redistribuir bicicletas?” y distinguir claramente la ventana de prueba.
