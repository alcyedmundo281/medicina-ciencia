"""Índice mínimo de imágenes del blog (``assets/data/imagenes-blog.json``).

El libro solo usa, de ``blog-index.json`` de medsemiotics, la imagen destacada de cada condición
y sus datos de licencia. Este módulo extrae esos campos, sin transformarlos, a un índice
pequeño y ordenado, y comprueba que el índice versionado coincide con el del blog.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUTA_INDICE = Path("assets") / "data" / "imagenes-blog.json"

# Campos de cada entrada de blog-index.json que usa el libro, con su nombre original.
CAMPOS = ("featured_image", "image_title", "image_license", "image_author", "image_alt", "image_source")


def extraer_indice(blog_index: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Entradas ``{condicion_id, campos de imagen}`` ordenadas por condición."""
    entradas = []
    for item in blog_index:
        cid = (item.get("grounding") or {}).get("condicion_id")
        if not cid or not item.get("featured_image"):
            continue
        entradas.append({"condicion_id": cid, **{c: item.get(c) for c in CAMPOS}})
    return sorted(entradas, key=lambda e: e["condicion_id"])


def serializar(entradas: list[dict[str, Any]]) -> str:
    return json.dumps(entradas, ensure_ascii=False, indent=2) + "\n"


def leer_indice(raiz: Path) -> list[dict[str, Any]]:
    ruta = raiz / RUTA_INDICE
    if not ruta.is_file():
        return []
    return json.loads(ruta.read_text(encoding="utf-8"))


def escribir_indice(raiz: Path, ruta_blog_index: Path) -> Path:
    blog_index = json.loads(ruta_blog_index.read_text(encoding="utf-8"))
    ruta = raiz / RUTA_INDICE
    ruta.write_text(serializar(extraer_indice(blog_index)), encoding="utf-8", newline="\n")
    return ruta


def diferencias(raiz: Path, ruta_blog_index: Path) -> list[str]:
    """Condiciones cuyo índice versionado no coincide con el ``blog-index.json`` dado."""
    blog = {e["condicion_id"]: e for e in extraer_indice(json.loads(ruta_blog_index.read_text(encoding="utf-8")))}
    local = {e["condicion_id"]: e for e in leer_indice(raiz)}
    return sorted(cid for cid in blog.keys() | local.keys() if blog.get(cid) != local.get(cid))
