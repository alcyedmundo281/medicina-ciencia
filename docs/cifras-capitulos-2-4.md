# Cifras del compendio para los capítulos 2 a 4

Nota de trabajo para redactar los capítulos 2 a 4, hoy esquemas. No es texto del libro y no
lo compila ninguna orden. Las cifras se extrajeron con un script, sin reescribirlas, del
cuerpo de los `posts/` de cada caso ancla (`medsemiotics-db@ea2f6e63b850`); conservan el
formato de la ficha (punto decimal, «Valor: …; IC del 95 %: …»). La redacción y la elección
de cifras son del autor. Esta nota sobra cuando los capítulos estén escritos.

## Observaciones para decidir

Lo que cada caso ancla permite y no permite ilustrar, según los datos de su ficha:

- **2.1 Apendicitis (`HM:6043`).** Un solo hallazgo con LR medido (signo ecográfico,
  `pmid:34420255`); los otros cuatro no tienen LR. La ficha no da probabilidad basal, así
  que el cálculo pretest → postest necesitaría una previa que el libro no tiene.
- **2.2 Pancreatitis (`HM:6040`) y colecistitis (`HM:6042`).** Pancreatitis no tiene ningún
  LR medido; colecistitis, uno (`pmid:37855790`). Ninguna de las dos permite multiplicar
  cocientes ni mostrar la dependencia condicional con cifras. Fichas con varios LR de una
  misma fuente: `HM:6030` (nueve, `pmid:9786377`), `HM:6038` (seis, `pmid:26717031`),
  `HM:6007` (cinco, `pmid:26547467`), `HM:6036` (cinco, `pmid:28763554`).
- **2.3 TEP (`HM:6044`) y TVP (`HM:6035`).** TVP es la ficha más completa para umbrales:
  probabilidad basal, prevalencia por tramo de probabilidad clínica y LR− del dímero D, todo
  de `pmid:16403932`. TEP no da probabilidad basal.
- **3.1 SCA (`HM:6007`) y neumonía infantil (`HM:6036`).** Todos los LR traen IC 95 %;
  ninguno cruza 1,0. Un IC ancho que se acerca a 1: New Orleans Criteria en `HM:6038`
  (LR− 0.08; IC 0.01–0.84). Crepitantes en `HM:6036` figura como «sin efecto
  discriminativo», sin cifra.
- **3.2 Cáncer de mama (`HM:6034`).** Dos cifras de un único estudio (`pmid:10517431`):
  QUADAS-2 se aplicaría a una sola referencia.
- **3.3 Lesión intracraneal (`HM:6038`).** Cubre la sección: prevalencia, LR por hallazgo y
  LR− de dos reglas de decisión.
- **4.2 IAM (`HM:6030`).** Solo cocientes de verosimilitud. La ficha no tiene AUC,
  calibración ni validación externa: el caso no ilustra con cifras propias un modelo de
  predicción.
- **4.3 HTA (`HM:6029`).** LR+ y LR− de PA en consulta y AMPA (`pmid:34313682`), sin
  probabilidad basal: para frecuencias naturales haría falta una previa con fuente.

## Capítulo 2

### 2.1 · `HM:6043` Apendicitis aguda

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Signo ecográfico de apendicitis aguda (HM:3177) | LR medido | 0.85 (0.74 / 0.92) | 0.63 (0.56 / 0.7) | Valor: 2.29; IC del 95 %: 1.85 / 2.84; Referencia: pmid:34420255 | Valor: 0.24; IC del 95 %: 0.14 / 0.42; Referencia: pmid:34420255 | pmid:34420255 |
| Dolor en fosa ilíaca derecha (HM:0204) | no medido | — | — | — | — | — |
| Irritación peritoneal (HM:0601) | no medido | — | — | — | — | — |
| Leucocitosis (HM:0712) | no medido | — | — | — | — | — |
| Fiebre (HM:0101) | no medido | — | — | — | — | — |

Otras cifras de la ficha:

- *Notas de uso* — VARIABILIDAD SEGÚN OPERADOR Y PROTOCOLO: mientras que el POCUS general de urgencias reporta LR+ de 2.29 (pmid:34420255), los metaanálisis de ecografía reglada que excluyen casos indeterminados (Arruzza 2022, pmid:36130469) alcanzan sensibilidad de 82.1% (73.8-88.2) y especificidad de 85.9% (72.7-93.3).

