import fs from 'node:fs/promises';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const ROOT = '/Users/leonel/Desktop/TAD';
const FIG = `${ROOT}/output/figures`;
const TMP = `${ROOT}/video/tmp_presentacion`;
const OUT = `${ROOT}/video/Presentacion_exposicion_proyecto_integrador.pptx`;

const C = {
  navy: '#12345B',
  blue: '#1E6FB9',
  sky: '#DCECF8',
  light: '#F4F7FA',
  gold: '#D99A21',
  text: '#24313D',
  muted: '#5E6B78',
  grid: '#D9E1E8',
  green: '#0E7C66',
  greenLight: '#E6F5F0',
  amber: '#C87800',
  amberLight: '#FFF2D8',
  red: '#B3403C',
  redLight: '#FBE9E8',
  white: '#FFFFFF',
};

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}
async function readBytes(path) {
  return await fs.readFile(path);
}
function addRect(slide, x, y, w, h, fill, lineFill = fill, radius = false) {
  return slide.shapes.add({
    geometry: radius ? 'roundRect' : 'rect',
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: 'solid', fill: lineFill, width: 0 },
    ...(radius ? { borderRadius: 'rounded-xl' } : {}),
  });
}
function addText(slide, text, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: 'textbox',
    position: { left: x, top: y, width: w, height: h },
    fill: 'none',
    line: { style: 'solid', fill: 'none', width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: options.fontSize ?? 22,
    bold: options.bold ?? false,
    color: options.color ?? C.text,
    alignment: options.alignment ?? 'left',
    italic: options.italic ?? false,
  };
  return shape;
}
function addFooter(slide, n, appendix = false) {
  addRect(slide, 72, 684, 1136, 1, C.grid);
  addText(slide, appendix ? 'ANEXO' : 'UCASAL | Técnicas avanzadas de análisis de datos', 72, 692, 560, 20, { fontSize: 12, color: C.muted });
  addText(slide, String(n), 1172, 692, 36, 20, { fontSize: 12, color: C.muted, alignment: 'right' });
}
function addSlideTitle(slide, title, n, options = {}) {
  addRect(slide, 72, 48, 8, 54, options.appendix ? C.gold : C.blue);
  addText(slide, title, 96, 43, 1065, 58, { fontSize: options.fontSize ?? 38, bold: true, color: C.navy });
  addFooter(slide, n, options.appendix);
}
function addBullet(slide, text, x, y, w, options = {}) {
  addRect(slide, x, y + 12, 8, 8, options.color ?? C.blue, options.color ?? C.blue, true);
  return addText(slide, text, x + 24, y, w - 24, options.h ?? 54, { fontSize: options.fontSize ?? 21, color: options.textColor ?? C.text, bold: options.bold ?? false });
}
async function addImage(slide, path, x, y, w, h, alt, options = {}) {
  if (options.frame !== false) {
    addRect(slide, x - 10, y - 10, w + 20, h + 20, options.frameFill ?? C.light, options.frameLine ?? C.grid, true);
  }
  const img = slide.images.add({
    blob: await readBytes(path),
    contentType: 'image/png',
    alt,
    fit: options.fit ?? 'contain',
    position: { left: x, top: y, width: w, height: h },
    geometry: 'rect',
  });
  return img;
}
function setNotes(slide, talk, sources) {
  const block = `${talk}\n\n[Sources]\n${sources.map(s => `- ${s}`).join('\n')}`;
  slide.speakerNotes.textFrame.setText(block);
  slide.speakerNotes.setVisible(true);
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// Slide 1 - cover
{
  const s = presentation.slides.add();
  s.background.fill = C.navy;
  addRect(s, 72, 72, 12, 460, C.gold);
  addText(s, 'Universidad Católica de Salta', 112, 76, 780, 38, { fontSize: 22, bold: true, color: C.sky });
  addText(s, 'Facultad de Ingeniería', 112, 112, 620, 30, { fontSize: 18, color: C.sky });
  addText(s, 'Clasificación supervisada de eventos sísmicos peligrosos', 112, 192, 980, 132, { fontSize: 52, bold: true, color: C.white });
  addText(s, 'Comparación de árbol de decisión, Naive Bayes, k-NN y regresión logística', 112, 344, 920, 70, { fontSize: 25, color: C.sky });
  addText(s, 'Proyecto integrador', 112, 450, 300, 28, { fontSize: 19, bold: true, color: C.gold });
  addText(s, 'Mauricio Leonel Martínez', 112, 490, 520, 32, { fontSize: 23, color: C.white });
  addText(s, 'Técnicas avanzadas de análisis de datos | 2026', 112, 548, 700, 28, { fontSize: 17, color: C.sky });
  addText(s, '1', 1170, 674, 38, 20, { fontSize: 12, color: C.sky, alignment: 'right' });
  setNotes(s,
    'Hola, mi nombre es Mauricio Leonel Martínez. Este trabajo no busca solamente identificar qué algoritmo obtiene el valor más alto en una métrica, sino determinar qué configuración resulta más coherente con un objetivo preventivo: reducir la omisión de eventos sísmicos peligrosos. La comparación de cuatro algoritmos y de sus variantes con SMOTE permite fundamentar esa decisión con evidencia experimental. Este enfoque es relevante porque la clase peligrosa es muy minoritaria y una evaluación superficial puede ofrecer una impresión engañosa de buen rendimiento. La conclusión debe interpretarse dentro del conjunto de datos y del protocolo evaluado: se trata de evidencia para apoyar decisiones, no de un sistema automático listo para operar.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

// Slide 2 - problem and objective
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'El desafío fue detectar una clase peligrosa muy minoritaria', 2, { fontSize: 36 });
  addText(s, '6,58%', 92, 152, 360, 100, { fontSize: 72, bold: true, color: C.blue });
  addText(s, 'de los registros corresponden a eventos peligrosos', 96, 258, 420, 78, { fontSize: 26, color: C.text });
  addRect(s, 94, 352, 330, 4, C.gold);
  addText(s, 'Pregunta central', 94, 390, 330, 34, { fontSize: 22, bold: true, color: C.navy });
  addText(s, '¿Qué modelo reduce mejor las omisiones de la clase 1 bajo una evaluación común?', 94, 432, 430, 112, { fontSize: 25, color: C.text });
  addRect(s, 624, 146, 520, 416, C.light, C.grid, true);
  addText(s, 'Objetivo del proyecto', 664, 178, 430, 40, { fontSize: 28, bold: true, color: C.navy });
  addBullet(s, 'Comparar cuatro algoritmos de clasificación supervisada.', 664, 244, 420, { fontSize: 22, h: 58 });
  addBullet(s, 'Evaluar accuracy, AUC, precisión, recall, F1 y matrices de confusión.', 664, 324, 420, { fontSize: 22, h: 78 });
  addBullet(s, 'Analizar SMOTE sin modificar el conjunto de prueba.', 664, 426, 420, { fontSize: 22, h: 58 });
  setNotes(s,
    'La clase peligrosa representa solo el 6,58% de los registros. Esto significa que la exactitud está estructuralmente condicionada por la clase mayoritaria: un modelo que casi siempre predijera la clase no peligrosa podría superar el 93% de aciertos y, al mismo tiempo, fallar precisamente en los casos que motivan el estudio. Por eso el problema no consistió en maximizar la exactitud, sino en comparar la capacidad real de detectar la clase 1. Este criterio sostiene la decisión de dar mayor importancia al recall y a los falsos negativos. La limitación es que esa prioridad supone un costo operativo desigual entre errores que debe ser validado por especialistas del dominio.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`, `${ROOT}/seismic-bumps.arff`]
  );
}

// Slide 3 - data
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'Seismic-Bumps contiene 2584 registros y 18 predictores', 3, { fontSize: 38 });
  await addImage(s, `${FIG}/distribucion_clases.png`, 78, 156, 720, 392, 'Distribución de las clases del conjunto Seismic-Bumps');
  addText(s, '2414', 850, 168, 260, 62, { fontSize: 48, bold: true, color: C.navy });
  addText(s, 'turnos no peligrosos', 850, 224, 280, 36, { fontSize: 22, color: C.muted });
  addRect(s, 850, 286, 300, 1, C.grid);
  addText(s, '170', 850, 316, 260, 62, { fontSize: 48, bold: true, color: C.red });
  addText(s, 'turnos peligrosos', 850, 372, 280, 36, { fontSize: 22, color: C.muted });
  addRect(s, 850, 434, 300, 1, C.grid);
  addText(s, 'Sin valores faltantes declarados', 850, 468, 300, 62, { fontSize: 22, bold: true, color: C.green });
  addText(s, 'La evaluación debía conservar este desbalance en Testing.', 82, 586, 1010, 40, { fontSize: 23, bold: true, color: C.navy });
  setNotes(s,
    'Seismic-Bumps contiene 2584 registros, 18 atributos predictivos y una variable objetivo binaria. La relación de 2414 casos no peligrosos frente a 170 peligrosos representa un escenario en el que la información más relevante también es la más escasa. Esto importa porque el modelo dispone de muchos más ejemplos para aprender la clase 0 y puede inclinarse hacia ella. Por esa razón se decidió conservar la distribución original en Testing y analizar métricas específicas de la clase 1, en lugar de balancear artificialmente toda la muestra. La ausencia de valores faltantes declarados simplifica la preparación, pero no elimina la limitación de trabajar con un único conjunto de datos ni demuestra generalización temporal o externa.',
    [`${ROOT}/seismic-bumps.arff`, `${FIG}/distribucion_clases.png`]
  );
}

