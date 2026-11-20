"""Presentación de las fichas derivadas de ``medsemiotics-db`` (solo capa de render).

Los ``posts/*.md`` son derivados de una revisión fijada y no se editan. Aquí solo se cambia
cómo se *muestran*:

* Los registros que el generador del blog serializa en prosa («Clave: valor; Clave: valor»)
  se convierten en tablas, **solo** cuando el texto se puede reconstruir sin pérdida: o bien a
  partir de los datos estructurados del front-matter (``evidencia``), o bien porque el registro
  es plano y su reserialización reproduce el texto original carácter por carácter. Si la
  reconstrucción no es exacta, el bloque se deja intacto: nunca se adivina una estructura.
* Los números se escriben con coma decimal y espacio fino antes de «%», sin tocar PMID, DOI,
  códigos, enlaces ni las referencias bibliográficas.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

# --- Reserialización idéntica a la del generador del blog -----------------------------------
# Copia de ``LABELS`` y de la lógica de ``render_value`` de
# alcyedmundo281/medsemiotics ``tools/generate_topic.py``. Solo se usa para *comprobar* que una
# línea del post corresponde exactamente a un dato estructurado; no produce texto publicado.

ETIQUETAS_BLOG: dict[str, str] = {
    "termino_en": "Nombre en inglés", "sinonimos": "Sinónimos",
    "codigos": "Códigos", "probabilidad_base": "Probabilidad basal",
    "factores_riesgo": "Factores de riesgo", "signos": "Hallazgos clínicos",
    "signos_de_alarma": "Signos de alarma", "nucleo": "Núcleo diagnóstico",
    "balance": "Balance de criterios", "reglas": "Reglas clínicas",
    "modificadores": "Modificadores", "escalas": "Escalas",
    "notas_de_uso": "Notas de uso", "conclusion_de_la_fuente": "Conclusión de la fuente",
    "pendiente": "Aspectos pendientes de documentación", "discrepancias": "Discrepancias entre fuentes",
    "no_emitidos": "Relaciones no incorporadas y sus motivos",
    "lr_positivo": "LR positivo", "lr_negativo": "LR negativo",
    "ic95": "IC del 95 %", "ref": "Referencia", "rango": "Rango documentado",
    "valor": "Valor", "estado_lr": "Estado del LR", "concepto": "Hallazgo",
    "poblacion": "Población", "umbral": "Umbral", "decision": "Decisión",
    "advertencia": "Advertencia", "motivo": "Motivo", "nota": "Nota",
    "sensibilidad": "Sensibilidad", "especificidad": "Especificidad",
    "graduacion": "Graduación", "parametro": "Parámetro",
}


def etiqueta_blog(clave: str) -> str:
    return ETIQUETAS_BLOG.get(clave, clave.replace("_", " ").capitalize())


def serializar_como_blog(valor: Any) -> str:
    """Réplica de ``render_value`` sin la sustitución de identificadores ``HM:`` (prosa)."""
    if valor is None:
        return "No documentado."
    if isinstance(valor, dict):
        return "; ".join(f"{etiqueta_blog(k)}: {serializar_como_blog(v)}" for k, v in valor.items())
    if isinstance(valor, list):
        return " / ".join(serializar_como_blog(v) for v in valor) if valor else "No documentado."
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return str(valor).strip()


# --- Formato numérico --------------------------------------------------------------------

ESPACIO_FINO = "\u202f"  # espacio fino de no separación (U+202F) antes de «%»

_PROTEGIDOS = re.compile(
    r"`[^`\n]*`"  # código en línea (PMID, HM:, DOI, revisiones)
    r"|\]\([^)\s]*\)"  # destino de enlaces e imágenes
    r"|<https?://[^>\s]+>"  # autoenlaces
    r"|https?://[^\s)>\]]+"  # URL sueltas
    r"|\b10\.\d{4,9}/\S+"  # DOI sin enlace
    r"|\b(?:pmid|PMID|doi|DOI|HM)[: ]\s?[\w./-]+"  # identificadores con prefijo
    r"|\{[^}\n]*\}"  # atributos Pandoc/Quarto ({#sec-…}, {tbl-colwidths=…})
    r"|\bPregunta \d+(?:\.\d+)+"  # numeración de las preguntas de los casos («Pregunta 1.2»)
)
_DECIMAL = re.compile(r"(?<![\w.,:])(\d+)\.(\d+)(?![\w]|[.,]\d)")
_PORCENTAJE = re.compile(r"(?<![\w.,])(\d+(?:,\d+)?)[ \u00a0\u2009\u202f]?%")


def _formatear_fragmento(texto: str) -> str:
    texto = _DECIMAL.sub(r"\1,\2", texto)
    return _PORCENTAJE.sub(lambda m: f"{m.group(1)}{ESPACIO_FINO}%", texto)


def formatear_numeros(texto: str) -> str:
    """Coma decimal y espacio fino antes de «%» fuera de los fragmentos protegidos."""
    partes: list[str] = []
    inicio = 0
    for m in _PROTEGIDOS.finditer(texto):
        partes.append(_formatear_fragmento(texto[inicio : m.start()]))
        partes.append(m.group(0))
        inicio = m.end()
    partes.append(_formatear_fragmento(texto[inicio:]))
    return "".join(partes)


def formatear_markdown(texto: str) -> str:
    """Aplica :func:`formatear_numeros` salvo en bloques de código y en listas de referencias.

    Las referencias bibliográficas citan títulos en su idioma original: no se reescriben.
    """
    salida: list[str] = []
    en_codigo = False
    en_referencias = False
    for linea in texto.split("\n"):
        if linea.startswith("```"):
            en_codigo = not en_codigo
            salida.append(linea)
            continue
        encabezado = re.match(r"^(#{1,4}) (.+)$", linea)
        if encabezado and not en_codigo:
            en_referencias = encabezado.group(2).startswith("Referencias y procedencia")
        if linea.startswith("**Referencias del caso:**"):
            en_referencias = True
        elif en_referencias and linea.strip() == ":::":
            en_referencias = False
        salida.append(linea if (en_codigo or en_referencias) else formatear_numeros(linea))
    return "\n".join(salida)


def porcentaje(valor: Any) -> str:
    """Proporción 0–1 como porcentaje con coma decimal (mínimo un decimal, sin perder precisión)."""
    d = Decimal(str(valor)) * 100
    d = d.normalize()
    if d.as_tuple().exponent >= 0:
        texto = f"{d:.1f}"
    else:
        texto = format(d, "f")
    return texto.replace(".", ",") + f"{ESPACIO_FINO}%"


def rango_porcentaje(a: Any, b: Any) -> str:
    """«32,0–43,0 %»: un solo signo de porcentaje al final del rango."""
    return f"{porcentaje(a).removesuffix(ESPACIO_FINO + '%')}–{porcentaje(b)}"


def _es_proporcion(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and 0 <= valor <= 1


def _numero(valor: Any) -> str:
    return str(valor).replace(".", ",") if isinstance(valor, (int, float)) else str(valor)


def rango_humano(desde: Any, hasta: Any, unidad: str | None = None) -> str:
    """Intervalo semiabierto ``[desde, hasta)`` en lenguaje humano.

    Con enteros (puntuaciones) el extremo superior es ``hasta − 1``: ``[7, 11)`` → «7–10 puntos».
    Con valores continuos se usan desigualdades: ``[1000, ∞)`` → «≥ 1000 mIU/mL».
    """
    sufijo = f" {unidad}" if unidad else ""
    enteros = all(isinstance(v, int) and not isinstance(v, bool) for v in (desde, hasta) if v is not None)
    if desde is not None and hasta is not None:
        if enteros:
            superior = hasta - 1
            if superior == desde:
                return f"{desde}{sufijo}"
            return f"{desde}–{superior}{sufijo}"
        return f"≥ {_numero(desde)} y < {_numero(hasta)}{sufijo}"
    if desde is not None:
        return f"≥ {_numero(desde)}{sufijo}"
    if hasta is not None:
        return f"≤ {hasta - 1}{sufijo}" if enteros else f"< {_numero(hasta)}{sufijo}"
    return "—"


# --- Tablas ------------------------------------------------------------------------------

_CLAVES_PROPORCION = {"sensibilidad", "especificidad", "prevalencia"}
_CLAVES_TEXTO = {"nota", "decision", "umbral", "umbral_condicion", "rango", "poblacion", "advertencia"}
_CLAVES_ETIQUETA_TRAMO = ("umbral", "umbral_condicion", "rango")


def _celda(texto: str) -> str:
    return texto.replace("|", "\\|").replace("\n", " ")


def _valor_celda(clave: str, valor: Any) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, tuple):  # (valor, [inferior, superior]) de _fusionar_intervalos
        cifra, (inferior, superior) = valor
        return f"{_valor_celda(clave, cifra)} ({_numero(inferior)}–{_numero(superior)})"
    if clave in ("ref", "ref_rendimiento") and isinstance(valor, str):
        return f"`{valor}`"
    if isinstance(valor, list) and len(valor) == 2 and all(isinstance(v, (int, float)) for v in valor):
        if clave in _CLAVES_PROPORCION or clave.startswith("prevalencia"):
            return rango_porcentaje(valor[0], valor[1])
        return f"{_numero(valor[0])}–{_numero(valor[1])}"
    if (clave in _CLAVES_PROPORCION or clave.startswith("prevalencia")) and _es_proporcion(valor):
        return porcentaje(valor)
    return _celda(serializar_como_blog(valor))


def _destino_ic(tramo: dict[str, Any], clave_ic: str) -> str | None:
    """LR al que pertenece un intervalo de la fila, o ``None`` si es ambiguo."""
    if clave_ic == "ic95_negativo":
        return "lr_negativo" if "lr_negativo" in tramo else None
    tiene_pos, tiene_neg = "lr_positivo" in tramo, "lr_negativo" in tramo
    if tiene_pos and (not tiene_neg or "ic95_negativo" in tramo):
        return "lr_positivo"
    if tiene_neg and not tiene_pos:
        return "lr_negativo"
    return None


def _fusionar_intervalos(tramos: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    """Pone cada IC junto a su LR («13 (7,0–24)»), como en la síntesis cuantitativa.

    Solo si en *todas* las filas el LR de destino es inequívoco; si no, ``None``.
    """
    fusionados = []
    for tramo in tramos:
        nuevo = dict(tramo)
        for clave_ic in ("ic95", "ic95_negativo"):
            if clave_ic not in tramo:
                continue
            ic = tramo[clave_ic]
            destino = _destino_ic(tramo, clave_ic)
            if destino is None or not (isinstance(ic, list) and len(ic) == 2):
                return None
            nuevo[destino] = (tramo[destino], ic)
            del nuevo[clave_ic]
        fusionados.append(nuevo)
    return fusionados


def tabla_tramos(tramos: list[dict[str, Any]], unidad: str | None = None) -> str:
    """Tabla Markdown de una lista de tramos de un hallazgo o escala."""
    tramos = _fusionar_intervalos(tramos) or tramos
    claves: list[str] = []
    for tramo in tramos:
        for clave in tramo:
            if clave not in claves:
                claves.append(clave)
    if "ref" in claves:  # la referencia, siempre en la última columna
        claves = [c for c in claves if c != "ref"] + ["ref"]
    tiene_etiqueta = any(c in claves for c in _CLAVES_ETIQUETA_TRAMO)
    columnas = [c for c in claves if not (tiene_etiqueta and c in ("desde", "hasta"))]
    if not tiene_etiqueta and ("desde" in claves or "hasta" in claves):
        columnas = ["__rango__"] + [c for c in columnas if c not in ("desde", "hasta")]

    def titulo(clave: str) -> str:
        if clave == "__rango__":
            return "Tramo"
        if clave in ("umbral", "umbral_condicion"):
            return "Umbral"
        if clave == "ref":
            return "Ref."
        if clave == "ic95_negativo":  # sin etiqueta en el blog («Ic95 negativo»)
            return "IC del 95 % (LR−)"
        return etiqueta_blog(clave)

    lineas = [
        "| " + " | ".join(titulo(c) for c in columnas) + " |",
        "| " + " | ".join(":---" for _ in columnas) + " |",
    ]
    for tramo in tramos:
        celdas = []
        for c in columnas:
            if c == "__rango__":
                celdas.append(rango_humano(tramo.get("desde"), tramo.get("hasta"), unidad))
            else:
                celdas.append(_valor_celda(c, tramo.get(c)) if c in tramo else "—")
        lineas.append("| " + " | ".join(celdas) + " |")
    pesos = [3.0 if c in _CLAVES_TEXTO else 1.9 if c == "ref" else 1.3 for c in columnas]
    anchos = [round(100 * p / sum(pesos)) for p in pesos]
    anchos[-1] += 100 - sum(anchos)
    lineas += ["", f': {{tbl-colwidths="[{",".join(str(a) for a in anchos)}]"}}']
    return "\n".join(lineas)


# Registros planos de secciones del post: solo estas claves, en este orden de lectura.
_CLAVES_CODIGOS = {"Snomed": "SNOMED CT", "Cie10": "CIE-10"}
_CLAVES_PROBABILIDAD = {
    "Valor": "Probabilidad basal",
    "Rango documentado": "Rango documentado",
    "IC del 95 %": "IC del 95 %",
    "Población": "Población",
    "Nota": "Nota",
    "Referencia": "Referencia",
}


def leer_registro_plano(texto: str, claves: dict[str, str]) -> list[tuple[str, str]] | None:
    """Separa «Clave: valor; Clave: valor» con claves conocidas; ``None`` si no es exacto.

    Un segmento que no empieza por una clave conocida es continuación del valor anterior (el
    generador no escapa los «;» internos). La lectura solo se acepta si reconstruye el texto.
    """
    campos: list[list[str]] = []
    for segmento in texto.split("; "):
        m = re.match(r"^([^:]+): (.*)$", segmento, re.DOTALL)
        if m and m.group(1) in claves:
            campos.append([m.group(1), m.group(2)])
        elif campos:
            campos[-1][1] += "; " + segmento
        else:
            return None
    if "; ".join(f"{k}: {v}" for k, v in campos) != texto:
        return None
    if len({k for k, _ in campos}) != len(campos):
        return None
    return [(k, v) for k, v in campos]


def _par_numerico(valor: str) -> tuple[float, float] | None:
    m = re.fullmatch(r"(\d+(?:\.\d+)?) / (\d+(?:\.\d+)?)", valor)
    return (float(m.group(1)), float(m.group(2))) if m else None


def _texto_proporcion(texto: str) -> str:
    try:
        x = float(texto)
    except ValueError:
        return _celda(texto)
    return porcentaje(Decimal(texto)) if 0 <= x <= 1 else _celda(texto)


def tabla_codigos(campos: list[tuple[str, str]]) -> str:
    lineas = ["| Sistema | Código |", "| :--- | :--- |"]
    lineas += [
        f"| {_CLAVES_CODIGOS[k]} | {'No documentado' if v == 'No documentado.' else f'`{v}`'} |"
        for k, v in campos
    ]
    return "\n".join(lineas)


def tabla_probabilidad(campos: list[tuple[str, str]]) -> str:
    lineas = ["| Dato | Valor |", "| :--- | :--- |"]
    for clave, valor in campos:
        if clave == "Valor":
            celda = _texto_proporcion(valor)
        elif clave in ("IC del 95 %", "Rango documentado") and _par_numerico(valor):
            a, b = valor.split(" / ")
            celda = (
                rango_porcentaje(Decimal(a), Decimal(b))
                if all(0 <= float(x) <= 1 for x in (a, b))
                else f"{_celda(a)}–{_celda(b)}"
            )
        elif clave == "Referencia" and re.fullmatch(r"[\w.:/-]+", valor):
            celda = f"`{valor}`"
        else:
            celda = _celda(valor)
        lineas.append(f"| {_CLAVES_PROBABILIDAD[clave]} | {celda} |")
    lineas += ["", ': {tbl-colwidths="[24,76]"}']
    return "\n".join(lineas)


# --- Cuerpo del post ---------------------------------------------------------------------

_SECCION_RE = re.compile(r"^## (.+)$", re.MULTILINE)
_HALLAZGO_RE = re.compile(r"^### .*\((HM:\d+)\)\s*$")
_LINEA_ETIQUETADA_RE = re.compile(r"^\*\*([^*]+):\*\* (.+)$")
_CAMPOS_EN_TABLA = {"tramos"}  # campos de hallazgo que se muestran como tabla


def presentar_cuerpo(cuerpo: str, evidencia: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> tuple[str, dict[str, int]]:
    """Devuelve el cuerpo con los registros serializados convertidos en tablas y un recuento."""
    por_concepto = {str(ev.get("concepto")): ev for ev in evidencia}
    recuento = {"codigos": 0, "probabilidad_basal": 0, "tramos": 0}
    salida: list[str] = []
    seccion = ""
    hallazgo: dict[str, Any] | None = None
    for linea in cuerpo.split("\n"):
        m_sec = _SECCION_RE.match(linea)
        if m_sec:
            seccion = m_sec.group(1).strip()
            hallazgo = None
            salida.append(linea)
            continue
        m_h = _HALLAZGO_RE.match(linea)
        if m_h:
            hallazgo = por_concepto.get(m_h.group(1))
            salida.append(linea)
            continue

        if seccion == "Códigos" and linea.strip():
            campos = leer_registro_plano(linea.strip(), _CLAVES_CODIGOS)
            if campos:
                salida.append(tabla_codigos(campos))
                recuento["codigos"] += 1
                continue
        if seccion == "Probabilidad basal" and linea.strip():
            campos = leer_registro_plano(linea.strip(), _CLAVES_PROBABILIDAD)
            if campos:
                salida.append(tabla_probabilidad(campos))
                recuento["probabilidad_basal"] += 1
                continue
        if hallazgo is not None:
            m_l = _LINEA_ETIQUETADA_RE.match(linea)
            if m_l:
                for clave in _CAMPOS_EN_TABLA:
                    valor = hallazgo.get(clave)
                    if (
                        isinstance(valor, list)
                        and m_l.group(1) == etiqueta_blog(clave)
                        and serializar_como_blog(valor) == m_l.group(2)
                    ):
                        unidad = (hallazgo.get("graduacion") or {}).get("unidad")
                        salida.append(f"**{etiqueta_blog(clave)}:**")
                        salida.append("")
                        salida.append(tabla_tramos(valor, unidad))
                        recuento[clave] += 1
                        break
                else:
                    salida.append(linea)
                continue
        salida.append(linea)
    return "\n".join(salida), recuento


# --- Escalas, reglas, núcleo y balance (desde la copia fijada de medsemiotics-db) ----------
# Su serialización en el post es ambigua (no se sabe a qué nivel pertenece cada campo), así
# que se leen del YAML fijado (``libro.fuente``). La sección solo se sustituye si el YAML,
# serializado como lo hace el blog (con los ``HM:`` traducidos a su nombre), reproduce
# exactamente cada línea del post.

SECCIONES_ESTRUCTURADAS = {
    "Escalas": "escalas",
    "Reglas clínicas": "reglas",
    "Núcleo diagnóstico": "nucleo",
    "Balance de criterios": "balance",
}
_ETIQUETAS_LIBRO = {  # claves sin etiqueta en el blog (que las mostraría sin tilde)
    "apoyos_minimos": "Apoyos mínimos",
    "banderas_maximas": "Banderas máximas",
    "y_al_menos_uno_de": "Y al menos uno de",
}
_HM_RE = re.compile(r"HM:\d+")


def _etiqueta_libro(clave: str) -> str:
    return _ETIQUETAS_LIBRO.get(clave, etiqueta_blog(clave))


def serializar_con_nombres(valor: Any, nombres: dict[str, str]) -> str:
    """``render_value`` del blog *con* prosa: los identificadores ``HM:`` se leen por su nombre."""
    if isinstance(valor, dict):
        return "; ".join(f"{etiqueta_blog(k)}: {serializar_con_nombres(v, nombres)}" for k, v in valor.items())
    if isinstance(valor, list):
        return " / ".join(serializar_con_nombres(v, nombres) for v in valor) if valor else "No documentado."
    if isinstance(valor, str) and _HM_RE.fullmatch(valor.strip()):
        return nombres.get(valor.strip(), valor.strip())
    return serializar_como_blog(valor)


def _texto_valor(clave: str, valor: Any, nombres: dict[str, str]) -> str:
    if isinstance(valor, str) and _HM_RE.fullmatch(valor.strip()):
        return f"{nombres.get(valor.strip(), valor.strip())} (`{valor.strip()}`)"
    if isinstance(valor, list) and valor and all(isinstance(v, str) and _HM_RE.fullmatch(v.strip()) for v in valor):
        return ", ".join(_texto_valor(clave, v, nombres) for v in valor)
    if isinstance(valor, list) and all(isinstance(v, str) for v in valor):
        return ", ".join(v.strip() for v in valor) if valor else "No documentado."
    if isinstance(valor, dict):
        return "; ".join(f"{_etiqueta_libro(k)}: {_texto_valor(k, v, nombres)}" for k, v in valor.items())
    return _valor_celda(clave, valor)


def _es_lista_de_registros(valor: Any) -> bool:
    return isinstance(valor, list) and bool(valor) and all(isinstance(v, dict) for v in valor)


def _es_mapa_de_registros(valor: Any) -> bool:
    return isinstance(valor, dict) and bool(valor) and all(isinstance(v, dict) for v in valor.values())


def _tabla_mapa(valor: dict[str, dict[str, Any]], nombres: dict[str, str]) -> str:
    claves: list[str] = []
    for fila in valor.values():
        claves += [c for c in fila if c not in claves]
    lineas = [
        "| Categoría | " + " | ".join(_etiqueta_libro(c) for c in claves) + " |",
        "| :--- | " + " | ".join(":---" for _ in claves) + " |",
    ]
    for nombre, fila in valor.items():
        celdas = [_texto_valor(c, fila[c], nombres) if c in fila else "—" for c in claves]
        lineas.append(f"| {_etiqueta_libro(nombre)} | " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def bloque_registro(registro: dict[str, Any], nombres: dict[str, str]) -> str:
    """Un registro (escala, regla, núcleo o balance) como lista de campos y tablas, en orden."""
    lineas: list[str] = []
    if registro.get("nombre"):
        lineas += [f"**{str(registro['nombre']).strip()}**", ""]
    unidad = (registro.get("graduacion") or {}).get("unidad") if isinstance(registro.get("graduacion"), dict) else None
    en_lista = False
    for clave, valor in registro.items():
        if clave == "nombre":
            continue
        if _es_lista_de_registros(valor) or _es_mapa_de_registros(valor):
            if en_lista:
                lineas.append("")
            tabla = tabla_tramos(valor, unidad) if isinstance(valor, list) else _tabla_mapa(valor, nombres)
            lineas += [f"**{_etiqueta_libro(clave)}:**", "", tabla, ""]
            en_lista = False
            continue
        lineas.append(f"- **{_etiqueta_libro(clave)}:** {_texto_valor(clave, valor, nombres)}")
        en_lista = True
    return "\n".join(lineas).rstrip() + "\n"


def presentar_estructuras(
    cuerpo: str, datos: dict[str, Any] | None, nombres: dict[str, str]
) -> tuple[str, int]:
    """Sustituye las secciones serializadas por su versión estructurada si coinciden exactamente."""
    if not datos:
        return cuerpo, 0
    convertidas = 0
    for titulo, clave in SECCIONES_ESTRUCTURADAS.items():
        m = re.search(rf"^## {re.escape(titulo)}\n(.*?)(?=^## |\Z)", cuerpo, re.M | re.S)
        if not m or clave not in datos:
            continue
        valor = datos[clave]
        registros = valor if isinstance(valor, list) else [valor]
        lineas_post = [l for l in m.group(1).split("\n") if l.strip()]
        if lineas_post != [serializar_con_nombres(r, nombres) for r in registros]:
            continue
        nuevo = "\n".join(bloque_registro(r, nombres) for r in registros)
        cuerpo = cuerpo[: m.start(1)] + "\n" + nuevo + "\n" + cuerpo[m.end(1) :]
        convertidas += len(registros)
    return cuerpo, convertidas


# --- Ficha de la condición (3c) -------------------------------------------------------------

SECCIONES_FICHA = ("Nombre en inglés", "Sinónimos", "Códigos")


def _seccion(cuerpo: str, titulo: str) -> re.Match[str] | None:
    return re.search(rf"^## {re.escape(titulo)}\n(.*?)(?=^## |\Z)", cuerpo, re.M | re.S)


def extraer_ficha(cuerpo: str) -> tuple[str, str | None]:
    """Quita «Nombre en inglés», «Sinónimos» y «Códigos» del cuerpo y devuelve un recuadro.

    Si alguna sección no tiene la forma esperada (una línea; códigos legibles sin pérdida), el
    cuerpo se devuelve intacto y sin recuadro.
    """
    filas: list[str] = []
    for titulo in SECCIONES_FICHA:
        m = _seccion(cuerpo, titulo)
        if m is None:
            continue
        lineas = [l.strip() for l in m.group(1).split("\n") if l.strip()]
        if not lineas or any(l.startswith(("#", "|", ">", "-", "*")) for l in lineas):
            return cuerpo, None
        if titulo == "Códigos":
            if len(lineas) != 1:
                return cuerpo, None
            campos = leer_registro_plano(lineas[0], _CLAVES_CODIGOS)
            if not campos:
                return cuerpo, None
            filas.append(
                "- "
                + " · ".join(
                    f"**{_CLAVES_CODIGOS[k]}:** " + ("no documentado" if v == "No documentado." else f"`{v}`")
                    for k, v in campos
                )
            )
        else:  # cada línea es un valor (los sinónimos van uno por párrafo)
            filas.append(f"- **{titulo}:** {'; '.join(lineas)}")
    if not filas:
        return cuerpo, None
    for titulo in SECCIONES_FICHA:
        m = _seccion(cuerpo, titulo)
        if m is not None:
            cuerpo = cuerpo[: m.start()] + cuerpo[m.end() :]
    recuadro = "\n".join(["::: {.ficha-condicion}", "**Ficha de la condición**", "", *filas, ":::"])
    return cuerpo, recuadro


# --- Dónde NO confiar (3c) ------------------------------------------------------------------

TITULO_NO_CONFIAR = "Dónde NO confiar"


def presentar_no_confiar(cuerpo: str, pmid: str | None) -> tuple[str, bool]:
    """«Conclusión de la fuente» pasa a «Dónde NO confiar»: cita literal y su atribución.

    El PMID solo se da si la ficha declara una única referencia (``pmid``); si no, se dice que
    la ficha no lo declara. Ningún texto de la conclusión se altera.
    """
    m = _seccion(cuerpo, "Conclusión de la fuente")
    if m is None:
        return cuerpo, False
    parrafos = [p.strip() for p in m.group(1).strip().split("\n\n") if p.strip()]
    if not parrafos:
        return cuerpo, False
    cita = "\n>\n".join("> " + p.replace("\n", "\n> ") for p in parrafos)
    atribucion = (
        f"> — Conclusión de la fuente (`{pmid}`)."
        if pmid
        else "> — Conclusión de la fuente (la ficha no declara de qué referencia procede)."
    )
    nuevo = f"## {TITULO_NO_CONFIAR}\n\n{cita}\n>\n{atribucion}\n\n"
    return cuerpo[: m.start()] + nuevo + cuerpo[m.end() :], True
