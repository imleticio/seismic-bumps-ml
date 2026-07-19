# Propuesta independiente: visualización científica

Propuesta alternativa para el informe académico sobre detección de eventos
sísmicos. No modifica `output/figures/` ni el informe canónico.

## Archivos

- `generate_candidate_figures.py`: script reproducible; valida el ARFF antes de
  exportar.
- `01_datos_y_confusion.pdf` / `.png`: composición de desequilibrio de clases y
  matriz de confusión del árbol.
- `02_metricas_arbol.pdf` / `.png`: rendimiento global y métricas de la clase
  positiva.

## Reproducción

Desde la raíz del proyecto:

```bash
python3 output/candidates/scientific-visualization/generate_candidate_figures.py
```

También se puede indicar otra ruta ARFF con `--dataset` y otra carpeta de
salida con `--output-dir`. El script se niega explícitamente a escribir en
`output/figures/`.

## Criterio de diseño

- Composición de doble columna de aproximadamente 7,25 pulgadas, adecuada
  para insertar en LaTeX a `\textwidth`.
- Paleta Okabe–Ito, con hachurados y formas redundantes para conservar la
  lectura en color y escala de grises.
- PDF vectorial con fuentes TrueType embebidas y PNG a 300 dpi.
- La matriz conserva la orientación filas = predicción y columnas = verdad.
- Solo se representan los resultados confirmados: exactitud, AUC optimista,
  precisión, recall micro y F-measure. La nota distingue el recall micro de
  `2,94 %` del valor del encabezado `3,05 % ± 4,36 %`; no se combinan ni se
  infieren incertidumbres faltantes.
