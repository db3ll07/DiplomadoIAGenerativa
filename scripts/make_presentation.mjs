/*
 * Crea una presentación editable para explicar el proyecto.
 *
 * Relación con el Diplomado: comunicación de proyectos de IA. Resume el
 * problema, los datos, el análisis, modelos, resultados, SQL/BI y el uso
 * responsable de IA generativa. Las notas de cada diapositiva sirven como guía
 * para explicar conceptos con palabras sencillas.
 *
 * Entrada: outputs/metrics/resultados.json, observaciones.csv y keras_history.csv.
 * Salida: presentacion/Proyecto_DemandaBicicletas.pptx.
 * Se ejecuta desde la raíz del repositorio con Node.js y Artifact Tool.
 */
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUT = path.join(ROOT, "outputs");
const BUILD = path.join(ROOT, ".build", "presentation-build");
const FINAL = path.join(ROOT, "presentacion", "Proyecto_DemandaBicicletas.pptx");
const NODE_MODULES = process.env.ARTIFACT_TOOL_NODE_MODULES || path.join(ROOT, "node_modules");
const ARTIFACT_MODULE = path.join(NODE_MODULES, "@oai", "artifact-tool", "dist", "artifact_tool.mjs");
const { Presentation, PresentationFile } = await import(pathToFileURL(ARTIFACT_MODULE).href);
const FONT = "Arial";
const C = { navy: "#12343B", teal: "#117C83", mint: "#DDEFEF", coral: "#E87552", paper: "#F5F8F7", ink: "#1B3137", mid: "#52666C", grid: "#D2DFE0", white: "#FFFFFF", pale: "#EAF1F1" };
const m = JSON.parse(await fs.readFile(path.join(OUT, "metrics", "resultados.json"), "utf8"));
const rows = m.classical_models;
const neural = m.neural_network;
const inference = m.inference;
const best = rows.find((r) => r.modelo === m.best_classical_model);

await fs.mkdir(BUILD, { recursive: true });
await fs.mkdir(path.dirname(FINAL), { recursive: true });

function addText(slide, text, pos, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox", position: pos, fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = { typeface: FONT, fontSize: 22, color: C.ink, ...style };
  shape.text.insets = 0;
  return shape;
}

function addSlide(title, subtitle = "") {
  const slide = pres.slides.add();
  slide.background.fill = C.paper;
  slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 1280, height: 16 }, fill: C.teal, line: { style: "solid", fill: C.teal, width: 0 } });
  addText(slide, title, { left: 72, top: 52, width: 1136, height: 58 }, { fontSize: 38, bold: true, color: C.navy });
  if (subtitle) addText(slide, subtitle, { left: 74, top: 112, width: 1110, height: 44 }, { fontSize: 19, color: C.mid });
  addText(slide, "Proyecto final · Demanda de bicicletas", { left: 72, top: 683, width: 820, height: 18 }, { fontSize: 11, color: C.mid });
  return slide;
}

function note(slide, text) { slide.speakerNotes.text = text; }

function addBulletLines(slide, lines, x = 92, y = 190, width = 1080, lineHeight = 68, fontSize = 24) {
  lines.forEach((line, idx) => {
    slide.shapes.add({ geometry: "ellipse", position: { left: x, top: y + idx * lineHeight + 12, width: 12, height: 12 }, fill: C.coral, line: { style: "solid", fill: C.coral, width: 0 } });
    addText(slide, line, { left: x + 28, top: y + idx * lineHeight, width: width - 28, height: lineHeight - 6 }, { fontSize, color: C.ink });
  });
}

