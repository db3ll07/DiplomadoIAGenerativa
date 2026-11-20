"""Genera una presentación HTML autónoma para el proyecto de demanda.

Relación con el Diplomado: organiza en una presentación el análisis exploratorio,
la preparación de variables, la evaluación de modelos y una demostración de
predicción. Los datos y los parámetros entrenados se incrustan en el HTML para
que quien descargue el proyecto lo pueda abrir sin iniciar un servidor.

Uso desde la raíz del repositorio:
    python scripts/build_interactive_html.py

No descarga datos ni cambia los modelos. Lee observaciones.csv y los modelos
guardados, y solo crea presentacion/Proyecto_DemandaBicicletas_interactiva.html.
"""
from __future__ import annotations

import base64
import gzip
import json
import struct
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

from common import ROOT, FEATURE_COLUMNS, load_observations
from train_models import make_preprocessor


def compact_base64(data: bytes) -> str:
    """Comprime datos JSON y los vuelve texto para guardarlos dentro del HTML."""
    return base64.b64encode(gzip.compress(data, compresslevel=9, mtime=0)).decode("ascii")


def model_bundle() -> dict:
    """Convierte los dos modelos guardados a arreglos que puede leer JavaScript."""
    rf = joblib.load(ROOT / "outputs" / "metrics" / "mejor_modelo.joblib")
    prep = rf.named_steps["preprocess"]
    forest = rf.named_steps["model"]
    num = prep.named_transformers_["numeric"]
    cat = prep.named_transformers_["categorical"]
    scaler = num.named_steps["scale"]
    rf_pre = {
        "numeric_medians": num.named_steps["impute"].statistics_.tolist(),
        "means": scaler.mean_.tolist(), "scales": scaler.scale_.tolist(),
        "categories": [arr.tolist() for arr in cat.named_steps["onehot"].categories_],
        "cat_medians": cat.named_steps["impute"].statistics_.tolist(),
    }
    trees = []
    for estimator in forest.estimators_:
        tr = estimator.tree_
        # Registro por nodo: hijo izq, hijo der, índice variable, umbral y valor.
        records = bytearray()
        for i in range(tr.node_count):
            records += struct.pack("<iii dd", int(tr.children_left[i]), int(tr.children_right[i]),
                                   int(tr.feature[i]), float(tr.threshold[i]), float(tr.value[i, 0, 0]))
        trees.append(base64.b64encode(gzip.compress(records, compresslevel=9, mtime=0)).decode("ascii"))

    # La red se preparó con el primer 85 % del bloque de entrenamiento temporal.
    df = load_observations().dropna(subset=["count"]).sort_values("datetime").reset_index(drop=True)
    X = df[FEATURE_COLUMNS]
    n_train = int(len(df) * .80)
    n_fit = int(n_train * .85)
    nn_prep = make_preprocessor()
    nn_prep.fit(X.iloc[:n_fit])
    nnum = nn_prep.named_transformers_["numeric"]
    ncat = nn_prep.named_transformers_["categorical"]
    nn_scaler = nnum.named_steps["scale"]
    nn_pre = {
        "numeric_medians": nnum.named_steps["impute"].statistics_.tolist(),
        "means": nn_scaler.mean_.tolist(), "scales": nn_scaler.scale_.tolist(),
        "categories": [arr.tolist() for arr in ncat.named_steps["onehot"].categories_],
        "cat_medians": ncat.named_steps["impute"].statistics_.tolist(),
    }
    nn = tf.keras.models.load_model(ROOT / "outputs" / "metrics" / "red_neuronal.keras", compile=False)
    dense = []
    for layer in nn.layers:
        weights = layer.get_weights()
        if weights:
            kernel, bias = weights
            dense.append({"rows": kernel.shape[0], "cols": kernel.shape[1],
                          "w": base64.b64encode(gzip.compress(np.asarray(kernel, dtype="<f4").tobytes(), 9, mtime=0)).decode("ascii"),
                          "b": base64.b64encode(gzip.compress(np.asarray(bias, dtype="<f4").tobytes(), 9, mtime=0)).decode("ascii")})
    return {"rf": {"prep": rf_pre, "trees": trees}, "nn": {"prep": nn_pre, "layers": dense}}


