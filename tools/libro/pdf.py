"""Compilación de Quarto (HTML, PDF LuaLaTeX y EPUB) y verificación con pdfinfo / zipfile."""

from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from typing import TYPE_CHECKING

from libro import (
    ALTO_MM,
    ALTO_PT,
    ALTO_PULGADAS,
    ANCHO_MM,
    ANCHO_PT,
    ANCHO_PULGADAS,
    NOMBRE_SALIDA,
    TOLERANCIA_PT,
)
from libro.datos import RAIZ
from libro.qmd import generar_proyecto_quarto

if TYPE_CHECKING:
    from pathlib import Path

_PAGE_SIZE_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*x\s*([0-9]+(?:\.[0-9]+)?)\s*pts")


@dataclass(frozen=True)
class InfoPDF:
    ruta: Path
    paginas: int
    ancho_pt: float
    alto_pt: float
    ancho_mm: float
    alto_mm: float
    ancho_in: float
    alto_in: float
    encriptado: str
    version_pdf: str
    productor: str
    tamano_bytes: int
    salida_bruta: str


def _ejecutar_quarto(carpeta_proyecto: Path, formato: str) -> None:
    quarto = shutil.which("quarto")
    if quarto is None:
        raise RuntimeError("No se encontró 'quarto' en el PATH.")
    res = subprocess.run(
        [quarto, "render", str(carpeta_proyecto), "--to", formato],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"quarto render --to {formato} falló ({res.returncode}):\n"
            f"STDOUT:\n{res.stdout[-2500:]}\nSTDERR:\n{res.stderr[-2500:]}"
        )


def parsear_salida_pdfinfo(ruta_pdf: Path, texto: str, tamano_bytes: int = 0) -> InfoPDF:
    campos: dict[str, str] = {}
    for linea in texto.splitlines():
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            campos[clave.strip()] = valor.strip()

    paginas = int(campos.get("Pages", "0"))
    page_size_raw = campos.get("Page size", "")
    match = _PAGE_SIZE_RE.search(page_size_raw)
    if not match:
        raise ValueError(f"pdfinfo: no se pudo extraer 'Page size' de: {page_size_raw!r}")

    ancho_pt = float(match.group(1))
    alto_pt = float(match.group(2))
    return InfoPDF(
        ruta=ruta_pdf,
        paginas=paginas,
        ancho_pt=ancho_pt,
        alto_pt=alto_pt,
        ancho_mm=round(ancho_pt * 25.4 / 72.0, 1),
        alto_mm=round(alto_pt * 25.4 / 72.0, 1),
        ancho_in=round(ancho_pt / 72.0, 2),
        alto_in=round(alto_pt / 72.0, 2),
        encriptado=campos.get("Encrypted", "no"),
        version_pdf=campos.get("PDF version", ""),
        productor=campos.get("Producer", ""),
        tamano_bytes=tamano_bytes,
        salida_bruta=texto,
    )


