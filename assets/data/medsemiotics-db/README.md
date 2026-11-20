# Copia fijada de `medsemiotics-db`

Copia literal (byte a byte) de los archivos de condición de
[`alcyedmundo281/medsemiotics-db`](https://github.com/alcyedmundo281/medsemiotics-db) en la
revisión `ea2f6e63b8508e6a36a28fd11950bd28c0900a49`, la misma de la que derivan los
`posts/*.md`.

Solo están las condiciones cuyas secciones «Escalas», «Reglas clínicas», «Núcleo
diagnóstico» y «Balance de criterios» el generador del blog serializa de forma ambigua. El
libro las lee de aquí para presentarlas como tablas.

- **No se editan.** Un error en estos datos se corrige en `medsemiotics-db` y se anota en
  [`docs/pendientes-upstream.md`](../../../docs/pendientes-upstream.md).
- **Se verifican al compilar.** `tools/libro/fuente.py` compara el sha256 de cada archivo con
  el que declara el front-matter del post (`fuente.archivos`). Si no coincide, la
  compilación se detiene.
- **Se comprueban contra el post.** Cada bloque solo se convierte en tabla si al
  reserializarlo como lo hace el blog reproduce exactamente el texto del post. Si no, se
  deja el texto original.
- `.gitattributes` los marca `-text` para que Git no cambie sus finales de línea.

Para actualizar a otra revisión, los archivos se copian de nuevo desde esa revisión junto
con los `posts/` regenerados. Nunca se retocan a mano.
