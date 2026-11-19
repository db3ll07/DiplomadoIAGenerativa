-- 1. Demanda media por hora y día laboral
SELECT h.hour_label, d.is_working_day, AVG(f.actual_demand) AS avg_hourly_demand
FROM FactDemand f
JOIN DimHour h ON f.hour_key = h.hour_key
JOIN DimDate d ON f.date_key = d.date_key
GROUP BY h.hour_label, d.is_working_day
ORDER BY h.hour_key, d.is_working_day;

-- 2. Demanda observada y pronosticada por mes
SELECT d.year, d.month, SUM(f.actual_demand) AS actual_rentals,
       SUM(f.predicted_classical) AS forecast_rentals
FROM FactDemand f
JOIN DimDate d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. Promedio por clima y franja horaria
SELECT c.weather, h.time_band, AVG(f.actual_demand) AS avg_hourly_demand,
       COUNT(*) AS observations
FROM FactDemand f
JOIN DimConditions c ON f.conditions_key = c.conditions_key
JOIN DimHour h ON f.hour_key = h.hour_key
GROUP BY c.weather, h.time_band
ORDER BY c.weather, h.time_band;

-- 4. Error absoluto medio por hora (solo donde existe pronóstico holdout)
SELECT h.hour_label,
       AVG(ABS(f.actual_demand - f.predicted_classical)) AS mae_by_hour
FROM FactDemand f
JOIN DimHour h ON f.hour_key = h.hour_key
WHERE f.predicted_classical IS NOT NULL
GROUP BY h.hour_label
ORDER BY h.hour_key;

