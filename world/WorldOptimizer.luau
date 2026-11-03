--!nonstrict
-- WorldOptimizer (3 Nov, world pass): measure and optimise WorldArt areas without changing the look.
-- Dev tool, Edit mode only:  local O = require(game.ServerStorage.DevTools.WorldOptimizer)
--   O.stats(root)                    -> text: parts, tris, unique meshes / textures, shadows, collision
--   O.swapKit(root, newKit)          -> ApplyMesh every RK_ piece to the low kit piece, keep size/cframe/tint
--   O.settings(root)                 -> collision, query, touch, shadow, RenderFidelity per piece class
--   O.ground(root, opts)             -> footprint raycasts, settle floating pieces, remove ungroundable
--   O.cull(root)                     -> remove rocks hidden inside bigger rocks or under terrain, thin scatter
-- Removed pieces go to ServerStorage.WorldRemoved_3Nov.<area>_opt (so nothing is lost).

local ServerStorage = game:GetService("ServerStorage")
local Terrain = workspace.Terrain
local O = {}

local SMALL = { RK_Pebbles = true, RK_Rubble = true }
local SCATTER = { RK_Boulder_A = true, RK_Boulder_B = true, RK_Boulder_C = true, RK_Boulder_Flat = true, RK_Slab_Tilted = true }
local SMALL_PLANTS = { FL_Lavender = true, FL_PinkFlowers = true, FL_WhiteFlowers = true, FL_BlueFlowers = true, FL_Bush_Low = true }

-- triangle counts (Blender, triangulated). RK hi = the v1 kit, RK lo = RockKitLite. FL = lite foliage kit.
O.TRIS_HI = {RK_Arch = 1656, RK_Boulder_A = 702, RK_Boulder_B = 350, RK_Boulder_C = 578, RK_Boulder_Flat = 518, RK_CliffCorner = 1738, RK_CliffTop_A = 2460, RK_CliffTop_B = 2080, RK_CliffWall_A = 2293, RK_CliffWall_B = 2360, RK_CliffWall_C = 2330, RK_Ledge_A = 560, RK_Ledge_B = 696, RK_MountainFace = 2342, RK_Outcrop_A = 1112, RK_Outcrop_B = 1250, RK_Outcrop_Tall = 746, RK_Pebbles = 492, RK_Rubble = 728, RK_Slab_Tilted = 536, RK_Spire = 764, RK_Stack_A = 867, RK_Stack_B = 1076, RK_LedgeWide = 484, RK_ShelfStep = 502,
	FL_BlueFlowers = 360, FL_Bush_A = 380, FL_Bush_B = 460, FL_Bush_Low = 340, FL_Ivy_A = 372, FL_Ivy_B = 568, FL_Lavender = 504, FL_PinkFlowers = 224, FL_WhiteFlowers = 208,
	SK_Trunk_A = 666, SK_Trunk_B = 666, SK_Trunk_C = 666, SK_Canopy_A = 1160, SK_Canopy_B = 1160, SK_Canopy_C = 1160}
O.TRIS_LO = {RK_Arch = 462, RK_Boulder_A = 294, RK_Boulder_B = 146, RK_Boulder_C = 242, RK_Boulder_Flat = 216, RK_CliffCorner = 486, RK_CliffTop_A = 688, RK_CliffTop_B = 582, RK_CliffWall_A = 641, RK_CliffWall_B = 658, RK_CliffWall_C = 652, RK_Ledge_A = 234, RK_Ledge_B = 292, RK_MountainFace = 654, RK_Outcrop_A = 466, RK_Outcrop_B = 524, RK_Outcrop_Tall = 312, RK_Pebbles = 196, RK_Rubble = 290, RK_Slab_Tilted = 224, RK_Spire = 320, RK_Stack_A = 363, RK_Stack_B = 450, RK_LedgeWide = 484, RK_ShelfStep = 502}

