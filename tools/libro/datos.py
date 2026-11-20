"""Carga y validación de mapa.yaml, 48 artículos del blog, 18 casos socráticos y exportación JSON."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from casos.articulo import Articulo, leer_articulo
from casos.compilar import CasoLeido, Rutas, compilar, leer_casos
from casos.presentacion import autores_texto

RAIZ = Path(__file__).resolve().parents[2]

_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_H1_RE = re.compile(r"^#\s+.+?\r?\n+", re.MULTILINE)

LICENCIAS: dict[str, str] = {
    "CC BY-NC-SA 4.0": "Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional",
    "CC BY-SA 4.0": "Creative Commons Atribución-CompartirIgual 4.0 Internacional",
}


@dataclass(frozen=True)
class AutorLibro:
    nombre: str
    nombre_bibliografico: str
    rol: str
    orcid: str | None
    afiliacion: str | None


@dataclass(frozen=True)
class MetadatosLibro:
    titulo: str
    subtitulo: str
    coleccion: str
    edicion: str
    version: str
    fecha_edicion: str
    doi: str
    isbn: str
    audiencia: str
    licencia: str
    licencia_nombre: str
    licencia_fuentes: str
    contacto: str
    url_repositorio: str
    url_web: str
    url_sitio: str
    url_blog: str
    fuente_clinica_repo: str
    fuente_clinica_revision: str
    fuente_clinica_doi: str
    fuente_blog_repo: str
    fuente_blog_revision: str
    fuente_blog_doi: str
    autores: tuple[AutorLibro, ...]


_TITULO_QMD_RE = re.compile(r"^# (.+?)(?:\s+\{[^}]*\})?\s*$", re.MULTILINE)


def _titulo_de_unidad(ruta: Path) -> str:
    """Título del capítulo: el encabezado de primer nivel de su ``.qmd`` (única fuente)."""
    m = _TITULO_QMD_RE.search(ruta.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{ruta}: no tiene encabezado de primer nivel («# Título»).")
    return m.group(1).strip()


@dataclass(frozen=True)
class UnidadCurso:
    numero: int
    clave: str
    archivo: str
    titulo: str  # del encabezado «# …» de su .qmd, no de mapa.yaml
    casos_ancla: tuple[str, ...]


@dataclass(frozen=True)
class ParteBlog:
    clave: str
    titulo: str
    condiciones: tuple[str, ...]


@dataclass(frozen=True)
class ImagenCondicion:
    url: str
    titulo_commons: str
    licencia: str
    autor: str
    alt: str
    fuente: str


@dataclass(frozen=True)
class OpcionQuiz:
    texto: str
    correcta: bool
    feedback: str


@dataclass(frozen=True)
class PreguntaQuiz:
    condicion_id: str
    condicion_nombre: str
    pregunta_id: str
    pregunta: str
    concepto_id: str | None
    referencia_id: str | None
    opciones: tuple[OpcionQuiz, ...]


@dataclass(frozen=True)
class HallazgoTabla:
    condicion_id: str
    condicion_nombre: str
    concepto_id: str
    concepto_nombre: str
    rol: str
    estado_lr: str
    sensibilidad: str
    especificidad: str
    lr_positivo: str
    lr_negativo: str
    referencia: str


@dataclass(frozen=True)
class CondicionBlog:
    condicion_id: str
    post_id: str
    slug: str
    archivo_post: str
    titulo: str
    nombre_corto: str
    subtitulo: str
    fecha: str
    autor: str
    categoria: str
    categoria_etiqueta: str
    dificultad: str
    tiempo_lectura: str
    revision_db: str
    triada: dict[str, str]
    evidencia: tuple[dict[str, Any], ...]
    hallazgos_tabla: tuple[HallazgoTabla, ...]
    preguntas: tuple[PreguntaQuiz, ...]
    imagen: ImagenCondicion | None
    caso_compilado: dict[str, Any] | None
    cuerpo_md: str
    articulo: Articulo
    fuente: dict[str, Any]


@dataclass(frozen=True)
class LibroCompleto:
    metadatos: MetadatosLibro
    unidades: tuple[UnidadCurso, ...]
    partes: tuple[ParteBlog, ...]
    condiciones: dict[str, CondicionBlog]

    @property
    def condiciones_ordenadas(self) -> list[CondicionBlog]:
        resultado: list[CondicionBlog] = []
        for parte in self.partes:
            for cid in parte.condiciones:
                resultado.append(self.condiciones[cid])
        return resultado


def _requerido(datos: dict[str, Any], clave: str, origen: str) -> str:
    valor = datos.get(clave)
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{origen}: falta el campo obligatorio «{clave}»")
    return valor.strip()


def _fecha_iso(valor: Any, origen: str) -> str:
    """Normaliza una fecha YAML (``date`` o texto) a ``AAAA-MM-DD`` y falla si no es válida."""
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor.strip()).isoformat()
        except ValueError:
            pass
    raise ValueError(f"{origen}: se esperaba una fecha AAAA-MM-DD, se obtuvo {valor!r}")


def identificador_asignado(valor: str) -> bool:
    """Un DOI o ISBN existe solo si su valor en ``mapa.yaml`` no empieza por «Pendiente»."""
    return bool(valor.strip()) and not valor.strip().lower().startswith("pendiente")


def _fmt_pct(valor: Any) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, (int, float)):
        return f"{valor * 100:.1f} %"
    return str(valor)


def _fmt_lr(campo: Any) -> str:
    if campo is None:
        return "—"
    if isinstance(campo, dict):
        if "valor" in campo and campo["valor"] is not None:
            txt = f"{campo['valor']}"
            ic = campo.get("ic95")
            if isinstance(ic, list) and len(ic) == 2:
                txt += f" ({ic[0]}–{ic[1]})"
            return txt
        rango = campo.get("rango")
        if isinstance(rango, list) and len(rango) == 2:
            return f"{rango[0]}–{rango[1]}"
    if isinstance(campo, (int, float)):
        return f"{campo}"
    return str(campo)


_CLAVES_REF = ("ref", "ref_rendimiento")
# Orden de lectura: primero la referencia de nivel superior, luego la de cada medida en el orden
# en que se muestran las columnas de la tabla; el resto (tramos, graduación…) en orden YAML.
_CLAVES_PRIORITARIAS = (*_CLAVES_REF, "sensibilidad", "especificidad", "lr_positivo", "lr_negativo")


def _referencias_evidencia(ev: dict[str, Any]) -> list[str]:
    """Referencias de una entrada de evidencia, a cualquier profundidad, sin duplicados y en orden estable.

    En los posts derivados de ``medsemiotics-db`` la referencia de un cociente vive dentro de la
    medida (``lr_positivo.ref``, ``tramos[].ref``…), no siempre en el nivel superior.
    """
    vistas: list[str] = []

    def recorrer(nodo: Any) -> None:
        if isinstance(nodo, dict):
            for clave, valor in nodo.items():
                if clave in _CLAVES_REF:
                    if isinstance(valor, str) and valor.strip() and valor.strip() not in vistas:
                        vistas.append(valor.strip())
                else:
                    recorrer(valor)
        elif isinstance(nodo, list):
            for item in nodo:
                recorrer(item)

    for clave in _CLAVES_PRIORITARIAS:
        if clave in ev:
            recorrer({clave: ev[clave]})
    recorrer({k: v for k, v in ev.items() if k not in _CLAVES_PRIORITARIAS})
    return vistas


def _extraer_nombres_conceptos(cuerpo: str) -> dict[str, str]:
    """Extrae pares ``HM:xxxx -> Nombre`` de las cabeceras ``### Nombre (HM:xxxx)``."""
    nombres: dict[str, str] = {}
    for m in re.finditer(r"^###\s+(.+?)\s+\((HM:\d+)\)\s*$", cuerpo, re.MULTILINE):
        nombres[m.group(2)] = m.group(1).strip()
    return nombres


