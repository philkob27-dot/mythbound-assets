-- GEARKIT_SOLID_PATCH (2 november 2026): kleine aanpassingen zodat de 15 nieuwe armorsets (gear15) werken.
-- De nieuwe meshes hebben geen palet-texture: elk onderdeel is een eigen MeshPart met een eigen kleur en
-- materiaal (role "solid"), en elk onderdeel zegt vanaf welke rarity het zichtbaar is (rarity).
-- Niets hiervan is al in Studio gezet. Drie plekken:

-- 1. ReplicatedStorage.Shared.data.GearMeshes, het type MeshPart: vier optionele velden erbij.
export type MeshPart = { role: string, center: Vector3, size: Vector3, glow: Color3?, attr: string?,
	light: { name: string, range: number, brightness: number }?,
	color: Color3?, material: string?, rarity: string?, sway: boolean? }

-- 2. ServerStorage.DevTools.art.GearKitSetup, in run(), in de lus over entry.parts: een tak voor "solid"
--    tussen de tak voor "glow" en de laatste else (de tint-tak).
--[[
			elseif meta.role == "solid" then
				for _, c in p:GetChildren() do
					if c:IsA("SurfaceAppearance") then
						c:Destroy()
					end
				end
				p.TextureID = ""
				p.Color = meta.color or Color3.new(1, 1, 1)
				local ok, mat = pcall(function()
					return (Enum.Material :: any)[meta.material or "SmoothPlastic"]
				end)
				p.Material = if ok and mat then mat else Enum.Material.SmoothPlastic
				if meta.rarity then
					p:SetAttribute("Rarity", meta.rarity)
				end
				if meta.sway then
					p:SetAttribute("Sway", true)
				end
				if root == nil then
					root = p
				end
]]

-- 3. ReplicatedStorage.Shared.gear.GearFit.build: een optionele rarity, zodat onderdelen boven de rarity
--    van het item niet getoond worden. Bovenaan GearFit:
local RANK = { Common = 1, Uncommon = 2, Rare = 3, Epic = 4, Legendary = 5 }
--    De kop van build wordt: function GearFit.build(name, character, tint, rarity: string?)
--    en in de lus over entry.parts, direct na de regel "for pname, meta in entry.parts do":
--[[
		if rarity and meta.rarity and (RANK[meta.rarity] or 1) > (RANK[rarity] or 5) then
			continue
		end
]]
--    Zonder rarity (zoals nu overal) wordt alles getoond, dus bestaande sets veranderen niet.
--
-- Gear.luau: de nieuwe sets hebben per slot meer modellen dan de oude helper set() maakt (handschoenen,
-- dijplaten, laarzen). De lijst per slot staat bovenaan elk <Set>_GearMeshes.luau bestand
-- ("Pieces per slot"); geef die lijsten mee als models van de pieces.
--
-- Sway: onderdelen met sway = true (capes, linten, kralen, veren, tasjes) zijn nu nog vast gelast aan hun
-- lichaamsdeel. Ze zijn apart gehouden zodat er later een zwaai-effect op kan.
return nil
