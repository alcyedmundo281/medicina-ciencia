"""CLI del libro Medicina y Ciencia: ``python -m libro <orden>``.

Tubería reproducible: JSON -> QMD -> Quarto (HTML, PDF LuaLaTeX 170 x 244 mm y EPUB 3).

Órdenes disponibles:
- ``json``:  exporta el manifiesto estructurado ``build/libro.json``.
- ``qmd``:   exporta ``build/libro.json`` y genera el proyecto Quarto en ``build/quarto``.
- ``html``:  compila la edición web HTML y la copia a ``build/html``.
- ``pdf`` / ``build``: compila el PDF con LuaLaTeX (170 x 244 mm) y verifica con ``pdfinfo``.
- ``epub``:  compila el EPUB 3 y verifica su estructura.
- ``all``:   genera JSON, QMD, HTML, PDF y EPUB.
- ``mapa``:  regenera ``mapa-maestro-libro.md``.
- ``registro-ia``: regenera ``docs/registro-ia.md`` desde los trailers ``Asistido-por``.
- ``casos``: recompila ``assets/data/casos/`` desde ``casos/`` y ``posts/``.
- ``imagenes``: regenera (``--desde``) o compara (``--comprobar``) ``assets/data/imagenes-blog.json``
             con el ``blog-index.json`` de medsemiotics.
- ``check``: valida ``mapa.yaml``, revisión fijada de ``medsemiotics-db``, 48 posts, 18 casos
             (``assets/data/casos/`` al día), índice de imágenes y artefactos compilados si existen.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from libro import ALTO_MM, ALTO_PULGADAS, ANCHO_MM, ANCHO_PULGADAS, NOMBRE_SALIDA
from libro.datos import RAIZ, cargar_libro, exportar_libro_json
from libro.mapa import escribir_mapa_maestro, renderizar_mapa_maestro
from libro.pdf import (
    compilar_libro_epub,
    compilar_libro_html,
    compilar_libro_pdf,
    empaquetar_latex,
    inspeccionar_pdf_con_pdfinfo,
    validar_epub,
    validar_html,
    validar_info_pdf,
    validar_tex_libro,
)
from libro.qmd import generar_proyecto_quarto

RUTA_JSON_DEFECTO = RAIZ / "build" / "libro.json"
RUTA_PROYECTO_DEFECTO = RAIZ / "build" / "quarto"
RUTA_PDF_DEFECTO = RAIZ / "build" / f"{NOMBRE_SALIDA}.pdf"
RUTA_EPUB_DEFECTO = RAIZ / "build" / f"{NOMBRE_SALIDA}.epub"
RUTA_HTML_DEFECTO = RAIZ / "build" / "html"
RUTA_LATEX_ZIP_DEFECTO = RAIZ / "build" / "medicina-ciencia-latex.zip"


def _verificar_pdf(ruta_proyecto: Path, ruta_pdf: Path) -> int:
    info = inspeccionar_pdf_con_pdfinfo(ruta_pdf)
    errores = validar_info_pdf(info)
    ruta_tex = ruta_proyecto / f"{NOMBRE_SALIDA}.tex"
    if ruta_tex.is_file():
        errores.extend(validar_tex_libro(ruta_tex))
    for err in errores:
        print(f"ERROR: {err}", file=sys.stderr)
    print(
        f"PDF verificado con pdfinfo: {info.ruta}\n"
        f"  Páginas       : {info.paginas}\n"
        f"  Page size (pt): {info.ancho_pt:.2f} × {info.alto_pt:.2f} pts\n"
        f"  Formato (mm)  : {info.ancho_mm:.1f} × {info.alto_mm:.1f} mm "
        f"(catálogo {ANCHO_MM} × {ALTO_MM} mm)\n"
        f"  Formato (in)  : {info.ancho_in:.2f} × {info.alto_in:.2f} in "
        f"(catálogo KDP / IngramSpark {ANCHO_PULGADAS} × {ALTO_PULGADAS} in)\n"
        f"  Versión PDF   : {info.version_pdf} · Encriptado: {info.encriptado}\n"
        f"  Tamaño archivo: {info.tamano_bytes:,} bytes"
    )
    return 1 if errores else 0


def _verificar_html(carpeta: Path) -> int:
    errores = validar_html(carpeta)
    for err in errores:
        print(f"ERROR: {err}", file=sys.stderr)
    if not errores:
        print(f"HTML verificado: {carpeta} ({len(list(carpeta.glob('*.html')))} páginas)")
    return 1 if errores else 0


def _verificar_epub(ruta_epub: Path) -> int:
    errores = validar_epub(ruta_epub)
    for err in errores:
        print(f"ERROR: {err}", file=sys.stderr)
    if not errores:
        print(
            f"EPUB verificado: {ruta_epub} ({ruta_epub.stat().st_size:,} bytes)"
        )
    return 1 if errores else 0


def _comprobar_fuentes(libro) -> list[str]:
    """Casos compilados al día con ``casos/`` e índice de imágenes completo."""
    from datetime import date

    from casos.compilar import Rutas, construir
    from libro.imagenes import RUTA_INDICE, leer_indice

    errores = [
        f"{ruta} no coincide con casos/; ejecute `python -m libro casos`."
        for ruta in construir(Rutas(RAIZ), date.today(), solo_comprobar=True)
    ]
    con_imagen = {e["condicion_id"] for e in leer_indice(RAIZ)}
    faltan = sorted(set(libro.condiciones) - con_imagen)
    if faltan:
        errores.append(f"{RUTA_INDICE.as_posix()} no tiene imagen para: {', '.join(faltan)}.")
    return errores


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="libro",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="orden", required=True)

    p_json = sub.add_parser("json", help="Exporta build/libro.json.")
    p_json.add_argument("--salida", type=Path, default=RUTA_JSON_DEFECTO)

    p_qmd = sub.add_parser("qmd", help="Genera build/libro.json y build/quarto/.")
    p_qmd.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)

    p_html = sub.add_parser("html", help="Compila el libro web HTML con Quarto.")
    p_html.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)
    p_html.add_argument("--salida", type=Path, default=RUTA_HTML_DEFECTO)

    for nombre in ("pdf", "build"):
        p_pdf = sub.add_parser(nombre, help="Compila el PDF (LuaLaTeX 170 x 244 mm).")
        p_pdf.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)
        p_pdf.add_argument("--salida", type=Path, default=RUTA_PDF_DEFECTO)

    p_epub = sub.add_parser("epub", help="Compila el EPUB 3 con Quarto.")
    p_epub.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)
    p_epub.add_argument("--salida", type=Path, default=RUTA_EPUB_DEFECTO)

    p_lzip = sub.add_parser("latex-zip", help="Empaqueta la fuente LuaLaTeX autocontenida.")
    p_lzip.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)
    p_lzip.add_argument("--salida", type=Path, default=RUTA_LATEX_ZIP_DEFECTO)

    p_all = sub.add_parser("all", help="Genera JSON, QMD, HTML, PDF, EPUB y ZIP LuaLaTeX.")
    p_all.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)
    p_all.add_argument("--pdf", type=Path, default=RUTA_PDF_DEFECTO)
    p_all.add_argument("--epub", type=Path, default=RUTA_EPUB_DEFECTO)
    p_all.add_argument("--html", type=Path, default=RUTA_HTML_DEFECTO)
    p_all.add_argument("--latex-zip", type=Path, default=RUTA_LATEX_ZIP_DEFECTO)

    sub.add_parser("mapa", help="Regenera mapa-maestro-libro.md.")
    sub.add_parser("registro-ia", help="Regenera docs/registro-ia.md desde git log.")

    sub.add_parser("casos", help="Recompila assets/data/casos/ desde casos/ y posts/.")

    p_img = sub.add_parser("imagenes", help="Índice mínimo de imágenes desde blog-index.json.")
    grupo = p_img.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--desde", type=Path, help="blog-index.json del blog: regenera el índice.")
    grupo.add_argument("--comprobar", type=Path, help="blog-index.json del blog: solo compara.")

    p_check = sub.add_parser("check", help="Valida fuentes, mapa, casos y salidas compiladas.")
    p_check.add_argument("--proyecto", type=Path, default=RUTA_PROYECTO_DEFECTO)
    p_check.add_argument("--pdf", type=Path, default=RUTA_PDF_DEFECTO)
    p_check.add_argument("--epub", type=Path, default=RUTA_EPUB_DEFECTO)
    p_check.add_argument("--html", type=Path, default=RUTA_HTML_DEFECTO)

    args = parser.parse_args(argv)

    if args.orden == "json":
        libro = cargar_libro(RAIZ)
        ruta = exportar_libro_json(libro, args.salida)
        print(f"JSON exportado en {ruta} ({ruta.stat().st_size:,} bytes).")
        return 0

    if args.orden == "qmd":
        archivos = generar_proyecto_quarto(args.proyecto, raiz=RAIZ)
        print(f"Proyecto Quarto generado en {args.proyecto} ({len(archivos)} archivos).")
        return 0

    if args.orden == "html":
        indice = compilar_libro_html(args.proyecto, raiz=RAIZ, destino=args.salida)
        print(f"Libro HTML compilado en {indice}.")
        return _verificar_html(args.salida)

    if args.orden in ("pdf", "build"):
        compilar_libro_pdf(args.salida, args.proyecto, raiz=RAIZ)
        return _verificar_pdf(args.proyecto, args.salida)

    if args.orden == "epub":
        compilar_libro_epub(args.salida, args.proyecto, raiz=RAIZ)
        return _verificar_epub(args.salida)

    if args.orden == "latex-zip":
        ruta = empaquetar_latex(args.salida, args.proyecto)
        print(f"Paquete LuaLaTeX generado en {ruta} ({ruta.stat().st_size:,} bytes).")
        return 0

    if args.orden == "all":
        indice = compilar_libro_html(args.proyecto, raiz=RAIZ, destino=args.html)
        print(f"Libro HTML compilado en {indice}.")
        rc_html = _verificar_html(args.html)
        compilar_libro_pdf(args.pdf, args.proyecto, raiz=RAIZ)
        rc_pdf = _verificar_pdf(args.proyecto, args.pdf)
        empaquetar_latex(args.latex_zip, args.proyecto)
        print(f"Paquete LuaLaTeX generado en {args.latex_zip}.")
        compilar_libro_epub(args.epub, args.proyecto, raiz=RAIZ)
        rc_epub = _verificar_epub(args.epub)
        return 1 if (rc_html or rc_pdf or rc_epub) else 0

    if args.orden == "mapa":
        ruta = escribir_mapa_maestro(RAIZ)
        print(f"Mapa maestro actualizado en {ruta}.")
        return 0

    if args.orden == "registro-ia":
        from libro.registro_ia import escribir_registro

        ruta = escribir_registro(RAIZ)
        print(f"Registro de uso de IA actualizado en {ruta}.")
        return 0

    if args.orden == "casos":
        from datetime import date

        from casos.compilar import Rutas, construir

        escritas = construir(Rutas(RAIZ), date.today(), solo_comprobar=False)
        print(f"Casos compilados: {len(escritas)} archivo(s) actualizado(s).")
        for ruta in escritas:
            print(f"  {ruta}")
        return 0

    if args.orden == "imagenes":
        from libro.imagenes import diferencias, escribir_indice

        if args.desde:
            ruta = escribir_indice(RAIZ, args.desde)
            print(f"Índice de imágenes actualizado en {ruta}.")
            return 0
        distintas = diferencias(RAIZ, args.comprobar)
        for cid in distintas:
            print(f"ERROR: la imagen de {cid} no coincide con {args.comprobar}.", file=sys.stderr)
        if not distintas:
            print("Índice de imágenes al día.")
        return 1 if distintas else 0

    # check
    libro = cargar_libro(RAIZ)
    errores_check = _comprobar_fuentes(libro)
    for err in errores_check:
        print(f"ERROR: {err}", file=sys.stderr)
    if errores_check:
        return 1
    esperado = renderizar_mapa_maestro(RAIZ)
    ruta_mapa_md = RAIZ / "mapa-maestro-libro.md"
    if not ruta_mapa_md.is_file() or ruta_mapa_md.read_text(encoding="utf-8") != esperado:
        print(
            "ERROR: mapa-maestro-libro.md está desactualizado; ejecute `python -m libro mapa`.",
            file=sys.stderr,
        )
        return 1

    total_casos = sum(1 for c in libro.condiciones.values() if c.caso_compilado is not None)
    total_quiz = sum(len(c.preguntas) for c in libro.condiciones.values())
    print(
        f"OK: {len(libro.unidades)} unidades · {len(libro.condiciones)} condiciones "
        f"(revisión fijada {libro.metadatos.fuente_clinica_revision[:12]}) · "
        f"{total_casos} casos socráticos · {total_quiz} preguntas de autoevaluación."
    )
    rc = 0
    if args.pdf.is_file():
        rc |= _verificar_pdf(args.proyecto, args.pdf)
    if args.epub.is_file():
        rc |= _verificar_epub(args.epub)
    if args.html.is_dir():
        rc |= _verificar_html(args.html)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