local function trisOf(p: MeshPart): number
	local a = p:GetAttribute("Tris")
	if a then return a end
	return O.TRIS_HI[p.Name] or 0
end
O.trisOf = trisOf

function O.stats(root: Instance): string
	local per = {}
	local tot = { parts = 0, tris = 0, shadow = 0, collide = 0, query = 0, touch = 0 }
	local meshes, cmaps, nmaps = {}, {}, {}
	for _, d in root:GetDescendants() do
		if d:IsA("MeshPart") then
			local grp = d.Parent and d.Parent.Name or "?"
			per[grp] = per[grp] or { n = 0, tris = 0 }
			per[grp].n += 1
			local t = trisOf(d)
			per[grp].tris += t
			tot.parts += 1
			tot.tris += t
			meshes[d.MeshId] = true
			local sa = d:FindFirstChildOfClass("SurfaceAppearance")
			if sa then
				cmaps[sa.ColorMap] = true
				if sa.NormalMap ~= "" then nmaps[sa.NormalMap] = true end
			elseif d.TextureID ~= "" then
				cmaps[d.TextureID] = true
			end
			if d.CastShadow then tot.shadow += 1 end
			if d.CanCollide then tot.collide += 1 end
			if d.CanQuery then tot.query += 1 end
			if d.CanTouch then tot.touch += 1 end
		end
	end
	local function cnt(t) local n = 0 for _ in t do n += 1 end return n end
	local lines = { string.format("TOTAL parts %d tris %d uniqueMeshes %d colourMaps %d normalMaps %d shadow %d collide %d query %d touch %d",
		tot.parts, tot.tris, cnt(meshes), cnt(cmaps), cnt(nmaps), tot.shadow, tot.collide, tot.query, tot.touch) }
	for g, v in per do
		table.insert(lines, string.format("  %s: %d parts, %d tris", g, v.n, v.tris))
	end
	return table.concat(lines, "\n")
end

-- ------------------------------------------------------------------ mesh swap
-- newKit: folder of low MeshParts named like the old ones, with BaseSize, Tris, SurfaceAppearance.
function O.swapKit(root: Instance, newKit: Instance, oldKit: Instance): string
	local n, miss = 0, 0
	for _, d in root:GetDescendants() do
		if d:IsA("MeshPart") and string.sub(d.Name, 1, 3) == "RK_" and not d:GetAttribute("Lite") then
			local lo = newKit:FindFirstChild(d.Name)
			local hi = oldKit:FindFirstChild(d.Name)
			if lo and hi then
				local scale = d.Size / (hi:GetAttribute("BaseSize") or hi.Size)
				local cf = d.CFrame
				local oldSa = d:FindFirstChildOfClass("SurfaceAppearance")
				local col = oldSa and oldSa.Color
				d:ApplyMesh(lo)
				d.Size = (lo:GetAttribute("BaseSize") or lo.Size) * scale
				d.CFrame = cf
				if oldSa then oldSa:Destroy() end
				local sa = lo:FindFirstChildOfClass("SurfaceAppearance"):Clone()
				if col then sa.Color = col end
				sa.Parent = d
				d:SetAttribute("Tris", lo:GetAttribute("Tris"))
				d:SetAttribute("Lite", true)
				n += 1
			else
				miss += 1
			end
			if n % 50 == 0 then task.wait() end
		end
	end
	return string.format("swapped %d, missing %d", n, miss)
end