const pres = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// 1. Portada
{
  const s = pres.slides.add(); s.background.fill = C.navy;
  s.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 22, height: 720 }, fill: C.coral, line: { style: "solid", fill: C.coral, width: 0 } });
  addText(s, "DEMANDA DE BICICLETAS", { left: 88, top: 145, width: 1060, height: 82 }, { fontSize: 52, bold: true, color: C.white });
  addText(s, "Pronóstico horario para apoyar la planeación operativa", { left: 90, top: 239, width: 980, height: 62 }, { fontSize: 30, color: C.mint });
  addText(s, "Proyecto final · Diplomado Liderazgo en la Era de la IA", { left: 92, top: 500, width: 900, height: 32 }, { fontSize: 20, color: C.white });
  addText(s, "Equipo por definir", { left: 92, top: 545, width: 500, height: 28 }, { fontSize: 17, color: "#B6CDD0" });
  note(s, "Apertura (45 segundos). Presentar la decisión: usar la demanda estimada para anticipar revisiones y redistribución. Aclarar desde el inicio que los datos son agregados por sistema.");
}

// 2. Decisión de negocio
{
  const s = addSlide("La decisión que queremos apoyar", "Una operación tiene que anticipar las horas concurridas para preparar los turnos de revisión y redistribución.");
  addBulletLines(s, [
    "¿Cuántos alquileres se esperan en cada hora?",
    "¿En qué horas conviene revisar la disponibilidad?",
    "¿Qué tan lejos queda el pronóstico de lo observado?",
  ], 96, 204, 1050, 86, 26);
  s.shapes.add({ geometry: "rect", position: { left: 100, top: 493, width: 1050, height: 92 }, fill: C.mint, line: { style: "solid", fill: C.mint, width: 0 } });
  addText(s, "El modelo orienta la planeación. No decide cuántas bicicletas mover ni a qué estación.", { left: 126, top: 517, width: 1000, height: 48 }, { fontSize: 22, bold: true, color: C.navy });
  note(s, "Tiempo: 1 minuto. La rúbrica pide una decisión recurrente y un destinatario. Aquí la decisión es horaria y el destinatario es el responsable de operación. No hay datos de costos, así que el costo del error se describe sin inventar cifras.");
}

// 3. Datos y objetivo
{
  const s = addSlide("Datos históricos de alquileres", "UCI Bike Sharing Dataset · Washington D. C. · enero de 2011 a diciembre de 2012");
  const stats = [
    ["17,379", "horas"], ["12", "predictores"], ["2 años", "periodo"], ["1", "sistema agregado"],
  ];
  stats.forEach(([big, small], i) => {
    const x = 78 + i * 287;
    addText(s, big, { left: x, top: 205, width: 250, height: 58 }, { fontSize: 39, bold: true, color: C.teal, alignment: "center" });
    addText(s, small, { left: x, top: 265, width: 250, height: 28 }, { fontSize: 18, color: C.mid, alignment: "center" });
  });
  addText(s, "Objetivo: alquileres totales por hora (count)", { left: 90, top: 338, width: 1050, height: 38 }, { fontSize: 26, bold: true, color: C.navy });
  addText(s, "Variables: hora, día, temporada, feriado, clima, temperatura, humedad y viento.", { left: 92, top: 386, width: 1070, height: 40 }, { fontSize: 22, color: C.ink });
  addText(s, "Se excluyen casual y registered: suman directamente count y filtrarían la respuesta hacia los predictores.", { left: 92, top: 459, width: 1075, height: 74 }, { fontSize: 20, color: C.coral, bold: true });
  addText(s, "Fuente: UCI Machine Learning Repository - datos horarios de Washington, D. C., 2011-2012.", { left: 92, top: 566, width: 1090, height: 42 }, { fontSize: 15, color: C.mid });
  note(s, "Tiempo: 1.5 minutos. La fuente es el Bike Sharing Dataset del UCI Machine Learning Repository. El corte de prueba principal es cronológico: reserva las últimas observaciones para evaluar el modelo con un periodo posterior.");
}

