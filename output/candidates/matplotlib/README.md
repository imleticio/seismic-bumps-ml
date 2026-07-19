# Propuesta independiente de figuras — Matplotlib

Esta carpeta contiene una alternativa editorial para el informe académico de detección de eventos sísmicos. No modifica el informe canónico ni `output/figures/`.

## Ejecución

Desde la raíz del proyecto:

```bash
python3 -m pip install "matplotlib>=3.10"
python3 output/candidates/matplotlib/generate_candidate_figures.py
```

El script valida que `seismic-bumps.arff` tenga 2.584 registros, 19 campos por fila, ninguna ausencia y las clases confirmadas antes de escribir los resultados. También verifica que la matriz de confusión suministrada sea compatible con los totales de clase.

## Archivos

- `generate_candidate_figures.py` — generación reproducible con la interfaz orientada a objetos de Matplotlib.
- `candidata_distribucion_clases.pdf` / `.png` — barras horizontales con conteos, porcentajes y razón de desequilibrio.
- `candidata_matriz_confusion.pdf` / `.png` — matriz con conteos y proporción dentro de cada clase verdadera.
- `candidata_metricas_arbol.pdf` / `.png` — puntos e intervalos para métricas globales y de la clase positiva.

## Criterio de diseño

Se priorizó una estética minimalista de baja tinta: jerarquía manual, espacio generoso, etiquetas directas y grillas discretas. La distinción no depende únicamente del color: se incorporan hatches, formas y etiquetas para facilitar la lectura en escala de grises. La matriz normaliza solo el relleno visual —los conteos siguen explícitos— para no ocultar la clase minoritaria. El AUC se muestra como 86,0% ± 4,1 puntos porcentuales, equivalente al valor suministrado 0,860 ± 0,041. La diferencia entre recall micro (2,94%) y el encabezado reportado (3,05% ± 4,36%) se conserva como nota, sin resolverla ni inventar una explicación.

Los PDF se construyen con texto, líneas y parches vectoriales; el degradado de la matriz también se compone con rectángulos, evitando imágenes rasterizadas dentro del PDF.