-- ------------------------------------------------------------------ settings
function O.settings(root: Instance): string
	local n = 0
	for _, d in root:GetDescendants() do
		if d:IsA("MeshPart") then
			n += 1
			d.CanTouch = false
			pcall(function() d.RenderFidelity = Enum.RenderFidelity.Automatic end)
			if string.sub(d.Name, 1, 3) == "RK_" then
				local m = math.max(d.Size.X, d.Size.Y, d.Size.Z)
				if SMALL[d.Name] then
					d.CanCollide = false; d.CanQuery = false; d.CastShadow = false
					pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Box end)
				elseif SCATTER[d.Name] or m < 14 then
					d.CastShadow = m >= 8
					pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Box end)
				else
					pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Hull end)
				end
			elseif string.sub(d.Name, 1, 3) == "FL_" or string.sub(d.Name, 1, 3) == "SK_" then
				if string.sub(d.Name, 1, 9) ~= "SK_Trunk_" then
					d.CanCollide = false; d.CanQuery = false
					pcall(function() d.CollisionFidelity = Enum.CollisionFidelity.Box end)
				end
				if SMALL_PLANTS[d.Name] or string.sub(d.Name, 1, 6) == "FL_Ivy" then
					d.CastShadow = false
				end
			end
		end
	end
	return "settings on " .. n
end

-- ------------------------------------------------------------------ grounding
local function removedFolder(root: Instance): Folder
	local rem = ServerStorage:FindFirstChild("WorldRemoved_3Nov") or Instance.new("Folder")
	rem.Name = "WorldRemoved_3Nov"; rem.Parent = ServerStorage
	local f = rem:FindFirstChild(root.Name .. "_opt")
	if not f then
		f = Instance.new("Folder"); f.Name = root.Name .. "_opt"; f.Parent = rem
	end
	return f
end
O.removedFolder = removedFolder

local function stash(root, p: Instance, why: string)
	p:SetAttribute("OptRemoved", why)
	p:SetAttribute("FromGroup", p.Parent and p.Parent.Name or "")
	p.Parent = removedFolder(root)
end
O.stash = stash

-- footprint sample points (local x,z in -1..1) : centre, 4 edge mids, 4 corners at 0.7
local FOOT = { { 0, 0 }, { 0.75, 0 }, { -0.75, 0 }, { 0, 0.75 }, { 0, -0.75 }, { 0.6, 0.6 }, { -0.6, 0.6 }, { 0.6, -0.6 }, { -0.6, -0.6 } }

-- support = terrain + rocks (not foliage, not self)
function O.gaps(root: Instance, part: BasePart, footScale: number?)
	local cf, s = part.CFrame, part.Size
	local fs = footScale or 1
	local p2 = RaycastParams.new()
	p2.FilterType = Enum.RaycastFilterType.Exclude
	local excl = { part }
	for _, n in { "Ivy", "Bushes", "Flowers", "Trees" } do
		local f = root:FindFirstChild(n); if f then table.insert(excl, f) end
	end
	for _, pl in game:GetService("Players"):GetPlayers() do if pl.Character then table.insert(excl, pl.Character) end end
	p2.FilterDescendantsInstances = excl
	p2.IgnoreWater = false
	local maxG, minG, hits = -math.huge, math.huge, 0
	local bottomY = math.huge
	local half = s * 0.5
	for _, sx in { -1, 1 } do
		for _, sy in { -1, 1 } do
			for _, sz in { -1, 1 } do
				local c = cf:PointToWorldSpace(Vector3.new(sx * half.X, sy * half.Y, sz * half.Z))
				bottomY = math.min(bottomY, c.Y)
			end
		end
	end
	local res = {}
	-- real underside: ray up from below the box into the part itself (collision hull). Points where the
	-- part has no underside are skipped. Parts that cannot be queried use the box bottom.
	local selfP = RaycastParams.new()
	selfP.FilterType = Enum.RaycastFilterType.Include
	selfP.FilterDescendantsInstances = { part }
	local canHit = part.CanQuery
	local tp = RaycastParams.new()
	tp.FilterType = Enum.RaycastFilterType.Include
	tp.FilterDescendantsInstances = { Terrain }
	for _, f in FOOT do
		local wp = cf:PointToWorldSpace(Vector3.new(f[1] * half.X * fs, 0, f[2] * half.Z * fs))
		local under = bottomY
		local skip = false
		if canHit then
			local u = workspace:Raycast(Vector3.new(wp.X, bottomY - 2, wp.Z), Vector3.new(0, s.Magnitude + 4, 0), selfP)
			if u then under = u.Position.Y else skip = true end
		end
		local r = nil
		if not skip then
			r = workspace:Raycast(Vector3.new(wp.X, under + 0.05, wp.Z), Vector3.new(0, -(s.Y + 60), 0), p2)
			-- ground above the underside (rock dug into a slope): look from higher up
			local above = workspace:Raycast(Vector3.new(wp.X, under + s.Y * 1.5, wp.Z), Vector3.new(0, -s.Y * 1.5, 0), tp)
			if above then r = above end
			if not r then
				-- ray started inside solid terrain: look for the surface from far above
				local high = workspace:Raycast(Vector3.new(wp.X, under + 400, wp.Z), Vector3.new(0, -400, 0), tp)
				if high then r = high end
			end
		end
		if skip then
			-- no underside here: ignore
		elseif r then
			hits += 1
			local g = under - r.Position.Y
			maxG = math.max(maxG, g); minG = math.min(minG, g)
			table.insert(res, g)
		else
			maxG = math.max(maxG, 999)
			table.insert(res, 999)
		end
	end
	return maxG, minG, hits, bottomY, res
