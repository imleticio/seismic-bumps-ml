# Seismic Bumps ML

Proyecto académico de **Machine Learning** orientado a la clasificación de eventos sísmicos potencialmente peligrosos en minería subterránea a partir del dataset **Seismic-Bumps** de UCI.

## Objetivo

Analizar cómo distintos algoritmos de clasificación supervisada responden ante un problema fuertemente desbalanceado, con especial atención a la detección de la clase peligrosa.

## Dataset

- 2.584 instancias.
- 18 atributos predictivos.
- Clasificación binaria: evento no peligroso / peligroso.
- Clase peligrosa: 170 casos (6,58 %).
- Formato original: ARFF.

## Modelos evaluados

- Decision Tree
- Naive Bayes
- k-NN
- Regresión logística

También se evaluaron variantes con **SMOTE** para estudiar el efecto del sobremuestreo de la clase minoritaria.

## Metodología

Los experimentos se realizaron con **validación cruzada estratificada de 10 particiones**. En las variantes con SMOTE, el sobremuestreo se aplica únicamente sobre el conjunto de entrenamiento de cada partición para evitar contaminación de los datos de evaluación.

Las métricas analizadas incluyen:

- Accuracy
- Precision
- Recall
- F1-score
- AUC
- Matriz de confusión

El análisis no se limita a accuracy, ya que el fuerte desbalance del dataset puede ocultar un bajo desempeño sobre la clase peligrosa.

## Resultados principales

En los modelos base, la regresión logística alcanzó el mayor recall y F1 de la clase peligrosa entre las configuraciones comparadas, mientras que k-NN obtuvo mayor precisión sobre esa clase.

Las variantes con SMOTE aumentaron el recall y redujeron falsos negativos, pero también incrementaron los falsos positivos. Por ello, los resultados se interpretan como un compromiso entre capacidad de detección y falsas alarmas, no como una mejora automática.

> Este proyecto es un estudio académico sobre el dataset Seismic-Bumps. No representa un sistema operativo de alerta sísmica ni una validación en un entorno minero real.

## Herramientas

- Altair AI Studio / RapidMiner
- Python
- LaTeX
- SMOTE
- Validación cruzada estratificada

## Estructura del repositorio

- `*.rmp`: procesos experimentales de Altair AI Studio / RapidMiner.
- `scripts/`: scripts utilizados para generar figuras y comparaciones.
- `output/`: figuras y artefactos empleados en el informe.
- `seismic-bumps.arff`: dataset utilizado en los experimentos.
- `Proyecto Integrador - Informe Final 2026 - MartinezMauricioLeonel.pdf`: informe del proyecto.

## Autor

**Mauricio Leonel Martínez**  
Ingeniería en Informática — Universidad Católica de Salta (UCASAL)
