import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';

const TMP='/Users/leonel/Desktop/TAD/tmp/presentation-simple-light';
const STARTER=`${TMP}/template-starter.pptx`;
const FINAL='/Users/leonel/Desktop/TAD/video/Presentacion_exposicion_proyecto_integrador_simple_light.pptx';
const MEDIA=`${TMP}/source-deck/template-inspect/assets/ppt/media`;
const FONT='Helvetica Neue';
const INK='#171615';
const TEXT='#2D2A27';
const MUTED='#6B645E';
const RUST='#A84A2A';
const WARM='#B9AEA4';
const GRID='#DED8D2';

const presentation=await PresentationFile.importPptx(await FileBlob.load(STARTER));
const slides=presentation.slides.items;
if(slides.length!==13) throw new Error(`Expected 13 slides, got ${slides.length}`);

function shapeText(shape){ try{return shape.text?.toString?.()??'';}catch{return '';} }
function titleShape(slide){ return slide.shapes.items.find(s=>s.placeholderType==='title') ?? slide.shapes.items.find(s=>/title/i.test(s.name||'') && shapeText(s)); }
function setText(shape,text,{size=20,color=TEXT,bold=false,align='left'}={}){
  shape.text.set(text);
  shape.text.typeface=FONT;
  shape.text.fontSize=size;
  shape.text.fill=color;
  shape.text.bold=bold;
  shape.text.alignment=align;
  shape.text.autoFit='none';
  shape.text.wrap='square';
}
function setTitle(slide,text){
  let s=titleShape(slide);
  if(!s) throw new Error(`Missing title on slide ${slide.index+1}`);
  // LibreOffice can misplace some imported Title Only placeholders outside
  // the slide canvas. Replace only those affected titles in the exact frame.
  if(new Set([3,4,5,6,9,11]).has(slide.index)){
    const position={left:41.33,top:36.12,width:1197.33,height:109.97};
    s.delete();
    s=slide.shapes.add({
      geometry:'textbox',
      name:`Replaced title ${slide.index+1}`,
      position,
      fill:'none',
      line:{style:'solid',fill:'none',width:0}
    });
  }
  setText(s,text,{size:40,color:INK,bold:false});
}
function setHeadingBody(shape,heading,body,{bodySize=19,headingSize=23}={}){
  shape.text.set(`${heading}\n${body}`);
  shape.text.typeface=FONT;
  shape.text.fontSize=bodySize;
  shape.text.fill=TEXT;
  shape.text.alignment='left';
  shape.text.autoFit='none';
  shape.text.wrap='square';
  const r=shape.text.get(heading); r.bold=true; r.fontSize=headingSize; r.fill=INK;
}
function setNumber(slide,n){ const s=slide.shapes.items.find(x=>x.placeholderType==='slideNumber'||/slide number/i.test(x.name||'')); if(s) setText(s,String(n),{size:12,color:INK}); }
function deleteFooter(slide){ for(const s of [...slide.shapes.items]) if(s.placeholderType==='footer'||/footer/i.test(s.name||'')) s.delete(); }
function finalizeChrome(slide,n){ deleteFooter(slide); setNumber(slide,n); slide.background.fill='#FFFEFC'; }
async function readBlob(file){ const b=await fs.readFile(file); return b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength); }
async function saveBlob(blob,file){await fs.mkdir(path.dirname(file),{recursive:true});await fs.writeFile(file,Buffer.from(await blob.arrayBuffer()));}
async function replaceImage(slide,file,alt){ const im=slide.images.items[0]; if(!im) throw new Error(`Missing inherited image on slide ${slide.index+1}`); const frame={...im.frame}; im.delete(); slide.images.add({blob:await readBlob(file),contentType:'image/png',alt,fit:'contain',position:frame}); }
function sourceNotes(extra=[]){return ['[Sources]','- /Users/leonel/Desktop/TAD/Proyecto Integrador - Informe Final 2026 - MartinezMauricioLeonel.pdf','- /Users/leonel/Desktop/TAD/video/Guion_video_proyecto_integrador.pdf',...extra.map(x=>`- ${x}`),'[/Sources]'].join('\n');}
function addNotes(slide,extra=[]){ slide.speakerNotes.textFrame.setText(sourceNotes(extra)); slide.speakerNotes.setVisible(true); }
function sortedTextShapes(slide,filter=()=>true){return slide.shapes.items.filter(s=>shapeText(s)&&filter(s)).sort((a,b)=>(a.frame.top-b.frame.top)||(a.frame.left-b.frame.left));}
function styleChart(chart,{categories,series,max=100}){
  chart.apply({
    title:'', hasLegend:true,
    legend:{position:'top',overlay:false,textStyle:{fontSize:14,fill:MUTED}},
    xAxis:{visible:true,textStyle:{fontSize:13,fill:TEXT},line:{style:'solid',fill:GRID,width:1},majorGridlines:null},
    yAxis:{visible:true,min:0,max,majorUnit:20,numberFormatCode:'0.00',textStyle:{fontSize:12,fill:MUTED},line:{style:'solid',fill:GRID,width:1},majorGridlines:{style:'solid',fill:'#EEEAE6',width:1}},
    dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:12,fill:INK,bold:true}},
    chartFill:'#FFFEFC',plotAreaFill:'#FFFEFC',chartLine:{style:'solid',fill:GRID,width:1},plotAreaLine:{style:'solid',fill:'#FFFEFC',width:0}
  });
  const items=chart.series.items;
  if(items.length<series.length) throw new Error('Not enough inherited chart series');
  for(let i=0;i<series.length;i++){
    const s=items[i], spec=series[i]; s.name=spec.name; s.categories=categories; s.values=spec.values; s.valuesFormatCode='0.00';
    if(spec.fill){ s.fill=spec.fill; s.line={style:'solid',fill:spec.fill,width:0}; }
    if(spec.line) s.line={style:'solid',fill:spec.line,width:3};
  }
}