end

-- settle: sink so the highest-floating footprint point touches; remove if that buries it too deep
-- opts: groups (default Rocks, Scatter, Bushes, Flowers, Trees), tol (studs), maxSinkFrac
function O.ground(root: Instance, opts): string
	opts = opts or {}
	local groups = opts.groups or { "Scatter", "Rocks", "Trees", "Bushes", "Flowers" }
	local log = {}
	for _, gname in groups do
		local g = root:FindFirstChild(gname)
		if g then
			local sunk, removed, ok, worst = 0, 0, 0, 0
			for _, p in g:GetChildren() do
				if p:IsA("BasePart") then
					local isRock = string.sub(p.Name, 1, 3) == "RK_"
					local tol = opts.tol or (isRock and math.max(0.35, p.Size.Y * 0.03) or 0.3)
					local footScale = if isRock then (opts.rockFoot or 0.9) else (opts.plantFoot or 0.4)
					if string.sub(p.Name, 1, 9) == "SK_Trunk_" then footScale = 0.25 end
					local maxG = O.gaps(root, p, footScale)
					if maxG > tol then
						local need = maxG + (isRock and 0.25 or 0.1)
						local frac = need / p.Size.Y
						local limit = opts.maxSinkFrac or (isRock and 0.55 or 0.6)
						if maxG >= 999 or frac > limit then
							if not opts.dry then stash(root, p, "float " .. math.floor(maxG * 10) / 10) end
							removed += 1
						else
							if not opts.dry then
								p.CFrame = p.CFrame - Vector3.new(0, need, 0)
								-- tree canopy follows its trunk
								local link = p:GetAttribute("Canopy")
								if link then
									local c = g:FindFirstChild(link)
									if c then c.CFrame = c.CFrame - Vector3.new(0, need, 0) end
								end
							end
							sunk += 1
							worst = math.max(worst, maxG)
						end
					else
						ok += 1
					end
				end
			end
			table.insert(log, string.format("%s ok %d sunk %d removed %d worstGap %.1f", gname, ok, sunk, removed, worst))
		end
		task.wait()
	end
	return table.concat(log, "\n")
end

-- ------------------------------------------------------------------ culling
local function insideBox(part: BasePart, p: Vector3, shrink: number): boolean
	local l = part.CFrame:PointToObjectSpace(p)
	local h = part.Size * 0.5 * shrink
	return math.abs(l.X) <= h.X and math.abs(l.Y) <= h.Y and math.abs(l.Z) <= h.Z
end

local function terrainSolidAt(p: Vector3): boolean
	local r = Region3.new(p - Vector3.new(2, 2, 2), p + Vector3.new(2, 2, 2)):ExpandToGrid(4)
	local mats, occ = Terrain:ReadVoxels(r, 4)
	local m = mats[1][1][1]
	return m ~= Enum.Material.Air and m ~= Enum.Material.Water and occ[1][1][1] > 0.9
