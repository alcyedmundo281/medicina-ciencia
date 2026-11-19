# Procedencia de las fuentes clínicas y editoriales

Este repositorio compila el libro **Medicina y Ciencia: ciencia de datos, estadística
biomédica y semiótica clínica basada en la evidencia**, publicación independiente de acceso
abierto dirigida al público general, estudiantes y profesionales de la salud. Su DOI y su
ISBN están pendientes de asignación.

## Árboles de procedencia fijados

| Fuente | Repositorio | Revisión (commit) | DOI |
| :--- | :--- | :--- | :--- |
| Blog clínico y casos socráticos | `alcyedmundo281/medsemiotics` | `956f3b1aa0b6b38f728caa5d6fc9b201f192e053` | `10.5281/zenodo.22069641` |
| Base clínica de evidencia | `alcyedmundo281/medsemiotics-db` | `ea2f6e63b8508e6a36a28fd11950bd28c0900a49` | `10.5281/zenodo.22064424` |
| Arquitectura tipográfica y motor de compilación | `alcyedmundo281/neurology` y `alcyedmundo281/biosemiotics` | Plantilla Quarto + LuaLaTeX (`170 × 244 mm`) + EPUB 3 | — |

## Inventario trasladado

- **`posts/`**: 48 artículos de semiología cuantitativa (`HM6001` a `HM6048`), todos
  generados a partir de una única revisión fijada de `medsemiotics-db`.
- **`casos/`**: 18 casos socráticos en YAML (`HM6001.yaml` a `HM6044.yaml`), cuyos
  tokens de evidencia (`{{lr+ ...}}`, `{{sensibilidad ...}}`, `{{estado ...}}`) se
  resuelven en tiempo de compilación contra `posts/` mediante `tools/casos/`.
- **`assets/data/`**: índice `blog-index.json` (48 entradas), fichas JSON de los 48
  artículos (`assets/data/posts/`) y 18 casos JSON compilados (`assets/data/casos/`).
- **`unidades/`**: 4 capítulos metodológicos sobre inferencia diagnóstica, razonamiento
  bayesiano, lectura crítica de evidencia, datos clínicos e inteligencia artificial.

## Política de sincronización

Todas las fichas de `posts/` deben compartir la misma revisión de `medsemiotics-db`.
`python -m libro check` bloquea la compilación si se mezclan revisiones o si algún caso
socrático presenta tokens sin resolver.