def inspeccionar_pdf_con_pdfinfo(ruta_pdf: Path) -> InfoPDF:
    if not ruta_pdf.is_file():
        raise FileNotFoundError(f"No existe el archivo PDF: {ruta_pdf}")
    ejecutable = shutil.which("pdfinfo")
    if ejecutable is None:
        raise RuntimeError("No se encontró 'pdfinfo' en el PATH.")
    res = subprocess.run(
        [ejecutable, str(ruta_pdf)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        raise RuntimeError(f"pdfinfo falló ({res.returncode}): {res.stderr.strip()}")
    return parsear_salida_pdfinfo(ruta_pdf, res.stdout, tamano_bytes=ruta_pdf.stat().st_size)


def validar_info_pdf(info: InfoPDF, paginas_minimas: int = 40) -> list[str]:
    errores: list[str] = []
    if info.paginas < paginas_minimas:
        errores.append(
            f"El PDF tiene muy pocas páginas ({info.paginas}); se esperaban >= {paginas_minimas}."
        )
    if abs(info.ancho_pt - ANCHO_PT) > TOLERANCIA_PT:
        errores.append(
            f"Ancho incorrecto: {info.ancho_pt:.2f} pt ({info.ancho_mm:.1f} mm); "
            f"esperado {ANCHO_PT:.2f} pt ({ANCHO_MM} mm / {ANCHO_PULGADAS} in)."
        )
    if abs(info.alto_pt - ALTO_PT) > TOLERANCIA_PT:
        errores.append(
            f"Alto incorrecto: {info.alto_pt:.2f} pt ({info.alto_mm:.1f} mm); "
            f"esperado {ALTO_PT:.2f} pt ({ALTO_MM} mm / {ALTO_PULGADAS} in)."
        )
    if not info.encriptado.lower().startswith("no"):
        errores.append(f"El PDF no debe estar encriptado (Encrypted: {info.encriptado}).")
    if info.tamano_bytes <= 0:
        errores.append("El PDF está vacío (0 bytes).")
    return errores


def validar_tex_libro(ruta_tex: Path) -> list[str]:
    if not ruta_tex.is_file():
        return [f"No se encontró el archivo LaTeX compilado: {ruta_tex}"]
    tex = ruta_tex.read_text(encoding="utf-8")
    errores: list[str] = []
    patrones = (
        (f"paperwidth={ANCHO_MM}mm", f"geometría ancho {ANCHO_MM}mm"),
        (f"paperheight={ALTO_MM}mm", f"geometría alto {ALTO_MM}mm"),
        (r"\portadalibro", "portada vectorial \\portadalibro"),
        (r"\begin{portadillapdf}", "entorno portadillapdf"),
        (r"\begin{creditospdf}", "entorno creditospdf"),
        (r"\begin{casosocratico}", "entorno casosocratico"),
        ("Libertinus Serif", "tipografía Libertinus Serif"),
    )
    for patron, desc in patrones:
        if patron not in tex:
            errores.append(f"{ruta_tex.name}: falta {desc} ({patron!r}).")
    return errores


def validar_epub(ruta_epub: Path) -> list[str]:
    if not ruta_epub.is_file():
        return [f"No se encontró el archivo EPUB: {ruta_epub}"]
    if ruta_epub.stat().st_size <= 0:
        return ["El archivo EPUB está vacío (0 bytes)."]
    errores: list[str] = []
    try:
        with zipfile.ZipFile(ruta_epub, "r") as zf:
            nombres = set(zf.namelist())
            if "mimetype" not in nombres:
                errores.append("EPUB inválido: falta 'mimetype'.")
            else:
                mime = zf.read("mimetype").decode("utf-8", errors="replace").strip()
                if mime != "application/epub+zip":
                    errores.append(f"EPUB inválido: mimetype inesperado ({mime!r}).")
            if "META-INF/container.xml" not in nombres:
                errores.append("EPUB inválido: falta 'META-INF/container.xml'.")
            xhtmls = [n for n in nombres if n.endswith(".xhtml")]
            if len(xhtmls) < 50:
                errores.append(
                    f"EPUB incompleto: solo {len(xhtmls)} documentos XHTML (se esperaban >= 50)."
                )
    except zipfile.BadZipFile as err:
        errores.append(f"EPUB corrupto (no es un ZIP válido): {err}")
    return errores


def compilar_libro_html(carpeta_proyecto: Path, raiz: Path = RAIZ, destino: Path | None = None) -> Path:
    """Compila el sitio HTML y lo copia a ``destino`` (por defecto ``build/html``).

    Quarto vacía ``_book/`` en cada render: si después se compila el EPUB o el PDF, el HTML
    desaparece de ahí. Por eso el sitio se copia fuera, igual que el PDF y el EPUB.
    """
    generar_proyecto_quarto(carpeta_proyecto, raiz=raiz)
    _ejecutar_quarto(carpeta_proyecto, "html")
    origen = carpeta_proyecto / "_book"
    if not (origen / "index.html").is_file():
        raise FileNotFoundError(f"Quarto no generó el sitio HTML esperado en {origen}")
    destino = destino or carpeta_proyecto.parent / "html"
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(origen, destino)
    return destino / "index.html"


def validar_html(carpeta_html: Path) -> list[str]:
    indice = carpeta_html / "index.html"
    if not indice.is_file():
        return [f"No se encontró el sitio HTML: {indice}"]
    paginas = list(carpeta_html.glob("*.html"))
    if len(paginas) < 50:
        return [f"Sitio HTML incompleto: solo {len(paginas)} páginas (se esperaban >= 50)."]
    return []


def compilar_libro_pdf(ruta_salida: Path, carpeta_proyecto: Path, raiz: Path = RAIZ) -> Path:
    generar_proyecto_quarto(carpeta_proyecto, raiz=raiz)
    _ejecutar_quarto(carpeta_proyecto, "pdf")
    origen = carpeta_proyecto / "_book" / f"{NOMBRE_SALIDA}.pdf"
    if not origen.is_file():
        raise FileNotFoundError(f"Quarto no generó el PDF esperado en {origen}")
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origen, ruta_salida)
    return ruta_salida


def compilar_libro_epub(ruta_salida: Path, carpeta_proyecto: Path, raiz: Path = RAIZ) -> Path:
    generar_proyecto_quarto(carpeta_proyecto, raiz=raiz)
    _ejecutar_quarto(carpeta_proyecto, "epub")
    origen = carpeta_proyecto / "_book" / f"{NOMBRE_SALIDA}.epub"
    if not origen.is_file():
        raise FileNotFoundError(f"Quarto no generó el EPUB esperado en {origen}")
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origen, ruta_salida)
    declarar_mathml_en_nav(ruta_salida)
    return ruta_salida