end

function O.cull(root: Instance, opts): string
	opts = opts or {}
	local rocks = {}
	for _, gname in { "Rocks", "Scatter" } do
		local g = root:FindFirstChild(gname)
		if g then for _, p in g:GetChildren() do if p:IsA("BasePart") and string.sub(p.Name, 1, 3) == "RK_" then table.insert(rocks, p) end end end
	end
	table.sort(rocks, function(a, b) return a.Size.Magnitude > b.Size.Magnitude end)
	local hidden, buried, thinned = 0, 0, 0
	local alive = {}
	for i, p in rocks do
		local s = p.Size * 0.5
		-- 9 test points: centre + top face corners and top centre (the visible part of a rock is its top)
		local pts = { p.Position }
		for _, sx in { -0.8, 0.8 } do
			for _, sz in { -0.8, 0.8 } do
				table.insert(pts, p.CFrame:PointToWorldSpace(Vector3.new(sx * s.X, 0.85 * s.Y, sz * s.Z)))
				table.insert(pts, p.CFrame:PointToWorldSpace(Vector3.new(sx * s.X, 0, sz * s.Z)))
			end
		end
		table.insert(pts, p.CFrame:PointToWorldSpace(Vector3.new(0, s.Y, 0)))
		-- inside a bigger rock?
		local covered = false
		for _, q in alive do
			if q.Size.Magnitude > p.Size.Magnitude * 1.2 and (q.Position - p.Position).Magnitude < q.Size.Magnitude then
				local allIn = true
				for _, pt in pts do
					if not insideBox(q, pt, 0.82) then allIn = false break end
				end
				if allIn then covered = true break end
			end
		end
		if covered then
			if not opts.dry then stash(root, p, "hidden in rock") end
			hidden += 1
		else
			-- buried: top and upper corners all under solid terrain
			local under = true
			for k = 2, #pts do
				if k % 2 == 0 or k == #pts then
					if not terrainSolidAt(pts[k] + Vector3.new(0, 1, 0)) then under = false break end
				end
			end
			if under then
				if not opts.dry then stash(root, p, "under terrain") end
				buried += 1
			else
				table.insert(alive, p)
			end
		end
		if i % 60 == 0 then task.wait() end
	end
	-- thin pebbles/rubble: keep one per ~14 studs, and none right against a big rock
	local sc = root:FindFirstChild("Scatter")
	if sc and not opts.keepScatter then
		local kept = {}
		for _, p in sc:GetChildren() do
			if SMALL[p.Name] and p.Parent then
				local close = false
				for _, q in kept do
					if (q.Position - p.Position).Magnitude < (opts.scatterGap or 14) then close = true break end
				end
				if close then
					if not opts.dry then stash(root, p, "thin scatter") end
					thinned += 1
				else
					table.insert(kept, p)
				end
			end
		end
	end
	return string.format("hidden %d buried %d scatterThinned %d", hidden, buried, thinned)
end

-- foliage overlap: drop flowers/bushes whose centre sits within r of another of the same kind
function O.thinFoliage(root: Instance, opts): string
	opts = opts or {}
	local out = {}
	for gname, r in { Flowers = opts.flowerGap or 5, Bushes = opts.bushGap or 6, Ivy = opts.ivyGap or 4 } do
		local g = root:FindFirstChild(gname)
		local n = 0
		if g then
			local kept = {}
			for _, p in g:GetChildren() do
				if p:IsA("BasePart") then
					local close = false
					for _, q in kept do
						if (q.Position - p.Position).Magnitude < r * math.max(1, p.Size.X / 6) then close = true break end
					end
					if close then
						if not opts.dry then stash(root, p, "overlap") end
						n += 1
					else
						table.insert(kept, p)
					end
				end
			end
		end
		table.insert(out, gname .. " -" .. n)
	end
	return table.concat(out, ", ")
end

return O
