"""Generador del proyecto Quarto (.qmd) de Medicina y Ciencia (HTML, PDF LuaLaTeX y EPUB)."""

from __future__ import annotations

import shutil
import subprocess
import textwrap
from html import escape
from typing import TYPE_CHECKING

import yaml

from libro import ALTO_MM, ALTO_PULGADAS, ANCHO_MM, ANCHO_PULGADAS, NOMBRE_SALIDA
from libro.datos import (
    RAIZ,
    CondicionBlog,
    LibroCompleto,
    MetadatosLibro,
    cargar_libro,
    exportar_libro_json,
    renderizar_caso_qmd,
)

if TYPE_CHECKING:
    from pathlib import Path

RUTA_PREAMBULO = RAIZ / "assets" / "libro" / "preambulo.tex"
RUTA_FILTRO_LUA = RAIZ / "assets" / "libro" / "diseno-pdf.lua"
RUTA_FILTRO_TITULO = RAIZ / "assets" / "libro" / "quitar-titulo.lua"
RUTA_CSS_WEB = RAIZ / "assets" / "libro" / "estilo-web.css"
RUTA_CSS_EPUB = RAIZ / "assets" / "libro" / "estilo-epub.css"
RUTA_DECLARACION_IA = RAIZ / "paratextos" / "declaracion-ia.md"


def _escapar_tex(texto: str) -> str:
    barra = chr(92)
    for caracter in "&%$#_{}":
        texto = texto.replace(caracter, barra + caracter)
    return texto


def _datos_libro_tex(meta: MetadatosLibro) -> str:
    barra = chr(92)
    nombres = (barra * 2 + " ").join(_escapar_tex(a.nombre) for a in meta.autores)
    sello = f"Edición 2026–2027 {barra}enspace·{barra}enspace {_escapar_tex(meta.licencia)}"
    return (
        "% GENERADO por tools/libro/qmd.py desde mapa.yaml. No editar a mano.\n"
        f"{barra}newcommand{{{barra}librocoleccion}}{{{_escapar_tex(meta.coleccion)}}}\n"
        f"{barra}newcommand{{{barra}librotitulo}}{{{_escapar_tex(meta.titulo)}}}\n"
        f"{barra}newcommand{{{barra}librosubtitulo}}{{{_escapar_tex(meta.subtitulo)}}}\n"
        f"{barra}newcommand{{{barra}libroautoresportada}}{{{nombres}}}\n"
        f"{barra}newcommand{{{barra}librosellopie}}{{{sello}}}\n"
    )


def _tspans(texto: str, ancho: int, salto: int, x: int = 164) -> list[str]:
    return [
        f'    <tspan x="{x}" dy="{0 if i == 0 else salto}">{escape(linea)}</tspan>'
        for i, linea in enumerate(textwrap.wrap(texto, ancho))
    ]