def declarar_mathml_en_nav(ruta_epub: Path) -> bool:
    """Declara ``mathml`` en el ítem ``nav`` del OPF si el índice contiene fórmulas.

    Pandoc copia al índice (``nav.xhtml``) la notación matemática de los títulos
    («La tabla 2 × 2», «LR+»), pero no declara la propiedad en el manifiesto, y EPUBCheck lo
    marca como error (OPF-014). El EPUB se reescribe con ``mimetype`` primero y sin comprimir.
    """
    with zipfile.ZipFile(ruta_epub) as zf:
        entradas = [(info, zf.read(info.filename)) for info in zf.infolist()]
    entradas.sort(key=lambda e: e[0].filename != "mimetype")  # estable: mimetype primero
    contenido = {info.filename: datos for info, datos in entradas}
    nav = next((n for n in contenido if n.endswith("nav.xhtml")), None)
    opf = next((n for n in contenido if n.endswith(".opf")), None)
    if nav is None or opf is None or b"<math" not in contenido[nav]:
        return False
    texto_opf = contenido[opf].decode("utf-8")
    nuevo_opf, n = re.subn(
        r'(<item\b[^>]*\bproperties=")nav(")', r"\1nav mathml\2", texto_opf, count=1
    )
    if n == 0:
        return False
    temporal = ruta_epub.with_suffix(".tmp")
    with zipfile.ZipFile(temporal, "w") as destino:
        for info, datos in entradas:
            if info.filename == opf:
                datos = nuevo_opf.encode("utf-8")
            compresion = zipfile.ZIP_STORED if info.filename == "mimetype" else zipfile.ZIP_DEFLATED
            destino.writestr(info.filename, datos, compress_type=compresion)
    temporal.replace(ruta_epub)
    return True


def empaquetar_latex(ruta_zip: Path, carpeta_proyecto: Path) -> Path:
    """Empaqueta la fuente LuaLaTeX autocontenida (modelo biosemiotics)."""
    ruta_tex = carpeta_proyecto / f"{NOMBRE_SALIDA}.tex"
    if not ruta_tex.is_file():
        raise FileNotFoundError(
            f"No existe {ruta_tex}; ejecute primero `python -m libro pdf`."
        )
    ruta_zip.parent.mkdir(parents=True, exist_ok=True)
    instrucciones = (
        "Fuente LuaLaTeX autocontenida — Medicina y Ciencia\n"
        "==================================================\n\n"
        "Requisitos: LuaLaTeX (TeX Live / MiKTeX) con las fuentes Libertinus Serif,\n"
        "Libertinus Sans, Libertinus Mono, Libertinus Serif Display y FreeSerif.\n\n"
        "Compilación (dos pasadas para tabla de contenidos y referencias cruzadas):\n"
        f"  lualatex {NOMBRE_SALIDA}.tex\n"
        f"  lualatex {NOMBRE_SALIDA}.tex\n"
    )
    archivos = [
        ruta_tex,
        carpeta_proyecto / "preambulo-libro.tex",
        carpeta_proyecto / "datos-libro.tex",
        carpeta_proyecto / "portada.svg",
    ]
    with zipfile.ZipFile(ruta_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for archivo in archivos:
            if archivo.is_file():
                zf.write(archivo, arcname=archivo.name)
        zf.writestr("README-COMPILAR.txt", instrucciones)
    return ruta_zip