// 4. EDA
{
  const s = addSlide("La demanda cambia a lo largo del día", "El análisis exploratorio muestra picos de uso y diferencias por temporada.");
  const raw = (await fs.readFile(path.join(ROOT, "datos", "processed", "observations.csv"), "utf8")).trim().split(/\r?\n/);
  const header = raw[0].split(","); const index = Object.fromEntries(header.map((v, i) => [v, i]));
  const hourCount = Array(24).fill(0), hourSum = Array(24).fill(0), seasonCount = Array(4).fill(0), seasonSum = Array(4).fill(0);
  for (const line of raw.slice(1)) {
    const parts = line.split(","); const h = Number(parts[index.datetime].slice(11, 13)); const season = Number(parts[index.season]) - 1; const count = Number(parts[index.count]);
    if (Number.isFinite(h) && Number.isFinite(count)) { hourSum[h] += count; hourCount[h] += 1; }
    if (season >= 0 && season < 4 && Number.isFinite(count)) { seasonSum[season] += count; seasonCount[season] += 1; }
  }
  const hourly = hourSum.map((v, i) => Math.round(v / hourCount[i] * 10) / 10);
  const seasonal = seasonSum.map((v, i) => Math.round(v / seasonCount[i] * 10) / 10);
  const chart = s.charts.add("line", {
    position: { left: 80, top: 187, width: 720, height: 412 },
    title: "Alquileres promedio por hora", titleTextStyle: { typeface: FONT, fontSize: 18, bold: true, fill: C.navy },
    categories: Array.from({ length: 24 }, (_, i) => `${i}:00`),
    series: [{ name: "Alquileres por hora", values: hourly, line: { style: "solid", fill: C.teal, width: 3 }, marker: { symbol: "circle", size: 5, fill: C.teal } }],
    hasLegend: false, lineOptions: { smooth: false },
    xAxis: { textStyle: { typeface: FONT, fontSize: 11, fill: C.mid }, majorGridlines: null },
    yAxis: { title: { text: "Alquileres", textStyle: { typeface: FONT, fontSize: 12, fill: C.mid } }, textStyle: { typeface: FONT, fontSize: 12, fill: C.mid }, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
    chartFill: C.paper, plotAreaFill: C.paper,
  });
  addText(s, "Temporadas 1–4", { left: 850, top: 200, width: 330, height: 30 }, { fontSize: 17, bold: true, color: C.navy });
  seasonal.forEach((val, i) => {
    const y = 252 + i * 76;
    addText(s, `T${i + 1}`, { left: 850, top: y, width: 42, height: 28 }, { fontSize: 17, bold: true, color: C.mid });
    s.shapes.add({ geometry: "rect", position: { left: 898, top: y + 3, width: Math.max(16, val / Math.max(...seasonal) * 214), height: 19 }, fill: i === 2 ? C.coral : C.teal, line: { style: "solid", fill: "none", width: 0 } });
    addText(s, `${val.toFixed(0)}`, { left: 1123, top: y, width: 65, height: 26 }, { fontSize: 16, color: C.ink });
  });
  addText(s, `Promedio general: ${inference.mean_demand_per_hour.toFixed(1)} alquileres/hora`, { left: 840, top: 575, width: 340, height: 34 }, { fontSize: 17, bold: true, color: C.navy });
  note(s, "Tiempo: 2 minutos. Explicar que la demanda cambia por hora y temporada. Datos provenientes del archivo horario del UCI Machine Learning Repository. La gráfica es descriptiva, no causal.");
}

// 5. Inferencia estadística
{
  const s = addSlide("Diferencia observada entre días laborales y no laborales", "Prueba t de Welch e intervalo de confianza de 95% para la diferencia de medias.");
  const y1 = 235, barMax = 330, scale = barMax / Math.max(inference.working_day_mean, inference.non_working_day_mean);
  [["Día laboral", inference.working_day_mean, y1], ["No laboral", inference.non_working_day_mean, y1 + 112]].forEach(([label, value, y]) => {
    addText(s, label, { left: 94, top: y, width: 180, height: 34 }, { fontSize: 20, bold: true, color: C.navy });
    s.shapes.add({ geometry: "rect", position: { left: 294, top: y + 3, width: value * scale, height: 28 }, fill: C.teal, line: { style: "solid", fill: "none", width: 0 } });
    addText(s, `${value.toFixed(1)}`, { left: 642, top: y, width: 90, height: 32 }, { fontSize: 20, bold: true, color: C.ink });
  });
  addText(s, `Diferencia: ${inference.difference_work_minus_nonwork.toFixed(1)} alquileres/hora`, { left: 90, top: 420, width: 760, height: 40 }, { fontSize: 25, bold: true, color: C.navy });
  addText(s, `IC 95%: ${inference.difference_ci95_welch[0].toFixed(1)} a ${inference.difference_ci95_welch[1].toFixed(1)} · p = ${inference.welch_p_value.toExponential(2)}`, { left: 92, top: 470, width: 1050, height: 36 }, { fontSize: 19, color: C.ink });
  s.shapes.add({ geometry: "rect", position: { left: 90, top: 540, width: 1050, height: 62 }, fill: C.mint, line: { style: "solid", fill: C.mint, width: 0 } });
  addText(s, "La diferencia es asociativa en estos datos; no demuestra que el calendario cause más alquileres.", { left: 115, top: 557, width: 1000, height: 30 }, { fontSize: 18, color: C.navy });
  note(s, "Tiempo: 1.5 minutos. Reportar la prueba y el intervalo con interpretación correcta. La inferencia describe diferencia observada, no causalidad.");
}

// 6. Datos para SQL/BI
{
  const s = addSlide("SQL y Power BI preparan la decisión", "Una tabla de hechos por hora y tres dimensiones para filtrar la historia.");
  const center = { x: 465, y: 282, w: 345, h: 144 };
  s.shapes.add({ geometry: "rect", position: { left: center.x, top: center.y, width: center.w, height: center.h }, fill: C.navy, line: { style: "solid", fill: C.navy, width: 0 } });
  addText(s, "FactDemand\nfecha · hora · clima\nobservado · pronosticado", { left: center.x + 22, top: center.y + 25, width: center.w - 44, height: 100 }, { fontSize: 22, bold: true, color: C.white, alignment: "center" });
  const dims = [
    { x: 96, y: 205, title: "DimDate", text: "año · mes\ndía laboral" },
    { x: 838, y: 205, title: "DimHour", text: "hora\nfranja" },
    { x: 465, y: 488, title: "DimConditions", text: "clima · temperatura\nhumedad · viento" },
  ];
  dims.forEach((d) => {
    s.shapes.add({ geometry: "rect", position: { left: d.x, top: d.y, width: 345, height: 112 }, fill: C.mint, line: { style: "solid", fill: C.teal, width: 2 } });
    addText(s, d.title, { left: d.x + 18, top: d.y + 15, width: 309, height: 29 }, { fontSize: 20, bold: true, color: C.navy, alignment: "center" });
    addText(s, d.text, { left: d.x + 18, top: d.y + 48, width: 309, height: 48 }, { fontSize: 16, color: C.mid, alignment: "center" });
  });
  [[441,261,465,306],[810,261,838,306],[637,426,637,488]].forEach(([x1,y1,x2,y2]) => s.shapes.add({ geometry: "line", position: { left:x1, top:y1, width:x2-x1, height:y2-y1 }, line: { style:"solid", fill:C.teal, width:2 } }));
  addText(s, "Las consultas SQL agregan demanda por hora, mes y clima. DAX resume observado, pronosticado, error y sesgo.", { left: 92, top: 613, width: 1090, height: 45 }, { fontSize: 17, color: C.ink });
  note(s, "Tiempo: 2 minutos. Mostrar el esquema estrella y explicar relaciones uno-a-muchos desde cada dimensión. Las consultas y medidas DAX están en el repositorio.");
}

// 7. Modelos clásicos
{
  const s = addSlide("Tres modelos clásicos, con validación temporal", "Los pliegues avanzan en el tiempo; ningún pliegue valida con observaciones futuras respecto de su entrenamiento.");
  const chart = s.charts.add("bar", {
    position: { left: 74, top: 186, width: 690, height: 418 },
    title: "RMSE medio en 5 pliegues · menor es mejor", titleTextStyle: { typeface: FONT, fontSize: 18, bold: true, fill: C.navy },
    categories: rows.map((r) => r.modelo),
    series: [{ name: "RMSE", values: rows.map((r) => Number(r.cv_rmse_promedio.toFixed(1))), fill: C.teal }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 60 }, hasLegend: false,
    xAxis: { title: { text: "Error en alquileres/hora", textStyle: { typeface: FONT, fontSize: 12, fill: C.mid } }, textStyle: { typeface: FONT, fontSize: 12, fill: C.mid }, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
    yAxis: { textStyle: { typeface: FONT, fontSize: 15, fill: C.ink }, majorGridlines: null },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { typeface: FONT, fontSize: 13, bold: true, fill: C.navy } },
    chartFill: C.paper, plotAreaFill: C.paper,
  });
  addBulletLines(s, [
    "Regresión lineal: referencia sencilla",
    "Árbol: reglas fáciles de visualizar",
    "Random Forest: menor RMSE CV",
  ], 810, 229, 390, 83, 19);
  addText(s, `Mejor modelo clásico: ${m.best_classical_model}`, { left: 805, top: 514, width: 380, height: 55 }, { fontSize: 22, bold: true, color: C.teal });
  note(s, "Tiempo: 2 minutos. El conjunto de entrenamiento se evaluó con cinco ventanas temporales. Random Forest obtuvo RMSE promedio 93.5, con desviación entre pliegues 23.3. No se usó accuracy porque es una tarea de regresión.");
}

// 8. Resultados comunes de prueba
{
  const s = addSlide("Resultados en el último 20% cronológico", `Prueba reservada: ${m.test_start.slice(0,10)} a ${m.test_end.slice(0,10)} · mismos registros para cada modelo`);
  const values = rows.map((r) => [r.modelo, r.test_rmse, r.test_mae, r.test_r2]);
  values.push(["Red neuronal Keras", neural.test_rmse, neural.test_mae, neural.test_r2]);
  const tableData = [["Modelo", "RMSE ↓", "MAE ↓", "R² ↑"], ...values.map((r) => [r[0], Number(r[1]).toFixed(1), Number(r[2]).toFixed(1), Number(r[3]).toFixed(3)])];
  const table = s.tables.add({ rows: tableData.length, columns: 4, left: 90, top: 205, width: 760, height: 292, values: tableData });
  table.borders.assign({ style: "solid", fill: C.grid, width: 1 });
  for (let r = 0; r < tableData.length; r++) {
    for (let c = 0; c < 4; c++) {
      const cell = table.getCell(r, c);
      cell.fill = r === 0 ? C.navy : (r % 2 ? C.white : C.pale);
      cell.text.style = { typeface: FONT, fontSize: r === 0 ? 17 : 18, bold: r === 0 || (r === tableData.length - 1 && c === 0), color: r === 0 ? C.white : C.ink };
    }
  }
  addText(s, "Interpretación", { left: 900, top: 221, width: 280, height: 38 }, { fontSize: 25, bold: true, color: C.navy });
  addText(s, `Random Forest: RMSE ${best.test_rmse.toFixed(1)} y R² ${best.test_r2.toFixed(3)}.\n\nKeras: RMSE ${neural.test_rmse.toFixed(1)} y R² ${neural.test_r2.toFixed(3)}.`, { left: 900, top: 280, width: 290, height: 153 }, { fontSize: 19, color: C.ink });
  s.shapes.add({ geometry: "rect", position: { left: 895, top: 485, width: 300, height: 102 }, fill: C.mint, line: { style: "solid", fill: C.mint, width: 0 } });
  addText(s, "Keras mejora en esta prueba, pero no se incluyó en la misma CV de 5 pliegues.", { left: 916, top: 504, width: 258, height: 67 }, { fontSize: 17, bold: true, color: C.navy });
  note(s, "Tiempo: 2 minutos. Comparar RMSE, MAE y R² en la misma prueba final. Explicar con honestidad la diferencia del diseño: los modelos clásicos tienen CV temporal; la red tiene validación interna para early stopping y prueba final compartida. Para una conclusión más fuerte, incluir Keras en la misma CV temporal.");
}

// 9. Red neuronal
{
  const s = addSlide("La red neuronal se detuvo cuando dejó de mejorar", "Keras · capas densas 64–32 · ReLU · dropout 0.15 · parada temprana");
  const histPath = path.join(OUT, "metrics", "keras_history.csv");
  const hist = (await fs.readFile(histPath, "utf8")).trim().split(/\r?\n/).map((line) => line.split(","));
  const epochs = hist.slice(1).map((_, i) => String(i + 1));
  const train = hist.slice(1).map((r) => Number(r[0]));
  const val = hist.slice(1).map((r) => Number(r[1]));
  const chart = s.charts.add("line", {
    position: { left: 72, top: 183, width: 790, height: 400 },
    title: "Error cuadrático medio por época", titleTextStyle: { typeface: FONT, fontSize: 18, bold: true, fill: C.navy },
    categories: epochs, series: [
      { name: "Entrenamiento", values: train, line: { style: "solid", fill: C.teal, width: 2 } },
      { name: "Validación", values: val, line: { style: "solid", fill: C.coral, width: 2 } },
    ], hasLegend: true, legend: { position: "bottom", textStyle: { typeface: FONT, fontSize: 13, fill: C.mid } },
    xAxis: { title: { text: "Época", textStyle: { typeface: FONT, fontSize: 12, fill: C.mid } }, textStyle: { typeface: FONT, fontSize: 10, fill: C.mid }, majorGridlines: null },
    yAxis: { title: { text: "MSE", textStyle: { typeface: FONT, fontSize: 12, fill: C.mid } }, textStyle: { typeface: FONT, fontSize: 12, fill: C.mid }, majorGridlines: { style: "solid", fill: C.grid, width: 1 } },
    chartFill: C.paper, plotAreaFill: C.paper,
  });
  addText(s, `Mejor época de validación: ${neural.epoca_mejor_validacion}\nEntrenamiento detenido: ${neural.epocas_entrenadas} épocas\n\nLa prueba final queda fuera del ajuste de pesos.`, { left: 904, top: 260, width: 292, height: 160 }, { fontSize: 20, color: C.ink });
  note(s, "Tiempo: 1.5 minutos. La curva muestra la pérdida de entrenamiento y validación. EarlyStopping restaura los pesos de la mejor época y detiene el proceso cuando la validación deja de mejorar.");
}

// 10. IA generativa
{
  const s = addSlide("Un asistente transforma el pronóstico en una guía breve", "El agente consulta el modelo como herramienta y deja la decisión final a la operación.");
  const steps = [
    ["1", "Pronóstico", "Modelo recibe hora, fecha y clima"],
    ["2", "Herramienta", "Devuelve alquileres estimados"],
    ["3", "Prompt", "Resume sin inventar estaciones ni inventario"],
    ["4", "Revisión", "Persona decide si revisa o redistribuye"],
  ];
  steps.forEach(([n, title, body], i) => {
    const x = 74 + i * 300;
    s.shapes.add({ geometry: "ellipse", position: { left: x + 96, top: 196, width: 66, height: 66 }, fill: i === 3 ? C.coral : C.teal, line: { style: "solid", fill: "none", width: 0 } });
    addText(s, n, { left: x + 115, top: 211, width: 30, height: 34 }, { fontSize: 27, bold: true, color: C.white, alignment: "center" });
    addText(s, title, { left: x + 8, top: 286, width: 242, height: 33 }, { fontSize: 21, bold: true, color: C.navy, alignment: "center" });
    addText(s, body, { left: x + 6, top: 334, width: 248, height: 82 }, { fontSize: 17, color: C.ink, alignment: "center" });
    if (i < 3) addText(s, "→", { left: x + 253, top: 211, width: 39, height: 38 }, { fontSize: 29, bold: true, color: C.coral, alignment: "center" });
  });
  addText(s, "Ejemplo: “Se esperan alrededor de 420 alquileres a las 08:00. Conviene revisar disponibilidad antes del pico. El pronóstico no informa cuántas bicicletas hay en cada estación.”", { left: 98, top: 488, width: 1082, height: 83 }, { fontSize: 20, color: C.navy, bold: true });
  addText(s, "La llamada a un LLM requiere credenciales; el repositorio incluye prompt, herramienta y modo de demostración local.", { left: 100, top: 594, width: 1080, height: 34 }, { fontSize: 15, color: C.mid });
  note(s, "Tiempo: 2 minutos. Mostrar que la herramienta predict_hour_demand invoca el modelo serializado. El agente no hace inventario por estación, porque no existen esas variables. El servicio LLM requiere API key y selección del modelo por el usuario.");
}

// 11. Conclusión, límites y recomendación
{
  const s = addSlide("Recomendación para la operación", "Usar la predicción como señal de planeación y validar antes de desplegarla.");
  addBulletLines(s, [
    "Revisar turnos antes de los picos horarios detectados.",
    "Registrar demanda observada para medir error y sesgo con el tiempo.",
    "Probar con datos recientes antes de usarlo en otra ciudad.",
  ], 92, 190, 1090, 78, 23);
  s.shapes.add({ geometry: "rect", position: { left: 93, top: 485, width: 1090, height: 125 }, fill: C.navy, line: { style: "solid", fill: C.navy, width: 0 } });
  addText(s, "Límite principal", { left: 120, top: 506, width: 300, height: 34 }, { fontSize: 20, bold: true, color: C.mint });
  addText(s, "El dataset es histórico y agregado; no permite decidir qué bicicleta mover entre estaciones.", { left: 120, top: 548, width: 1010, height: 43 }, { fontSize: 22, bold: true, color: C.white });
  note(s, "Tiempo: 1.5 minutos. Recomendar piloto con observación humana y medición continua. Para una segunda versión hacen falta datos actuales y ubicación/inventario por estación.");
}

// 12. Referencias
{
  const s = addSlide("Referencias y fuentes", "Conjunto de datos y estudios consultados");
  const refs = [
    "UCI Machine Learning Repository (2013). Bike Sharing Dataset. archive.ics.uci.edu/dataset/275/bike+sharing+dataset",
    "Fanaee-T, H., & Gama, J. (2014). Progress in Artificial Intelligence, 2, 113–127. doi:10.1007/s13748-013-0040-3",
    "Nam, H., et al. (2024). International Journal of Urban Sciences, 28(4). doi:10.1080/12265934.2024.2317198",
    "Feng, J., Liu, H., Zhou, J., & Zhou, Y. (2024). ACM TKDD, 18(9), Article 232. doi:10.1145/3690388",
    "Chen, J., et al. (2022). Sensors, 22(3), 1060. doi:10.3390/s22031060",
  ];
  refs.forEach((r, i) => addText(s, r, { left: 92, top: 182 + i * 69, width: 1090, height: 56 }, { fontSize: 17, color: C.ink }));
  note(s, "Cierre (45 segundos). Referencias completas APA 7 en el artículo. Los datos analizados se obtuvieron del UCI Machine Learning Repository.");
}

const candidate = path.join(BUILD, "candidate.pptx");
await (await PresentationFile.exportPptx(pres)).save(candidate);
await fs.copyFile(candidate, FINAL);
console.log(JSON.stringify({ final: FINAL, slides: pres.slides.items.length }, null, 2));
