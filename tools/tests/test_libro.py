"""Pruebas del contrato del libro Medicina y Ciencia (JSON -> QMD -> Quarto)."""

from __future__ import annotations

import json
from pathlib import Path

from libro.datos import RAIZ, cargar_libro, exportar_libro_json
from libro.mapa import renderizar_mapa_maestro
from libro.qmd import generar_proyecto_quarto


def test_carga_completa_48_condiciones_y_18_casos() -> None:
    libro = cargar_libro(RAIZ)
    assert len(libro.unidades) == 4
    assert len(libro.partes) == 6
    assert len(libro.condiciones) == 48
    casos = [c for c in libro.condiciones.values() if c.caso_compilado is not None]
    assert len(casos) == 18
    total_quiz = sum(len(c.preguntas) for c in libro.condiciones.values())
    assert total_quiz == 90


def test_revision_fijada_unica_en_todos_los_posts() -> None:
    libro = cargar_libro(RAIZ)
    esperada = libro.metadatos.fuente_clinica_revision
    revisiones = {c.revision_db for c in libro.condiciones.values()}
    assert revisiones == {esperada}


def test_exportacion_json_y_generacion_quarto(tmp_path: Path) -> None:
    proyecto = tmp_path / "quarto"
    ruta_json = tmp_path / "libro.json"
    generados = generar_proyecto_quarto(proyecto, raiz=RAIZ, ruta_json=ruta_json)

    assert ruta_json.is_file()
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert datos["esquema"] == "powersemiotics.libro.v1"
    assert datos["estadisticas"]["condiciones"] == 48
    assert datos["estadisticas"]["casos_socraticos"] == 18
    assert datos["estadisticas"]["preguntas_autoevaluacion"] == 90

    assert (proyecto / "_quarto.yml").is_file()
    assert (proyecto / "index.qmd").is_file()
    assert (proyecto / "portada.svg").is_file()
    assert (proyecto / "preambulo-libro.tex").is_file()
    assert (proyecto / "datos-libro.tex").is_file()
    assert (proyecto / "diseno-pdf.lua").is_file()
    assert (proyecto / "quitar-titulo.lua").is_file()
    assert (proyecto / "estilo-web.css").is_file()
    assert (proyecto / "estilo-epub.css").is_file()
    assert (proyecto / "apendice-a-autoevaluacion.qmd").is_file()
    assert (proyecto / "apendice-b-evidencia-iconografia.qmd").is_file()
    assert (proyecto / "apendice-c-declaracion-ia.qmd").is_file()
    assert len(generados) >= 60


def test_mapa_maestro_sincronizado() -> None:
    ruta_mapa = RAIZ / "mapa-maestro-libro.md"
    assert ruta_mapa.is_file()
    assert ruta_mapa.read_text(encoding="utf-8") == renderizar_mapa_maestro(RAIZ)