// Slide 4 - methodology
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'La evaluación usó validación cruzada estratificada', 4, { fontSize: 36 });
  addText(s, 'Modelos evaluados', 86, 144, 260, 32, { fontSize: 22, bold: true, color: C.navy });
  addText(s, 'Árbol de decisión  |  Naive Bayes  |  k-NN (k=5)  |  Regresión logística', 86, 186, 1110, 38, { fontSize: 22, color: C.text });
  await addImage(s, `${FIG}/proceso_cross_validation.png`, 190, 256, 900, 306, 'Flujo de validación cruzada en Altair AI Studio');
  addText(s, 'Cada modelo se entrenó en Training y se evaluó en Testing.', 244, 594, 790, 36, { fontSize: 22, bold: true, color: C.navy, alignment: 'center' });
  setNotes(s,
    'La validación cruzada estratificada de 10 particiones hace que cada algoritmo sea evaluado bajo divisiones comparables y conserva una proporción semejante de las dos clases en cada fold. Esto reduce la dependencia de una única partición y permite comparar árbol, Naive Bayes, k-NN y regresión logística con un protocolo común. La decisión metodológica respalda una comparación interna más estable y obliga a leer conjuntamente exactitud, AUC, precisión, recall, F1 y matrices de confusión. Sin embargo, la validación cruzada sobre el mismo conjunto no prueba que el rendimiento se mantenga en otro yacimiento, en otro período ni ante cambios en la distribución de los datos.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`, `${FIG}/proceso_cross_validation.png`]
  );
}

