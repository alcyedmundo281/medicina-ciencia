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
    assert (proyecto / "apendice-d-declaracion-ia.qmd").is_file()
    assert len(generados) >= 60


def test_mapa_maestro_sincronizado() -> None:
    ruta_mapa = RAIZ / "mapa-maestro-libro.md"
    assert ruta_mapa.is_file()
    assert ruta_mapa.read_text(encoding="utf-8") == renderizar_mapa_maestro(RAIZ)


# --- Ciclo 1: columna «Ref.» y caso socrático completo ---------------------------------


def _refs_anidadas(nodo: object) -> list[str]:
    """Todas las claves de referencia (``ref``/``ref_rendimiento``) de una entrada, a cualquier nivel."""
    encontradas: list[str] = []
    if isinstance(nodo, dict):
        for clave, valor in nodo.items():
            if clave in ("ref", "ref_rendimiento") and isinstance(valor, str) and valor.strip():
                encontradas.append(valor.strip())
            else:
                encontradas.extend(_refs_anidadas(valor))
    elif isinstance(nodo, list):
        for item in nodo:
            encontradas.extend(_refs_anidadas(item))
    return encontradas


def test_columna_ref_no_queda_vacia_si_la_evidencia_esta_referenciada() -> None:
    libro = cargar_libro(RAIZ)
    fallos: list[str] = []
    for cond in libro.condiciones.values():
        assert len(cond.evidencia) == len(cond.hallazgos_tabla)
        for ev, fila in zip(cond.evidencia, cond.hallazgos_tabla):
            refs = _refs_anidadas(ev)
            if not refs:
                continue
            if fila.referencia == "—" or any(r not in fila.referencia for r in refs):
                fallos.append(f"{cond.condicion_id} {fila.concepto_id}: {fila.referencia!r} vs {refs}")
    assert not fallos, f"{len(fallos)} filas con referencia perdida, p. ej. {fallos[:3]}"


def test_columna_ref_sin_duplicados_y_en_orden_estable() -> None:
    libro = cargar_libro(RAIZ)
    for cond in libro.condiciones.values():
        for fila in cond.hallazgos_tabla:
            if fila.referencia == "—":
                continue
            partes = [p.strip() for p in fila.referencia.split(";")]
            assert len(partes) == len(set(partes)), fila


def test_caso_renderizado_contiene_aviso_cierre_omitidos_y_referencias() -> None:
    from libro.datos import renderizar_caso_qmd

    libro = cargar_libro(RAIZ)
    casos = [c for c in libro.condiciones.values() if c.caso_compilado is not None]
    assert len(casos) == 18
    for cond in casos:
        caso = cond.caso_compilado
        texto = renderizar_caso_qmd(caso)
        # El aviso de caso ficticio va al inicio, antes de la viñeta.
        assert caso["aviso"] in texto, cond.condicion_id
        assert texto.index(caso["aviso"]) < texto.index(caso["vineta"]["texto"])
        for necesidad in caso["cierre"].get("necesidades_aprendizaje") or []:
            assert necesidad in texto, cond.condicion_id
        for omitido in caso.get("omitidos") or []:
            assert omitido["nombre"] in texto and omitido["motivo"] in texto, cond.condicion_id
        assert caso["referencias"], cond.condicion_id
        for ref in caso["referencias"]:
            assert ref["id"] in texto and ref["cita"] in texto, cond.condicion_id