### 2.2 · `HM:6040` Pancreatitis aguda

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Hiperlipasemia (HM:0732) | no medido | — | — | — | — | — |
| Hiperamilasemia (HM:0731) | no medido | — | — | — | — | — |
| Dolor epigástrico (HM:0202) | no medido | — | — | — | — | — |
| Vómitos (HM:0302) | no medido | — | — | — | — | — |
| Irritación peritoneal (HM:0601) | no medido | — | — | — | — | — |
| Signo de Cullen (HM:0611) | no medido | — | — | — | — | — |
| Hallazgos de imagen compatibles con pancreatitis (HM:0901) | no medido | — | — | — | — | — |

Otras cifras de la ficha:

- *Notas de uso* — LOS CRITERIOS DE ATLANTA NO ESTÁN AQUÍ COMO REGLA, solo descritos abajo en prosa. Una `regla` exige `ref` y su fuente es Atlanta 2012 (pmid:23100216), que ya está cotejada y sin errata pendiente, así que el validador no lo impide: falta registrar la regla.
- *Notas de uso* — Lo único cuantificado como criterio es la regla de Atlanta, que no es un cociente sino un criterio de clasificación: dice cuándo el diagnóstico está hecho, no cuánto se mueve la probabilidad con cada hallazgo. Además, la lipasa y la amilasa traen sensibilidad y especificidad (pmid:28431198).

### 2.2 · `HM:6042` Colecistitis aguda

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Signo ecográfico de colecistitis aguda (HM:3175) | LR medido | 0.709 (0.623 / 0.782) | 0.944 (0.882 / 0.975) | Valor: 12.7; IC del 95 %: 5.8 / 27.5; Referencia: pmid:37855790 | Valor: 0.31; IC del 95 %: 0.23 / 0.41; Referencia: pmid:37855790 | pmid:37855790 |
| Litiasis biliar en imagen (HM:0903) | no medido | — | — | — | — | — |
| Dolor en hipocondrio derecho (HM:0203) | no medido | — | — | — | — | — |
| Fiebre (HM:0101) | no medido | — | — | — | — | — |
| Leucocitosis (HM:0712) | no medido | — | — | — | — | — |
| Elevación de proteína C reactiva (HM:0761) | no medido | — | — | — | — | — |
| Irritación peritoneal (HM:0601) | no medido | — | — | — | — | — |

Otras cifras de la ficha:

- *Notas de uso* — CRITERIOS DE TOKIO 2018 (TG18, pmid:29032636): el diagnóstico definitivo requiere un ítem del grupo A (signos locales: Murphy o dolor/masa en CSD), uno del grupo B (signos sistémicos: fiebre, PCR > 10 mg/L o leucocitos > 10 000/µL) y un hallazgo confirmatorio del grupo C (ecografía: cálculo, pared engrosada > 3 mm, Murphy ecográfico, líquido perivesicular). La coexistencia de A + B establece sospecha diagnóstica.

### 2.3 · `HM:6044` Tromboembolia pulmonar

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Ventrículo derecho dilatado en ecografía (HM:3162) | LR medido | 0.53 (0.45 / 0.61) | 0.83 (0.74 / 0.9) | Valor: 3.12; IC del 95 %: 1.96 / 4.97; Referencia: pmid:28495379 | Valor: 0.57; IC del 95 %: 0.47 / 0.68; Referencia: pmid:28495379 | pmid:28495379 |
| Dímero D elevado (HM:3144) | LR medido | — | — | — | Valor: 0.08; IC del 95 %: 0.04 / 0.18; Referencia: pmid:16052017 | pmid:16052017 |
| Disnea (HM:0401) | no medido | — | — | — | — | — |
| Taquicardia (HM:0104) | no medido | — | — | — | — | — |
| Dolor torácico pleurítico (HM:3133) | no medido | — | — | — | — | — |
| Hipoxemia (HM:0110) | no medido | — | — | — | — | — |

### 2.3 · `HM:6035` Trombosis venosa profunda

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Dímero D elevado (HM:3144) | LR medido | — | — | — | Valor: 0.1; IC del 95 %: 0.03 / 0.37; Población: sospecha clínica baja, ensayo de alta sensibilidad; Nota: es la lectura que la conclusión de la fuente convierte en decisión; Referencia: pmid:16403932 | pmid:16403932 |

Otras cifras de la ficha:

