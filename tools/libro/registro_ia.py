"""Registro verificable del uso de IA: ``docs/registro-ia.md`` generado desde ``git log``.

Cada commit asistido por IA lleva el trailer ``Asistido-por: <herramienta> (<modelo>)``. Este
módulo lee esos trailers y escribe una tabla con hash, fecha y alcance (asunto del commit). Es la
evidencia que cita ``paratextos/declaracion-ia.md``.

El registro se regenera antes de cada commit (``python -m libro registro-ia``), de modo que
siempre lista todos los commits asistidos excepto, como mucho, el propio commit que lo actualiza:
ese aparece en la regeneración siguiente.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from libro.datos import RAIZ

TRAILER = "Asistido-por"
RUTA_REGISTRO = RAIZ / "docs" / "registro-ia.md"

_SEP_CAMPO = "\x1f"
_SEP_COMMIT = "\x1e"


@dataclass(frozen=True)
class CommitAsistido:
    hash: str
    fecha: str
    asistente: str
    alcance: str


def _git(raiz: Path, *args: str) -> str:
    res = subprocess.run(
        ["git", "-C", str(raiz), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return res.stdout


def historial_disponible(raiz: Path = RAIZ) -> bool:
    """``True`` si hay un repositorio git con historia completa (no un clon superficial)."""
    try:
        return _git(raiz, "rev-parse", "--is-shallow-repository").strip() == "false"
    except (OSError, subprocess.CalledProcessError):
        return False


def leer_commits_asistidos(raiz: Path = RAIZ) -> list[CommitAsistido]:
    """Commits con trailer ``Asistido-por``, del más antiguo al más reciente."""
    formato = _SEP_CAMPO.join(
        ["%H", "%ad", "%s", f"%(trailers:key={TRAILER},valueonly,separator=; )"]
    )
    salida = _git(raiz, "log", "--reverse", "--date=short", f"--format={formato}{_SEP_COMMIT}")
    commits: list[CommitAsistido] = []
    for bloque in salida.split(_SEP_COMMIT):
        bloque = bloque.strip("\n")
        if not bloque:
            continue
        hash_, fecha, asunto, asistente = bloque.split(_SEP_CAMPO)
        if asistente.strip():
            commits.append(
                CommitAsistido(
                    hash=hash_.strip(),
                    fecha=fecha.strip(),
                    asistente=asistente.strip(),
                    alcance=asunto.strip(),
                )
            )
    return commits


def _celda(texto: str) -> str:
    return texto.replace("|", "\\|")


def renderizar_registro(commits: list[CommitAsistido], url_repositorio: str) -> str:
    lineas = [
        "# Registro de uso de inteligencia artificial",
        "",
        "<!-- GENERADO por `python -m libro registro-ia` desde `git log`. No editar a mano. -->",
        "",
        f"Este registro lista los commits de este repositorio que llevan el trailer `{TRAILER}`.",
        "Cada fila se puede comprobar con `git show <hash>`. El alcance es el asunto del commit;",
        "el cuerpo del commit detalla qué archivos cambiaron y por qué.",
        "",
        "Los commits sin ese trailer no declaran asistencia de IA en el historial.",
        "",
        "| Commit | Fecha | Asistencia | Alcance |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for c in commits:
        enlace = f"[`{c.hash[:7]}`]({url_repositorio}/commit/{c.hash})"
        lineas.append(f"| {enlace} | {c.fecha} | {_celda(c.asistente)} | {_celda(c.alcance)} |")
    if not commits:
        lineas.append("| — | — | — | Sin commits asistidos registrados |")
    lineas.append("")
    return "\n".join(lineas)


def escribir_registro(raiz: Path = RAIZ, url_repositorio: str | None = None) -> Path:
    from libro.datos import leer_metadatos

    url = url_repositorio or leer_metadatos(raiz)[0].url_repositorio
    ruta = raiz / "docs" / "registro-ia.md"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(renderizar_registro(leer_commits_asistidos(raiz), url), encoding="utf-8", newline="\n")
    return ruta


def hashes_en_registro(texto: str) -> list[str]:
    """Hashes completos enlazados en un registro ya renderizado."""
    import re

    return re.findall(r"/commit/([0-9a-f]{40})\)", texto)
