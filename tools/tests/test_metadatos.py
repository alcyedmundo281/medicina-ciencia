"""Pruebas de coherencia de metadatos entre mapa.yaml, CITATION.cff y .zenodo.json."""

from __future__ import annotations

import json

import yaml

from libro.datos import RAIZ, leer_metadatos


def test_coherencia_citation_zenodo_y_mapa() -> None:
    meta, unidades, partes = leer_metadatos(RAIZ)
    cff = yaml.safe_load((RAIZ / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = json.loads((RAIZ / ".zenodo.json").read_text(encoding="utf-8"))

    assert meta.url_repositorio == cff["repository-code"]
    assert meta.url_repositorio == "https://github.com/alcyedmundo281/medicina-ciencia"
    assert zenodo["license"] == cff["license"] == "CC-BY-NC-SA-4.0"
    assert zenodo["language"] == "spa"
    assert len(unidades) == 4
    assert sum(len(p.condiciones) for p in partes) == 48