// 1. Cover
{
 const s=slides[0];
 const ttl=s.shapes.items.find(x=>x.placeholderType==='title');
 const sub=s.shapes.items.find(x=>x.placeholderType==='subtitle');
 const supert=s.shapes.items.find(x=>!x.placeholderType&&shapeText(x));
 setText(supert,'PROYECTO INTEGRADOR · 2026',{size:18,color:RUST,bold:true});
 setText(ttl,'Detección preventiva de eventos\nsísmicos peligrosos',{size:64,color:INK});
 setText(sub,'Comparación de cuatro modelos sobre Seismic-Bumps\nMauricio Leonel Martínez',{size:21,color:TEXT});
 s.background.fill='#FFFEFC'; addNotes(s);
}

// 2. Problem and question
{
 const s=slides[1]; setTitle(s,'La clase peligrosa representa solo el 6,58% del conjunto');
 const bodies=sortedTextShapes(s,x=>!x.placeholderType&&!/532|533/.test(x.name||''));
 setHeadingBody(bodies[0],'Riesgo operativo','170 de 2.584 registros corresponden a eventos peligrosos. Un clasificador que predice siempre “no peligroso” supera el 93% de accuracy y, aun así, falla el objetivo preventivo.',{bodySize:19});
 setHeadingBody(bodies[1],'Pregunta de investigación','¿Qué diferencias presentan árbol de decisión, Naive Bayes, k-NN y regresión logística en rendimiento global y detección de la clase peligrosa, bajo un procedimiento de evaluación común?',{bodySize:19});
 finalizeChrome(s,2); addNotes(s);
}

// 3. General objective
{
 const s=slides[2]; setTitle(s,'Comparar modelos sin perder de vista el riesgo');
 const bodies=sortedTextShapes(s,x=>!x.placeholderType&&!/532|533/.test(x.name||''));
 setHeadingBody(bodies[0],'Objetivo general','Analizar comparativamente el comportamiento de un árbol de decisión, Naive Bayes, k-NN y regresión logística para clasificar la ocurrencia de eventos sísmicos peligrosos en Seismic-Bumps.',{bodySize:20});
 setHeadingBody(bodies[1],'Criterio de análisis','La comparación se realiza con un protocolo común y considera tanto el rendimiento global como la capacidad de detectar la clase 1. La selección final prioriza el criterio preventivo, no la accuracy aislada.',{bodySize:20});
 finalizeChrome(s,3); addNotes(s);
}

