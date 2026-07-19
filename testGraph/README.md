# Figuras publicables: Seismic-Bumps

## Fuentes

- **Datos:** `../seismic-bumps.arff`, el dataset local Seismic-Bumps de Sikora y Wrobel.
- **Resultados de modelos:** matrices de confusión base confirmadas en el informe del repositorio. Se usan exactamente estas matrices, con filas = clase real y columnas = clase predicha:
  - Decision Tree base: `[[2394, 20], [165, 5]]`.
  - Naive Bayes base: `[[2120, 294], [100, 70]]`.

## Método y reproducción

El script no usa red ni instala paquetes. Requiere solamente Python, NumPy y Matplotlib disponibles en `.venv-figures`.

```bash
./.venv-figures/bin/python testGraph/create_publication_figures.py
```

También puede ejecutarse desde `testGraph`:

```bash
cd testGraph
../.venv-figures/bin/python create_publication_figures.py
```

El script valida antes de crear cualquier salida que el ARFF tenga 2.584 filas, 19 campos, clases `0=2.414` y `1=170`, y ningún valor faltante. Luego crea cuatro figuras en SVG, PDF y PNG. Las imágenes PNG se exportan a 600 DPI; SVG y PDF son formatos vectoriales.

`02_atributos_por_clase` muestra todas las observaciones de `genergy`, `gpuls` y `energy`, separadas por clase, con transformación `log10(valor + 1)`, jitter determinista y media con IC bootstrap del 95% (semilla fija). Los colores siguen la paleta Okabe-Ito.

`03_recall_clase_peligrosa` reconstruye los 170 resultados positivos de cada matriz agregada: TP y FN. El intervalo es Wilson del 95% para la proporción de positivos correctamente detectados.

## Limitaciones exactas

- El repositorio no contiene valores de rendimiento por fold. Por eso **no se fabrican puntos de 10 folds** y ningún valor reportado como `media ± ...` se relabela como IC del 95%.
- Los puntos de la figura 03 son resultados individuales agrupados de casos positivos reales reconstruidos desde los conteos agregados; no son observaciones independientes de folds ni conservan el orden de los casos originales.
- Los IC bootstrap de la figura 02 describen incertidumbre de la media de las observaciones disponibles bajo remuestreo, no incertidumbre de generalización del modelo.
- Las matrices de confusión corresponden a los resultados agregados confirmados, no se recalculan entrenando modelos. Sus porcentajes son porcentajes por fila.
- El dataset es muy desbalanceado; la distribución de clases es contexto descriptivo y no evidencia de calidad predictiva.
