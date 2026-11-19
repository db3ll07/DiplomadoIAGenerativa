"""Explora los datos, compara modelos y guarda predicciones y gráficas.

Relación con el Diplomado: análisis de datos, estadística, Machine Learning y
redes neuronales. Este es el script principal del proyecto. Primero resume los
datos; luego compara tres modelos clásicos con validación temporal; por último
entrena una red neuronal sencilla con Keras. La última parte de la cronología
se reserva para evaluar los modelos en horas que no usaron para aprender.

Términos útiles:
- RMSE: tamaño típico del error; se expresa en alquileres y menor es mejor.
- MAE: error absoluto promedio, también en alquileres.
- R²: resumen de qué tanto acompaña el modelo los cambios observados.
- Validación temporal: entreno con periodos anteriores y valido con posteriores.

Entrada: datos/processed/observations.csv (o datos/raw/ si no se preparó).
Salida: métricas, modelo guardado, predicciones y figuras dentro de outputs/.
Desde la raíz: python scripts/train_models.py
"""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.base import clone
import joblib
from common import ROOT, RAW, PROCESSED, OUTPUTS, FEATURE_COLUMNS, CATEGORICAL, NUMERIC, load_observations

warnings.filterwarnings("ignore", category=UserWarning)
RANDOM_STATE = 42


def make_preprocessor():
    """Completa valores faltantes y convierte columnas para los modelos."""
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    return ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)],
                             verbose_feature_names_out=False)


def ci_mean(values, confidence=0.95):
    """Calcula un intervalo de confianza sencillo para un promedio."""
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    se = stats.sem(values)
    lo, hi = stats.t.interval(confidence, len(values) - 1, loc=mean, scale=se)
    return [float(lo), float(hi)]