HTML = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Demanda de bicicletas | Presentación interactiva</title>
<style>
:root{--ink:#202332;--muted:#687083;--paper:#faf9f6;--card:#fff;--coral:#e94b4f;--purple:#5865ad;--teal:#177e89;--line:#e4e4e8;--soft:#f1f0ed}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif}button,input,select{font:inherit}.top{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 4vw;border-bottom:1px solid var(--line);background:#fff}.brand{font-weight:800;letter-spacing:.02em}.brand b{color:var(--coral)}.progress{display:flex;gap:7px}.dot{width:9px;height:9px;border:0;border-radius:10px;background:#d2d3d9;cursor:pointer;padding:0}.dot.on{background:var(--coral);width:24px}.deck{min-height:calc(100vh - 128px);padding:4vh 5vw 3vh;max-width:1500px;margin:auto}.slide{display:none;animation:up .25s ease}.slide.active{display:block}@keyframes up{from{opacity:.4;transform:translateY(7px)}to{opacity:1;transform:none}}.eyebrow{color:var(--coral);font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.15em;margin:0 0 14px}h1{font-size:clamp(2.7rem,6vw,5.8rem);line-height:.98;max-width:950px;margin:0 0 24px;letter-spacing:-.055em}h2{font-size:clamp(2rem,4vw,3.5rem);letter-spacing:-.04em;margin:0 0 12px}h3{margin:0 0 10px}.lede{font-size:clamp(1.05rem,1.6vw,1.4rem);line-height:1.55;color:var(--muted);max-width:800px}.hero{padding-top:9vh}.hero .stamp{display:inline-block;background:#ffe8e4;color:#a82b36;padding:9px 14px;border-radius:20px;font-weight:700;margin-top:30px}.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;margin-top:26px}.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 5px 22px #2222}.span4{grid-column:span 4}.span5{grid-column:span 5}.span6{grid-column:span 6}.span7{grid-column:span 7}.span8{grid-column:span 8}.span12{grid-column:span 12}.metric{font-size:2.5rem;font-weight:850;letter-spacing:-.05em}.small{font-size:.9rem;color:var(--muted);line-height:1.5}.pill{display:inline-block;background:#f0edff;color:#4d4a94;border-radius:99px;padding:7px 12px;font-size:.82rem;font-weight:700}.controls{display:grid;gap:13px}.field label{display:flex;justify-content:space-between;font-size:.87rem;font-weight:700;margin-bottom:7px}.field output{color:var(--purple)}input[type=range]{width:100%;accent-color:var(--purple)}select,input[type=date]{border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;color:var(--ink);width:100%}.seg{display:flex;gap:7px;flex-wrap:wrap}.seg button{border:1px solid var(--line);background:#fff;border-radius:20px;padding:8px 13px;cursor:pointer;color:var(--muted)}.seg button.selected{background:var(--purple);color:white;border-color:var(--purple)}canvas{width:100%;height:310px;display:block}.plot-label{font-size:.86rem;color:var(--muted)}.callout{border-left:4px solid var(--coral);padding:4px 0 4px 15px;line-height:1.55}.result{font-size:2.4rem;font-weight:850;color:var(--purple)}.table{width:100%;border-collapse:collapse;font-size:.92rem}.table td,.table th{padding:11px;border-bottom:1px solid var(--line);text-align:left}.table th{color:var(--muted)}.bottom{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 4vw;background:white;border-top:1px solid var(--line)}.nav{display:flex;gap:8px}.nav button{border:1px solid var(--line);border-radius:11px;padding:10px 16px;background:#fff;cursor:pointer;font-weight:700}.nav button.primary{background:var(--ink);color:#fff}.note{font-size:.78rem;color:var(--muted)}@media(max-width:800px){.grid{grid-template-columns:1fr}.span4,.span5,.span6,.span7,.span8,.span12{grid-column:1}.deck{padding:30px 20px}.top{padding:0 18px}.bottom{padding:0 18px}.hide-mobile{display:none}canvas{height:250px}}
</style></head><body>
<header class="top"><div class="brand"><b>●</b> DEMANDA / BICICLETAS</div><div class="progress" id="progress"></div><div class="small hide-mobile">Proyecto de análisis predictivo</div></header>
<main class="deck">
<section class="slide active"><div class="hero"><p class="eyebrow">Proyecto final · análisis de datos y aprendizaje automático</p><h1>¿Cuántas bicicletas se alquilarán?</h1><p class="lede">Exploramos los patrones horarios del sistema de bicicletas compartidas de Washington, D. C. y probamos modelos para estimar la demanda de cada hora.</p><span class="stamp">Datos horarios · 2011–2012 · 17,379 registros</span><div class="grid"><div class="card span4"><span class="pill">Pregunta</span><p>¿Qué condiciones se relacionan con una mayor demanda por hora?</p></div><div class="card span4"><span class="pill">Objetivo</span><p>Predecir el total de alquileres de bicicletas (variable <b>count</b>).</p></div><div class="card span4"><span class="pill">Método</span><p>Exploración, preparación de variables y comparación de regresores.</p></div></div></div></section>
<section class="slide"><p class="eyebrow">01 · Decisión de negocio</p><h2>Preparar la disponibilidad por hora</h2><p class="lede">Una estimación de la demanda puede apoyar la redistribución de bicicletas y la planeación de capacidad. El modelo es un apoyo para decidir, no una garantía del número real.</p><div class="grid"><div class="card span6"><h3>La pregunta predictiva</h3><p>Con fecha, hora, clima y tipo de día como contexto, ¿cuál es el número esperado de alquileres?</p><p class="small">Tipo de problema: regresión. La respuesta es numérica y no una categoría.</p></div><div class="card span6"><h3>Uso responsable</h3><p class="callout">Las predicciones deben contrastarse con datos recientes y con el conocimiento operativo de cada estación.</p><p class="small">Asociación estadística no equivale a causalidad.</p></div></div></section>
<section class="slide"><p class="eyebrow">02 · Datos y preparación</p><h2>Una fila representa una hora</h2><p class="lede">El conjunto público de alquileres incluye calendario, clima y cantidad de bicicletas rentadas. Ordenamos por fecha y derivamos hora, día de semana, mes y año.</p><div class="grid"><div class="card span4"><div class="metric">17,379</div><div class="small">observaciones horarias</div></div><div class="card span4"><div class="metric">12</div><div class="small">variables predictoras consideradas</div></div><div class="card span4"><div class="metric">count</div><div class="small">objetivo: alquileres en esa hora</div></div><div class="card span12"><h3>Preparación explicada</h3><p>Las columnas numéricas (temperatura, sensación térmica, humedad y viento) se completan con la mediana y se escalan. Las columnas categóricas se completan con la categoría más frecuente y se convierten a indicadores (one-hot). Se excluyen <b>casual</b> y <b>registered</b> porque suman directamente el objetivo y causarían fuga de información.</p></div></div></section>
<section class="slide"><p class="eyebrow">03 · Exploración interactiva</p><h2>La demanda cambia durante el día</h2><p class="lede">Filtra las observaciones y compara la media de alquileres por hora o por temporada. Los datos se encuentran dentro de esta presentación.</p><div class="grid"><div class="card span4"><div class="controls"><div class="field"><label>Vista</label><div class="seg" id="chartMode"><button class="selected" data-mode="hour">Por Hora</button><button data-mode="season">Por Temporada</button></div></div><div class="field"><label>Año</label><select id="fYear"><option value="all">Todos</option><option>2011</option><option>2012</option></select></div><div class="field"><label>Temporada</label><select id="fSeason"><option value="all">Todas</option><option value="1">Invierno</option><option value="2">Primavera</option><option value="3">Verano</option><option value="4">Otoño</option></select></div><div class="field"><label>Tipo de día</label><select id="fWork"><option value="all">Todos</option><option value="1">Laborable</option><option value="0">No laborable</option></select></div><div class="field"><label>Clima</label><select id="fWeather"><option value="all">Todos</option><option value="1">Despejado</option><option value="2">Nublado</option><option value="3">Lluvia ligera</option></select></div></div></div><div class="card span8"><div class="plot-label" id="chartCaption">Media de alquileres registrados</div><canvas id="eda" aria-label="Gráfica de demanda"></canvas><p class="small" id="chartStatus"></p></div></div></section>
<section class="slide"><p class="eyebrow">04 · Comparación de modelos</p><h2>Evaluar con horas futuras</h2><p class="lede">Separamos cronológicamente: las últimas horas quedan para la evaluación final. La validación cruzada temporal compara modelos sin mezclar el pasado con el futuro.</p><div class="grid"><div class="card span7"><table class="table"><thead><tr><th>Modelo</th><th>RMSE prueba</th><th>MAE prueba</th><th>R²</th></tr></thead><tbody id="metricRows"></tbody></table><p class="small">RMSE y MAE se expresan en bicicletas por hora: más bajo es mejor. R² resume el ajuste, más alto suele ser mejor.</p></div><div class="card span5"><span class="pill">Mejor clásico por CV temporal</span><div class="metric" style="margin-top:18px">Random Forest</div><p class="small">RMSE medio temporal: 93.46. En la prueba final: RMSE 88.71, MAE 59.74 y R² 0.838.</p><div class="callout">Una red neuronal obtuvo RMSE 74.74 y MAE 53.16 en la misma prueba final, pero no participó en la misma validación cruzada de 5 pliegues. La comparación debe leerse con esa diferencia de procedimiento.</div></div></div></section>
<section class="slide"><p class="eyebrow">05 · Red neuronal sencilla</p><h2>Aprender combinaciones de variables</h2><p class="lede">La red conecta las variables transformadas con capas densas. La función ReLU permite representar relaciones no lineales. El entrenamiento usa una validación interna para decidir cuándo detenerse.</p><div class="grid"><div class="card span6"><h3>Arquitectura</h3><p>Entrada preparada → 64 neuronas ReLU → Dropout 0.15 → 32 neuronas ReLU → salida numérica.</p><p class="small">Pérdida: error cuadrático medio. Optimizador: Adam. Early stopping: detiene el entrenamiento si la pérdida de validación deja de mejorar.</p></div><div class="card span6"><h3>Resultado de prueba</h3><div class="metric">RMSE 74.74</div><p>MAE 53.16 alquileres por hora · R² 0.885 · mejor época 133.</p><p class="small">La red se entrenó con el bloque inicial y se evaluó en el 20 % cronológicamente posterior. El desempeño puede cambiar con otros periodos.</p></div></div></section>
<section class="slide"><p class="eyebrow">06 · Interpretación y límites</p><h2>Una predicción no explica por sí sola el fenómeno</h2><div class="grid"><div class="card span6"><h3>Lo que aprendimos</h3><p>El patrón por hora y las variables de calendario ayudan a describir la demanda. La temperatura, la hora y el tipo de día ofrecen señales útiles para el modelo.</p><p class="small">En estos registros la media fue 189.46 alquileres por hora (IC 95 %: 186.77–192.16).</p></div><div class="card span6"><h3>Lo que hay que cuidar</h3><ul><li>Son datos históricos de una ciudad y periodo concreto.</li><li>La media puede ocultar diferencias entre estaciones.</li><li>La asociación con clima o calendario no demuestra causalidad.</li><li>Para uso real se necesita monitoreo y actualización periódica.</li></ul></div><div class="card span12"><p class="callout">Siguiente paso razonable: probar la estimación con datos recientes por estación, medir el error operativo y decidir umbrales con el equipo que redistribuye bicicletas.</p></div></div></section>
<section class="slide"><p class="eyebrow">07 · Laboratorio en vivo</p><h2>Prueba un escenario</h2><p class="lede">Cambia los controles y calcula la demanda estimada. Los dos modelos ejecutan localmente dentro de este HTML: no hay servidor, API ni archivos externos que descargar.</p><div class="grid"><div class="card span5"><div class="controls"><div class="field"><label>Fecha</label><input id="date" type="date" min="2011-01-01" max="2012-12-31" value="2012-06-15"></div><div class="field"><label>Hora <output id="hourOut">8:00</output></label><input id="hour" type="range" min="0" max="23" value="8"></div><div class="field"><label>Temperatura °C <output id="tempOut">20</output></label><input id="temp" type="range" min="0" max="41" value="20"></div><div class="field"><label>Sensación térmica °C <output id="atempOut">23</output></label><input id="atemp" type="range" min="0" max="50" value="23"></div><div class="field"><label>Humedad % <output id="humOut">60</output></label><input id="hum" type="range" min="0" max="100" value="60"></div><div class="field"><label>Viento km/h <output id="windOut">13</output></label><input id="wind" type="range" min="0" max="67" value="13"></div><div class="field"><label>Temporada</label><select id="season"><option value="1">Invierno</option><option value="2">Primavera</option><option value="3" selected>Verano</option><option value="4">Otoño</option></select></div><div class="field"><label>Clima</label><select id="weather"><option value="1">Despejado / parcialmente nublado</option><option value="2" selected>Nublado / niebla</option><option value="3">Lluvia ligera</option><option value="4">Lluvia intensa / nieve</option></select></div><div class="field"><label>Día laborable</label><div class="seg" id="workBtns"><button class="selected" data-value="1">Sí</button><button data-value="0">No</button></div></div></div></div><div class="card span7"><span class="pill">Estimación · bicicletas por hora</span><div class="grid"><div class="card span6"><div class="small">Random Forest</div><div id="rfResult" class="result">—</div></div><div class="card span6"><div class="small">Red neuronal</div><div id="nnResult" class="result">—</div></div></div><p id="scenario" class="small"></p><div class="callout">La salida es una estimación promedio del modelo con datos históricos. No es una promesa de disponibilidad ni incluye eventos que no estén en las variables de entrada.</div><p class="small" id="modelState">Cargando los modelos incluidos…</p></div></div></section>
</main><footer class="bottom"><div class="note" id="counter">01 / 08 · Usa ← y → para avanzar</div><div class="nav"><button id="prev">← Anterior</button><button class="primary" id="next">Siguiente →</button></div></footer>
<script id="embedded-data" type="application/octet-stream">__DATA__</script><script id="embedded-models" type="application/octet-stream">__MODELS__</script>
<script>
(()=>{'use strict';const slides=[...document.querySelectorAll('.slide')],progress=document.getElementById('progress');let page=0;slides.forEach((_,i)=>{const b=document.createElement('button');b.className='dot'+(!i?' on':'');b.title='Diapositiva '+(i+1);b.onclick=()=>show(i);progress.appendChild(b)});function show(i){page=Math.max(0,Math.min(slides.length-1,i));slides.forEach((s,j)=>s.classList.toggle('active',j===page));[...progress.children].forEach((b,j)=>b.classList.toggle('on',j===page));document.getElementById('counter').textContent=String(page+1).padStart(2,'0')+' / 08 · Usa ← y → para avanzar';document.getElementById('prev').disabled=page===0;document.getElementById('next').textContent=page===7?'Finalizar':'Siguiente →';if(page===3)drawChart();}document.getElementById('prev').onclick=()=>show(page-1);document.getElementById('next').onclick=()=>show(page===7?0:page+1);document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')show(page+1);if(e.key==='ArrowLeft')show(page-1)});
let chartMode='hour';document.querySelectorAll('#chartMode button').forEach(b=>b.onclick=()=>{chartMode=b.dataset.mode;document.querySelectorAll('#chartMode button').forEach(x=>x.classList.toggle('selected',x===b));drawChart()});['fYear','fSeason','fWork','fWeather'].forEach(id=>document.getElementById(id).onchange=drawChart);
let data,models;function decodeGzip64(s){const raw=Uint8Array.from(atob(s),c=>c.charCodeAt(0));return new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer()}async function jsonBlob(id){return JSON.parse(new TextDecoder().decode(await decodeGzip64(document.getElementById(id).textContent.trim())))}
function drawChart(){if(!data)return;const cv=document.getElementById('eda'),ctx=cv.getContext('2d'),rect=cv.getBoundingClientRect(),dpr=window.devicePixelRatio||1;cv.width=rect.width*dpr;cv.height=rect.height*dpr;ctx.scale(dpr,dpr);const year=document.getElementById('fYear').value,season=document.getElementById('fSeason').value,work=document.getElementById('fWork').value,weather=document.getElementById('fWeather').value;let rows=data.filter(r=>(year==='all'||r.y==+year)&&(season==='all'||r.s==+season)&&(work==='all'||r.w==+work)&&(weather==='all'||r.c==+weather));let n=chartMode==='hour'?24:4,vals=Array.from({length:n},()=>[0,0]);rows.forEach(r=>{const k=chartMode==='hour'?r.h:r.s-1;vals[k][0]+=r.v;vals[k][1]+=r.n});const means=vals.map(v=>v[1]?v[0]/v[1]:null);const valid=means.filter(v=>v!==null);ctx.clearRect(0,0,rect.width,rect.height);if(!valid.length){document.getElementById('chartStatus').textContent='No hay observaciones para esta combinación de filtros. Prueba otra selección.';return}const W=rect.width,H=rect.height,L=42,R=12,T=16,B=35,max=Math.ceil(Math.max(...valid)*1.12/50)*50;ctx.font='12px Segoe UI';ctx.strokeStyle='#e4e4e8';ctx.fillStyle='#687083';for(let j=0;j<=4;j++){let y=T+(H-T-B)*j/4;ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(W-R,y);ctx.stroke();ctx.fillText(Math.round(max*(1-j/4)),3,y+4)}const pts=[];means.forEach((v,i)=>{if(v!==null)pts.push([L+(W-L-R)*i/(n-1),T+(H-T-B)*(1-v/max),i,v])});ctx.strokeStyle='#177e89';ctx.lineWidth=3;ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.stroke();pts.forEach(p=>{ctx.beginPath();ctx.fillStyle='#e94b4f';ctx.arc(p[0],p[1],3.5,0,Math.PI*2);ctx.fill()});let labels=chartMode==='hour'?['0','4','8','12','16','20','23']:['Invierno','Primavera','Verano','Otoño'];(chartMode==='hour'?[0,4,8,12,16,20,23]:[0,1,2,3]).forEach(i=>{const x=L+(W-L-R)*i/(n-1);ctx.fillStyle='#687083';ctx.fillText(labels[chartMode==='hour'?(i===23?6:i/4):i],x-10,H-8)});document.getElementById('chartStatus').textContent=`${rows.reduce((a,r)=>a+r.n,0).toLocaleString('es-MX')} observaciones; se muestran medias por ${chartMode==='hour'?'hora del día':'temporada'}.`;document.getElementById('chartCaption').textContent=`Media de alquileres · ${chartMode==='hour'?'por hora':'por temporada'}`}
const catIds=['season','holiday','workingday','weather','hour','dayofweek','month','year'];function features(input,prep){const nums=[input.temp,input.atemp,input.humidity,input.windspeed],out=[];nums.forEach((v,i)=>out.push(Math.fround((v-prep.numeric_medians[i]-0)/prep.scales[i]+(prep.numeric_medians[i]-prep.means[i])/prep.scales[i])));catIds.forEach((key,i)=>{const v=input[key]??prep.cat_medians[i],cats=prep.categories[i];cats.forEach(c=>out.push(c===v?1:0))});return out}async function inflateF32(b64){const b=await decodeGzip64(b64);return new Float32Array(b)}async function inflateTree(b64){const b=await decodeGzip64(b64),v=new DataView(b),l=b.byteLength/28,left=new Int32Array(l),right=new Int32Array(l),feat=new Int32Array(l),thr=new Float64Array(l),value=new Float64Array(l);for(let i=0;i<l;i++){let o=i*28;left[i]=v.getInt32(o,true);right[i]=v.getInt32(o+4,true);feat[i]=v.getInt32(o+8,true);thr[i]=v.getFloat64(o+12,true);value[i]=v.getFloat64(o+20,true)}return{left,right,feat,thr,value}}let rfTrees=[],nnLayers=[];function predictRF(x){let total=0;for(const t of rfTrees){let i=0,guard=0;while(t.left[i]>=0&&guard++<100){i=x[t.feat[i]]<=t.thr[i]?t.left[i]:t.right[i]}total+=t.value[i]}return Math.max(0,total/rfTrees.length)}function predictNN(x){let a=x;for(let k=0;k<nnLayers.length;k++){const L=nnLayers[k],z=new Float32Array(L.cols);for(let j=0;j<L.cols;j++){let v=L.b[j];for(let i=0;i<L.rows;i++)v+=a[i]*L.w[i*L.cols+j];z[j]=k<nnLayers.length-1?Math.max(0,v):v}a=z}return Math.max(0,a[0])}
function scenario(){const date=document.getElementById('date').value||'2012-06-15',d=new Date(date+'T12:00:00'),hour=+document.getElementById('hour').value,inp={season:+document.getElementById('season').value,holiday:0,workingday:+document.querySelector('#workBtns .selected').dataset.value,weather:+document.getElementById('weather').value,temp:+document.getElementById('temp').value,atemp:+document.getElementById('atemp').value,humidity:+document.getElementById('hum').value,windspeed:+document.getElementById('wind').value,hour,dayofweek:(d.getDay()+6)%7,month:d.getMonth()+1,year:d.getFullYear()};const x1=features(inp,models.rf.prep),x2=features(inp,models.nn.prep);document.getElementById('rfResult').textContent=Math.round(predictRF(x1)).toLocaleString('es-MX');document.getElementById('nnResult').textContent=Math.round(predictNN(x2)).toLocaleString('es-MX');document.getElementById('scenario').textContent=`Escenario: ${date}, ${hour}:00 · temperatura ${inp.temp} °C · humedad ${inp.humidity} % · ${inp.workingday?'día laborable':'día no laborable'}.`}
function wireRange(id,out,format){const el=document.getElementById(id),o=document.getElementById(out);const update=()=>{o.value=format(+el.value);if(models)scenario()};el.oninput=update;update()}wireRange('hour','hourOut',v=>v+':00');wireRange('temp','tempOut',v=>v+' °C');wireRange('atemp','atempOut',v=>v+' °C');wireRange('hum','humOut',v=>v+' %');wireRange('wind','windOut',v=>v+' km/h');document.querySelectorAll('#workBtns button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#workBtns button').forEach(x=>x.classList.toggle('selected',x===b));if(models)scenario()});['date','season','weather'].forEach(id=>document.getElementById(id).onchange=()=>models&&scenario());window.onresize=()=>page===3&&drawChart();
Promise.all([jsonBlob('embedded-data'),jsonBlob('embedded-models')]).then(async([d,m])=>{data=d;models=m;rfTrees=await Promise.all(m.rf.trees.map(inflateTree));nnLayers=await Promise.all(m.nn.layers.map(async l=>({rows:l.rows,cols:l.cols,w:await inflateF32(l.w),b:await inflateF32(l.b)})));document.getElementById('modelState').textContent='Modelos listos. El cálculo y los datos permanecen en este archivo.';drawChart();scenario()}).catch(e=>{document.getElementById('modelState').textContent='No se pudieron preparar los modelos incluidos: '+e.message});
const rawMetrics=__METRICS__;document.getElementById('metricRows').innerHTML=rawMetrics.map(x=>`<tr><td>${x.modelo}</td><td>${(+x.test_rmse).toFixed(2)}</td><td>${(+x.test_mae).toFixed(2)}</td><td>${(+x.test_r2).toFixed(3)}</td></tr>`).join('');
})();
</script></body></html>'''


def main() -> None:
    """Ensambla el HTML, incrustando agregados y modelos como datos locales."""
    df = load_observations().dropna(subset=["count"])
    # Cada registro del gráfico agrupa año, temporada, jornada, clima y hora.
    agg = (df.groupby(["year", "season", "workingday", "weather", "hour"], as_index=False)
           ["count"].agg(["sum", "count"]).reset_index())
    agg = agg.rename(columns={"year": "y", "season": "s", "workingday": "w", "weather": "c",
                              "hour": "h", "sum": "v", "count": "n"})
    data = [{"y": int(r.y), "s": int(r.s), "w": int(r.w), "c": int(r.c), "h": int(r.h),
             "v": float(r.v / r.n), "n": int(r.n)} for r in agg.itertuples()]
    # La gráfica recalcula el promedio ponderado: guardamos el total real en v.
    for item, row in zip(data, agg.itertuples()):
        item["v"] = float(row.v)
    metrics = pd.read_csv(ROOT / "outputs" / "metrics" / "comparacion_modelos.csv").to_dict("records")
    data_blob = compact_base64(json.dumps(data, separators=(",", ":")).encode("utf-8"))
    model_blob = compact_base64(json.dumps(model_bundle(), separators=(",", ":")).encode("utf-8"))
    html = HTML.replace("__DATA__", data_blob).replace("__MODELS__", model_blob)
    html = html.replace("__METRICS__", json.dumps(metrics, ensure_ascii=False, separators=(",", ":")))
    out = ROOT / "presentacion" / "Proyecto_DemandaBicicletas_interactiva.html"
    out.write_text(html, encoding="utf-8")
    print(f"Presentación creada: {out}")
    print(f"Tamaño: {out.stat().st_size / 1024 / 1024:.2f} MB; {len(data):,} grupos horario-filtro.")


if __name__ == "__main__":
    main()
