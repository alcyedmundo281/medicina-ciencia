"""Ciclo 3: presentación de las fichas (registros como tablas y formato numérico)."""

from __future__ import annotations

import re

import pytest

from libro.datos import RAIZ, cargar_libro
from libro.presentacion import (
    ESPACIO_FINO,
    formatear_markdown,
    formatear_numeros,
    leer_registro_plano,
    porcentaje,
    presentar_cuerpo,
    rango_humano,
    serializar_como_blog,
)

F = ESPACIO_FINO


@pytest.fixture(scope="module")
def libro():
    return cargar_libro(RAIZ)


# --- Rangos semiabiertos -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("desde", "hasta", "unidad", "esperado"),
    [
        (7, 11, "puntos", "7–10 puntos"),
        (0, 4, "puntos", "0–3 puntos"),
        (4, 5, "puntos", "4 puntos"),
        (None, 1, "puntos", "≤ 0 puntos"),
        (1000, None, "mIU/mL", "≥ 1000 mIU/mL"),
        (3.0, None, None, "≥ 3,0"),
        (1.5, 2.5, "cm", "≥ 1,5 y < 2,5 cm"),
    ],
)
def test_rango_humano(desde, hasta, unidad, esperado) -> None:
    assert rango_humano(desde, hasta, unidad) == esperado


def test_porcentaje_no_pierde_precision() -> None:
    assert porcentaje(0.37) == f"37,0{F}%"
    assert porcentaje(0.217) == f"21,7{F}%"
    assert porcentaje(0.0125) == f"1,25{F}%"
    assert porcentaje(1) == f"100,0{F}%"


# --- Formato numérico ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "salida"),
    [
        ("LR+ 3.4", "LR+ 3,4"),
        ("sensibilidad 0.96", "sensibilidad 0,96"),
        ("96.0 %", f"96,0{F}%"),
        ("ronda el 56%;", f"ronda el 56{F}%;"),
        ("(2.0–6.0)", "(2,0–6,0)"),
    ],
)
def test_coma_decimal_y_espacio_fino(entrada: str, salida: str) -> None:
    assert formatear_numeros(entrada) == salida


@pytest.mark.parametrize(
    "intacto",
    [
        "`pmid:11147989`",
        "pmid:11147989",
        "doi:10.1001/jama.284.22.2912",
        "10.1086/340979",
        "`10.5281/zenodo.22064424`",
        "CIE-10 J02.0",
        "(HM:3026)",
        "[blog](https://powersemiotics.com/a/1.5)",
        "<https://doi.org/10.1/x.2>",
        ': {tbl-colwidths="[25,11,11]"}',
        "IC95%",
        "versión 1.2.3",
        "{#sec-hm6009}",
        "**Pregunta 1.2.** ¿Qué",
    ],
)
def test_no_toca_identificadores(intacto: str) -> None:
    assert formatear_numeros(intacto) == intacto


def test_formato_es_idempotente(libro) -> None:
    for cond in libro.condiciones.values():
        texto = formatear_markdown(cond.cuerpo_md)
        assert formatear_markdown(texto) == texto


def test_referencias_bibliograficas_no_se_reescriben() -> None:
    texto = "## Referencias y procedencia\n\n1. Smith J. A 2.5-fold rise. J Med. 2001.\n"
    assert formatear_markdown(texto) == texto


# --- Registros serializados -----------------------------------------------------------------


def test_registro_plano_admite_punto_y_coma_en_el_valor() -> None:
    texto = "Valor: 0.37; Población: niños; metaanálisis de 29 estudios; Referencia: pmid:1"
    campos = leer_registro_plano(texto, {"Valor": "", "Población": "", "Referencia": ""})
    assert campos == [
        ("Valor", "0.37"),
        ("Población", "niños; metaanálisis de 29 estudios"),
        ("Referencia", "pmid:1"),
    ]


def test_registro_plano_rechaza_claves_desconocidas() -> None:
    assert leer_registro_plano("Otra: 1; Valor: 2", {"Valor": ""}) is None


def test_todas_las_secciones_planas_y_tramos_se_convierten(libro) -> None:
    total = {"codigos": 0, "probabilidad_basal": 0, "tramos": 0}
    for cond in libro.condiciones.values():
        _, recuento = presentar_cuerpo(cond.cuerpo_md, cond.evidencia)
        for clave, n in recuento.items():
            total[clave] += n
    secciones = {
        "Códigos": sum("\n## Códigos" in "\n" + c.cuerpo_md for c in libro.condiciones.values()),
        "Probabilidad basal": sum(
            "\n## Probabilidad basal" in "\n" + c.cuerpo_md for c in libro.condiciones.values()
        ),
    }
    assert total["codigos"] == secciones["Códigos"] == 48
    assert total["probabilidad_basal"] == secciones["Probabilidad basal"] == 23
    assert total["tramos"] == sum(
        1 for c in libro.condiciones.values() for ev in c.evidencia if isinstance(ev.get("tramos"), list)
    )


def test_tablas_de_tramos_conservan_cada_cifra(libro) -> None:
    """Ninguna cifra de los tramos se pierde ni se altera al pasar a tabla."""
    for cond in libro.condiciones.values():
        texto, _ = presentar_cuerpo(cond.cuerpo_md, cond.evidencia)
        texto = formatear_markdown(texto)
        for ev in cond.evidencia:
            for tramo in ev.get("tramos") or []:
                assert serializar_como_blog(tramo) not in texto
                for clave, valor in tramo.items():
                    if clave in ("desde", "hasta") or not isinstance(valor, (int, float)):
                        continue
                    esperado = (
                        porcentaje(valor) if clave in ("sensibilidad", "especificidad") else str(valor).replace(".", ",")
                    )
                    assert esperado in texto, (cond.condicion_id, clave, valor)


