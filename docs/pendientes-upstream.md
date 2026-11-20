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

## Área «Medicina Interna» asignada por defecto

30 de las 48 condiciones llevan `category: medicina_interna` («Medicina Interna»). En la
mayoría no corresponde: casi todas son de la serie `HM:6016`–`HM:6048`, lo que sugiere un
valor por defecto del generador. El libro imprime ese campo en la cabecera de cada capítulo
(«**Área:** Medicina Interna») y en el mapa maestro, así que el error se ve en la obra.

El libro no lo corrige: el área es un dato de la ficha. Las condiciones afectadas, por la
parte del libro en que están:

| Parte del libro | Condiciones con «Medicina Interna» |
| :--- | :--- |
| Urgencias, medicina crítica y aparato cardiovascular | `HM:6026` Insuficiencia aórtica, `HM:6029` Hipertensión arterial en adultos, `HM:6030` Infarto agudo de miocardio, `HM:6035` Trombosis venosa profunda, `HM:6037` Sobrecarga de volumen, `HM:6044` Tromboembolia pulmonar, `HM:6045` Taponamiento cardíaco |
| Abdomen agudo, gastroenterología y hepatología | `HM:6040` Pancreatitis aguda, `HM:6042` Colecistitis aguda, `HM:6043` Apendicitis aguda, `HM:6046` Síndrome ascítico, `HM:6047` Síndrome esplenomegálico |
| Infectología, neumología, inmunología y endocrinología | `HM:6028` Alergia a penicilina, `HM:6041` Absceso de partes blandas, `HM:6048` Bocio |
| Neurología, oftalmología y salud mental | `HM:6017` Conjuntivitis bacteriana, `HM:6018` Apnea obstructiva del sueño, `HM:6022` Glaucoma primario de ángulo abierto, `HM:6023` Conmoción cerebral pediátrica, `HM:6031` Trastorno de ansiedad generalizada, `HM:6032` Trastorno de pánico, `HM:6038` Lesión intracraneal en el TCE leve del adulto, `HM:6039` Trastorno de estrés postraumático |
| Pediatría, obstetricia, oncología y dermatología | `HM:6016` Embarazo ectópico, `HM:6024` Maltrato físico infantil, `HM:6025` Hipertensión arterial secundaria pediátrica, `HM:6033` Melanoma cutáneo, `HM:6034` Cáncer de mama, `HM:6036` Neumonía infantil |
| Aparato locomotor y traumatología | `HM:6027` Rotura del ligamento cruzado anterior |

Los casos más claros son los que no son de medicina interna en ningún sentido: embarazo
ectópico (obstetricia), glaucoma y conjuntivitis (oftalmología), rotura del LCA
(traumatología), maltrato físico infantil, neumonía infantil, HTA secundaria pediátrica y
conmoción cerebral pediátrica (pediatría), melanoma (dermatología), cáncer de mama
(oncología o mastología), ansiedad, pánico y TEPT (psiquiatría), apendicitis y colecistitis
(cirugía). En los cardiovasculares y digestivos «Medicina Interna» no es falso, pero rompe
la convención de las demás fichas («Cardiología», «Gastroenterología»).

Propuesta: revisar `category` y `category_label` de esas 30 condiciones en
`medsemiotics-db` y que el generador no asigne un área por defecto.

La parte del libro en que va cada condición sí es de este repositorio (`mapa.yaml`). Allí
había un error propio: la apnea obstructiva del sueño (`HM:6018`) estaba en «Pediatría,
obstetricia, oncología y dermatología», aunque la ficha no trata de población pediátrica ni
obstétrica (su prevalencia procede de cribado comunitario y de unidades de sueño,
`pmid:23989984`). Por decisión del autor pasa a «Neurología, oftalmología y salud mental».
