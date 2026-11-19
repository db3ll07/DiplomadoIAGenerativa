"""Demuestra un asistente que consulta el modelo antes de redactar una respuesta.

Relación con el Diplomado: IA generativa, diseño de instrucciones (prompt) y
uso de herramientas por un modelo de lenguaje. El modelo predictivo calcula
los alquileres aproximados; el LLM solo los explica. Si no hay credenciales,
el programa muestra un resumen fijo local para que se pueda explorar sin API.

Entrada: fecha/hora y condiciones escritas en el ejemplo al final del archivo.
Requisito: ejecutar antes scripts/train_models.py. Para LLM, definir
OPENAI_API_KEY y OPENAI_MODEL en el entorno. Desde la raíz:
python scripts/demand_agent.py
"""
from pathlib import Path
import json
import os
import urllib.request
import urllib.error
import pandas as pd
import joblib
from common import ROOT, OUTPUTS, FEATURE_COLUMNS

SYSTEM_PROMPT = (
    "Eres un asistente de planeación de bicicletas compartidas. Usa solo la fecha, hora, "
    "clima y predicción que recibes. Distingue estimación de certeza. No inventes estaciones, "
    "capacidades ni inventario. En tres frases: interpreta el pronóstico, sugiere una revisión "
    "operativa y declara una limitación."
)
TOOL_SPEC = [{
    "type": "function", "name": "predict_hour_demand",
    "description": "Predice el total de alquileres en una hora usando el modelo entrenado.",
    "parameters": {"type": "object", "properties": {
        "datetime": {"type": "string", "description": "Fecha y hora, por ejemplo 2012-07-10 08:00"},
        "season": {"type": "integer", "minimum": 1, "maximum": 4},
        "holiday": {"type": "integer", "minimum": 0, "maximum": 1},
        "workingday": {"type": "integer", "minimum": 0, "maximum": 1},
        "weather": {"type": "integer", "minimum": 1, "maximum": 4},
        "temp": {"type": "number"}, "atemp": {"type": "number"},
        "humidity": {"type": "number"}, "windspeed": {"type": "number"},
    }, "required": ["datetime", "season", "holiday", "workingday", "weather", "temp", "atemp", "humidity", "windspeed"],
       "additionalProperties": False}, "strict": True,
}]


def predict_hour_demand(arguments):
    """Usa el modelo guardado para calcular una estimación de una hora."""
    model_path = OUTPUTS / "metrics" / "mejor_modelo.joblib"
    if not model_path.exists():
        raise FileNotFoundError("Ejecuta primero python scripts/train_models.py")
    when = pd.Timestamp(arguments["datetime"])
    row = {key: arguments[key] for key in ["season", "holiday", "workingday", "weather", "temp", "atemp", "humidity", "windspeed"]}
    row.update(hour=when.hour, dayofweek=when.day_of_week, month=when.month, year=when.year)
    pred = float(joblib.load(model_path).predict(pd.DataFrame([row])[FEATURE_COLUMNS])[0])
    return {"datetime": when.isoformat(sep=" "), "estimated_rentals": round(max(0, pred), 1),
            "model": "mejor modelo clásico por validación temporal"}


def _local_summary(prediction):
    """Arma una explicación breve sin llamar a un modelo de lenguaje."""
    value = prediction["estimated_rentals"]
    when = prediction["datetime"]
    return (f"Para {when} se estiman alrededor de {value:,.0f} alquileres. "
            "La operación puede revisar la disponibilidad antes de esa hora y ajustar su plan con las condiciones actuales. "
            "El modelo predice demanda agregada histórica y no conoce el inventario ni la ubicación de las bicicletas.")


def _post_responses(payload, api_key):
    """Envía una solicitud a la API Responses y devuelve su JSON."""
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"La API de OpenAI respondió HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"No se pudo conectar con la API de OpenAI: {exc.reason}") from exc


def _response_text(response):
    """Extrae texto final tanto del atajo output_text como de output[].content[]."""
    text = (response.get("output_text") or "").strip()
    if text:
        return text
    parts = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                parts.append(content["text"])
    return "\n".join(parts).strip()


def generate_summary(arguments):
    """Pide un pronóstico y, si está configurado, se lo pasa al LLM."""
    prediction = predict_hour_demand(arguments)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model_name = os.environ.get("OPENAI_MODEL", "").strip()
    if not api_key and not model_name:
        return {"prediction": prediction, "summary": _local_summary(prediction),
                "mode": "demostración local; configura OPENAI_API_KEY y OPENAI_MODEL para usar el LLM"}
    if not api_key or not model_name:
        raise RuntimeError(
            "Para usar el LLM configura ambas variables: OPENAI_API_KEY y OPENAI_MODEL. "
            "Si quieres usar solo el modo local, elimina ambas de la sesión."
        )

    payload = {"model": model_name, "input": [
        {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": [{"type": "input_text", "text": "Prepara el resumen operativo para esta hora: " + json.dumps(arguments, ensure_ascii=False)}]},
    ], "tools": TOOL_SPEC, "tool_choice": "required"}
    response = _post_responses(payload, api_key)
    for _ in range(5):
        summary = _response_text(response)
        if summary:
            return {"prediction": prediction, "summary": summary,
                    "mode": f"OpenAI Responses API ({model_name}) + herramienta predict_hour_demand"}

        calls = [item for item in response.get("output", [])
                 if item.get("type") == "function_call"]
        if response.get("status") == "incomplete":
            details = response.get("incomplete_details") or {}
            raise RuntimeError(f"La respuesta de OpenAI quedó incompleta: {details}")
        if not calls:
            output_types = [item.get("type", "desconocido") for item in response.get("output", [])]
            raise RuntimeError(
                "La API respondió sin texto ni llamadas a herramientas. "
                f"Estado: {response.get('status', 'desconocido')}; elementos: {output_types}"
            )

        outputs = []
        for call in calls:
            if call.get("name") != "predict_hour_demand":
                raise RuntimeError(f"El modelo solicitó una herramienta no reconocida: {call.get('name')}")
            args = json.loads(call["arguments"])
            outputs.append({"type": "function_call_output", "call_id": call["call_id"],
                            "output": json.dumps(predict_hour_demand(args), ensure_ascii=False)})
        if not response.get("id"):
            raise RuntimeError("La respuesta de OpenAI no incluyó un ID para continuar el ciclo de herramientas.")
        followup = {"model": model_name, "previous_response_id": response["id"],
                    "input": outputs, "tools": TOOL_SPEC}
        response = _post_responses(followup, api_key)

    raise RuntimeError("El modelo no produjo un resumen después de cinco rondas de llamadas a herramientas.")


if __name__ == "__main__":
    example = {"datetime": "2012-07-10 08:00", "season": 3, "holiday": 0, "workingday": 1,
               "weather": 1, "temp": 28.0, "atemp": 31.0, "humidity": 62.0, "windspeed": 11.0}
    result = generate_summary(example)
    print(json.dumps(result, indent=2, ensure_ascii=False))

