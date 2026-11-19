"""Generador de mapa-maestro-libro.md desde mapa.yaml, posts/ y casos/."""

from __future__ import annotations

from typing import TYPE_CHECKING

from libro.datos import RAIZ, cargar_libro

if TYPE_CHECKING:
    from pathlib import Path


def renderizar_mapa_maestro(raiz: Path = RAIZ) -> str:
    libro = cargar_libro(raiz)
    meta = libro.metadatos
    total_cond = len(libro.condiciones)
    total_casos = sum(1 for c in libro.condiciones.values() if c.caso_compilado is not None)
    total_quiz = sum(len(c.preguntas) for c in libro.condiciones.values())

    lineas: list[str] = [
        "# Mapa maestro del libro",
        "",
        "<!-- GENERADO desde mapa.yaml, posts/ y casos/ con `python -m libro mapa`. No editar a mano. -->",
        "",
        f"**Obra:** {meta.titulo} — *{meta.subtitulo}*  ",
        f"**Edición:** {meta.edicion} · **DOI:** {meta.doi} · **ISBN:** {meta.isbn}  ",
        f"**Fuente clínica fijada:** `{meta.fuente_clinica_repo}@{meta.fuente_clinica_revision[:12]}` "
        f"(DOI `{meta.fuente_clinica_doi}`)  ",
        f"**Licencia:** {meta.licencia} (obra) · {meta.licencia_fuentes} (fichas del blog) · MIT (código)",
        "",
        (
            f"**Resumen de la obra:** {len(libro.unidades)} capítulos de fundamentos · "
            f"{len(libro.partes)} partes clínicas · {total_cond} condiciones verificadas · "
            f"{total_casos} casos socráticos · {total_quiz} preguntas de autoevaluación."
        ),
        "",
        "## Parte I — Fundamentos: del hallazgo a la decisión",
        "",
        "| Cap. | Bloque | Título | Casos ancla |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for u in libro.unidades:
        anclas = ", ".join(f"`{a}`" for a in u.casos_ancla)
        lineas.append(f"| {u.numero} | {u.semanas} | {u.titulo} | {anclas} |")

    for idx_parte, parte in enumerate(libro.partes, start=2):
        lineas.extend(
            [
                "",
                f"## Parte {idx_parte} — {parte.titulo}",
                "",
                "| Código | Condición | Área | Caso socrático | Preguntas | Archivo |",
                "| :--- | :--- | :--- | :---: | :---: | :--- |",
            ]
        )
        for cid in parte.condiciones:
            c = libro.condiciones[cid]
            caso_txt = "✅ Sí" if c.caso_compilado is not None else "—"
            lineas.append(
                f"| `{c.condicion_id}` | {c.nombre_corto} | {c.categoria_etiqueta} | "
                f"{caso_txt} | {len(c.preguntas)} | `{c.archivo_post}` |"
            )

    lineas.append("")
    return "\n".join(lineas)


def escribir_mapa_maestro(raiz: Path = RAIZ) -> Path:
    destino = raiz / "mapa-maestro-libro.md"
    destino.write_text(renderizar_mapa_maestro(raiz), encoding="utf-8")
    return destino
