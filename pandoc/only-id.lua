-- Keep only the element whose id equals the metadata value "keep-id".
local keep
function Meta(m) keep = pandoc.utils.stringify(m["keep-id"] or "") end
function Pandoc(doc)
  local found
  doc:walk({ Div = function(d) if d.identifier == keep and not found then found = d end end })
  if not found then error("no element with id " .. keep) end
  return pandoc.Pandoc(found.content, doc.meta)
end
