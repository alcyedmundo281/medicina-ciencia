# Declaración de uso de inteligencia artificial y trazabilidad {#sec-declaracion-ia .unnumbered}

Esta obra adopta de forma estricta las reglas éticas y metodológicas de la cátedra
*Medicina y Ciencia* y del ecosistema *PowerSemiotics*:

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
   sujeto a verificación determinista y revisión docente humana; nunca como fuente clínica.
3. **Asistente de la cátedra (`medsemiotics-copilot`).** En el aula, el asistente
   conversacional responde únicamente desde los artículos del blog y `medsemiotics-db`
   citando PMID/DOI, formula preguntas socráticas sin entregar las claves de evaluación y
   no recibe ni almacena datos personales de pacientes ni de estudiantes.
4. **Privacidad clínica.** Todo caso clínico y toda base de datos empleada en prácticas
   del curso está completamente anonimizada; se prohíbe cargar nombres, cédulas o
   identificadores de pacientes en cualquier herramienta digital.
