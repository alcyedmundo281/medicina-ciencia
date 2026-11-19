# Declaración de uso de inteligencia artificial y trazabilidad {#sec-declaracion-ia}

Esta publicación independiente adopta reglas verificables sobre evidencia clínica y uso de
herramientas computacionales:

1. **Fuente clínica única y verificable.** Ninguna cifra de sensibilidad, especificidad,
   cociente de verosimilitud ($\text{LR}^+$ o $\text{LR}^-$), intervalo de confianza ni
   probabilidad basal se genera con modelos de lenguaje. Todos los valores numéricos
   proceden de `medsemiotics-db` (DOI `10.5281/zenodo.22064424`, revisión fijada
   `ea2f6e63b8508e6a36a28fd11950bd28c0900a49`) y conservan su referencia primaria en
   PubMed o DOI. Cuando la literatura no documenta un cociente de verosimilitud o este no
   es medible por sesgo de incorporación, el texto lo declara explícitamente.
2. **Transparencia en la asistencia computacional.** En la preparación técnica y editorial
   de esta obra se emplearon herramientas de inteligencia artificial en las tareas que se
   declaran más abajo, y solo en ellas. La salida de cualquier modelo de lenguaje se trata
   siempre como borrador sujeto a verificación determinista y revisión humana; nunca como
   fuente clínica.
3. **Privacidad clínica.** Todos los casos clínicos de esta obra son viñetas educativas
   ficticias o datos completamente anonimizados; no se emplean datos identificables de
   pacientes reales.
4. **Independencia editorial.** Esta obra es una publicación independiente y no implica
   aval, representación ni postura oficial de ninguna institución sanitaria o académica.

## Qué hizo la inteligencia artificial {.unnumbered}

- **Andamiaje de compilación, pruebas y maquetación:** la tubería
  `JSON → QMD → Quarto + LuaLaTeX / EPUB`, sus pruebas automatizadas y el diseño tipográfico
  de las tres ediciones.
- **Auditoría técnica y editorial del repositorio** (19 de noviembre de 2026): revisión del
  código, de los metadatos y de la coherencia entre los paratextos y la base clínica, de la
  que salió una lista de correcciones que el autor priorizó.
- **Corrección de la capa de render:** cambios en `tools/libro/` y `assets/libro/` que
  modifican cómo se presentan los datos (tablas, casos socráticos, portada, coma decimal y
  espacio fino ante «%», composición de página), no los datos.
- **Propuestas de redacción de paratextos** (prefacio, portada, créditos y esta
  declaración), que el autor revisó y aprobó antes de incorporarlas.

## Qué no hizo la inteligencia artificial {.unnumbered}

- No generó ni modificó ninguna cifra clínica.
- No editó las fichas de `posts/`, que se derivan de `medsemiotics-db` en una revisión
  fijada; los errores que se detectan en los datos de origen se anotan para corregirlos en
  esa base, no en este libro.
- No redactó los capítulos.

## Herramienta, modelo y periodo {.unnumbered}

Desde el 19 de noviembre de 2026 se usa **Claude Code** con el modelo **Claude Opus 5.5**,
de Anthropic. Cada commit asistido lleva el trailer
`Asistido-por: Claude Code (Claude Opus 5.5)` y figura, con su hash, su fecha y su alcance,
en el [registro de uso de inteligencia artificial]({{URL_REGISTRO_IA}}), que se genera
desde el historial de git y puede comprobarse commit por commit. El andamiaje inicial del
repositorio, anterior a ese registro, se preparó con herramientas de ingeniería asistida por
inteligencia artificial; esos commits no llevan el trailer.

## Autoría y responsabilidad {.unnumbered}

La inteligencia artificial no es autora de esta obra y no puede serlo: no puede asumir
responsabilidad por lo que se afirma. Conforme a las recomendaciones del ICMJE y a las
orientaciones de COPE sobre herramientas de inteligencia artificial, el autor revisó y
aprobó todo el contenido y asume la responsabilidad íntegra de la obra, incluidas las
partes en cuya preparación intervino la inteligencia artificial.