def _generar_portada_svg(meta: MetadatosLibro) -> str:
    """Genera portada vectorial SVG 1700 × 2440 (170 × 244 mm) para HTML y EPUB."""
    autores_txt = " · ".join(a.nombre for a in meta.autores)
    lineas = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 1700 2440" width="1700" height="2440">',
        '  <rect width="1700" height="2440" fill="#0D1B2A" />',
        '  <rect x="96" y="96" width="1508" height="2248" fill="none" '
        'stroke="#F8F6F1" stroke-opacity="0.22" stroke-width="2" />',
        '  <rect x="114" y="114" width="1472" height="2212" fill="none" '
        'stroke="#C69C6D" stroke-opacity="0.52" stroke-width="3" />',
        '  <text x="164" y="210" fill="#C69C6D" font-family="sans-serif" '
        f'font-size="26" font-weight="700" letter-spacing="2">{escape(meta.coleccion)}</text>',
        '  <line x1="164" y1="242" x2="920" y2="242" stroke="#C69C6D" stroke-width="3" />',
        '  <text x="164" y="365" fill="#F8F6F1" font-family="Georgia, serif" '
        'font-size="96" font-weight="700">',
        *_tspans(meta.titulo, 22, 108),
        "  </text>",
        '  <text x="164" y="510" fill="#F8F6F1" fill-opacity="0.90" '
        'font-family="Georgia, serif" font-size="40" font-style="italic">',
        *_tspans(meta.subtitulo, 46, 54),
        "  </text>",
        '  <line x1="164" y1="670" x2="1536" y2="670" stroke="#C69C6D" '
        'stroke-opacity="0.65" stroke-width="2" />',
        '  <g transform="translate(850, 1245)">',
        '    <line x1="-380" y1="300" x2="380" y2="300" stroke="#F8F6F1" stroke-opacity="0.28" stroke-width="2" />',
        '    <line x1="-380" y1="-300" x2="-380" y2="300" stroke="#F8F6F1" stroke-opacity="0.28" stroke-width="2" />',
        '    <line x1="-380" y1="300" x2="380" y2="-300" stroke="#F8F6F1" stroke-opacity="0.25" stroke-dasharray="10,10" stroke-width="2" />',
        '    <path d="M -380 300 C -360 -180, -160 -290, 380 -300" fill="none" stroke="#4EA8DE" stroke-width="6" />',
        '    <path d="M -380 300 C -260 -40, -20 -220, 380 -300" fill="none" stroke="#C69C6D" stroke-opacity="0.78" stroke-width="4" />',
        '    <line x1="-260" y1="-230" x2="-260" y2="230" stroke="#C69C6D" stroke-opacity="0.45" stroke-width="2" />',
        '    <line x1="0" y1="-230" x2="0" y2="230" stroke="#C69C6D" stroke-opacity="0.45" stroke-width="2" />',
        '    <line x1="260" y1="-230" x2="260" y2="230" stroke="#C69C6D" stroke-opacity="0.45" stroke-width="2" />',
        '    <polyline points="-260,120 0,-30 260,-180" fill="none" stroke="#C69C6D" stroke-width="5" />',
        '    <circle cx="-260" cy="120" r="14" fill="#C69C6D" stroke="#F8F6F1" stroke-width="2" />',
        '    <circle cx="0" cy="-30" r="14" fill="#C69C6D" stroke="#F8F6F1" stroke-width="2" />',
        '    <circle cx="260" cy="-180" r="14" fill="#C69C6D" stroke="#F8F6F1" stroke-width="2" />',
        '    <text x="-260" y="-255" text-anchor="middle" fill="#C69C6D" font-family="sans-serif" font-size="24" font-weight="700">P₀</text>',
        '    <text x="0" y="-255" text-anchor="middle" fill="#C69C6D" font-family="sans-serif" font-size="24" font-weight="700">LR</text>',
        '    <text x="260" y="-255" text-anchor="middle" fill="#C69C6D" font-family="sans-serif" font-size="24" font-weight="700">P₁</text>',
        '    <text x="0" y="355" text-anchor="middle" fill="#C69C6D" font-family="sans-serif" font-size="22" letter-spacing="2">SENSIBILIDAD · ESPECIFICIDAD · LR+ · LR− · FAGAN</text>',
        "  </g>",
        '  <rect x="164" y="1720" width="1372" height="215" fill="#F8F6F1" fill-opacity="0.06" stroke="#C69C6D" stroke-opacity="0.45" stroke-width="2" />',
        '  <text x="205" y="1782" fill="#C69C6D" font-family="sans-serif" font-size="26" font-weight="700">TEXTO OFICIAL DE LA CÁTEDRA · UNIVERSIDAD CENTRAL DEL ECUADOR</text>',
        '  <text x="205" y="1840" fill="#F8F6F1" fill-opacity="0.92" font-family="sans-serif" font-size="24">4 unidades (16 semanas) · 48 condiciones verificadas de medsemiotics-db</text>',
        '  <text x="205" y="1892" fill="#F8F6F1" fill-opacity="0.82" font-family="sans-serif" font-size="24">18 casos socráticos ABP · 90 preguntas de autoevaluación · HTML, PDF y EPUB</text>',
        '  <text x="164" y="2110" fill="#F8F6F1" font-family="sans-serif" '
        f'font-size="36" font-weight="700">{escape(autores_txt)}</text>',
        '  <text x="164" y="2295" fill="#C69C6D" font-family="sans-serif" '
        f'font-size="24">Edición 2026–2027 · {escape(meta.licencia)}</text>',
        "</svg>\n",
    ]
    return "\n".join(lineas)