// Slide 5 - SMOTE methodology
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'SMOTE se aplicó únicamente dentro de Training', 5, { fontSize: 36 });
  await addImage(s, `${FIG}/diagrama_smote_naive_bayes.png`, 82, 154, 1116, 360, 'Tubería de Naive Bayes con SMOTE dentro de Training');
  addRect(s, 106, 556, 468, 70, C.greenLight, C.green, true);
  addText(s, 'Training', 130, 570, 120, 28, { fontSize: 22, bold: true, color: C.green });
  addText(s, 'incluye ejemplos sintéticos', 248, 570, 286, 28, { fontSize: 21, color: C.text });
  addRect(s, 706, 556, 468, 70, C.sky, C.blue, true);
  addText(s, 'Testing', 730, 570, 110, 28, { fontSize: 22, bold: true, color: C.blue });
  addText(s, 'conserva la distribución original', 832, 570, 300, 28, { fontSize: 21, color: C.text });
  setNotes(s,
    'SMOTE genera ejemplos sintéticos de la clase minoritaria para que el algoritmo encuentre más señales asociadas con eventos peligrosos durante el aprendizaje. Se aplicó únicamente dentro de Training, de modo que esos registros modifican el proceso de entrenamiento, pero no la evidencia utilizada para evaluar el modelo. Mantener Testing con la distribución original evita fuga de información y permite estimar el comportamiento frente al desbalance real. Esta decisión respalda una comparación válida entre variantes con y sin SMOTE. La contrapartida es que los ejemplos sintéticos pueden simplificar o distorsionar la estructura de la clase minoritaria, por lo que una mejora de recall no debe interpretarse automáticamente como una mejora global.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`, `${FIG}/diagrama_smote_naive_bayes.png`]
  );
}

