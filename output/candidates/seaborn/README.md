# Candidata Seaborn: desbalance y errores de la clase positiva

Alternativa independiente para el informe académico sobre detección de eventos sísmicos. No modifica `output/figures/` ni el informe canónico.

## Ejecución reproducible

Desde la raíz del repositorio:

```bash
python3 output/candidates/seaborn/generate_seaborn_figures.py
```

Dependencia principal: `seaborn==0.13.2` (con sus dependencias de NumPy, pandas y Matplotlib). También se puede indicar otro ARFF y directorio de salida:

```bash
python3 output/candidates/seaborn/generate_seaborn_figures.py \
  --dataset seismic-bumps.arff \
  --output-dir output/candidates/seaborn
```

El script valida 2.584 registros, las frecuencias de clase confirmadas y la ausencia de faltantes. La matriz de confusión proviene del resumen confirmado de CV 10-fold; no se reentrena ningún modelo.

## Archivos

- `01_soporte_desbalance.pdf/png`: soporte de las clases con porcentajes exactos y razón 14,2:1. Las tramas complementan el color para facilitar la lectura en escala de grises.
- `02_errores_clase_positiva.pdf/png`: composición de los casos verdaderamente positivos (TP/FN) y de los casos predichos como positivos (TP/FP), con conteos y porcentajes dentro de cada barra.
- `03_heatmap_confusion_anotado.pdf/png`: heatmap anotado en dos vistas: conteos absolutos y porcentajes normalizados por clase verdadera. La orientación es filas = clase verdadera y columnas = clase predicha.

## Criterio de diseño

Seaborn se usa sobre datos tabulares explícitos (`barplot` y `heatmap`) con `sns.set_theme(style="ticks", context="paper")`. Se priorizan una paleta colorblind-safe basada en Okabe–Ito, `cividis` para magnitudes ordenadas, tramas redundantes, ejes que comienzan en cero y anotaciones de conteos para que el desbalance no oculte los 165 FN ni los 5 TP. Los PDF se exportan como vector y los PNG a 300 dpi.
