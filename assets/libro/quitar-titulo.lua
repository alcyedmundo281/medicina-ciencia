-- Suprime el \chapter* automático de Quarto en index.qmd para que la portada TikZ sea la página 1.

local quitada = false

function Header(el)
  if quitada or not quarto.doc.is_format("pdf") then
    return nil
  end
  if el.level == 1 and el.classes:includes("titulo-de-obra") then
    quitada = true
    return {}
  end
  return nil
end