// Slide 6 - base models chart
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'La accuracy ocultó una baja detección de peligrosos', 6, { fontSize: 36 });
  s.charts.add('bar', {
    position: { left: 88, top: 148, width: 1098, height: 412 },
    categories: ['Árbol', 'Naive Bayes', 'k-NN', 'Reg. logística'],
    series: [
      { name: 'Accuracy', values: [92.84, 84.75, 93.07, 87.89], fill: C.navy, valuesFormatCode: '0.00' },
      { name: 'Recall clase 1', values: [2.94, 41.18, 9.41, 44.12], fill: C.gold, valuesFormatCode: '0.00' },
    ],
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 65 },
    hasLegend: true,
    legend: { position: 'bottom', overlay: false, textStyle: { fontSize: 16, fill: C.text } },
    xAxis: { textStyle: { fontSize: 16, fill: C.text }, line: { style: 'solid', fill: C.grid, width: 1 } },
    yAxis: { min: 0, max: 100, majorUnit: 20, numberFormatCode: '0', title: { text: 'Porcentaje (%)', textStyle: { fontSize: 15, fill: C.muted } }, textStyle: { fontSize: 15, fill: C.muted }, majorGridlines: { style: 'solid', fill: C.grid, width: 1 } },
    dataLabels: { showValue: true, position: 'outEnd', textStyle: { fontSize: 14, fill: C.text, bold: true } },
    chartFill: C.white,
    plotAreaFill: C.white,
    chartLine: { style: 'solid', fill: C.white, width: 0 },
  });
  addText(s, 'El árbol y k-NN superaron 92% de accuracy, pero detectaron menos del 10% de la clase 1.', 116, 586, 1040, 46, { fontSize: 23, bold: true, color: C.navy, alignment: 'center' });
  setNotes(s,
    'Los modelos base muestran que una exactitud alta puede coexistir con una detección deficiente de la clase peligrosa. El árbol alcanzó 92,84% de exactitud y 2,94% de recall, mientras que k-NN obtuvo 93,07% y 9,41%, respectivamente. Esto representa modelos que aprendieron principalmente el patrón de la clase mayoritaria: aciertan muchos casos rutinarios, pero omiten casi todos los casos críticos. Para un objetivo preventivo, ese comportamiento es inseguro y justifica descartar la exactitud como criterio principal de selección. Naive Bayes y la regresión logística ofrecen mayor sensibilidad, aunque pierden exactitud; además, estos resultados siguen dependiendo del umbral y de la muestra utilizada.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

// Slide 7 - SMOTE chart
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'SMOTE aumentó el recall, pero también las falsas alarmas', 7, { fontSize: 37 });
  s.charts.add('bar', {
    position: { left: 88, top: 150, width: 1098, height: 408 },
    categories: ['Árbol + SMOTE', 'NB + SMOTE', 'k-NN + SMOTE', 'Logística + SMOTE'],
    series: [
      { name: 'Precisión clase 1', values: [18.62, 13.65, 14.71, 10.24], fill: C.blue, valuesFormatCode: '0.00' },
      { name: 'Recall clase 1', values: [57.06, 67.06, 43.53, 81.76], fill: C.green, valuesFormatCode: '0.00' },
    ],
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 60 },
    hasLegend: true,
    legend: { position: 'bottom', overlay: false, textStyle: { fontSize: 16, fill: C.text } },
    xAxis: { textStyle: { fontSize: 15, fill: C.text }, line: { style: 'solid', fill: C.grid, width: 1 } },
    yAxis: { min: 0, max: 100, majorUnit: 20, numberFormatCode: '0', title: { text: 'Porcentaje (%)', textStyle: { fontSize: 15, fill: C.muted } }, textStyle: { fontSize: 15, fill: C.muted }, majorGridlines: { style: 'solid', fill: C.grid, width: 1 } },
    dataLabels: { showValue: true, position: 'outEnd', textStyle: { fontSize: 14, fill: C.text, bold: true } },
    chartFill: C.white,
    plotAreaFill: C.white,
    chartLine: { style: 'solid', fill: C.white, width: 0 },
  });
  addText(s, 'Detectar más eventos peligrosos implicó aceptar más falsos positivos.', 176, 584, 928, 44, { fontSize: 23, bold: true, color: C.navy, alignment: 'center' });
  setNotes(s,
    'Con SMOTE, los cuatro modelos identificaron una proporción mayor de eventos peligrosos porque el entrenamiento dejó de estar dominado en la misma medida por la clase 0. El resultado representa un desplazamiento del equilibrio entre precisión y recall, no una mejora simultánea de todas las métricas. La regresión logística con SMOTE alcanzó 81,76% de recall, pero su precisión descendió a 10,24%, de modo que muchas alertas positivas serían falsas. Este intercambio apoya la selección de una variante con SMOTE solamente si se considera que omitir un evento peligroso cuesta más que revisar una falsa alarma. La limitación operativa es la carga de inspecciones innecesarias y el posible desgaste de confianza ante alertas frecuentes.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

// Slide 8 - selected model
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'La selección final prioriza detectar la clase peligrosa', 8, { fontSize: 38 });
  addText(s, '81,76%', 92, 156, 390, 96, { fontSize: 76, bold: true, color: C.green });
  addText(s, 'recall de la clase 1', 98, 252, 380, 38, { fontSize: 25, color: C.text });
  addText(s, '139 de 170 eventos peligrosos detectados', 98, 316, 430, 58, { fontSize: 25, bold: true, color: C.navy });
  addText(s, '31 falsos negativos', 98, 396, 340, 42, { fontSize: 25, color: C.red, bold: true });
  addText(s, '1219 falsos positivos', 98, 450, 360, 42, { fontSize: 25, color: C.amber, bold: true });
  addText(s, 'La configuración no es globalmente superior: es la más coherente con un criterio preventivo.', 98, 532, 440, 80, { fontSize: 22, color: C.muted });

  addText(s, 'Matriz de confusión', 694, 144, 400, 36, { fontSize: 25, bold: true, color: C.navy, alignment: 'center' });
  addText(s, 'Pred. 0', 744, 196, 150, 28, { fontSize: 18, bold: true, color: C.muted, alignment: 'center' });
  addText(s, 'Pred. 1', 918, 196, 150, 28, { fontSize: 18, bold: true, color: C.muted, alignment: 'center' });
  addText(s, 'Verd. 0', 598, 266, 130, 28, { fontSize: 18, bold: true, color: C.muted, alignment: 'right' });
  addText(s, 'Verd. 1', 598, 380, 130, 28, { fontSize: 18, bold: true, color: C.muted, alignment: 'right' });
  addRect(s, 746, 238, 148, 92, C.sky, C.blue, true); addText(s, '1195', 746, 266, 148, 40, { fontSize: 30, bold: true, color: C.navy, alignment: 'center' });
  addRect(s, 920, 238, 148, 92, C.amberLight, C.amber, true); addText(s, '1219', 920, 266, 148, 40, { fontSize: 30, bold: true, color: C.amber, alignment: 'center' });
  addRect(s, 746, 352, 148, 92, C.redLight, C.red, true); addText(s, '31', 746, 380, 148, 40, { fontSize: 30, bold: true, color: C.red, alignment: 'center' });
  addRect(s, 920, 352, 148, 92, C.greenLight, C.green, true); addText(s, '139', 920, 380, 148, 40, { fontSize: 30, bold: true, color: C.green, alignment: 'center' });
  addText(s, 'Precisión: 10,24%', 686, 492, 220, 34, { fontSize: 22, color: C.muted });
  addText(s, 'AUC: 0,757', 938, 492, 180, 34, { fontSize: 22, color: C.muted });
  addRect(s, 648, 544, 500, 58, C.greenLight, C.green, true);
  addText(s, 'Modelo elegido: regresión logística + SMOTE', 676, 560, 450, 30, { fontSize: 23, bold: true, color: C.green, alignment: 'center' });
  setNotes(s,
    'La regresión logística con SMOTE detectó 139 de los 170 eventos peligrosos y dejó 31 falsos negativos. Este resultado representa la mayor cobertura de la clase 1 entre las configuraciones evaluadas y respalda su selección cuando los falsos negativos se consideran más costosos que los falsos positivos. Sin embargo, los 1219 falsos positivos y la precisión de 10,24% implican que solo una fracción pequeña de las alertas correspondería realmente a eventos peligrosos, con un riesgo operativo considerable de saturación y fatiga de alarmas. Por ello no se afirma que sea el mejor modelo en términos absolutos: es el más coherente con el criterio preventivo adoptado y requeriría calibración y validación antes de cualquier uso real.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

// Slide 9 - conclusions
{
  const s = presentation.slides.add();
  s.background.fill = C.navy;
  addText(s, 'Conclusiones', 78, 56, 640, 62, { fontSize: 44, bold: true, color: C.white });
  addRect(s, 78, 128, 180, 6, C.gold);
  addBullet(s, 'La accuracy no describió adecuadamente el rendimiento sobre la clase peligrosa.', 98, 184, 1060, { fontSize: 25, h: 64, color: C.gold, textColor: C.white });
  addBullet(s, 'SMOTE aumentó el recall de la clase 1, pero también incrementó las falsas alarmas.', 98, 276, 1060, { fontSize: 25, h: 72, color: C.gold, textColor: C.white });
  addBullet(s, 'La regresión logística + SMOTE fue la configuración más coherente con el objetivo preventivo.', 98, 382, 1060, { fontSize: 25, h: 72, color: C.gold, textColor: C.white });
  addRect(s, 80, 514, 1118, 1, '#45617D');
  addText(s, 'Próximos pasos', 94, 548, 250, 34, { fontSize: 23, bold: true, color: C.gold });
  addText(s, 'Calibrar umbrales  |  Analizar costos  |  Validar con datos temporales o externos', 94, 588, 1050, 42, { fontSize: 23, color: C.sky });
  addText(s, '9', 1170, 674, 38, 20, { fontSize: 12, color: C.sky, alignment: 'right' });
  setNotes(s,
    'La evidencia muestra que la exactitud no describe adecuadamente el desempeño cuando la clase relevante es minoritaria. Los modelos base favorecieron la clase 0, mientras que SMOTE desplazó el equilibrio hacia una mayor detección de peligrosos a costa de más falsas alarmas. La regresión logística con SMOTE fue seleccionada porque el criterio preventivo asignó mayor costo a los falsos negativos, no porque dominara todas las métricas. La decisión es experimental y sirve como apoyo para analizar alternativas; no constituye un sistema automático de alertas desplegable. Para avanzar hacia un uso operativo sería necesario calibrar umbrales, cuantificar costos, evaluar estabilidad temporal y validar con datos externos y conocimiento experto.',
    [`${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

// Slide 10 - appendix ROC
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'Anexo | Curvas ROC documentadas en AI Studio', 10, { appendix: true, fontSize: 36 });
  await addImage(s, `${FIG}/roc_smote_composite.png`, 112, 126, 1056, 500, 'Curvas ROC de las cuatro variantes con SMOTE');
  setNotes(s,
    'Las curvas ROC resumen la capacidad de ordenar casos positivos y negativos a través de múltiples umbrales. El árbol con SMOTE obtuvo el AUC más alto, 0,812, frente a 0,757 de la regresión logística con SMOTE. Ese resultado indica una mejor discriminación global del árbol, pero no reemplaza el criterio operativo: el AUC es independiente de un umbral concreto, mientras que la selección priorizó el recall alcanzado en el umbral evaluado y el costo de los falsos negativos. Por eso el AUC más alto no invalida la elección de la regresión logística. La limitación es que estas curvas no determinan por sí solas qué umbral resulta aceptable ni incorporan el costo real de las falsas alarmas.',
    [`${FIG}/roc_smote_composite.png`, `${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

// Slide 11 - appendix attributes
{
  const s = presentation.slides.add();
  s.background.fill = C.white;
  addSlideTitle(s, 'Anexo | Sensibilidad al número de atributos', 11, { appendix: true, fontSize: 36 });
  await addImage(s, `${FIG}/error_atributos_logistica_smote.png`, 128, 132, 760, 480, 'Error de clasificación según número de atributos');
  addText(s, 'Resultado suplementario', 934, 170, 250, 36, { fontSize: 24, bold: true, color: C.navy });
  addText(s, 'El menor error medio se observó con 3 atributos, pero la alta variabilidad y el carácter separado del experimento impiden reemplazar la selección final.', 934, 228, 250, 184, { fontSize: 22, color: C.text });
  addRect(s, 934, 452, 238, 92, C.amberLight, C.amber, true);
  addText(s, 'No modifica el modelo elegido', 958, 475, 190, 48, { fontSize: 22, bold: true, color: C.amber, alignment: 'center' });
  setNotes(s,
    'Este análisis suplementario exploró cómo cambiaba el error al conservar 3, 6, 9, 12, 15 y 18 atributos seleccionados dentro de Training. El menor error medio apareció con 3 atributos, pero ese valor aislado no basta para afirmar que sea la configuración superior: existe variabilidad entre particiones, la relación no fue monotónica y el ensayo se ejecutó como un proceso separado de la comparación principal. En consecuencia, el resultado sirve para plantear una posible simplificación y una futura validación específica, pero no para reemplazar la selección final. La principal limitación es que todavía no se demostró que el subconjunto reducido mantenga su ventaja bajo el mismo protocolo completo y en datos externos.',
    [`${FIG}/error_atributos_logistica_smote.png`, `${ROOT}/Proyecto Integrador - Informe Final v2 - MartinezMauricioLeonel.tex`]
  );
}

await fs.mkdir(`${TMP}/rendered`, { recursive: true });
for (const [i, slide] of presentation.slides.items.entries()) {
  const stem = `slide-${String(i + 1).padStart(2, '0')}`;
  await writeBlob(`${TMP}/rendered/${stem}.png`, await presentation.export({ slide, format: 'png', scale: 1 }));
  await fs.writeFile(`${TMP}/rendered/${stem}.layout.json`, await (await slide.export({ format: 'layout' })).text());
}
await writeBlob(`${TMP}/montage.webp`, await presentation.export({ format: 'webp', montage: true, scale: 1 }));
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUT);
console.log(OUT);
