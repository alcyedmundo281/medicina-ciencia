# Medicina y Ciencia

**Ciencia de datos, estadística biomédica y semiótica clínica basada en la evidencia.**

Publicación independiente dirigida al público general, estudiantes y profesionales de la
salud, con DOI e ISBN propios, compilada a partir del
[blog de MedSemiotics](https://powersemiotics.com/medsemiotics/index.html) y
[`medsemiotics-db`](https://github.com/alcyedmundo281/medsemiotics-db) con la arquitectura
editorial de [`alcyedmundo281/neurology`](https://github.com/alcyedmundo281/neurology) y el
motor de publicación de [`alcyedmundo281/biosemiotics`](https://github.com/alcyedmundo281/biosemiotics).

## Contenido del libro

El [mapa maestro](mapa-maestro-libro.md) registra la estructura completa:

- **Parte I — Fundamentos: del hallazgo a la decisión:** 4 capítulos metodológicos
  (inferencia clínica y tabla $2 \times 2$, razonamiento bayesiano, valoración crítica de
  la evidencia, datos clínicos, IA y comunicación del riesgo), enlazados a sus casos ancla.
- **Partes II–VII — Compendio completo del blog MedSemiotics:** las **48 condiciones
  clínicas verificadas** (`HM:6001` a `HM:6048`) a una única revisión fijada de
  `medsemiotics-db` (`ea2f6e63b850`, DOI `10.5281/zenodo.22064424`), con sus **18 casos
  socráticos** compilados determinísticamente desde `casos/`.
- **Apéndices:** banco completo de **90 preguntas de autoevaluación** (*Reto clínico*) con
  clave razonada, índice maestro de hallazgos con $\text{LR}^+ / \text{LR}^-$ medido,
  registro de iconografía abierta de Wikimedia Commons y declaración de uso de IA.

## Arquitectura: `JSON → QMD → Quarto (HTML, PDF LuaLaTeX y EPUB)`

1. **Capa de datos y JSON:** `mapa.yaml`, `posts/*.md`, `casos/*.yaml` y
   `assets/data/blog-index.json` se validan y consolidan en `build/libro.json`.
2. **Capa QMD:** `tools/libro/qmd.py` proyecta el proyecto Quarto completo en
   `build/quarto/` (`_quarto.yml`, capítulos `.qmd`, portada vectorial `portada.svg`,
   preámbulo `preambulo-libro.tex`, filtros Lua y hojas CSS web/EPUB).
3. **Salidas compiladas:**
   - **Web HTML:** `quarto render build/quarto --to html` (publicable en GitHub Pages).
   - **PDF impreso (`170 × 244 mm`, KDP/IngramSpark):** `scrbook` + *Libertinus Serif* +
     LuaLaTeX, verificado con `pdfinfo`.
   - **EPUB 3:** edición portátil con portada vectorial y validación de archivo.

## Uso

```bash
python -m pip install -r requirements.txt
export PYTHONPATH=tools                 # PowerShell: $env:PYTHONPATH = 'tools'

python -m libro check                   # valida mapa, revisión fijada, 48 posts y 18 casos
python -m pytest                        # ejecuta la batería de pruebas
cffconvert --validate                   # valida CITATION.cff

python -m libro json                    # exporta build/libro.json
python -m libro qmd                     # genera build/quarto/
python -m libro html                    # compila HTML en build/quarto/_book/
python -m libro pdf                     # compila build/libro-medicina-y-ciencia.pdf (LuaLaTeX)
python -m libro epub                    # compila build/libro-medicina-y-ciencia.epub (EPUB 3)
python -m libro all                     # compila HTML, PDF y EPUB
```

## Procedencia, cita y licencia

Consulte [docs/procedencia.md](docs/procedencia.md) para la trazabilidad de commits y DOI.
Use [CITATION.cff](CITATION.cff) para citar esta obra.

- Obra compilada y unidades del curso: [CC BY-NC-SA 4.0](LICENSE).
- Fichas del blog derivadas de MedSemiotics: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Código fuente (`tools/`, filtros Lua, preámbulo y workflows): [MIT](LICENSE-CODIGO).