def _leer_frontmatter_y_cuerpo(ruta: Path) -> tuple[dict[str, Any], str]:
    texto = ruta.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(texto)
    if not m:
        raise ValueError(f"{ruta}: falta frontmatter YAML")
    fm = yaml.safe_load(m.group(1))
    if not isinstance(fm, dict):
        raise ValueError(f"{ruta}: frontmatter YAML inválido")
    cuerpo = texto[m.end() :].strip()
    # Quita el H1 inicial del post para evitar duplicarlo con el H1 del capítulo Quarto.
    cuerpo = _H1_RE.sub("", cuerpo, count=1).strip()
    return fm, cuerpo


def leer_metadatos(raiz: Path = RAIZ) -> tuple[MetadatosLibro, tuple[UnidadCurso, ...], tuple[ParteBlog, ...]]:
    ruta_mapa = raiz / "mapa.yaml"
    if not ruta_mapa.is_file():
        raise FileNotFoundError(f"Falta {ruta_mapa}")
    raw = yaml.safe_load(ruta_mapa.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{ruta_mapa}: se esperaba un mapeo YAML")

    obra = raw["obra"]
    fc = obra["fuente_clinica"]
    fb = obra["fuente_blog"]

    lic = _requerido(obra, "licencia", "mapa.yaml")
    if lic not in LICENCIAS:
        raise ValueError(f"mapa.yaml: licencia desconocida: {lic}")

    ruta_cff = raiz / "CITATION.cff"
    cff = yaml.safe_load(ruta_cff.read_text(encoding="utf-8"))

    autores = tuple(
        AutorLibro(
            nombre=_requerido(a, "nombre", "mapa.yaml"),
            nombre_bibliografico=_requerido(a, "nombre_bibliografico", "mapa.yaml"),
            rol=_requerido(a, "rol", "mapa.yaml"),
            orcid=a.get("orcid"),
            afiliacion=a.get("afiliacion"),
        )
        for a in raw["autores"]
    )
    meta = MetadatosLibro(
        titulo=_requerido(obra, "titulo", "mapa.yaml"),
        subtitulo=_requerido(obra, "subtitulo", "mapa.yaml"),
        coleccion=_requerido(obra, "coleccion", "mapa.yaml"),
        edicion=_requerido(obra, "edicion", "mapa.yaml"),
        version=_requerido(obra, "version", "mapa.yaml"),
        fecha_edicion=_fecha_iso(obra.get("fecha_edicion"), "mapa.yaml: fecha_edicion"),
        doi=_requerido(obra, "doi", "mapa.yaml"),
        isbn=_requerido(obra, "isbn", "mapa.yaml"),
        audiencia=_requerido(obra, "audiencia", "mapa.yaml"),
        licencia=lic,
        licencia_nombre=LICENCIAS[lic],
        licencia_fuentes=_requerido(obra, "licencia_fuentes", "mapa.yaml"),
        contacto=_requerido(obra, "contacto", "mapa.yaml"),
        url_repositorio=_requerido(cff, "repository-code", "CITATION.cff"),
        url_web=_requerido(cff, "url", "CITATION.cff"),
        url_sitio=_requerido(obra, "url_sitio", "mapa.yaml"),
        url_blog=_requerido(obra, "url_blog", "mapa.yaml"),
        fuente_clinica_repo=_requerido(fc, "repositorio", "mapa.yaml"),
        fuente_clinica_revision=_requerido(fc, "revision", "mapa.yaml"),
        fuente_clinica_doi=_requerido(fc, "doi", "mapa.yaml"),
        fuente_blog_repo=_requerido(fb, "repositorio", "mapa.yaml"),
        fuente_blog_revision=_requerido(fb, "revision", "mapa.yaml"),
        fuente_blog_doi=_requerido(fb, "doi", "mapa.yaml"),
        autores=autores,
    )
    unidades = tuple(
        UnidadCurso(
            numero=int(u["numero"]),
            clave=_requerido(u, "clave", "mapa.yaml"),
            archivo=_requerido(u, "archivo", "mapa.yaml"),
            titulo=_titulo_de_unidad(raiz / _requerido(u, "archivo", "mapa.yaml")),
            casos_ancla=tuple(u.get("casos_ancla", ())),
        )
        for u in raw["unidades"]
    )
    partes = tuple(
        ParteBlog(
            clave=_requerido(p, "clave", "mapa.yaml"),
            titulo=_requerido(p, "titulo", "mapa.yaml"),
            condiciones=tuple(p["condiciones"]),
        )
        for p in raw["partes_blog"]
    )
    return meta, unidades, partes


def _leer_imagenes_blog(raiz: Path) -> dict[str, ImagenCondicion]:
    """Imagen destacada de cada condición, del índice mínimo ``assets/data/imagenes-blog.json``."""
    from libro.imagenes import leer_indice

    imagenes: dict[str, ImagenCondicion] = {}
    for item in leer_indice(raiz):
        cid = item.get("condicion_id")
        url = item.get("featured_image")
        if cid and url:
            imagenes[cid] = ImagenCondicion(
                url=str(url),
                titulo_commons=str(item.get("image_title") or ""),
                licencia=str(item.get("image_license") or ""),
                autor=str(item.get("image_author") or ""),
                alt=str(item.get("image_alt") or ""),
                fuente=str(item.get("image_source") or ""),
            )
    return imagenes


def _compilar_casos_socraticos(raiz: Path) -> dict[str, dict[str, Any]]:
    dir_casos = raiz / "casos"
    if not dir_casos.is_dir():
        return {}
    rutas = Rutas(raiz)
    leidos: list[CasoLeido] = leer_casos(rutas)
    compilados: dict[str, dict[str, Any]] = {}
    for caso in leidos:
        cid = caso.articulo.condicion_id
        compilados[cid] = compilar(caso, date.today())
    return compilados


def cargar_libro(raiz: Path = RAIZ) -> LibroCompleto:
    """Carga y valida todo el corpus: mapa.yaml, 48 posts, 18 casos socráticos e imágenes."""
    meta, unidades, partes = leer_metadatos(raiz)
    imagenes = _leer_imagenes_blog(raiz)
    casos_compilados = _compilar_casos_socraticos(raiz)

    dir_posts = raiz / "posts"
    archivos_post = sorted(dir_posts.glob("*.md"))
    if not archivos_post:
        raise FileNotFoundError(f"No hay archivos .md en {dir_posts}")

    condiciones: dict[str, CondicionBlog] = {}
    revisiones_vistas: set[str] = set()

    for ruta in archivos_post:
        fm, cuerpo = _leer_frontmatter_y_cuerpo(ruta)
        articulo = leer_articulo(ruta)
        cid = articulo.condicion_id
        revision = str(fm.get("fuente", {}).get("revision") or "").strip()
        revisiones_vistas.add(revision)

        nombres_conceptos = _extraer_nombres_conceptos(cuerpo)
        nombre_corto = str(fm.get("grounding", {}).get("condicion_nombre") or fm["title"]).strip()

        evidencia_raw = fm.get("evidencia") or []
        filas: list[HallazgoTabla] = []
        for ev in evidencia_raw:
            concepto_id = str(ev.get("concepto") or "")
            ref = "; ".join(_referencias_evidencia(ev)) or "—"
            filas.append(
                HallazgoTabla(
                    condicion_id=cid,
                    condicion_nombre=nombre_corto,
                    concepto_id=concepto_id,
                    concepto_nombre=nombres_conceptos.get(concepto_id, concepto_id),
                    rol=str(ev.get("rol") or "—").replace("_", " "),
                    estado_lr=str(ev.get("estado_lr") or "—").replace("_", " "),
                    sensibilidad=_fmt_pct(ev.get("sensibilidad")),
                    especificidad=_fmt_pct(ev.get("especificidad")),
                    lr_positivo=_fmt_lr(ev.get("lr_positivo")),
                    lr_negativo=_fmt_lr(ev.get("lr_negativo")),
                    referencia=ref,
                )
            )

        preguntas: list[PreguntaQuiz] = []
        for q in fm.get("autoevaluacion") or []:
            opciones = tuple(
                OpcionQuiz(
                    texto=str(op.get("texto") or ""),
                    correcta=bool(op.get("correcta")),
                    feedback=str(op.get("feedback") or ""),
                )
                for op in q.get("opciones") or []
            )
            preguntas.append(
                PreguntaQuiz(
                    condicion_id=cid,
                    condicion_nombre=nombre_corto,
                    pregunta_id=str(q.get("id") or ""),
                    pregunta=str(q.get("pregunta") or ""),
                    concepto_id=q.get("concepto_id"),
                    referencia_id=q.get("referencia_id"),
                    opciones=opciones,
                )
            )

        triada_raw = fm.get("triada") or {}
        triada = {
            k: str(v).strip()
            for k, v in triada_raw.items()
            if isinstance(v, str) and v.strip()
        }

        condiciones[cid] = CondicionBlog(
            condicion_id=cid,
            post_id=str(fm.get("id") or cid),
            slug=str(fm.get("slug") or ruta.stem),
            archivo_post=ruta.name,
            titulo=str(fm.get("title") or nombre_corto),
            nombre_corto=nombre_corto,
            subtitulo=str(fm.get("subtitle") or ""),
            fecha=str(fm.get("date") or ""),
            autor=str(fm.get("author") or meta.autores[0].nombre_bibliografico),
            categoria=str(fm.get("category") or ""),
            categoria_etiqueta=str(fm.get("category_label") or ""),
            dificultad=str(fm.get("difficulty") or ""),
            tiempo_lectura=str(fm.get("reading_time") or ""),
            revision_db=revision,
            triada=triada,
            evidencia=tuple(evidencia_raw),
            hallazgos_tabla=tuple(filas),
            preguntas=tuple(preguntas),
            imagen=imagenes.get(cid),
            caso_compilado=casos_compilados.get(cid),
            cuerpo_md=cuerpo,
            articulo=articulo,
            fuente=dict(fm.get("fuente") or {}),
        )

    # Contrato 1: revisión única fijada de medsemiotics-db
    if revisiones_vistas != {meta.fuente_clinica_revision}:
        raise ValueError(
            "Revisión de medsemiotics-db inconsistente en posts/: "
            f"esperada {meta.fuente_clinica_revision!r}, encontradas {sorted(revisiones_vistas)}"
        )

    # Contrato 2: cobertura exacta 1-a-1 entre mapa.yaml y posts/
    asignadas: list[str] = [cid for parte in partes for cid in parte.condiciones]
    if len(asignadas) != len(set(asignadas)):
        duplicadas = sorted({c for c in asignadas if asignadas.count(c) > 1})
        raise ValueError(f"mapa.yaml contiene condiciones duplicadas: {duplicadas}")
    set_mapa = set(asignadas)
    set_posts = set(condiciones)
    if set_mapa != set_posts:
        faltan_en_posts = sorted(set_mapa - set_posts)
        faltan_en_mapa = sorted(set_posts - set_mapa)
        raise ValueError(
            f"Desajuste entre mapa.yaml y posts/: faltan en posts={faltan_en_posts}, "
            f"faltan en mapa={faltan_en_mapa}"
        )

    # Contrato 3: todos los casos ancla de las unidades existen en el compendio
    for unidad in unidades:
        ruta_u = raiz / unidad.archivo
        if not ruta_u.is_file():
            raise FileNotFoundError(f"Falta el archivo de unidad: {ruta_u}")
        for ancla in unidad.casos_ancla:
            if ancla not in condiciones:
                raise ValueError(f"Unidad {unidad.numero}: caso ancla inexistente {ancla}")

    return LibroCompleto(
        metadatos=meta,
        unidades=unidades,
        partes=partes,
        condiciones=condiciones,
    )


def renderizar_caso_qmd(compilado: dict[str, Any], ancla_claves: str | None = None) -> str:
    """Convierte un caso socrático compilado (JSON) a un bloque Markdown/Quarto estructurado.

    Con ``ancla_claves`` las claves docentes no se imprimen tras cada pregunta: el caso remite
    al apéndice de claves (véase :func:`renderizar_claves_caso_qmd`).
    """
    vineta = compilado["vineta"]
    autoria = compilado["autoria"]
    pub = compilado["publicacion"]
    revisor_txt = (
        f" · Revisión clínica: {autoria['revisor']}" if autoria.get("revisor") else ""
    )

    lineas: list[str] = [
        "::: {.caso-socratico}",
        f"**Caso socrático ABP — {vineta['titulo']}**  ",
        (
            f"*Autoría:* {autores_texto(autoria)}{revisor_txt} · "
            f"*Nivel:* {compilado['nivel']} · *Duración estimada:* {compilado['duracion_min']} min · "
            f"*Publicado:* `{pub['fecha']}`"
        ),
        "",
    ]
    if compilado.get("aviso"):
        lineas.extend([f"*{compilado['aviso']}*", ""])
    lineas.extend([f"**Viñeta clínica.** {vineta['texto']}", ""])

    datos_vineta = vineta.get("datos") or []
    if datos_vineta:
        lineas.append("**Datos iniciales:**")
        lineas.append("")
        for d in datos_vineta:
            lineas.append(f"- **{d['etiqueta']}:** {d['valor']}")
        lineas.append("")

    objetivos = compilado.get("objetivos") or []
    if objetivos:
        lineas.append("**Objetivos de aprendizaje:**")
        lineas.append("")
        for obj in objetivos:
            lineas.append(f"- {obj}")
        lineas.append("")

    for idx, etapa in enumerate(compilado.get("etapas") or [], start=1):
        lineas.append(f"#### Etapa {idx}. {etapa['titulo']} {{.unnumbered}}")
        lineas.append("")
        if etapa.get("informacion"):
            lineas.append(etapa["informacion"])
            lineas.append("")
        for d in etapa.get("datos") or []:
            lineas.append(f"- **{d['etiqueta']}:** {d['valor']}")
        if etapa.get("datos"):
            lineas.append("")
        for q_idx, preg in enumerate(etapa.get("preguntas") or [], start=1):
            lineas.append(f"**Pregunta {idx}.{q_idx}.** {preg['pregunta']}")
            lineas.append("")
            if ancla_claves is None:
                lineas.append(f"*Clave docente y evidencia:* {preg['clave']}")
                lineas.append("")

    if ancla_claves is not None and any(e.get("preguntas") for e in compilado.get("etapas") or []):
        lineas.append(f"*Las claves docentes de este caso están en @{ancla_claves}.*")
        lineas.append("")

    cierre = compilado.get("cierre")
    if isinstance(cierre, dict):
        if cierre.get("sintesis"):
            lineas.append(f"**Síntesis clínica.** {cierre['sintesis']}")
            lineas.append("")
        necesidades = cierre.get("necesidades_aprendizaje") or []
        if necesidades:
            lineas.append("**Necesidades de aprendizaje:**")
            lineas.append("")
            lineas.extend(f"- {n}" for n in necesidades)
            lineas.append("")
    elif isinstance(cierre, str) and cierre.strip():
        lineas.append(f"**Cierre.** {cierre.strip()}")
        lineas.append("")

    omitidos = compilado.get("omitidos") or []
    if omitidos:
        lineas.append("**Hallazgos de la ficha que este caso no usa:**")
        lineas.append("")
        lineas.extend(f"- {o['nombre']} (`{o['id']}`): {o['motivo'].rstrip('.')}." for o in omitidos)
        lineas.append("")

    referencias = compilado.get("referencias") or []
    if referencias:
        lineas.append("**Referencias del caso:**")
        lineas.append("")
        lineas.extend(f"- `{r['id']}` — {r['cita']}" for r in referencias)
        lineas.append("")

    lineas.append(":::")
    return "\n".join(lineas)


def renderizar_claves_caso_qmd(compilado: dict[str, Any], titulo: str, ancla: str) -> str:
    """Sección del apéndice de claves docentes para un caso: cada pregunta con su clave."""
    lineas = [f"## {titulo} {{#{ancla}}}", ""]
    for idx, etapa in enumerate(compilado.get("etapas") or [], start=1):
        for q_idx, preg in enumerate(etapa.get("preguntas") or [], start=1):
            lineas.append(f"**Pregunta {idx}.{q_idx}.** {preg['pregunta']}")
            lineas.append("")
            lineas.append(f"*Clave docente y evidencia:* {preg['clave']}")
            lineas.append("")
    return "\n".join(lineas)


def exportar_libro_json(libro: LibroCompleto, ruta_salida: Path) -> Path:
    """Exporta la representación JSON canónica completa del libro (capa JSON del pipeline)."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    total_casos = sum(1 for c in libro.condiciones.values() if c.caso_compilado is not None)
    total_quiz = sum(len(c.preguntas) for c in libro.condiciones.values())
    total_hallazgos = sum(len(c.hallazgos_tabla) for c in libro.condiciones.values())
    total_medidos = sum(
        1
        for c in libro.condiciones.values()
        for h in c.hallazgos_tabla
        if h.estado_lr == "medido"
    )

    payload = {
        "esquema": "powersemiotics.libro.v1",
        "metadatos": asdict(libro.metadatos),
        "estadisticas": {
            "unidades": len(libro.unidades),
            "partes_blog": len(libro.partes),
            "condiciones": len(libro.condiciones),
            "casos_socraticos": total_casos,
            "preguntas_autoevaluacion": total_quiz,
            "hallazgos_totales": total_hallazgos,
            "hallazgos_lr_medido": total_medidos,
        },
        "unidades": [asdict(u) for u in libro.unidades],
        "partes": [
            {
                "clave": parte.clave,
                "titulo": parte.titulo,
                "condiciones": [
                    {
                        "condicion_id": c.condicion_id,
                        "post_id": c.post_id,
                        "slug": c.slug,
                        "archivo_post": c.archivo_post,
                        "titulo": c.titulo,
                        "nombre_corto": c.nombre_corto,
                        "subtitulo": c.subtitulo,
                        "fecha": c.fecha,
                        "autor": c.autor,
                        "categoria": c.categoria,
                        "categoria_etiqueta": c.categoria_etiqueta,
                        "dificultad": c.dificultad,
                        "tiempo_lectura": c.tiempo_lectura,
                        "revision_db": c.revision_db,
                        "triada": c.triada,
                        "hallazgos": [asdict(h) for h in c.hallazgos_tabla],
                        "preguntas": [asdict(q) for q in c.preguntas],
                        "imagen": asdict(c.imagen) if c.imagen else None,
                        "caso_socratico": c.caso_compilado,
                    }
                    for cid in parte.condiciones
                    for c in (libro.condiciones[cid],)
                ],
            }
            for parte in libro.partes
        ],
    }
    ruta_salida.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return ruta_salida
