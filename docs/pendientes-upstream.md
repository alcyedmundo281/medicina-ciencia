# Pendientes para `medsemiotics-db`

Datos de origen que este libro no corrige: los `posts/*.md` derivan de
`alcyedmundo281/medsemiotics-db@ea2f6e63b850` y no se editan a mano. Cada punto se resuelve en
esa base y llega al libro al regenerar los posts.

## Conclusión de la fuente sin referencia declarada

El campo `conclusion_de_la_fuente` no dice de qué referencia procede. El libro lo presenta en
«Dónde NO confiar» como cita literal y solo da el PMID cuando la ficha declara una única
referencia (23 de 38 condiciones). En las 15 restantes la ficha declara varias y el libro no
elige una: imprime «la ficha no declara de qué referencia procede».

Propuesta: añadir a cada condición un campo con la referencia de la conclusión (por ejemplo
`conclusion_de_la_fuente_ref: 'pmid:…'`) y que el generador del blog lo publique.

| Condición | Nombre | Referencias declaradas | PMID candidatos |
| :--- | :--- | :--- | :--- |
| `HM:6010` | Síncope cardíaco | 4 | `pmid:12239256`, `pmid:29136314`, `pmid:31237649`, `pmid:33382159` |
| `HM:6020` | Intubación difícil | 4 | `pmid:18362772`, `pmid:19194154`, `pmid:19735399`, `pmid:30721300` |
| `HM:6037` | Sobrecarga de volumen | 2 | `pmid:22392031`, `pmid:41729549` |
| `HM:6044` | Tromboembolia pulmonar | 8 | `pmid:10737280`, `pmid:16052017`, `pmid:16403932`, `pmid:19679614`, `pmid:28495379`, `pmid:31340984`, `pmid:38263123`, `pmid:9786377` |
| `HM:6045` | Taponamiento cardíaco | 2 | `pmid:35696801`, `pmid:41729549` |
| `HM:6040` | Pancreatitis aguda | 6 | `pmid:23100216`, `pmid:25088919`, `pmid:26844279`, `pmid:27820614`, `pmid:28431198`, `pmid:6237447` |
| `HM:6042` | Colecistitis aguda | 10 | `pmid:20138397`, `pmid:2017956`, `pmid:29032636`, `pmid:33517707`, `pmid:35258527`, `pmid:37838525`, `pmid:37855790`, `pmid:38037062`, `pmid:41928009`, `pmid:8480871` |
| `HM:6043` | Apendicitis aguda | 11 | `pmid:2239906`, `pmid:24113477`, `pmid:28826614`, `pmid:2934762`, `pmid:30293146`, `pmid:31743429`, `pmid:33688952`, `pmid:34420255`, `pmid:35100766`, `pmid:3538138`, `pmid:36130469` |
| `HM:6009` | Faringitis estreptocócica | 7 | `pmid:11147989`, `pmid:20696723`, `pmid:21631919`, `pmid:25774295`, `pmid:25822555`, `pmid:6763125`, `pmid:9475915` |
| `HM:6011` | Infección precoz por VIH | 3 | `pmid:25027143`, `pmid:27929264`, `pmid:33000916` |
| `HM:6041` | Absceso de partes blandas | 3 | `pmid:28073795`, `pmid:32081383`, `pmid:34379709` |
| `HM:6021` | Trastorno por consumo de alcohol | 5 | `pmid:28260680`, `pmid:30054643`, `pmid:30689217`, `pmid:32213910`, `pmid:38592385` |
| `HM:6023` | Conmoción cerebral pediátrica | 4 | `pmid:18441863`, `pmid:23055768`, `pmid:27144627`, `pmid:41941197` |
| `HM:6016` | Embarazo ectópico | 7 | `pmid:16308901`, `pmid:18441863`, `pmid:23055768`, `pmid:23262929`, `pmid:23613077`, `pmid:27144627`, `pmid:36063623` |
| `HM:6019` | Luxación de cadera en el lactante | 2 | `pmid:38355007`, `pmid:38619828` |

## Serialización ambigua del generador del blog

`tools/generate_topic.py::render_value` aplana diccionarios y listas anidadas en una sola
línea («Nombre: …; Tramos: …; Decisión: …»), de modo que no se sabe a qué nivel pertenece
cada campo. El libro lee esas secciones (Escalas, Reglas clínicas, Núcleo diagnóstico,
Balance de criterios) de una copia fijada y verificada de la base
(`assets/data/medsemiotics-db/`). Si el generador emitiera la estructura, esa copia
sobraría.

## Etiquetas que faltan en el generador

Claves sin etiqueta en `LABELS`, que el blog muestra con la forma automática:
`ic95_negativo` («Ic95 negativo»), `apoyos_minimos` y `banderas_maximas` (sin tilde).