def main():
    for folder in [OUTPUTS / "figures", OUTPUTS / "metrics", OUTPUTS / "predictions"]:
        folder.mkdir(parents=True, exist_ok=True)
    df = load_observations().dropna(subset=["count"]).copy()
    df = df.sort_values("datetime").reset_index(drop=True)
    X = df[FEATURE_COLUMNS].copy()
    y = df["count"].astype(float)

    # Primero miro cómo son los datos antes de intentar predecirlos.
    desc = df[["count", "temp", "atemp", "humidity", "windspeed"]].describe().T
    desc.to_csv(OUTPUTS / "metrics" / "estadistica_descriptiva.csv")
    work = df.loc[df.workingday == 1, "count"].to_numpy()
    nonwork = df.loc[df.workingday == 0, "count"].to_numpy()
    t_stat, p_value = stats.ttest_ind(work, nonwork, equal_var=False)
    diff = float(work.mean() - nonwork.mean())
    # Este intervalo compara dos grupos sin suponer que tienen igual variabilidad.
    se_diff = np.sqrt(work.var(ddof=1) / len(work) + nonwork.var(ddof=1) / len(nonwork))
    df_welch = (work.var(ddof=1) / len(work) + nonwork.var(ddof=1) / len(nonwork)) ** 2 / (
        (work.var(ddof=1) / len(work)) ** 2 / (len(work) - 1) +
        (nonwork.var(ddof=1) / len(nonwork)) ** 2 / (len(nonwork) - 1))
    ci_diff = [float(diff - stats.t.ppf(.975, df_welch) * se_diff),
               float(diff + stats.t.ppf(.975, df_welch) * se_diff)]
    inference = {
        "mean_demand_per_hour": float(y.mean()),
        "mean_demand_ci95_t": ci_mean(y),
        "working_day_mean": float(work.mean()), "non_working_day_mean": float(nonwork.mean()),
        "difference_work_minus_nonwork": diff, "difference_ci95_welch": ci_diff,
        "welch_t_statistic": float(t_stat), "welch_p_value": float(p_value),
        "interpretation": "Asociación en estos datos; no prueba que el calendario cause la demanda.",
    }
    (OUTPUTS / "metrics" / "inferencia.json").write_text(json.dumps(inference, indent=2, ensure_ascii=False), encoding="utf-8")

    # Guardo el 20% final como si fueran horas futuras que aún no conozco.
    split = int(len(df) * 0.80)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    # Cada ronda entrena con pasado y valida con el siguiente bloque de tiempo.
    cv = TimeSeriesSplit(n_splits=5)
    models = {
        "Regresión lineal": LinearRegression(),
        "Árbol de decisión": DecisionTreeRegressor(max_depth=18, min_samples_leaf=5, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=22, min_samples_leaf=3,
                                               n_jobs=-1, random_state=RANDOM_STATE),
    }
    rows = []
    fitted = {}
    # Comparo varios métodos manteniendo los mismos pasos de preparación.
    for name, estimator in models.items():
        pipe = Pipeline([("preprocess", make_preprocessor()), ("model", estimator)])
        cv_rmse = -cross_val_score(pipe, X_train, y_train, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=1)
        cv_r2 = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="r2", n_jobs=1)
        pipe.fit(X_train, y_train)
        pred = np.clip(pipe.predict(X_test), 0, None)
        fitted[name] = pipe
        rows.append({"modelo": name, "cv_rmse_promedio": float(cv_rmse.mean()),
                     "cv_rmse_std": float(cv_rmse.std(ddof=1)), "cv_r2_promedio": float(cv_r2.mean()),
                     "test_rmse": float(mean_squared_error(y_test, pred) ** .5),
                     "test_mae": float(mean_absolute_error(y_test, pred)),
                     "test_r2": float(r2_score(y_test, pred))})
    results = pd.DataFrame(rows).sort_values("cv_rmse_promedio").reset_index(drop=True)
    results.to_csv(OUTPUTS / "metrics" / "comparacion_modelos.csv", index=False)
    best_name = results.iloc[0].modelo
    best = fitted[best_name]
    joblib.dump(best, OUTPUTS / "metrics" / "mejor_modelo.joblib")

    pred_best = np.clip(best.predict(X_test), 0, None)
    nn_metrics = None
    nn_history = None
    # También pruebo una red neuronal, que aprende combinaciones de variables.
    # La validación interna ayuda a detener el entrenamiento antes de sobreajustar.
    try:
        import tensorflow as tf
        tf.keras.utils.set_random_seed(RANDOM_STATE)
        prep = make_preprocessor()
        n_fit = int(len(X_train) * .85)
        X_fit = prep.fit_transform(X_train.iloc[:n_fit]).astype("float32")
        X_val = prep.transform(X_train.iloc[n_fit:]).astype("float32")
        X_holdout = prep.transform(X_test).astype("float32")
        y_fit = y_train.iloc[:n_fit].to_numpy(dtype="float32")
        y_val = y_train.iloc[n_fit:].to_numpy(dtype="float32")
        y_holdout = y_test.to_numpy(dtype="float32")
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(X_fit.shape[1],)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dropout(.15),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(1),
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=.001), loss="mse", metrics=["mae"])
        early = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True)
        hist = model.fit(X_fit, y_fit, validation_data=(X_val, y_val), epochs=200, batch_size=128,
                         callbacks=[early], verbose=0)
        pred_nn = np.clip(model.predict(X_holdout, verbose=0).ravel(), 0, None)
        nn_metrics = {"modelo": "Red neuronal Keras", "test_rmse": float(mean_squared_error(y_holdout, pred_nn) ** .5),
                      "test_mae": float(mean_absolute_error(y_holdout, pred_nn)), "test_r2": float(r2_score(y_holdout, pred_nn)),
                      "epocas_entrenadas": len(hist.history["loss"]), "epoca_mejor_validacion": int(np.argmin(hist.history["val_loss"]) + 1)}
        nn_history = hist.history
        model.save(OUTPUTS / "metrics" / "red_neuronal.keras")
    except Exception as exc:
        pred_nn = np.full_like(pred_best, np.nan)
        nn_metrics = {"modelo": "Red neuronal Keras", "error": str(exc)}
    all_metrics = {"source_file": "hour.csv" if (RAW / "hour.csv").exists() else "train.csv",
                   "n_observations": int(len(df)), "n_train": int(len(X_train)), "n_test": int(len(X_test)),
                   "test_start": str(df.datetime.iloc[split]), "test_end": str(df.datetime.iloc[-1]),
                   "model_selection": "Menor RMSE medio en validación cruzada temporal de 5 pliegues",
                   "best_classical_model": str(best_name), "classical_models": rows,
                   "neural_network": nn_metrics, "inference": inference}
    (OUTPUTS / "metrics" / "resultados.json").write_text(json.dumps(all_metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    pred_df = pd.DataFrame({"datetime": df.datetime.iloc[split:].to_numpy(), "actual_demand": y_test.to_numpy(),
                            "predicted_classical": pred_best, "predicted_neural": pred_nn,
                            "model_classical": best_name})
    pred_df.to_csv(OUTPUTS / "predictions" / "holdout_predictions.csv", index=False)
    if nn_history:
        pd.DataFrame(nn_history).to_csv(OUTPUTS / "metrics" / "keras_history.csv", index=False)

    # Figuras para el reporte, tablero y exposición.
    sns.set_theme(style="whitegrid")
    hourly = df.groupby("hour", as_index=False)["count"].mean()
    plt.figure(figsize=(9, 4.6)); sns.lineplot(data=hourly, x="hour", y="count", marker="o", color="#177E89")
    plt.title("Demanda promedio por hora"); plt.xlabel("Hora del día"); plt.ylabel("Alquileres por hora (promedio)")
    plt.tight_layout(); plt.savefig(OUTPUTS / "figures" / "demanda_por_hora.png", dpi=160); plt.close()
    seasonal = df.groupby("season", as_index=False)["count"].mean()
    plt.figure(figsize=(7, 4.5)); sns.barplot(data=seasonal, x="season", y="count", color="#177E89")
    plt.title("Demanda promedio por temporada"); plt.xlabel("Temporada (1 a 4)"); plt.ylabel("Alquileres por hora (promedio)")
    plt.tight_layout(); plt.savefig(OUTPUTS / "figures" / "demanda_por_temporada.png", dpi=160); plt.close()
    plt.figure(figsize=(6, 6)); sns.scatterplot(x=y_test, y=pred_best, s=16, alpha=.45, color="#177E89")
    lim = max(float(y_test.max()), float(pred_best.max())); plt.plot([0, lim], [0, lim], "--", color="#E76F51")
    plt.title(f"Prueba final: observado vs. estimado ({best_name})"); plt.xlabel("Alquileres observados"); plt.ylabel("Alquileres estimados")
    plt.tight_layout(); plt.savefig(OUTPUTS / "figures" / "observado_vs_estimado.png", dpi=160); plt.close()
    if nn_history:
        plt.figure(figsize=(8, 4.5)); plt.plot(nn_history["loss"], label="Entrenamiento"); plt.plot(nn_history["val_loss"], label="Validación")
        plt.title("Red neuronal: pérdida durante el entrenamiento"); plt.xlabel("Época"); plt.ylabel("Error cuadrático medio"); plt.legend()
        plt.tight_layout(); plt.savefig(OUTPUTS / "figures" / "keras_early_stopping.png", dpi=160); plt.close()
    print(results.to_string(index=False))
    print("Mejor modelo clásico:", best_name)
    print("Red neuronal:", nn_metrics)
    print("Resultados guardados en outputs/metrics y outputs/predictions")
    return all_metrics


if __name__ == "__main__":
    main()

