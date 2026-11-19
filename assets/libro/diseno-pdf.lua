-- Filtro Lua de diseño editorial para la salida PDF (LuaLaTeX) de Medicina y Ciencia.
-- Convierte divisiones semánticas de Quarto en entornos LaTeX definidos en
-- assets/libro/preambulo.tex y reemplaza reglas horizontales por filetes.

local MapaEntornos = {
  ["portadilla-pdf"] = "portadillapdf",
  ["portadilla-titulo"] = "portadillatitulo",
  ["creditos-pdf"] = "creditospdf",
  ["triada-signo"] = "triadasigno",
  ["alerta-ficha"] = "alertaficha",
  ["caso-socratico"] = "casosocratico",
  ["perlas-clinicas"] = "perlasclinicas",
  ["enlace-ficha"] = "enlaceficha",
}

local function envolver_entorno(bloques, nombre_entorno)
  local resultado = pandoc.List({
    pandoc.RawBlock("latex", "\\begin{" .. nombre_entorno .. "}"),
  })
  resultado:extend(bloques)
  resultado:insert(pandoc.RawBlock("latex", "\\end{" .. nombre_entorno .. "}"))
  return resultado
end

function Div(el)
  if not quarto.doc.is_format("pdf") then
    return nil
  end
  for clase, entorno in pairs(MapaEntornos) do
    if el.classes:includes(clase) then
      return envolver_entorno(el.content, entorno)
    end
  end
  return nil
end

function HorizontalRule()
  if not quarto.doc.is_format("pdf") then
    return nil
  end
  return pandoc.RawBlock(
    "latex",
    "\\par\\vspace{0.55em}{\\color{libroborde}\\hrule height 0.4pt}\\vspace{0.55em}"
  )
end

-- Identificadores largos en código (PMID, DOI, revisiones) como \path: con xurl admiten
-- cortes de línea y no desbordan las columnas estrechas. Los encabezados se dejan intactos
-- porque \path no es robusto en argumentos móviles (índice y cabeceras).
local LONGITUD_MINIMA_PATH = 11

local function codigo_a_path(el)
  if #el.text < LONGITUD_MINIMA_PATH or el.text:find("|", 1, true) then
    return nil
  end
  -- «pmid:12345678»: corte preferente tras el prefijo, para que el número no se parta.
  local prefijo, resto = el.text:match("^(%a+:)(.+)$")
  if prefijo then
    return pandoc.RawInline("latex", "\\path|" .. prefijo .. "|\\allowbreak\\path|" .. resto .. "|")
  end
  return pandoc.RawInline("latex", "\\path|" .. el.text .. "|")
end

-- Intervalos «(29,0–210,0)» en columnas estrechas: se permite cortar tras la raya.
local function intervalo_cortable(el)
  local a, b = el.text:match("^(%(?[%d,]+–)([%d,]+%)?[.,;]?)$")
  if not a then
    return nil
  end
  return { pandoc.Str(a), pandoc.RawInline("latex", "\\penalty500{}"), pandoc.Str(b) }
end

-- Encabezado seguido de tabla: \Needspace evita que el título quede al pie y que longtable
-- repita la cabecera de la tabla por encima de él en la página siguiente.
local filtro_encabezado_tabla = {
  Blocks = function(bloques)
    if not quarto.doc.is_format("pdf") then
      return nil
    end
    local salida = pandoc.Blocks({})
    for i, b in ipairs(bloques) do
      local siguiente = bloques[i + 1]
      if b.t == "Header" and siguiente and siguiente.t == "Table" then
        salida:insert(pandoc.RawBlock("latex", "\\Needspace{8\\baselineskip}"))
      end
      salida:insert(b)
    end
    return salida
  end,
}

local filtro_codigo = {
  traverse = "topdown",
  Header = function(el)
    return el, false
  end,
  Code = function(el)
    if not quarto.doc.is_format("pdf") then
      return nil
    end
    return codigo_a_path(el)
  end,
  -- DOI escritos como texto llano en las referencias («DOI: 10.1016/j.acra.2017.06.007.»):
  -- mismo tratamiento, conservando la puntuación final fuera de \path. El texto no cambia.
  Str = function(el)
    if not quarto.doc.is_format("pdf") then
      return nil
    end
    local doi, cola = el.text:match("^(10%.%d%d%d%d+/[^%s|]-)([.,;:)]*)$")
    if not doi or #doi < LONGITUD_MINIMA_PATH then
      return intervalo_cortable(el)
    end
    local salida = { pandoc.RawInline("latex", "\\path|" .. doi .. "|") }
    if cola ~= "" then
      table.insert(salida, pandoc.Str(cola))
    end
    return salida
  end,
}

return {
  { Div = Div, HorizontalRule = HorizontalRule },
  filtro_encabezado_tabla,
  filtro_codigo,
}