def _generar_index_qmd(libro: LibroCompleto) -> str:
    meta = libro.metadatos
    curso = meta.curso
    total_cond = len(libro.condiciones)
    total_casos = sum(1 for c in libro.condiciones.values() if c.caso_compilado is not None)
    total_quiz = sum(len(c.preguntas) for c in libro.condiciones.values())
    total_hallazgos = sum(len(c.hallazgos_tabla) for c in libro.condiciones.values())
    tamano_str = (
        f"{ANCHO_MM} × {ALTO_MM} mm ({ANCHO_PULGADAS:.2f} × {ALTO_PULGADAS:.2f} pulgadas)".replace(
            ".", ","
        )
    )

    lineas_autores = []
    for a in meta.autores:
        detalle = [a.rol] + ([a.afiliacion] if a.afiliacion else [])
        linea = f"**{a.nombre}** — {'; '.join(detalle)}"
        if a.orcid:
            linea += f" · ORCID: <https://orcid.org/{a.orcid}>"
        lineas_autores.append(linea + "  ")

    lineas: list[str] = [
        "```{=latex}",
        "\\portadalibro",
        "```",
        "",
        "::: {.portadilla-pdf}",
        f"# {meta.titulo} {{.unnumbered .unlisted .titulo-de-obra}}",
        "",
        "::: {.portadilla-titulo}",
        meta.titulo,
        ":::",
        "",
        f"*{meta.subtitulo}*",
        "",
        *[f"**{a.nombre}**  " for a in meta.autores],
        f"{curso.institucion}",
        ":::",
        "",
        "::: {.creditos-pdf}",
        f"**{meta.titulo}**  ",
        f"*{meta.subtitulo}*",
        "",
        "**Autoría y docencia:**  ",
        *lineas_autores,
        "",
        f"**Cátedra:** {curso.catedra}  ",
        f"**Período académico:** {curso.periodo}  ",
        f"**Horario y sedes:** {curso.horario} · {curso.sedes}  ",
        f"**Aula virtual:** {curso.aula_virtual}  ",
        f"**Repositorio fuente:** <{meta.url_repositorio}>  ",
        f"**Edición web:** <{meta.url_web}>  ",
        f"**Blog clínico de origen:** <{meta.url_blog}>  ",
        f"**Contacto editorial:** <{meta.contacto}>",
        "",
        (
            f"**Fuente clínica única verificada:** las cifras de sensibilidad, especificidad y "
            f"cocientes de verosimilitud ($\\text{{LR}}^+$ y $\\text{{LR}}^-$) proceden íntegramente "
            f"de `{meta.fuente_clinica_repo}` (DOI `{meta.fuente_clinica_doi}`, revisión fijada "
            f"`{meta.fuente_clinica_revision[:12]}`) a través del blog de `{meta.fuente_blog_repo}` "
            f"(DOI `{meta.fuente_blog_doi}`, revisión `{meta.fuente_blog_revision[:12]}`)."
        ),
        "",
        (
            f"**Arquitectura de compilación:** canal reproducible `JSON → QMD → Quarto` con "
            f"edición web HTML, maqueta impresa {tamano_str} en KOMA-Script (`scrbook` 10,5 pt, "
            "*Libertinus Serif*, motor LuaLaTeX) y edición portátil EPUB 3."
        ),
        "",
        (
            f"**Licencia:** la obra compilada se distribuye bajo **{meta.licencia_nombre} "
            f"({meta.licencia})**; las fichas del blog derivadas de MedSemiotics conservan "
            f"**{meta.licencia_fuentes}** y el código fuente se distribuye bajo **MIT**."
        ),
        "",
        "::: {.alerta-ficha}",
        "**Aviso médico-legal y docente:** Esta obra tiene carácter exclusivamente educativo y "
        "científico para estudiantes de medicina, residentes y profesionales de la salud. Ningún "
        "algoritmo, cociente de verosimilitud o caso socrático sustituye el juicio clínico "
        "individual frente al paciente ni las guías oficiales vigentes.",
        ":::",
        ":::",
        "",
        "```{=latex}",
        "\\tableofcontents",
        "\\cleardoublepage",
        "```",
        "",
        "# Prefacio y guía metodológica del curso {.unnumbered}",
        "",
        (
            "La cátedra **Medicina y Ciencia** enseña ciencia de datos y estadística biomédica "
            "como instrumento de decisión diagnóstica. Cada concepto estadístico se aprende "
            "resolviendo un caso clínico real del **blog MedSemiotics**, y la herramienta "
            "computacional (calculadora de estadísticos, SQL, R o Python) entra exactamente cuando "
            "el caso la necesita."
        ),
        "",
        "## La ruta de un hallazgo clínico {.unnumbered}",
        "",
        (
            "Todo hallazgo semiológico sigue una misma cadena inferencial desde la cabecera del "
            "paciente hasta la decisión terapéutica: **hallazgo clínico** $\\rightarrow$ "
            "**probabilidad basal** (*¿qué tan frecuente es?*) $\\rightarrow$ **exactitud "
            "diagnóstica** (sensibilidad, especificidad, $\\text{LR}^+$ y $\\text{LR}^-$) "
            "$\\rightarrow$ **incertidumbre** (IC 95 %, calidad STARD/QUADAS-2) $\\rightarrow$ "
            "**umbrales de decisión** (*¿cambia la conducta?*) $\\rightarrow$ **comunicación al "
            "paciente** con frecuencias naturales."
        ),
        "",
        "$$",
        "\\text{Odds}_{\\text{postest}} = \\text{Odds}_{\\text{pretest}} \\times \\text{LR}, "
        "\\qquad \\text{donde } \\text{Odds} = \\frac{P}{1 - P}",
        "$$",
        "",
        "$$",
        "\\text{LR}^+ = \\frac{\\text{Sensibilidad}}{1 - \\text{Especificidad}}, "
        "\\qquad "
        "\\text{LR}^- = \\frac{1 - \\text{Sensibilidad}}{\\text{Especificidad}}",
        "$$",
        "",
        "## Estructura de cada sesión (90 minutos) {.unnumbered}",
        "",
        "| Minutos | Momento | Actividad en aula |",
        "| :--- | :--- | :--- |",
        "| 0–10 | Caso socrático | Viñeta ABP sin revelar el cociente; estimación de probabilidad pretest |",
        "| 10–35 | Concepto | Mini-clase del concepto estadístico del día anclado en el caso |",
        "| 35–65 | Cálculo y debate | Trabajo en parejas: tabla $2 \\times 2$, LR y postest (calculadora o R/Python) |",
        "| 65–80 | Autoevaluación | Preguntas del blog (*Reto clínico*) sobre el LR documentado |",
        "| 80–90 | Cierre | «¿Qué cambia en la conducta?» y límites de la evidencia |",
        "",
        ': {tbl-colwidths="[14,22,64]"}',
        "",
        "## Contenido de esta edición {.unnumbered}",
        "",
        (
            f"Este volumen integra las **{len(libro.unidades)} unidades del sílabo** (16 semanas), "
            f"el compendio completo de las **{total_cond} condiciones verificadas** del blog "
            f"MedSemiotics (**{total_hallazgos} hallazgos clínicos documentados**), "
            f"**{total_casos} casos socráticos ABP** con resolución determinista de evidencia y "
            f"**{total_quiz} preguntas de autoevaluación** con clave razonada."
        ),
        "",
    ]
    return "\n".join(lineas)