- *Probabilidad basal* — Valor: 0.19; IC del 95 %: 0.16 / 0.23; Población: pacientes ambulatorios consecutivos y no seleccionados con sospecha clínica de TVP, sin antecedente de TVP previa salvo que el modelo lo incorporase; Referencia: pmid:16403932
- *Escalas* — Nombre: Regla de predicción clínica para TVP; Componentes declarados: el abstract no los enumera; catorce estudios con más de 8000 pacientes aplicaron una regla de predicción clínica antes del dímero D o la imagen; Tramos: Rango documentado: probabilidad clínica baja; Prevalencia: 0.05; Ic95 prevalencia: 0.04 / 0.08; Referencia: pmid:16403932 / Rango documentado: probabilidad clínica moderada; Prevalencia: 0.17; Ic95 prevalencia: 0.13 / 0.23; Referencia: pmid:16403932 / Rango documentado: probabilidad clínica alta; Prevalencia: 0.53; Ic95 prevalencia: 0.44 / 0.61; Referencia: pmid:16403932; Decisión: estimar la probabilidad clínica ANTES de pedir pruebas es lo que mejora la exactitud diagnóstica, según la conclusión de la fuente
- *Notas de uso* — Rendimiento agrupado del dímero D por estrato, con todos los ensayos combinados: sospecha baja, sensibilidad 88% (IC95% 81-92) y especificidad 72% (IC95% 65-78); sospecha moderada, sensibilidad 90% (IC95% 80-95) y especificidad 58% (IC95% 49-67); sospecha alta, sensibilidad 92% (IC95% 85-96) y especificidad 45% (IC95% 37-52).
- *Notas de uso* — La especificidad del dímero D cae según sube la probabilidad previa —72%, 58%, 45%—, que es la razón aritmética de que la fuente desaconseje apoyarse en él cuando la sospecha es alta.


## Capítulo 3

### 3.1 · `HM:6007` Síndrome coronario agudo

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Descenso del segmento ST (HM:3015) | LR medido | — | 0.95 | Valor: 5.3; IC del 95 %: 2.1 / 8.6; Referencia: pmid:26547467 | — | — |
| Signos de isquemia en el electrocardiograma (HM:3016) | LR medido | — | 0.91 | Valor: 3.6; IC del 95 %: 1.6 / 5.7; Referencia: pmid:26547467 | — | — |
| Prueba de esfuerzo previa anormal (HM:3017) | LR medido | — | 0.96 | Valor: 3.1; IC del 95 %: 2.0 / 4.7; Referencia: pmid:26547467 | — | — |
| Enfermedad arterial periférica (HM:3018) | LR medido | — | 0.97 | Valor: 2.7; IC del 95 %: 1.5 / 4.8; Referencia: pmid:26547467 | — | — |
| Dolor torácico irradiado a ambos brazos (HM:3014) | LR medido | — | 0.96 | Valor: 2.6; IC del 95 %: 1.8 / 3.7; Referencia: pmid:26547467 | — | — |
| Dolor torácico (HM:0206) | LR no medible | — | — | — | — | — |

Otras cifras de la ficha:

- *Probabilidad basal* — Valor: 0.1; Población: pacientes que acuden a urgencias con dolor torácico agudo; Referencia: pmid:26547467
- *Escalas* — Nombre: HEART; Componentes declarados: anamnesis, electrocardiograma, edad, factores de riesgo y primera troponina; Graduación: Parámetro: Puntuación HEART; Unidad: puntos; Lectura: disjunto; Tramos: Rango documentado: 7 a 10 (riesgo alto); Desde: 7; Hasta: 11; LR positivo: 13; IC del 95 %: 7.0 / 24; Referencia: pmid:26547467 / Rango documentado: 0 a 3 (riesgo bajo); Desde: 0; Hasta: 4; LR negativo: 0.2; IC del 95 %: 0.13 / 0.3; Referencia: pmid:26547467; Decisión: el instrumento más potente en ambos sentidos: confirma en el tramo alto y descarta en el bajo
- *Escalas* — Nombre: TIMI; Graduación: Parámetro: Puntuación TIMI; Unidad: puntos; Lectura: disjunto; Tramos: Rango documentado: 5 a 7 (riesgo alto); Desde: 5; Hasta: 8; LR positivo: 6.8; IC del 95 %: 5.2 / 8.9; Referencia: pmid:26547467 / Rango documentado: 0 a 1 (riesgo bajo); Desde: 0; Hasta: 2; LR negativo: 0.31; IC del 95 %: 0.23 / 0.43; Referencia: pmid:26547467
- *Escalas* — Nombre: Algoritmo de la Heart Foundation of Australia y la Cardiac Society of Australia and New Zealand; Tramos: Rango documentado: riesgo bajo a intermedio; LR negativo: 0.24; IC del 95 %: 0.19 / 0.31; Referencia: pmid:26547467

