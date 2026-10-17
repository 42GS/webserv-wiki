-- Keep the body of a pubs.opengroup.org page: the blocks after the first
-- top-level div.NAVHEADER, up to the block holding "return to top of page".
local stop = "return to top of page"
function Pandoc(doc)
  local start, finish
  for i, block in ipairs(doc.blocks) do
    if not start and block.t == "Div" and block.classes:includes("NAVHEADER") then
      start = i + 1
    elseif start and pandoc.utils.stringify(block):find(stop, 1, true) then
      finish = i - 1
      break
    end
  end
  if not start then error("no div.NAVHEADER") end
  if not finish then error("no \"" .. stop .. "\"") end
  local kept = {}
  for i = start, finish do kept[#kept + 1] = doc.blocks[i] end
  return pandoc.Pandoc(kept, doc.meta)
end
