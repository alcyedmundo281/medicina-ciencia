"""Ciclo 2: veracidad de metadatos, identificadores y declaración de uso de IA."""

from __future__ import annotations

import dataclasses
import json
import re
import tomllib
from pathlib import Path

import pytest
import yaml

from libro.datos import RAIZ, cargar_libro, identificador_asignado
from libro.qmd import _datos_libro_tex, _generar_portada_svg, _sello_edicion, generar_proyecto_quarto
from libro.registro_ia import hashes_en_registro, historial_disponible, leer_commits_asistidos


@pytest.fixture(scope="module")
def libro():
    return cargar_libro(RAIZ)


@pytest.fixture(scope="module")
def proyecto(tmp_path_factory) -> Path:
    carpeta = tmp_path_factory.mktemp("quarto")
    generar_proyecto_quarto(carpeta, raiz=RAIZ, ruta_json=carpeta / "libro.json")
    return carpeta


# --- Identificadores pendientes ------------------------------------------------------------


def afirmaciones_de_identificador(texto: str, nombre: str) -> list[str]:
    """Frases que afirman que la obra tiene ``nombre`` (DOI o ISBN) propio.

    Una mención como «**ISBN:** Pendiente de asignación» o el DOI de una *fuente* no es una
    afirmación; «con DOI e ISBN propios» sí lo es.
    """
    patron = re.compile(
        rf"\b(con|tiene|posee|cuenta con)\b[^.\n|]{{0,30}}\b{nombre}\b"
        rf"|\b{nombre}\b[^.\n|]{{0,30}}\bpropios?\b",
        re.IGNORECASE,
    )
    frases = []
    for m in patron.finditer(texto):
        inicio = max(texto.rfind(".", 0, m.start()), texto.rfind("\n\n", 0, m.start())) + 1
        fin_punto = texto.find(".", m.end())
        frase = texto[inicio : fin_punto if fin_punto != -1 else len(texto)]
        if not re.search(r"\bpendientes?\b", frase, re.IGNORECASE):  # no «independiente»
            frases.append(m.group(0))
    return frases


def test_detector_reconoce_la_afirmacion_antigua() -> None:
    assert afirmaciones_de_identificador("EDICIÓN CON DOI E ISBN PROPIOS", "DOI")
    assert afirmaciones_de_identificador("EDICIÓN CON DOI E ISBN PROPIOS", "ISBN")
    assert afirmaciones_de_identificador("Publicación independiente, con DOI e ISBN propios, compilada", "ISBN")
    assert not afirmaciones_de_identificador("**ISBN:** Pendiente de asignación (edición impresa)", "ISBN")
    assert not afirmaciones_de_identificador("Su DOI y su ISBN están pendientes de asignación.", "DOI")


def _paratextos(proyecto: Path) -> dict[str, str]:
    rutas = [
        RAIZ / "README.md",
        RAIZ / "LICENSE",
        RAIZ / "CITATION.cff",
        RAIZ / ".zenodo.json",
        RAIZ / "mapa-maestro-libro.md",
        RAIZ / "assets" / "libro" / "preambulo.tex",
        *sorted((RAIZ / "docs").glob("*.md")),
        *sorted((RAIZ / "paratextos").glob("*.md")),
        proyecto / "index.qmd",
        proyecto / "portada.svg",
        proyecto / "datos-libro.tex",
    ]
    return {str(r.relative_to(r.parents[1])): r.read_text(encoding="utf-8") for r in rutas}


def test_ningun_paratexto_afirma_doi_o_isbn_pendiente(libro, proyecto) -> None:
    meta = libro.metadatos
    fallos = []
    for nombre, valor in (("DOI", meta.doi), ("ISBN", meta.isbn)):
        if identificador_asignado(valor):
            continue
        for ruta, texto in _paratextos(proyecto).items():
            for frase in afirmaciones_de_identificador(texto, nombre):
                fallos.append(f"{ruta}: «{frase}» con {nombre} = {valor!r}")
    assert not fallos, "\n".join(fallos)


def test_metadatos_de_cita_no_declaran_doi_pendiente(libro) -> None:
    cff = yaml.safe_load((RAIZ / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))
    if not identificador_asignado(libro.metadatos.doi):
        assert "doi" not in cff
        assert not any(i.get("type") == "doi" for i in cff.get("identifiers", []))
        assert "doi" not in zenodo
    else:
        assert cff["doi"] == libro.metadatos.doi


def test_sello_de_portada_condicional(libro) -> None:
    meta = libro.metadatos
    assert _sello_edicion(dataclasses.replace(meta, doi="Pendiente", isbn="Pendiente")) == (
        "PUBLICACIÓN INDEPENDIENTE"
    )
    con_ambos = dataclasses.replace(meta, doi="10.5281/zenodo.1", isbn="978-0-00-000000-0")
    assert _sello_edicion(con_ambos).endswith("EDICIÓN CON DOI E ISBN PROPIOS")
    con_doi = dataclasses.replace(meta, doi="10.5281/zenodo.1", isbn="Pendiente")
    assert _sello_edicion(con_doi).endswith("EDICIÓN CON DOI PROPIO")


