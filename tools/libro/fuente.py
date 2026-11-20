"""Lectura verificada de la copia fijada de ``medsemiotics-db`` (``assets/data/medsemiotics-db``).

Cada archivo se acepta solo si su sha256 coincide con el que declara el front-matter del post
(``fuente.archivos``) y la revisión del post es la fijada. No se edita ni se interpreta nada:
el YAML se devuelve tal cual para que la capa de render lo presente.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

CARPETA_FIJADA = Path("assets") / "data" / "medsemiotics-db"


class FuenteAlterada(ValueError):
    """La copia local no coincide con el hash declarado por el post."""


def ruta_fijada(raiz: Path, relativa: str) -> Path:
    return raiz / CARPETA_FIJADA / relativa


def cargar_condicion_fijada(raiz: Path, fuente: dict[str, Any]) -> dict[str, Any] | None:
    """YAML de la condición del post si está en la copia fijada; ``None`` si no se copió.

    Lanza :class:`FuenteAlterada` si el archivo existe pero sus bytes no son los declarados.
    """
    relativa = str(fuente.get("condicion") or "")
    if not relativa:
        return None
    ruta = ruta_fijada(raiz, relativa)
    if not ruta.is_file():
        return None
    esperado = str((fuente.get("archivos") or {}).get(relativa) or "")
    obtenido = hashlib.sha256(ruta.read_bytes()).hexdigest()
    if not esperado or obtenido != esperado:
        raise FuenteAlterada(
            f"{ruta}: sha256 {obtenido} no coincide con el declarado por el post ({esperado or 'ausente'})."
        )
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    return datos if isinstance(datos, dict) else None


def referencias_declaradas(fuente: dict[str, Any]) -> list[str]:
    """PMID de los archivos ``referencias/pmid-N.yaml`` que el post declara como fuente."""
    pmids = []
    for relativa in (fuente.get("archivos") or {}):
        nombre = Path(str(relativa))
        if nombre.parent.name == "referencias" and nombre.stem.startswith("pmid-"):
            pmids.append("pmid:" + nombre.stem.removeprefix("pmid-"))
    return pmids