// 4. Eight objectives
{
 const s=slides[3]; setTitle(s,'Ocho objetivos estructuran la comparación');
 const boxes=sortedTextShapes(s,x=>!x.placeholderType && /Placeholder/.test(x.name||''));
 const items=[
 ['1 · Datos','Describir el ARFF, sus atributos y la distribución de clases.'],
 ['2 · Preparación','Documentar el proceso sin transformaciones no comprobadas.'],
 ['3 · Modelos base','Evaluar con validación cruzada estratificada.'],
 ['4 · Matrices','Leer filas verdaderas y columnas predichas.'],
 ['5 · Métricas','Comparar accuracy, AUC (optimistic), precisión, recall y F1 de clase 1.'],
 ['6 · SMOTE','Medir su efecto aplicado solo dentro de Training.'],
 ['7 · Selección','Priorizar la detección de la clase peligrosa.'],
 ['8 · Limitaciones','Explicitar las limitaciones metodológicas de los resultados.']
 ];
 if(boxes.length!==8) throw new Error(`Slide 4: expected 8 boxes, got ${boxes.length}`);
 items.forEach((it,i)=>setHeadingBody(boxes[i],it[0],it[1],{bodySize:15,headingSize:18}));
 finalizeChrome(s,4); addNotes(s);
}

// 5. Dataset
{
 const s=slides[4]; setTitle(s,'El riesgo se concentra en solo 170 registros');
 const body=s.shapes.items.find(x=>!x.placeholderType&&shapeText(x));
 setHeadingBody(body,'Seismic-Bumps','2.584 registros · 18 atributos predictivos · variable objetivo binaria “class”\n\n2.414 clase 0 — 93,42%\n170 clase 1 — 6,58%\n\nEl encabezado ARFF no declara valores faltantes.',{bodySize:20,headingSize:25});
 await replaceImage(s,`${MEDIA}/image.png`,'Distribución real de la variable objetivo: 2414 no peligrosos y 170 peligrosos.');
 finalizeChrome(s,5); addNotes(s,['/Users/leonel/Desktop/TAD/video/Presentacion_exposicion_proyecto_integrador.pptx']);
}

// 6. Protocol
{
 const s=slides[5]; setTitle(s,'Un protocolo común permite comparar los cuatro algoritmos');
 const body=s.shapes.items.find(x=>!x.placeholderType&&shapeText(x));
 setHeadingBody(body,'Validación cruzada estratificada de 10 particiones','Árbol de decisión · Naive Bayes · k-NN (k = 5) · Regresión logística\n\nTraining: aprende el modelo y aplica la preparación permitida.\n\nTesting: aplica el modelo y mide desempeño sobre datos no usados para aprender.',{bodySize:19,headingSize:24});
 await replaceImage(s,`${MEDIA}/image2.png`,'Proceso real de validación cruzada: Training a la izquierda y Testing a la derecha.');
 finalizeChrome(s,6); addNotes(s,['/Users/leonel/Desktop/TAD/video/Presentacion_exposicion_proyecto_integrador.pptx']);
}

// 7. Preparation
{
 const s=slides[6]; setTitle(s,'La preparación cambia Training; Testing permanece intacto');
 const body=s.shapes.items.find(x=>!x.placeholderType&&shapeText(x));
 setHeadingBody(body,'Preparación por partición','k-NN: normalización dentro de cada fold.\n\nVariantes con SMOTE: ejemplos sintéticos únicamente en Training.\n\nTesting no se normaliza con información futura ni se rebalancea. Así se evita contaminar la estimación.',{bodySize:20,headingSize:24});
 await replaceImage(s,`${MEDIA}/image3.png`,'Tubería real de Naive Bayes con SMOTE dentro de Training; Testing sin remuestreo.');
 finalizeChrome(s,7); addNotes(s,['/Users/leonel/Desktop/TAD/video/Presentacion_exposicion_proyecto_integrador.pptx']);
}

// 8. Base results
{
 const s=slides[7]; setTitle(s,'La accuracy alta ocultó una detección peligrosa muy baja');
 const chart=s.charts.items[0]; chart.apply({barOptions:{direction:'column',grouping:'clustered',gapWidth:55}});
 styleChart(chart,{categories:['Árbol','Naive Bayes','k-NN','Logística'],series:[
  {name:'Accuracy (%)',values:[92.84,84.75,93.07,87.89],fill:WARM},
  {name:'Recall clase 1 (%)',values:[2.94,41.18,9.41,44.12],fill:RUST}
 ]});
 const intro=s.shapes.items.find(x=>x.name==='Content Placeholder 1');
 setHeadingBody(intro,'Accuracy | Recall de clase 1','Árbol 92,84 | 2,94\nNaive Bayes 84,75 | 41,18\nk-NN 93,07 | 9,41\nLogística 87,89 | 44,12',{bodySize:17,headingSize:22});
 const stats=s.shapes.items.filter(x=>/Content Placeholder 9/.test(x.name||'')).sort((a,b)=>a.frame.left-b.frame.left);
 const labels=s.shapes.items.filter(x=>/Content Placeholder 15/.test(x.name||'')).sort((a,b)=>a.frame.left-b.frame.left);
 setText(stats[0],'2,94%',{size:50,color:RUST}); setText(labels[0],'Recall del árbol\nsin SMOTE',{size:17,color:TEXT});
 setText(stats[1],'44,12%',{size:50,color:RUST}); setText(labels[1],'Mayor recall base:\nregresión logística',{size:17,color:TEXT});
 finalizeChrome(s,8); addNotes(s);
}

