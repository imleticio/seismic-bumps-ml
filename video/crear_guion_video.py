from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether, HRFlowable
)
from reportlab.lib.utils import ImageReader

ROOT = Path('/Users/leonel/Desktop/TAD')
OUT_DIR = ROOT / 'video'
OUT = OUT_DIR / 'Guion_video_proyecto_integrador.pdf'
FIG = ROOT / 'output' / 'figures'

NAVY = colors.HexColor('#12345B')
BLUE = colors.HexColor('#1E6FB9')
LIGHT_BLUE = colors.HexColor('#EAF3FB')
PALE = colors.HexColor('#F5F8FC')
GOLD = colors.HexColor('#D99A21')
DARK = colors.HexColor('#25313C')
GRAY = colors.HexColor('#5E6B78')
GREEN = colors.HexColor('#EAF6EF')
RED_PALE = colors.HexColor('#FFF1F0')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='CoverTitle', parent=styles['Title'], fontName='Helvetica-Bold',
    fontSize=22, leading=27, alignment=TA_CENTER, textColor=NAVY,
    spaceAfter=10
))
styles.add(ParagraphStyle(
    name='CoverSubtitle', parent=styles['Normal'], fontName='Helvetica',
    fontSize=12, leading=16, alignment=TA_CENTER, textColor=DARK,
    spaceAfter=6
))
styles.add(ParagraphStyle(
    name='Meta', parent=styles['Normal'], fontName='Helvetica',
    fontSize=10.5, leading=15, alignment=TA_CENTER, textColor=DARK
))
styles.add(ParagraphStyle(
    name='H1Video', parent=styles['Heading1'], fontName='Helvetica-Bold',
    fontSize=18, leading=22, textColor=NAVY, spaceBefore=2, spaceAfter=8
))
styles.add(ParagraphStyle(
    name='H2Video', parent=styles['Heading2'], fontName='Helvetica-Bold',
    fontSize=13, leading=16, textColor=BLUE, spaceBefore=4, spaceAfter=5
))
styles.add(ParagraphStyle(
    name='BodyVideo', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=10.5, leading=15, textColor=DARK, spaceAfter=7
))
styles.add(ParagraphStyle(
    name='SmallVideo', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=9, leading=12, textColor=GRAY, spaceAfter=4
))
styles.add(ParagraphStyle(
    name='ScriptText', parent=styles['BodyText'], fontName='Helvetica',
    fontSize=10.5, leading=15, textColor=DARK, leftIndent=5, rightIndent=5,
    spaceAfter=4
))
styles.add(ParagraphStyle(
    name='BoxTitle', parent=styles['BodyText'], fontName='Helvetica-Bold',
    fontSize=10, leading=13, textColor=NAVY, spaceAfter=4
))
styles.add(ParagraphStyle(
    name='CaptionVideo', parent=styles['Normal'], fontName='Helvetica-Oblique',
    fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=GRAY,
    spaceBefore=3, spaceAfter=8
))
styles.add(ParagraphStyle(
    name='TableHeaderVideo', parent=styles['Normal'], fontName='Helvetica-Bold',
    fontSize=8.5, leading=10, textColor=colors.white, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    name='TableCellVideo', parent=styles['Normal'], fontName='Helvetica',
    fontSize=8.5, leading=10, textColor=DARK, alignment=TA_CENTER
))


def p(text, style='BodyVideo'):
    return Paragraph(text, styles[style])


def image_flow(path, max_width, max_height=None):
    path = Path(path)
    iw, ih = ImageReader(str(path)).getSize()
    width = max_width
    height = width * ih / iw
    if max_height and height > max_height:
        height = max_height
        width = height * iw / ih
    im = Image(str(path), width=width, height=height)
    im.hAlign = 'CENTER'
    return im