def _anchor_id(condicion_id: str) -> str:
    return "sec-" + condicion_id.lower().replace(":", "")


def _nombre_archivo_condicion(cond: CondicionBlog) -> str:
    prefijo = cond.condicion_id.lower().replace(":", "")
    slug_corto = cond.slug.replace("-precision-semiotica", "")
    return f"{prefijo}-{slug_corto}.qmd"


def _generar_capitulo_condicion(cond: CondicionBlog, meta: MetadatosLibro) -> str:
    ancla = _anchor_id(cond.condicion_id)
    url_post = f"{meta.url_sitio}post.html?slug={cond.slug}"

    lineas: list[str] = [
        f"# {cond.nombre_corto} (`{cond.condicion_id}`) {{#{ancla}}}",
        "",
        "::: {.enlace-ficha}",
        (
            f"**Código:** `{cond.condicion_id}` · **Área:** {cond.categoria_etiqueta} · "
            f"**Nivel:** {cond.dificultad} · **Fecha:** `{cond.fecha}` · "
            f"**Base:** `medsemiotics-db@{cond.revision_db[:10]}` · "
            f"[Artículo en el blog]({url_post})"
        ),
        ":::",
        "",
    ]

    if cond.triada:
        lineas.extend(["::: {.triada-signo}", "**Tríada semiótica del hallazgo ancla**", ""])
        if cond.triada.get("significante"):
            lineas.append(f"- **Significante:** {cond.triada['significante']}")
        if cond.triada.get("significado"):
            lineas.append(f"- **Significado:** {cond.triada['significado']}")
        if cond.triada.get("decision"):
            lineas.append(f"- **Decisión clínica:** {cond.triada['decision']}")
        lineas.extend([":::", ""])

    if cond.hallazgos_tabla:
        lineas.extend(
            [
                "## Síntesis cuantitativa de evidencia",
                "",
                "| Hallazgo | Rol | Estado | Sens. | Esp. | LR+ | LR− | Ref. |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ]
        )
        for h in cond.hallazgos_tabla:
            lineas.append(
                f"| {h.concepto_nombre} (`{h.concepto_id}`) | {h.rol} | {h.estado_lr} | "
                f"{h.sensibilidad} | {h.especificidad} | {h.lr_positivo} | {h.lr_negativo} | "
                f"`{h.referencia}` |"
            )
        lineas.extend(["", ': {tbl-colwidths="[25,11,11,9,9,12,12,11]"}', ""])

    lineas.append(cond.cuerpo_md.strip())
    lineas.append("")

    if cond.caso_compilado is not None:
        lineas.extend(
            [
                "## Caso socrático ABP",
                "",
                renderizar_caso_qmd(cond.caso_compilado),
                "",
            ]
        )

    return "\n".join(lineas)


def _generar_apendice_autoevaluacion(libro: LibroCompleto) -> str:
    todas = [q for c in libro.condiciones_ordenadas for q in c.preguntas]
    lineas: list[str] = [
        "# Banco de autoevaluación clínica (Reto clínico) {#sec-apendice-autoevaluacion}",
        "",
        (
            f"Este apéndice reúne las **{len(todas)} preguntas de autoevaluación** publicadas en "
            f"los {len(libro.condiciones)} artículos del blog MedSemiotics. Primero se presentan "
            "los enunciados para estudio autónomo y al final la clave razonada con su respaldo en "
            "`medsemiotics-db`."
        ),
        "",
        "## Enunciados",
        "",
    ]

    for idx, q in enumerate(todas, start=1):
        ref_txt = f" (`{q.referencia_id}`)" if q.referencia_id else ""
        lineas.extend(
            [
                f"### Pregunta {idx}. {q.condicion_nombre} (`{q.condicion_id}`){ref_txt} {{.unnumbered}}",
                "",
                q.pregunta,
                "",
            ]
        )
        for op_idx, op in enumerate(q.opciones):
            letra = chr(ord("A") + op_idx)
            lineas.append(f"- **{letra}.** {op.texto}")
        lineas.append("")

    lineas.extend(["---", "", "## Clave de respuestas razonadas", ""])

    for idx, q in enumerate(todas, start=1):
        correcta_idx = next((i for i, o in enumerate(q.opciones) if o.correcta), 0)
        letra = chr(ord("A") + correcta_idx)
        op_ok = q.opciones[correcta_idx]
        lineas.extend(
            [
                "::: {.perlas-clinicas}",
                f"**Pregunta {idx} ({q.condicion_nombre}, `{q.condicion_id}`) — Respuesta correcta: {letra}** "
                f"(*{op_ok.texto}*).",
                "",
                op_ok.feedback or "Verificado en `medsemiotics-db`.",
                ":::",
                "",
            ]
        )

    return "\n".join(lineas)


def _generar_apendice_evidencia(libro: LibroCompleto) -> str:
    medidos = [
        h
        for c in libro.condiciones_ordenadas
        for h in c.hallazgos_tabla
        if h.estado_lr == "medido"
    ]
    lineas: list[str] = [
        "# Índice maestro de evidencia diagnóstica e iconografía abierta {#sec-apendice-evidencia}",
        "",
        "## Hallazgos con cociente de verosimilitud medido",
        "",
        (
            f"La siguiente tabla consolida los **{len(medidos)} hallazgos con LR medido** "
            f"documentados en los {len(libro.condiciones)} artículos del blog MedSemiotics "
            f"(revisión fijada `{libro.metadatos.fuente_clinica_revision[:12]}`)."
        ),
        "",
        "| Código | Condición | Hallazgo | Sens. | Esp. | LR+ | LR− |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for h in medidos:
        lineas.append(
            f"| `{h.condicion_id}` | {h.condicion_nombre} | {h.concepto_nombre} (`{h.concepto_id}`) | "
            f"{h.sensibilidad} | {h.especificidad} | {h.lr_positivo} | {h.lr_negativo} |"
        )
    lineas.extend(
        [
            "",
            ': {tbl-colwidths="[10,20,28,9,9,12,12]"}',
            "",
            "## Registro de iconografía clínica abierta (Wikimedia Commons)",
            "",
            "| Código | Condición | Archivo | Licencia | Autoría |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
    )
    for c in libro.condiciones_ordenadas:
        if c.imagen is not None:
            img = c.imagen
            lineas.append(
                f"| `{c.condicion_id}` | {c.nombre_corto} | `{img.titulo_commons}` | "
                f"{img.licencia} | {img.autor} |"
            )
    lineas.extend(["", ': {tbl-colwidths="[10,22,30,14,24]"}', ""])
    return "\n".join(lineas)


def _configuracion_quarto(
    meta: MetadatosLibro,
    capitulos: list[object],
    apendices: list[str],
    portada_epub: str = "portada.svg",
) -> dict[str, object]:
    return {
        "project": {
            "type": "book",
            "output-dir": "_book",
        },
        "lang": "es",
        "book": {
            "title": meta.titulo,
            "subtitle": meta.subtitulo,
            "author": [a.nombre for a in meta.autores],
            "date": "2026-11-19",
            "output-file": NOMBRE_SALIDA,
            "repo-url": meta.url_repositorio,
            "chapters": ["index.qmd", *capitulos],
            "appendices": apendices,
            "cover-image": portada_epub,
        },
        "filters": [
            "diseno-pdf.lua",
            {"type": "lua", "path": "quitar-titulo.lua", "at": "post-quarto"},
        ],
        "format": {
            "html": {
                "theme": "cosmo",
                "css": "estilo-web.css",
                "toc": True,
                "toc-depth": 3,
                "number-sections": True,
                "html-math-method": "katex",
            },
            "pdf": {
                "documentclass": "scrbook",
                "pdf-engine": "lualatex",
                "keep-tex": True,
                "toc": False,
                "number-sections": True,
                "classoption": ["twoside", "openright", "10.5pt", "BCOR=8mm", "DIV=calc"],
                "geometry": [
                    f"paperwidth={ANCHO_MM}mm",
                    f"paperheight={ALTO_MM}mm",
                    "top=19mm",
                    "bottom=21mm",
                    "inner=20mm",
                    "outer=18mm",
                    "headsep=6mm",
                    "footskip=10mm",
                ],
                "mainfont": "Libertinus Serif",
                "sansfont": "Libertinus Sans",
                "monofont": "Libertinus Mono",
                "colorlinks": True,
                "linkcolor": "libroprimario",
                "urlcolor": "libroacento",
                "include-in-header": ["datos-libro.tex", "preambulo-libro.tex"],
            },
            "epub": {
                "epub-cover-image": portada_epub,
                "css": "estilo-epub.css",
                "toc": True,
                "toc-depth": 2,
                "number-sections": True,
                "html-math-method": "mathml",
            },
        },
    }


def generar_proyecto_quarto(
    carpeta_salida: Path,
    raiz: Path = RAIZ,
    ruta_json: Path | None = None,
) -> list[Path]:
    """Ejecuta la tubería JSON → QMD y escribe el proyecto Quarto completo en ``carpeta_salida``."""
    libro = cargar_libro(raiz)
    meta = libro.metadatos

    destino_json = ruta_json or (carpeta_salida.parent / "libro.json")
    exportar_libro_json(libro, destino_json)

    carpeta_salida.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(RUTA_PREAMBULO, carpeta_salida / "preambulo-libro.tex")
    (carpeta_salida / "datos-libro.tex").write_text(_datos_libro_tex(meta), encoding="utf-8")
    shutil.copyfile(RUTA_FILTRO_LUA, carpeta_salida / "diseno-pdf.lua")
    shutil.copyfile(RUTA_FILTRO_TITULO, carpeta_salida / "quitar-titulo.lua")
    shutil.copyfile(RUTA_CSS_WEB, carpeta_salida / "estilo-web.css")
    shutil.copyfile(RUTA_CSS_EPUB, carpeta_salida / "estilo-epub.css")

    ruta_portada = carpeta_salida / "portada.svg"
    ruta_portada.write_text(_generar_portada_svg(meta), encoding="utf-8")

    # Rasteriza portada.svg -> portada.png si rsvg-convert está disponible (compatibilidad Kindle/Calibre).
    portada_epub = "portada.svg"
    rsvg = shutil.which("rsvg-convert")
    if rsvg is not None:
        ruta_png = carpeta_salida / "portada.png"
        res = subprocess.run(
            [rsvg, "-w", "1700", "-h", "2440", str(ruta_portada), "-o", str(ruta_png)],
            check=False,
            capture_output=True,
        )
        if res.returncode == 0 and ruta_png.is_file() and ruta_png.stat().st_size > 0:
            portada_epub = "portada.png"

    generados: list[Path] = [
        destino_json,
        carpeta_salida / "preambulo-libro.tex",
        carpeta_salida / "datos-libro.tex",
        carpeta_salida / "diseno-pdf.lua",
        carpeta_salida / "quitar-titulo.lua",
        carpeta_salida / "estilo-web.css",
        carpeta_salida / "estilo-epub.css",
        ruta_portada,
    ]
    planas: list[str] = []

    def escribir(nombre: str, contenido: str) -> str:
        ruta = carpeta_salida / nombre
        ruta.write_text(contenido, encoding="utf-8")
        generados.append(ruta)
        planas.append(contenido)
        return nombre

    escribir("index.qmd", _generar_index_qmd(libro))

    # Parte I: Unidades del curso
    archivos_unidades: list[str] = []
    for u in libro.unidades:
        texto_u = (raiz / u.archivo).read_text(encoding="utf-8")
        archivos_unidades.append(escribir(f"{u.clave}.qmd", texto_u))

    capitulos: list[object] = [
        {
            "part": "Programa del curso Medicina y Ciencia (16 semanas)",
            "chapters": archivos_unidades,
        }
    ]

    # Partes II–VII: 48 condiciones del blog MedSemiotics
    for parte in libro.partes:
        archivos_parte: list[str] = []
        for cid in parte.condiciones:
            cond = libro.condiciones[cid]
            nombre = _nombre_archivo_condicion(cond)
            archivos_parte.append(escribir(nombre, _generar_capitulo_condicion(cond, meta)))
        capitulos.append({"part": parte.titulo, "chapters": archivos_parte})

    # Apéndices
    apendices = [
        escribir("apendice-a-autoevaluacion.qmd", _generar_apendice_autoevaluacion(libro)),
        escribir("apendice-b-evidencia-iconografia.qmd", _generar_apendice_evidencia(libro)),
        escribir(
            "apendice-c-declaracion-ia.qmd",
            RUTA_DECLARACION_IA.read_text(encoding="utf-8"),
        ),
    ]

    cfg = _configuracion_quarto(meta, capitulos, apendices, portada_epub=portada_epub)
    ruta_quarto = carpeta_salida / "_quarto.yml"
    ruta_quarto.write_text(
        yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    generados.append(ruta_quarto)

    ruta_plano = carpeta_salida / "libro-plano.md"
    ruta_plano.write_text("\n\n---\n\n".join(planas), encoding="utf-8")
    generados.append(ruta_plano)

    return generados