# --- Contadores y fecha desde los datos ----------------------------------------------------


def test_portada_sin_contadores_fijos(libro) -> None:
    preambulo = (RAIZ / "assets" / "libro" / "preambulo.tex").read_text(encoding="utf-8")
    assert not re.search(r"\d+ (capítulos|condiciones|casos|preguntas)", preambulo)
    casos = sum(1 for c in libro.condiciones.values() if c.caso_compilado is not None)
    preguntas = sum(len(c.preguntas) for c in libro.condiciones.values())
    esperados = [
        f"{len(libro.unidades)} capítulos de fundamentos",
        f"{len(libro.condiciones)} condiciones verificadas",
        f"{casos} casos socráticos",
        f"{preguntas} preguntas de autoevaluación",
    ]
    tex, svg = _datos_libro_tex(libro), _generar_portada_svg(libro)
    for texto in esperados:
        assert texto in tex and texto in svg, texto


def test_version_y_fecha_coinciden_en_todas_las_fuentes(libro, proyecto) -> None:
    meta = libro.metadatos
    cff = yaml.safe_load((RAIZ / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))
    pyproject = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    quarto = yaml.safe_load((proyecto / "_quarto.yml").read_text(encoding="utf-8"))

    assert str(cff["version"]) == zenodo["version"] == pyproject["project"]["version"] == meta.version
    assert str(cff["date-released"]) == zenodo["publication_date"] == meta.fecha_edicion
    assert quarto["book"]["date"] == meta.fecha_edicion


# --- Declaración de uso de IA --------------------------------------------------------------

RUTA_DECLARACION = RAIZ / "paratextos" / "declaracion-ia.md"


def test_declaracion_en_apendices_y_citada_en_creditos(proyecto) -> None:
    quarto = yaml.safe_load((proyecto / "_quarto.yml").read_text(encoding="utf-8"))
    assert "apendice-c-declaracion-ia.qmd" in quarto["book"]["appendices"]
    apendice = (proyecto / "apendice-c-declaracion-ia.qmd").read_text(encoding="utf-8")
    assert "{#sec-declaracion-ia}" in apendice
    assert "{{" not in apendice, "marcadores sin resolver en la declaración"
    assert "/docs/registro-ia.md" in apendice
    creditos = (proyecto / "index.qmd").read_text(encoding="utf-8")
    assert "@sec-declaracion-ia" in creditos


def test_declaracion_nombra_herramienta_modelo_y_responsabilidad() -> None:
    texto = RUTA_DECLARACION.read_text(encoding="utf-8")
    for requerido in ("Claude Code", "Claude Opus 5.5", "Anthropic", "ICMJE", "COPE", "no es autora"):
        assert requerido in texto, requerido


def _oraciones(texto: str) -> list[str]:
    return [o.strip() for o in re.split(r"(?<=[.;:])\s+|\n\n", texto) if o.strip()]


def test_declaracion_no_restringe_el_alcance_que_el_registro_contradice() -> None:
    """«exclusivamente» junto a un alcance de la IA es falso si el registro tiene commits.

    Los commits registrados incluyen correcciones de la capa de render y paratextos, que no son
    «andamiaje»; por eso cualquier alcance restringido con «exclusivamente» queda contradicho.
    """
    registro = (RAIZ / "docs" / "registro-ia.md").read_text(encoding="utf-8")
    if not hashes_en_registro(registro):
        pytest.skip("el registro aún no tiene commits asistidos")
    texto = RUTA_DECLARACION.read_text(encoding="utf-8")
    contradichas = [
        o
        for o in _oraciones(texto)
        if re.search(r"\bexclusivamente\b", o, re.IGNORECASE)
        and re.search(r"\b(IA|inteligencia artificial|herramientas|modelo)\b", o, re.IGNORECASE)
    ]
    assert not contradichas, contradichas


def test_registro_ia_al_dia_con_el_historial() -> None:
    """Todo commit asistido, salvo a lo sumo el último (el que actualiza el registro), figura en él."""
    if not historial_disponible(RAIZ):
        pytest.skip("sin historial git completo (p. ej. clon superficial en CI)")
    registrados = set(hashes_en_registro((RAIZ / "docs" / "registro-ia.md").read_text(encoding="utf-8")))
    asistidos = [c.hash for c in leer_commits_asistidos(RAIZ)]
    assert registrados <= set(asistidos), "el registro lista commits que no existen o no están asistidos"
    faltan = [h for h in asistidos[:-1] if h not in registrados]
    assert not faltan, f"regenere con `python -m libro registro-ia`; faltan {faltan}"