def screen_box(title, items, color=LIGHT_BLUE):
    content = [p(title, 'BoxTitle')]
    for item in items:
        content.append(p('&bull; ' + item, 'SmallVideo'))
    tbl = Table([[content]], colWidths=[16.8 * cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('BOX', (0, 0), (-1, -1), 0.8, BLUE),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    return tbl


def script_box(text, color=PALE):
    tbl = Table([[p('<b>Texto sugerido para decir</b><br/><br/>' + text, 'ScriptText')]], colWidths=[16.8 * cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#B7C5D4')),
        ('LEFTPADDING', (0, 0), (-1, -1), 11),
        ('RIGHTPADDING', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tbl


def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor('#D4DCE5'))
    canvas.setLineWidth(0.5)
    canvas.line(1.8 * cm, 1.35 * cm, w - 1.8 * cm, 1.35 * cm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.8 * cm, 0.9 * cm, 'Guion de video - Proyecto integrador')
    canvas.drawRightString(w - 1.8 * cm, 0.9 * cm, f'{doc.page}')
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, rightMargin=1.8 * cm, leftMargin=1.8 * cm,
    topMargin=1.55 * cm, bottomMargin=1.7 * cm,
    title='Guion para video de presentación - Proyecto integrador',
    author='Mauricio Leonel Martinez'
)

story = []

# Cover
story += [Spacer(1, 1.0 * cm), p('Universidad Católica de Salta (UCASAL)', 'CoverSubtitle'),
          p('Facultad de Ingeniería', 'CoverSubtitle'), Spacer(1, 0.35 * cm),
          p('Guion para video de presentación', 'CoverTitle'),
          p('Proyecto integrador: clasificación supervisada de eventos sísmicos peligrosos en minería subterránea', 'CoverSubtitle'),
          Spacer(1, 0.4 * cm), HRFlowable(width='80%', thickness=1, color=NAVY, hAlign='CENTER'), Spacer(1, 0.35 * cm),
          p('<b>Materia:</b> Técnicas avanzadas de análisis de datos<br/><b>Estudiante:</b> Mauricio Leonel Martínez<br/><b>Docentes:</b> Cardoso, Alejandra Carolina; Pastrana, Analía Verónica; Talame, María Lorena<br/><b>Año:</b> 2026', 'Meta'),
          Spacer(1, 0.8 * cm),
          screen_box('Cómo usar este documento', [
              'Duración sugerida: aproximadamente 6 minutos.',
              'Usá las pantallas indicadas como apoyo visual; no leas las tablas completas.',
              'Explicá el problema, el criterio de selección y el costo del modelo elegido.',
              'Mostrá solamente las evidencias principales: datos, proceso, resultados, ROC y conclusión.'
          ], color=LIGHT_BLUE),
          Spacer(1, 0.4 * cm),
          p('<b>Idea central del video:</b> la exactitud podía parecer alta por el desbalance, pero el objetivo real era detectar la clase peligrosa y reducir los falsos negativos.', 'BodyVideo'),
          PageBreak()]

# Scene 1 and 2
story += [p('1. Presentación del problema y objetivo', 'H1Video'),
          p('<b>Tiempo sugerido:</b> 0:00 - 0:45', 'SmallVideo'),
          screen_box('Qué mostrar en pantalla', [
              'La portada del informe final.',
              'El título del proyecto y el objetivo general.',
              'No mostrar todavía las tablas de resultados.'
          ]), Spacer(1, 0.2 * cm),
          script_box('Hola, mi nombre es Mauricio Leonel Martínez y este es mi proyecto integrador para la materia Técnicas avanzadas de análisis de datos. El trabajo analiza la identificación de eventos sísmicos peligrosos en minería subterránea mediante clasificación supervisada. La pregunta no fue solamente qué algoritmo obtiene el número más alto, sino cuál resulta más coherente con un objetivo preventivo. Por eso comparé cuatro modelos y sus variantes con SMOTE, priorizando la reducción de eventos peligrosos no detectados. La selección final se interpreta como evidencia experimental para apoyar una decisión, no como un sistema de alertas listo para operar.'),
          PageBreak(),
          p('2. Descripción de los datos', 'H1Video'),
          p('<b>Tiempo sugerido:</b> 0:45 - 1:35', 'SmallVideo'),
          screen_box('Qué mostrar en pantalla', [
              'El gráfico de distribución de clases.',
              'La tabla o página del informe donde aparecen las características del dataset.',
              'Señalar visualmente la diferencia entre clase 0 y clase 1.'
          ]), Spacer(1, 0.2 * cm),
          image_flow(FIG / 'distribucion_clases.png', 15.7 * cm, 5.0 * cm),
          p('Gráfico de distribución de la variable objetivo utilizado en el informe.', 'CaptionVideo'),
          script_box('Se utilizó el conjunto Seismic-Bumps, almacenado en formato ARFF, con 2584 registros, 18 atributos predictivos y una variable objetivo binaria. La clase 0 reúne 2414 casos no peligrosos y la clase 1 solamente 170, es decir, el 6,58% del total. Esta proporción cambia completamente la lectura de los resultados: un modelo que casi siempre predijera la clase 0 podría superar el 93% de exactitud y, aun así, no cumplir el objetivo preventivo. Por eso la exactitud es estructuralmente engañosa si se analiza de manera aislada. La evaluación debía concentrarse también en el recall de la clase 1 y en los falsos negativos. El archivo no declara valores faltantes, pero trabajar con un único conjunto sigue limitando la generalización de los hallazgos.'),
          PageBreak()]

# Scene 3
story += [p('3. Explicación del proceso realizado', 'H1Video'),
          p('<b>Tiempo sugerido:</b> 1:35 - 2:50', 'SmallVideo'),
          screen_box('Qué mostrar en pantalla', [
              'El flujo de validación cruzada estratificada.',
              'El diagrama de Naive Bayes con SMOTE.',
              'Señalar que SMOTE está dentro de Training y no en Testing.'
          ]), Spacer(1, 0.18 * cm),
          image_flow(FIG / 'proceso_cross_validation.png', 12.6 * cm, 4.1 * cm),
          p('Flujo general de evaluación mediante validación cruzada.', 'CaptionVideo'),
          image_flow(FIG / 'diagrama_smote_naive_bayes.png', 15.7 * cm, 4.0 * cm),
          p('Ejemplo de la tubería de Naive Bayes con SMOTE.', 'CaptionVideo'),
          script_box('El procesamiento se realizó en Altair AI Studio mediante validación cruzada estratificada de 10 particiones. La estratificación mantuvo proporciones comparables de ambas clases y permitió evaluar árbol de decisión, Naive Bayes, k-NN con k igual a 5 y regresión logística bajo un protocolo común. Esto mejora la comparabilidad interna, pero no demuestra que los resultados se mantengan en otro período o en otro entorno. Se analizaron exactitud, AUC, precisión, recall, F1 y matrices de confusión porque ninguna métrica aislada describe por completo el problema. En las variantes con SMOTE, los ejemplos sintéticos se generaron únicamente dentro de Training. De este modo modificaron el aprendizaje, pero no el conjunto utilizado para evaluar; Testing conservó la distribución original y se evitó fuga de información. Para k-NN se aplicó normalización debido a su dependencia de las distancias.'),
          PageBreak()]

# Scene 4 part 1
story += [p('4. Resultados obtenidos', 'H1Video'),
          p('<b>Tiempo sugerido:</b> 2:50 - 4:00', 'SmallVideo'),
          screen_box('Qué mostrar en pantalla', [
              'La tabla comparativa de los modelos base.',
              'Luego, la tabla comparativa de las variantes con SMOTE.',
              'No leer todas las filas: destacar solo las diferencias principales.'
          ]), Spacer(1, 0.25 * cm),
          p('<b>Resultados que conviene mencionar:</b>', 'H2Video'),
          Table([
              [p('Configuración', 'TableHeaderVideo'), p('Exactitud', 'TableHeaderVideo'), p('Recall clase 1', 'TableHeaderVideo'), p('Interpretación', 'TableHeaderVideo')],
              [p('Árbol base', 'TableCellVideo'), p('92,84%', 'TableCellVideo'), p('2,94%', 'TableCellVideo'), p('Alta exactitud, pero casi no detecta peligrosos.', 'TableCellVideo')],
              [p('k-NN base', 'TableCellVideo'), p('93,07%', 'TableCellVideo'), p('9,41%', 'TableCellVideo'), p('La exactitud oculta el desbalance.', 'TableCellVideo')],
              [p('Regresión logística base', 'TableCellVideo'), p('87,89%', 'TableCellVideo'), p('44,12%', 'TableCellVideo'), p('Mejor equilibrio base por F1.', 'TableCellVideo')],
              [p('Regresión logística + SMOTE', 'TableCellVideo'), p('51,63%', 'TableCellVideo'), p('81,76%', 'TableCellVideo'), p('Mayor cobertura de la clase peligrosa.', 'TableCellVideo')],
          ], colWidths=[3.6*cm, 2.4*cm, 3.0*cm, 7.8*cm], repeatRows=1, style=TableStyle([
              ('BACKGROUND', (0,0), (-1,0), NAVY), ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#B7C5D4')),
              ('BACKGROUND', (0,1), (-1,-1), colors.white), ('BACKGROUND', (0,4), (-1,4), GREEN),
              ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 5),
              ('RIGHTPADDING', (0,0), (-1,-1), 5), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
          ])),
          Spacer(1, 0.35 * cm),
          script_box('Los modelos base muestran por qué no debía elegirse por exactitud. El árbol obtuvo 92,84% y k-NN 93,07%, pero sus recalls para la clase peligrosa fueron 2,94% y 9,41%. En términos prácticos, estos modelos aprendieron principalmente la clase mayoritaria: clasificaron bien los casos habituales, pero omitieron casi todos los casos críticos. Para un objetivo preventivo, ese comportamiento sería inseguro. Naive Bayes y la regresión logística base detectaron más peligrosos, aunque con menor exactitud. Al aplicar SMOTE aumentó el recall en las cuatro variantes, pero también crecieron los falsos positivos. Por lo tanto, SMOTE no mejoró todo el desempeño; desplazó el equilibrio entre precisión y recall hacia una mayor sensibilidad.'),
          PageBreak()]

# Scene 4 part 2
story += [p('4. Resultados y modelo elegido', 'H1Video'),
          p('<b>Tiempo sugerido:</b> 4:00 - 5:15', 'SmallVideo'),
          screen_box('Qué mostrar en pantalla', [
              'La composición de curvas ROC de los cuatro modelos con SMOTE.',
              'La matriz LaTeX de regresión logística + SMOTE, sin mostrar matrices duplicadas.',
              'El gráfico de error según la cantidad de atributos, como análisis complementario.'
          ]), Spacer(1, 0.18 * cm),
          image_flow(FIG / 'roc_smote_composite.png', 13.8 * cm, 7.0 * cm),
          p('Curvas ROC documentadas directamente desde AI Studio.', 'CaptionVideo'),
          script_box('Las curvas ROC muestran la capacidad de discriminación de los modelos a través de distintos umbrales. El árbol con SMOTE obtuvo el AUC más alto, 0,812, mientras que la regresión logística con SMOTE obtuvo 0,757. Sin embargo, el AUC es independiente de un umbral operativo concreto y no reemplaza el criterio del proyecto. En el umbral evaluado, la regresión logística con SMOTE alcanzó el mayor recall, 81,76%: detectó 139 de 170 eventos peligrosos y dejó 31 falsos negativos. Se eligió porque se consideró que omitir un evento peligroso era más costoso que generar una falsa alarma. El costo es serio: produjo 1219 falsos positivos y una precisión de 10,24%, lo que podría saturar la revisión operativa y generar fatiga de alarmas. El análisis de atributos fue complementario. Aunque k igual a 3 presentó el menor error medio, la variabilidad y el hecho de corresponder a una ejecución separada impiden usarlo como evidencia suficiente para cambiar el modelo final.'),
          Spacer(1, 0.15 * cm),
          image_flow(FIG / 'error_atributos_logistica_smote.png', 10.5 * cm, 4.5 * cm),
          PageBreak()]

# Scene 5
story += [p('5. Conclusiones principales', 'H1Video'),
          p('<b>Tiempo sugerido:</b> 5:15 - 6:00', 'SmallVideo'),
          screen_box('Qué mostrar en pantalla', [
              'La página de conclusiones del informe.',
              'Si se desea, volver a mostrar la matriz de regresión logística + SMOTE y señalar FN=31.',
              'Cerrar con el nombre del modelo seleccionado y sus limitaciones.'
          ], color=GREEN), Spacer(1, 0.25 * cm),
          script_box('Como conclusión, el proyecto demuestra que una exactitud alta no equivale a una buena protección cuando la clase peligrosa es minoritaria. Los modelos base favorecieron la clase no peligrosa, mientras que SMOTE permitió detectar más eventos críticos a cambio de más falsas alarmas. La regresión logística con SMOTE fue seleccionada porque el criterio preventivo asignó mayor costo a los falsos negativos y esta configuración alcanzó el mayor recall. No se sostiene que sea superior en todas las métricas: sus 1219 falsos positivos y su baja precisión representan una limitación operativa central. En consecuencia, el resultado debe entenderse como evidencia experimental para apoyar decisiones y no como un sistema automático de alertas desplegable. Antes de cualquier aplicación real sería necesario calibrar umbrales, cuantificar costos, validar con datos temporales o externos e incorporar la evaluación de especialistas. El principal aporte fue fundamentar la elección del modelo según el riesgo que se buscaba reducir. Muchas gracias.'),
          Spacer(1, 0.4 * cm),
          p('Checklist antes de grabar', 'H2Video'),
          Table([
              [p('Antes de empezar', 'TableHeaderVideo'), p('Durante el video', 'TableHeaderVideo'), p('Antes de entregar', 'TableHeaderVideo')],
              [p('Cerrar ventanas innecesarias y preparar las pantallas.', 'TableCellVideo'), p('Hablar pausadamente y explicar el criterio de selección.', 'TableCellVideo'), p('Verificar que el audio se entienda y que las figuras sean legibles.', 'TableCellVideo')],
              [p('Tener abierto el PDF y las figuras principales.', 'TableCellVideo'), p('No leer todas las tablas ni enumerar todos los atributos.', 'TableCellVideo'), p('Comprobar que la duración respete la consigna.', 'TableCellVideo')],
              [p('Ensayar una vez siguiendo los tiempos.', 'TableCellVideo'), p('Repetir la idea central: exactitud alta no implica buena detección.', 'TableCellVideo'), p('Finalizar mencionando fortalezas y limitaciones.', 'TableCellVideo')],
          ], colWidths=[5.6*cm, 5.6*cm, 5.6*cm], repeatRows=1, style=TableStyle([
              ('BACKGROUND', (0,0), (-1,0), NAVY), ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#B7C5D4')),
              ('BACKGROUND', (0,1), (-1,-1), PALE), ('VALIGN', (0,0), (-1,-1), 'TOP'),
              ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
              ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
          ])),
          Spacer(1, 0.5 * cm),
          p('<b>Frase para recordar:</b> “La exactitud era alta porque predominaba la clase no peligrosa; por eso la decisión final se tomó priorizando el recall de la clase peligrosa.”', 'BodyVideo')]

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(OUT)