// 9. SMOTE variants
{
 const s=slides[8]; setTitle(s,'SMOTE cambia el equilibrio');
 const oldChart=s.charts.items[0];
 const chartFrame={...oldChart.frame};
 s.charts.deleteById(oldChart.id);
 s.charts.add('bar',{
  position:chartFrame,
  categories:['Árbol','Naive Bayes','k-NN','Logística'],
  series:[
   {name:'Precisión (%)',values:[18.62,13.65,14.71,10.24],fill:WARM,line:{style:'solid',fill:WARM,width:0},valuesFormatCode:'0.00'},
   {name:'Recall (%)',values:[57.06,67.06,43.53,81.76],fill:RUST,line:{style:'solid',fill:RUST,width:0},valuesFormatCode:'0.00'}
  ],
  hasLegend:true,
  legend:{position:'top',overlay:false,textStyle:{fontSize:14,fill:MUTED}},
  barOptions:{direction:'column',grouping:'clustered',gapWidth:55},
  xAxis:{visible:true,textStyle:{fontSize:13,fill:TEXT},line:{style:'solid',fill:GRID,width:1},majorGridlines:null},
  yAxis:{visible:true,min:0,max:100,majorUnit:20,numberFormatCode:'0.00',textStyle:{fontSize:12,fill:MUTED},line:{style:'solid',fill:GRID,width:1},majorGridlines:{style:'solid',fill:'#EEEAE6',width:1}},
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00',textStyle:{fontSize:12,fill:INK,bold:true}},
  chartFill:'#FFFEFC',plotAreaFill:'#FFFEFC',chartLine:{style:'solid',fill:GRID,width:1},plotAreaLine:{style:'solid',fill:'#FFFEFC',width:0}
 });
 const cards=s.shapes.items.filter(x=>/Content Placeholder 10/.test(x.name||'')).sort((a,b)=>a.frame.top-b.frame.top);
 setHeadingBody(cards[0],'Árbol + SMOTE','Precisión 18,62% · Recall 57,06%',{bodySize:18,headingSize:22});
 setHeadingBody(cards[1],'Naive Bayes + SMOTE','Precisión 13,65% · Recall 67,06%',{bodySize:18,headingSize:22});
 setHeadingBody(cards[2],'k-NN y Logística','k-NN: 14,71% · 43,53%\nLogística: 10,24% · 81,76%',{bodySize:17,headingSize:22});
 finalizeChrome(s,9); addNotes(s);
}

// 10. ROC evidence
{
 const s=slides[9]; setTitle(s,'La evidencia ROC antecede la selección final');
 const body=s.shapes.items.find(x=>!x.placeholderType&&shapeText(x));
 setHeadingBody(body,'AUC (optimistic)','Naive Bayes 0,748 ± 0,034\nRegresión logística 0,757 ± 0,060\nk-NN 0,753 ± 0,041\nÁrbol 0,812 ± 0,065\n\nEl árbol lidera la discriminación global. La selección operativa considera el recall en un umbral concreto: son criterios distintos.',{bodySize:18,headingSize:23});
 await replaceImage(s,`${MEDIA}/image4.png`,'Curvas ROC reales documentadas en AI Studio para los cuatro modelos con SMOTE.');
 finalizeChrome(s,10); addNotes(s,['/Users/leonel/Desktop/TAD/video/Presentacion_exposicion_proyecto_integrador.pptx']);
}

// 11. Selected model
{
 const s=slides[10]; setTitle(s,'Regresión logística + SMOTE: elección preventiva');
 const intro=s.shapes.items.find(x=>/Content Placeholder 15/.test(x.name||''));
 setHeadingBody(intro,'Selección preventiva','Recall 81,76% · 139 de 170 detectados · Precisión 10,24% · AUC (optimistic): 0,757\nMatriz de confusión: filas verdaderas, columnas predichas. La elección no es globalmente dominante.',{bodySize:18,headingSize:22});
 const boxes=s.shapes.items.filter(x=>/Content Placeholder 10/.test(x.name||'')).sort((a,b)=>(a.frame.top-b.frame.top)||(a.frame.left-b.frame.left));
 const vals=[['TN — 1.195','Verdadera 0 · Predicha 0'],['FP — 1.219','Verdadera 0 · Predicha 1'],['FN — 31','Verdadera 1 · Predicha 0'],['TP — 139','Verdadera 1 · Predicha 1']];
 vals.forEach((v,i)=>setHeadingBody(boxes[i],v[0],v[1],{bodySize:18,headingSize:28}));
 finalizeChrome(s,11); addNotes(s);
}

