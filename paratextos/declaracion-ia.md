# Declaración de uso de inteligencia artificial y trazabilidad {#sec-declaracion-ia .unnumbered}

Esta publicación independiente adopta reglas verificables sobre evidencia clínica y uso de
herramientas computacionales:

1. **Fuente clínica única y verificable.** Ninguna cifra de sensibilidad, especificidad,
   cociente de verosimilitud ($\text{LR}^+$ o $\text{LR}^-$), intervalo de confianza ni
   probabilidad basal se genera con modelos de lenguaje. Todos los valores numéricos
   proceden de `medsemiotics-db` (DOI `10.5281/zenodo.22064424`, revisión fijada
   `ea2f6e63b8508e6a36a28fd11950bd28c0900a49`) y conservan su referencia primaria en
   PubMed o DOI. Cuando la literatura no documenta un cociente de verosimilitud o este no
   es medible por sesgo de incorporación, el texto lo declara explícitamente.
2. **Transparencia en la asistencia computacional.** Se emplearon herramientas de
   ingeniería asistida por IA exclusivamente para el andamiaje de compilación
   (`JSON → QMD → Quarto + LuaLaTeX / EPUB`), las pruebas automatizadas y la maquetación
   editorial. La salida de cualquier modelo de lenguaje se trata siempre como borrador
   sujeto a verificación determinista y revisión humana; nunca como fuente clínica.
3. **Privacidad clínica.** Todos los casos clínicos de esta obra son viñetas educativas
   ficticias o datos completamente anonimizados; no se emplean datos identificables de
   pacientes reales.
4. **Independencia editorial.** Esta obra es una publicación independiente y no implica
   aval, representación ni postura oficial de ninguna institución sanitaria o académica.