def test_ninguna_tabla_nueva_deja_decimales_con_punto(libro) -> None:
    for cond in libro.condiciones.values():
        texto, _ = presentar_cuerpo(cond.cuerpo_md, cond.evidencia)
        texto = formatear_markdown(texto)
        for linea in texto.splitlines():
            if linea.startswith("| ") and "`" not in linea:
                assert not re.search(r"(?<![\w.])\d+\.\d+(?![\w/])", linea), linea


# --- Copia fijada de medsemiotics-db y secciones estructuradas -------------------------------


def test_copia_fijada_se_verifica_por_sha256(libro, tmp_path) -> None:
    import shutil

    from libro.fuente import CARPETA_FIJADA, FuenteAlterada, cargar_condicion_fijada

    fijadas = [c for c in libro.condiciones.values() if cargar_condicion_fijada(RAIZ, c.fuente)]
    assert len(fijadas) == 8
    cond = fijadas[0]
    copia = tmp_path / CARPETA_FIJADA / cond.fuente["condicion"]
    copia.parent.mkdir(parents=True)
    shutil.copyfile(RAIZ / CARPETA_FIJADA / cond.fuente["condicion"], copia)
    with copia.open("ab") as f:
        f.write(b"\n")
    with pytest.raises(FuenteAlterada):
        cargar_condicion_fijada(tmp_path, cond.fuente)


def test_escalas_reglas_nucleo_y_balance_se_estructuran(libro) -> None:
    from libro.datos import _extraer_nombres_conceptos
    from libro.fuente import cargar_condicion_fijada
    from libro.presentacion import SECCIONES_ESTRUCTURADAS, presentar_estructuras

    total = 0
    for cond in libro.condiciones.values():
        datos = cargar_condicion_fijada(RAIZ, cond.fuente)
        texto, n = presentar_estructuras(cond.cuerpo_md, datos, _extraer_nombres_conceptos(cond.cuerpo_md))
        total += n
        for titulo in SECCIONES_ESTRUCTURADAS:
            seccion = re.search(rf"^## {titulo}\n(.*?)(?=^## |\Z)", texto, re.M | re.S)
            if seccion:  # ninguna línea serializada «Clave: valor; Clave: valor» sobrevive
                assert not re.search(r"^\w[^|\n]*: [^\n]*; \w[^\n]*: ", seccion.group(1), re.M), cond.condicion_id
    assert total == 14


def test_ficha_reune_nombre_sinonimos_y_codigos(libro) -> None:
    from libro.presentacion import SECCIONES_FICHA, extraer_ficha

    for cond in libro.condiciones.values():
        texto, ficha = extraer_ficha(cond.cuerpo_md)
        assert ficha is not None, cond.condicion_id
        for titulo in SECCIONES_FICHA:
            assert f"\n## {titulo}\n" not in "\n" + texto
        for titulo in ("Nombre en inglés", "Sinónimos"):
            seccion = re.search(rf"^## {titulo}\n(.*?)(?=^## |\Z)", cond.cuerpo_md, re.M | re.S)
            for valor in (seccion.group(1).split("\n") if seccion else []):
                assert valor.strip() in ficha, (cond.condicion_id, valor)


def test_donde_no_confiar_cita_literal_y_solo_pmid_inequivoco(libro) -> None:
    from libro.fuente import referencias_declaradas
    from libro.presentacion import TITULO_NO_CONFIAR, presentar_no_confiar

    n = 0
    for cond in libro.condiciones.values():
        refs = referencias_declaradas(cond.fuente)
        texto, hecho = presentar_no_confiar(cond.cuerpo_md, refs[0] if len(refs) == 1 else None)
        original = re.search(r"^## Conclusión de la fuente\n(.*?)(?=^## |\Z)", cond.cuerpo_md, re.M | re.S)
        assert hecho == bool(original)
        if not original:
            continue
        n += 1
        assert f"## {TITULO_NO_CONFIAR}" in texto and "## Conclusión de la fuente" not in texto
        for parrafo in original.group(1).strip().split("\n\n"):
            assert parrafo.strip() in texto.replace("\n> ", "\n")
        citados = set(re.findall(r"— Conclusión de la fuente \(`(pmid:\d+)`\)", texto))
        assert citados <= set(refs) and (not citados or len(refs) == 1)
    assert n == 38


def test_claves_docentes_van_al_apendice(libro, tmp_path) -> None:
    from libro.qmd import generar_proyecto_quarto

    generar_proyecto_quarto(tmp_path)
    capitulos = "".join(p.read_text(encoding="utf-8") for p in tmp_path.glob("hm*.qmd"))
    apendice = (tmp_path / "apendice-c-claves-docentes.qmd").read_text(encoding="utf-8")
    assert "Clave docente" not in capitulos
    total = 0
    for cond in libro.condiciones.values():
        if cond.caso_compilado is None:
            continue
        ancla = "sec-claves-" + cond.condicion_id.lower().replace(":", "")
        assert f"@{ancla}" in capitulos and f"{{#{ancla}}}" in apendice
        for etapa in cond.caso_compilado["etapas"]:
            for preg in etapa.get("preguntas") or []:
                total += 1
                assert formatear_markdown(preg["clave"]) in apendice
    assert apendice.count("*Clave docente y evidencia:*") == total == 198