// 12. Attribute sensitivity
{
 const s=slides[11]; setTitle(s,'La cantidad de atributos no mejora el error de forma monotónica');
 const body=s.shapes.items.find(x=>!x.placeholderType&&shapeText(x));
 setHeadingBody(body,'Experimento complementario','Atributos: 3 · 6 · 9 · 12 · 15 · 18\nError medio (%): 39,09 · 52,16 · 50,46 · 55,34 · 49,31 · 47,44\nVariabilidad (±): 2,39 · 14,04 · 2,84 · 3,94 · 3,36 · 5,64\n\nEl patrón es no monotónico. Este análisis separado no reemplaza al modelo seleccionado.',{bodySize:17,headingSize:22});
 await replaceImage(s,`${MEDIA}/image5.png`,'Gráfico real del error medio y su variabilidad según la cantidad de atributos.');
 finalizeChrome(s,12); addNotes(s,['/Users/leonel/Desktop/TAD/video/Presentacion_exposicion_proyecto_integrador.pptx']);
}

// 13. Conclusions
{
 const s=slides[12]; setTitle(s,'La elección preventiva exige validación antes de operar');
 const left=s.shapes.items.find(x=>/Google Shape;534/.test(x.name||''));
 setHeadingBody(left,'Conclusión','La accuracy es inadecuada como criterio único. SMOTE aumenta el recall, pero también las falsas alarmas. Regresión logística + SMOTE se selecciona por el objetivo preventivo.\n\nLa evidencia es experimental y apoya decisiones: no constituye un sistema automático de alertas listo para operar.',{bodySize:18,headingSize:24});
 const titles=s.shapes.items.filter(x=>/Content Placeholder 10/.test(x.name||'')&&x.frame.left<720).sort((a,b)=>a.frame.top-b.frame.top);
 const descs=s.shapes.items.filter(x=>/Content Placeholder 10/.test(x.name||'')&&x.frame.left>=720).sort((a,b)=>a.frame.top-b.frame.top);
 const items=[
  ['Calibrar umbrales','Ajustar el equilibrio entre omisiones y falsas alarmas.'],
  ['Analizar costos','Cuantificar el costo operativo de FP y FN.'],
  ['Validar en nuevos contextos','Realizar validación temporal y externa.'],
  ['Evaluar con especialistas','Someter el resultado a especialistas antes de cualquier uso real.']
 ];
 items.forEach((v,i)=>{setText(titles[i],v[0],{size:20,color:INK,bold:true});setText(descs[i],v[1],{size:18,color:TEXT});});
 finalizeChrome(s,13); addNotes(s);
}

await fs.mkdir(path.dirname(FINAL),{recursive:true});
const out=await PresentationFile.exportPptx(presentation); await out.save(FINAL);
const renderDir=`${TMP}/final-render`; const layoutDir=`${TMP}/final-layout`; await fs.rm(renderDir,{recursive:true,force:true}); await fs.rm(layoutDir,{recursive:true,force:true}); await fs.mkdir(renderDir,{recursive:true}); await fs.mkdir(layoutDir,{recursive:true});
for(let i=0;i<slides.length;i++){
 const png=await presentation.export({slide:slides[i],format:'png',scale:2}); await saveBlob(png,`${renderDir}/slide-${String(i+1).padStart(2,'0')}.png`);
 const layout=await presentation.export({slide:slides[i],format:'layout'}); await saveBlob(layout,`${layoutDir}/slide-${String(i+1).padStart(2,'0')}.layout.json`);
}
const montage=await presentation.export({format:'webp',montage:true,scale:1}); await saveBlob(montage,`${TMP}/final-montage.webp`);
const inspect=await presentation.inspect({kind:'slide,textbox,shape,image,table,chart,notes,layout',max_chars:200000}); await fs.writeFile(`${TMP}/final-inspect.ndjson`,inspect.ndjson||'');
console.log(JSON.stringify({output:FINAL,slides:slides.length,renderDir,layoutDir},null,2));