### 3.1 · `HM:6036` Neumonía infantil

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Hipoxemia (HM:0110) | LR medido | 0.64 | 0.77 | Valor: 2.8; IC del 95 %: 2.1 / 3.6; Umbral: saturación de oxígeno ≤ 96%; Referencia: pmid:28763554 | Valor: 0.47; IC del 95 %: 0.32 / 0.67; Umbral: saturación de oxígeno > 96%; Referencia: pmid:28763554 | — |
| Aumento del trabajo respiratorio (HM:3145) | LR medido | — | — | Valor: 2.1; IC del 95 %: 1.6 / 2.7; Nota: quejido, aleteo y tiraje medidos en conjunto, no por separado; Referencia: pmid:28763554 | — | — |
| Dolor torácico (HM:0206) | LR medido | — | — | Rango documentado: 1.5 / 5.5; Población: dos estudios que incluían adolescentes; Referencia: pmid:28763554 | — | — |
| Fiebre (HM:0101) | LR medido | — | — | Rango documentado: 1.7 / 1.8; Umbral: temperatura > 37.5 °C; Referencia: pmid:28763554 | — | — |
| Taquipnea (HM:0106) | LR medido | 0.79 | 0.51 | Valor: 1.5; IC del 95 %: 1.3 / 1.7; Umbral: frecuencia respiratoria > 40 por minuto; Referencia: pmid:28763554 | — | — |
| Crepitantes (HM:0406) | Sin efecto discriminativo | — | — | — | — | — |

Otras cifras de la ficha:

- *Probabilidad basal* — Rango documentado: 0.19 / 0.37; Población: niños con sospecha de neumonía: 19% (IC95% 11-31) en los estudios norteamericanos y 37% (IC95% 26-50) fuera de Norteamérica; Referencia: pmid:28763554; Nota: la previa cambia con el entorno asistencial, no es un rango de incertidumbre sobre un mismo valor; quien puebla un protocolo elige según dónde atiende

### 3.2 · `HM:6034` Cáncer de mama

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Masa mamaria palpable o hallazgo sospechoso en la exploración (HM:3142) | LR medido | 0.54 | 0.94 | Valor: 10.6; IC del 95 %: 5.8 / 19.2; Referencia: pmid:10517431 | — | — |
| Examen clínico de mama reglado normal (HM:3143) | LR medido | — | — | — | Valor: 0.47; IC del 95 %: 0.4 / 0.56; Referencia: pmid:10517431 | — |

### 3.3 · `HM:6038` Lesión intracraneal en el traumatismo craneal leve del adulto

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Signos de fractura de cráneo (HM:3049) | LR medido | — | 0.99 | Valor: 16; IC del 95 %: 3.1 / 59; Referencia: pmid:26717031 | — | — |
| Puntuación de Glasgow de 13 (HM:3050) | LR medido | — | 0.97 | Valor: 4.9; IC del 95 %: 2.8 / 8.5; Referencia: pmid:26717031 | — | — |
| Vómitos en dos o más episodios (HM:3052) | LR medido | — | 0.92 | Valor: 3.6; IC del 95 %: 3.1 / 4.1; Referencia: pmid:26717031 | — | — |
| Puntuación de Glasgow menor de 14 a las dos horas del traumatismo (HM:3152) | LR medido | — | — | Valor: 3.4; IC del 95 %: 1.4 / 8.4; Referencia: pmid:26717031 | — | — |
| Descenso de la puntuación de Glasgow (HM:3051) | LR medido | — | — | Rango documentado: 3.4 / 16; Población: entre los estudios que lo midieron; Referencia: pmid:26717031 | — | — |
| Peatón atropellado por vehículo (HM:3053) | LR medido | — | — | Rango documentado: 3.0 / 4.3; Población: entre los estudios que lo midieron; Referencia: pmid:26717031 | — | — |

Otras cifras de la ficha:

