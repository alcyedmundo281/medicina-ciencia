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


def test_casos_compilados_al_dia() -> None:
    from datetime import date

    from casos.compilar import Rutas, construir

    assert construir(Rutas(RAIZ), date.today(), solo_comprobar=True) == []


def test_check_detecta_caso_compilado_desactualizado(tmp_path) -> None:
    import shutil
    from datetime import date

    from casos.compilar import Rutas, construir

    for carpeta in ("casos", "posts", "assets/data/casos"):
        shutil.copytree(RAIZ / carpeta, tmp_path / carpeta)
    victima = sorted((tmp_path / "assets/data/casos").glob("*.json"))[0]
    victima.write_text(victima.read_text(encoding="utf-8") + " ", encoding="utf-8")
    sobrante = tmp_path / "assets/data/casos/sobrante.json"
    sobrante.write_text("{}", encoding="utf-8")
    pendientes = construir(Rutas(tmp_path), date.today(), solo_comprobar=True)
    assert f"assets/data/casos/{victima.name}" in pendientes
    assert "assets/data/casos/sobrante.json" in pendientes


def test_indice_de_imagenes_cubre_todas_las_condiciones() -> None:
    from libro.imagenes import CAMPOS, leer_indice

    libro = cargar_libro(RAIZ)
    indice = leer_indice(RAIZ)
    assert {e["condicion_id"] for e in indice} == set(libro.condiciones)
    for entrada in indice:
        assert set(entrada) == {"condicion_id", *CAMPOS}
        assert entrada["featured_image"] and entrada["image_license"], entrada["condicion_id"]
    assert [e["condicion_id"] for e in indice] == sorted(e["condicion_id"] for e in indice)


def test_extraer_indice_conserva_los_campos_tal_cual() -> None:
    from libro.imagenes import extraer_indice

    blog = [
        {"grounding": {"condicion_id": "HM:6002"}, "featured_image": "b.jpg", "image_license": "CC BY",
         "image_title": "B", "image_author": "Ana", "image_alt": "alt", "image_source": "s", "body": "x"},
        {"grounding": {"condicion_id": "HM:6001"}, "featured_image": "a.jpg"},
        {"grounding": {}, "featured_image": "sin-condicion.jpg"},
    ]
    indice = extraer_indice(blog)
    assert [e["condicion_id"] for e in indice] == ["HM:6001", "HM:6002"]
    assert indice[1]["image_author"] == "Ana" and "body" not in indice[1]
    assert indice[0]["image_license"] is None


def test_titulos_de_unidades_salen_de_su_qmd() -> None:
    import yaml

    mapa = yaml.safe_load((RAIZ / "mapa.yaml").read_text(encoding="utf-8"))
    for u in mapa["unidades"]:
        assert "titulo" not in u and "semanas" not in u, u["clave"]
    for unidad in cargar_libro(RAIZ).unidades:
        primera = next(
            l for l in (RAIZ / unidad.archivo).read_text(encoding="utf-8").splitlines() if l.startswith("# ")
        )
        assert primera.startswith(f"# {unidad.titulo}"), unidad.clave


def test_epub_declara_mathml_en_nav(tmp_path) -> None:
    import zipfile

    from libro.pdf import declarar_mathml_en_nav

    epub = tmp_path / "libro.epub"
    with zipfile.ZipFile(epub, "w") as zf:
        zf.writestr("META-INF/container.xml", "<container/>")
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("EPUB/nav.xhtml", '<nav><a>La tabla <math><mn>2</mn></math></a></nav>')
        zf.writestr("EPUB/content.opf", '<item id="nav" href="nav.xhtml" properties="nav" />')
    assert declarar_mathml_en_nav(epub)
    with zipfile.ZipFile(epub) as zf:
        assert zf.infolist()[0].filename == "mimetype"
        assert zf.infolist()[0].compress_type == zipfile.ZIP_STORED
        assert 'properties="nav mathml"' in zf.read("EPUB/content.opf").decode()
    assert not declarar_mathml_en_nav(epub)  # idempotente: ya declarado