- *Probabilidad basal* — Valor: 0.071; IC del 95 %: 0.068 / 0.074; Población: adultos atendidos por traumatismo craneal leve, 23 079 pacientes; Referencia: pmid:26717031; Nota: es la prevalencia de lesión intracraneal GRAVE, que es el desenlace contra el que se leen todos los cocientes de esta condición. La fuente publica además un desenlace más estrecho —lesión mortal o que requiere neurocirugía— con prevalencia del 0.9% (IC95% 0.78-1.0), y esos cocientes NO son los de aquí
- *Escalas* — Nombre: Canadian CT Head Rule; Componentes declarados: el abstract no los enumera; el Glasgow menor de 14 a las dos horas es uno de ellos, y la corrección de este artículo cambió justo ese corte; Tramos: Rango documentado: regla negativa (ningún criterio presente); LR negativo: 0.04; Ic95 negativo: 0 / 0.65; Referencia: pmid:26717031; Nota: el límite inferior del intervalo es 0, como lo publica la fuente; Decisión: es el cociente negativo más fuerte de la condición: una regla canadiense negativa hace la lesión intracraneal muy improbable
- *Escalas* — Nombre: New Orleans Criteria; Componentes declarados: el abstract no los enumera; la amnesia de más de 30 minutos es uno de ellos; Tramos: Rango documentado: criterios ausentes; LR negativo: 0.08; Ic95 negativo: 0.01 / 0.84; Referencia: pmid:26717031; Decisión: descarta con fuerza, aunque algo menos que la regla canadiense y con un intervalo que llega hasta 0.84
- *Notas de uso* — Todos los cocientes se leen contra la LESIÓN INTRACRANEAL GRAVE, prevalencia 7.1%. El desenlace más estrecho de la fuente —lesión mortal o quirúrgica, 0.9%— tiene sus propias cifras y no son éstas.
- *Notas de uso* — El valor de esta condición está en sus cocientes NEGATIVOS. Con una prevalencia previa del 7.1%, una regla canadiense negativa (LR 0.04) deja una probabilidad posterior por debajo del 0.4%, que es lo que sostiene la decisión de no pedir la tomografía.


## Capítulo 4

### 4.2 · `HM:6030` Infarto agudo de miocardio

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Elevación nueva del segmento ST en el ECG (HM:3130) | LR medido | — | — | Valor: 22.0; IC del 95 %: 5.7 / 53.9; Referencia: pmid:9786377 | — | — |
| Nueva onda Q patológica en el ECG (HM:3131) | LR medido | — | — | Valor: 11.0; IC del 95 %: 5.3 / 24.8; Referencia: pmid:9786377 | — | — |
| Dolor torácico irradiado a ambos brazos (HM:3014) | LR medido | — | — | Valor: 7.1; IC del 95 %: 3.5 / 14.2; Referencia: pmid:9786377 | — | — |
| Tercer tono cardíaco (R3) (HM:3132) | LR medido | — | — | Valor: 3.2; IC del 95 %: 1.6 / 6.5; Referencia: pmid:9786377 | — | — |
| Hipotensión arterial (HM:0109) | LR medido | — | — | Valor: 3.1; IC del 95 %: 1.6 / 6.2; Referencia: pmid:9786377 | — | — |
| Dolor torácico pleurítico (HM:3133) | LR medido | — | — | Valor: 0.2; IC del 95 %: 0.1 / 0.4; Referencia: pmid:9786377 | — | pmid:9786377 |
| Dolor torácico reproducible a la palpación (HM:3134) | LR medido | — | — | Valor: 0.3; IC del 95 %: 0.2 / 0.4; Referencia: pmid:9786377 | — | pmid:9786377 |
| Dolor torácico punzante o cortante (HM:3135) | LR medido | — | — | Valor: 0.3; IC del 95 %: 0.1 / 0.6; Referencia: pmid:9786377 | — | pmid:9786377 |
| Dolor torácico posicional (HM:3136) | LR medido | — | — | Valor: 0.3; IC del 95 %: 0.1 / 0.7; Referencia: pmid:9786377 | — | pmid:9786377 |

### 4.3 · `HM:6029` Hipertensión arterial en adultos

| Hallazgo | Estado del LR | Sensibilidad (IC 95 %) | Especificidad (IC 95 %) | LR+ | LR− | Referencia |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Presión arterial en consulta mayor o igual a 140/90 mmHg (HM:3127) | LR medido | — | — | Valor: 4.2; IC del 95 %: 2.9 / 6.1; Referencia: pmid:34313682 | Valor: 0.56; IC del 95 %: 0.46 / 0.68; Referencia: pmid:34313682 | — |
| Automonitorización domiciliaria (AMPA) mayor o igual a 135/85 mmHg (HM:3128) | LR medido | — | — | Valor: 3.1; IC del 95 %: 2.3 / 4.2; Referencia: pmid:34313682 | Valor: 0.33; IC del 95 %: 0.24 / 0.46; Referencia: pmid:34313682 | — |

