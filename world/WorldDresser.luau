--!nonstrict
-- WorldDresser (3 Nov, world pass): dresses a terrain area with the self-made RockKit and FoliageKit in the
-- style of Philip's reference shots. Dev tool, Edit mode only (run through execute_luau or the command bar):
--   local D = require(game.ServerStorage.DevTools.WorldDresser)
--   D.run(D.Areas.Watchstone)        -- backup, remove old cliff props, rocks, terrain repaint, foliage
--   D.undo("Watchstone")             -- removes everything it placed and puts the old props + terrain back
-- Kits: ServerStorage.RockKit (RK_*) and ServerStorage.FoliageKit (FL_*), MeshParts with SurfaceAppearance and
-- an attribute BaseSize (the size in studs the piece was modelled at). RockKit pieces also carry Tint (the
-- calibrated sand tone for SurfaceAppearance.Color).
-- Output: workspace.WorldArt.<area>.{Rocks, Ivy, Bushes, Flowers, Scatter, Trees}; every piece has the
-- attribute Dresser = <area>. Terrain backup: ServerStorage.WorldBackup_3Nov.<area> (Corner attribute).
-- Removed props: ServerStorage.WorldRemoved_3Nov.<area> (attribute FromPath on each).

local ServerStorage = game:GetService("ServerStorage")
local Terrain = workspace.Terrain

local D = {}

D.Areas = {
	Watchstone = {
		name = "Watchstone",
		min = Vector3.new(-8320, 0, -1280),
		max = Vector3.new(-7680, 440, -520),
		-- keep clear: story spots (x, z, r)
		keepOut = { { -8100, -1100, 70 } }, -- the stone circle on the top
		seed = 3112026,
		ivyCap = 230,
	},
}

local ROCK_STEEP = { "RK_CliffWall_A", "RK_CliffWall_B", "RK_CliffWall_C", "RK_CliffWall_A", "RK_CliffWall_B", "RK_CliffCorner", "RK_Outcrop_Tall" }
local ROCK_MID = { "RK_MountainFace", "RK_CliffTop_A", "RK_CliffTop_B", "RK_Stack_A", "RK_Stack_B", "RK_Ledge_A", "RK_Ledge_B", "RK_Outcrop_A", "RK_Outcrop_B", "RK_MountainFace" }
local SCATTER = { "RK_Boulder_A", "RK_Boulder_B", "RK_Boulder_C", "RK_Boulder_Flat", "RK_Pebbles", "RK_Rubble", "RK_Slab_Tilted", "RK_Pebbles" }
local FLOWERS = { "FL_Lavender", "FL_Lavender", "FL_Lavender", "FL_PinkFlowers", "FL_PinkFlowers", "FL_PinkFlowers", "FL_BlueFlowers", "FL_WhiteFlowers" }
local BUSHES = { "FL_Bush_A", "FL_Bush_B", "FL_Bush_Low" }
local IVY = { "FL_Ivy_A", "FL_Ivy_B" }
local OLD_ROCK_NAMES = { "^Cliff_", "^Boulder" }

D.UseLite = false -- v4: true = place RockKitLite pieces (decimated, shared atlases) once their textures are processed
local function kit(name: string): MeshPart
	local lite = D.UseLite and ServerStorage:FindFirstChild("RockKitLite")
	local k = (lite and lite:FindFirstChild(name)) or ServerStorage:FindFirstChild("RockKit"):FindFirstChild(name) or ServerStorage:FindFirstChild("FoliageKit"):FindFirstChild(name)
	assert(k, "kit piece missing: " .. name)
	return k
end

local function folder(parent: Instance, name: string): Folder
	local f = parent:FindFirstChild(name)
	if not f then
		f = Instance.new("Folder")
		f.Name = name
		f.Parent = parent
	end
	return f
end

local function terrainParams()
	local p = RaycastParams.new()
	p.FilterType = Enum.RaycastFilterType.Include
	p.FilterDescendantsInstances = { Terrain }
	p.IgnoreWater = false
	return p
end

local function riverPoints(): { Vector3 }
	local pts = {}
	local br = workspace:FindFirstChild("BrindleRiver")
	if br then
		for _, d in br:GetDescendants() do
			if d:IsA("BasePart") then
				table.insert(pts, d.Position)
			end
		end
	end
	-- the river line from data.WorldMap (Brindle River)
	for _, xz in { { -8100, -1000 }, { -7800, -600 }, { -7560, -100 } } do
		table.insert(pts, Vector3.new(xz[1], 0, xz[2]))
	end
	return pts
end

local function distSeg2(p: Vector3, a: Vector3, b: Vector3): number
	local ax, az, bx, bz, px, pz = a.X, a.Z, b.X, b.Z, p.X, p.Z
	local dx, dz = bx - ax, bz - az
	local l2 = dx * dx + dz * dz
	local t = if l2 > 0 then math.clamp(((px - ax) * dx + (pz - az) * dz) / l2, 0, 1) else 0
	local qx, qz = ax + dx * t - px, az + dz * t - pz
	return math.sqrt(qx * qx + qz * qz)
end

-- distance (2D) from p to the river: nearest of the waterfall parts and the polyline
local riverCache: { Vector3 }? = nil
local function riverDist(p: Vector3): number
	riverCache = riverCache or riverPoints()
	local best = math.huge
	local pts = riverCache :: { Vector3 }
	for i, q in pts do
		local dx, dz = q.X - p.X, q.Z - p.Z
		best = math.min(best, math.sqrt(dx * dx + dz * dz))
	end
	local line = { Vector3.new(-8100, 0, -1000), Vector3.new(-7800, 0, -600), Vector3.new(-7560, 0, -100) }
	for i = 1, #line - 1 do
		best = math.min(best, distSeg2(p, line[i], line[i + 1]))
	end
	return best
end
D.riverDist = riverDist

-- v4 masks: area circles + island-wide circles (D.Masks: {x, z, r}) + segments (D.MaskSegs: {ax, az, bx, bz, r},
-- roads and paths) + any terrain water within 10 studs. Filled by D.buildMasks() (see below).
D.Masks = {}
D.MaskSegs = {}
local waterCache = {}
local function waterNear(p: Vector3, r: number): boolean
	local key = math.floor(p.X / 8) .. "," .. math.floor(p.Z / 8) .. "," .. r
	local c = waterCache[key]
	if c ~= nil then return c end
	local res = false
	local reg = Region3.new(p - Vector3.new(r, 8, r), p + Vector3.new(r, 6, r)):ExpandToGrid(4)
	local ok, ch = pcall(function() return Terrain:ReadVoxelChannels(reg, 4, { "LiquidOccupancy" }) end)
	if ok then
		local L = ch.LiquidOccupancy
		for x = 1, #L do for y = 1, #L[x] do for z = 1, #L[x][y] do
			if L[x][y][z] > 0.05 then res = true end
		end end end
	end
	waterCache[key] = res
	return res
end
D.waterNear = waterNear
function D.clearWaterCache() waterCache = {} end
local function keptOut(area, p: Vector3): boolean
	for _, k in area.keepOut do
		local dx, dz = p.X - k[1], p.Z - k[2]
		if dx * dx + dz * dz < k[3] * k[3] then
			return true
		end
	end
	for _, k in D.Masks do
		local dx, dz = p.X - k[1], p.Z - k[2]
		if dx * dx + dz * dz < k[3] * k[3] then
			return true
		end
	end
	for _, s in D.MaskSegs do
		if distSeg2(p, Vector3.new(s[1], 0, s[2]), Vector3.new(s[3], 0, s[4])) < s[5] then
			return true
		end
	end
	if area.waterMask ~= false and waterNear(p, 10) then
		return true
	end
	return false
end
D.keptOut = keptOut

-- ------------------------------------------------------------------ backup and cleanup

function D.backup(area)
	local root = folder(ServerStorage, "WorldBackup_3Nov")
	if root:FindFirstChild(area.name) then
		return "backup exists"
	end
	local mn = Vector3int16.new(math.floor(area.min.X / 4), math.floor(area.min.Y / 4), math.floor(area.min.Z / 4))
	local mx = Vector3int16.new(math.floor(area.max.X / 4) - 1, math.floor(area.max.Y / 4) - 1, math.floor(area.max.Z / 4) - 1)
	local reg = Terrain:CopyRegion(Region3int16.new(mn, mx))
	reg.Name = area.name
	reg:SetAttribute("Corner", Vector3.new(mn.X * 4, mn.Y * 4, mn.Z * 4))
	reg:SetAttribute("Restore", "workspace.Terrain:PasteRegion(reg, Vector3int16.new(Corner.X/4, Corner.Y/4, Corner.Z/4), true)")
	reg.Parent = root
	return "backup " .. tostring(reg.SizeInCells)
end

local function inArea(area, p: Vector3): boolean
	return p.X >= area.min.X and p.X <= area.max.X and p.Z >= area.min.Z and p.Z <= area.max.Z
end

function D.removeOld(area)
	local dest = folder(folder(ServerStorage, "WorldRemoved_3Nov"), area.name)
	local n = 0
	for _, tile in workspace.Nature:GetChildren() do
		for _, m in tile:GetChildren() do
			local old = false
			for _, pat in OLD_ROCK_NAMES do
				if string.match(m.Name, pat) then
					old = true
				end
			end
			if old then
				local pos = if m:IsA("Model") then m:GetPivot().Position elseif m:IsA("BasePart") then m.Position else nil
				if pos and inArea(area, pos) and not keptOut(area, pos) then
					m:SetAttribute("FromPath", m.Parent:GetFullName())
					m.Parent = dest
					n += 1
				end
			end
		end
	end
	return n
end

-- ------------------------------------------------------------------ terrain scan

function D.scan(area, step: number)
	local params = terrainParams()
	local cells = {}
	local x = area.min.X + step / 2
	local count = 0
	while x < area.max.X do
		local z = area.min.Z + step / 2
		while z < area.max.Z do
			local r = workspace:Raycast(Vector3.new(x, area.max.Y + 200, z), Vector3.new(0, -(area.max.Y + 400), 0), params)
			if r then
				table.insert(cells, { p = r.Position, n = r.Normal, m = r.Material })
			end
			z += step
			count += 1
			if count % 2000 == 0 then
				task.wait()
			end
		end
		x += step
	end
	return cells
end

-- ------------------------------------------------------------------ placing

local function place(name: string, parent: Instance, cf: CFrame, scale: number, areaName: string, opts): MeshPart
	local k = kit(name)
	local c = k:Clone()
	local base = k:GetAttribute("BaseSize") or k.Size
	c.Size = base * scale * (if opts and opts.stretch then opts.stretch else Vector3.one)
	c.CFrame = cf
	c.Anchored = true
	c:SetAttribute("Dresser", areaName)
	-- v3: small per-piece tint jitter on rocks (kit Tint attribute = the calibrated sand tone)
	local sa = c:FindFirstChildOfClass("SurfaceAppearance")
	local tint = k:GetAttribute("Tint")
	if sa and typeof(tint) == "Color3" then
		local j = 0.93 + ((c.Position.X * 0.37 + c.Position.Z * 0.61) % 1) * 0.1
		sa.Color = Color3.new(math.min(tint.R * j, 1), math.min(tint.G * j, 1), math.min(tint.B * j * 0.98, 1))
	end
	if opts and opts.noCollide then
		c.CanCollide = false
		c.CanQuery = false
		c.CanTouch = false
	end
	if opts and opts.noShadow then
		c.CastShadow = false
	end
	c.Parent = parent
	return c
end

local function hasKit(name: string): boolean
	local lite = ServerStorage:FindFirstChild("RockKitLite")
	local rk = ServerStorage:FindFirstChild("RockKit")
	return (lite and lite:FindFirstChild(name) ~= nil) or (rk and rk:FindFirstChild(name) ~= nil) or false
end
local function pick(rng: Random, list: { string }): string
	return list[rng:NextInteger(1, #list)]
end

function D.placeRocks(area, cells, out: Folder, rng: Random)
	local placed = {}
	local function free(p: Vector3, r: number): boolean
		for _, q in placed do
			local d = (Vector3.new(q.p.X, q.p.Y * 0.6, q.p.Z) - Vector3.new(p.X, p.Y * 0.6, p.Z)).Magnitude
			if d < (q.r + r) * 0.5 then
				return false
			end
		end
		return true
	end
	local cand = {}
	for _, c in cells do
		if c.n.Y < (area.rocksMaxNy or 0.82) and c.m ~= Enum.Material.Water and riverDist(c.p) > 24 and not keptOut(area, c.p) then
			table.insert(cand, c)
		end
	end
	table.sort(cand, function(a, b)
		return a.n.Y < b.n.Y
	end)
	local n = 0
	for i, c in cand do
		local steep = c.n.Y < 0.6
		local name = if steep then pick(rng, ROCK_STEEP) else pick(rng, ROCK_MID)
		local k = kit(name)
		local base = k:GetAttribute("BaseSize") or k.Size
		local scale = if steep then rng:NextNumber(1.3, 2.0) else rng:NextNumber(0.9, 1.5)
		local size = base * scale
		local footprint = math.max(size.X, size.Z)
		if area.rocksCap and n >= area.rocksCap then break end
		if free(c.p, footprint) then
			local out2 = Vector3.new(c.n.X, 0, c.n.Z)
			if out2.Magnitude < 0.05 then
				out2 = Vector3.new(1, 0, 0)
			end
			out2 = out2.Unit
			local yaw = math.rad(rng:NextNumber(-14, 14))
			local look = CFrame.lookAt(Vector3.zero, out2) * CFrame.Angles(0, yaw, 0)
			local slope = math.deg(math.acos(math.clamp(c.n.Y, -1, 1)))
			local lean = if name == "RK_MountainFace" then 0 else math.rad(math.clamp((90 - slope) * 0.25, 0, 14))
			local rot = look * CFrame.Angles(-lean, 0, 0)
			local sink = size.Y * (if steep then 0.14 else 0.22)
			local pos = c.p + Vector3.new(0, size.Y / 2 - sink, 0) - out2 * (size.Z * 0.28)
			place(name, out, CFrame.new(pos) * rot, scale, area.name)
			table.insert(placed, { p = c.p, r = footprint, name = name, out = out2 })
			n += 1
			if n % 10 == 0 then
				task.wait()
			end
		end
	end
	return placed
end

-- Cover pass: walks the slope cells steepest first and drops a piece wherever the terrain is not yet
-- under a kit rock (ray from above), so steep faces end up built from stacked rocks instead of a sprinkle.
-- v2: every piece is stretched wider and squatter (stretch X 1.15..1.45, Y 0.7..0.9) and never pitched
-- forward, so the faces read as horizontal layers. Pass 2 fills edges and gaps with medium pieces.
-- v3: no column pieces (CliffWall, Outcrop_Tall, Spire) any more: the refs are big rounded boulders and
-- flat-topped blocks packed together. Boulders get scaled way up (scale is chosen from a target width).
-- v3b: the thin pieces (Ledge, Slab, Boulder_Flat, MountainFace's slab stack) turned into floating pancakes
-- once stretched, so cover uses only chunky masses; stretch is mild and pieces sink deeper.
-- v4: wide low shelves for plateaus and terraced flanks (RockKitExtra, only used when present in the kit)
local EXTRA_MID = { "RK_LedgeWide", "RK_ShelfStep" }
local COVER_STEEP = { "RK_CliffTop_A", "RK_CliffTop_B", "RK_Boulder_A", "RK_Boulder_B", "RK_Boulder_C", "RK_CliffTop_B", "RK_Boulder_A", "RK_Outcrop_B" }
local COVER_MID = { "RK_CliffTop_A", "RK_CliffTop_B", "RK_Boulder_A", "RK_Boulder_B", "RK_Boulder_C", "RK_Stack_B", "RK_Outcrop_B" }
local COVER_EDGE = { "RK_Stack_A", "RK_Stack_B", "RK_Outcrop_A", "RK_Outcrop_B", "RK_Boulder_C", "RK_Boulder_A", "RK_Boulder_B" }
D.Cover = { steepW = { 75, 115 }, midW = { 52, 80 }, edgeW = { 22, 40 }, stretchX = { 1.05, 1.3 }, stretchY = { 0.85, 1.05 }, sink = 0.36 }

function D.cover(area, cells, out: Folder, rng: Random)
	local rp = RaycastParams.new()
	rp.FilterType = Enum.RaycastFilterType.Include
	rp.FilterDescendantsInstances = { out }
	local function covered(p: Vector3): boolean
		local r = workspace:Raycast(p + Vector3.new(0, 300, 0), Vector3.new(0, -600, 0), rp)
		return r ~= nil and r.Position.Y > p.Y - 3
	end
	-- paths (Ground, Mud, Cobblestone, Pavement, Sand) stay walkable: no rock footprint may touch one
	local tp = terrainParams()
	local PATH = { [Enum.Material.Ground] = true, [Enum.Material.Mud] = true, [Enum.Material.Cobblestone] = true, [Enum.Material.Pavement] = true, [Enum.Material.Sand] = true }
	local function onPath(p: Vector3, half: number): boolean
		for _, o in { Vector3.zero, Vector3.new(half, 0, 0), Vector3.new(-half, 0, 0), Vector3.new(0, 0, half), Vector3.new(0, 0, -half) } do
			local r = workspace:Raycast(p + o + Vector3.new(0, 300, 0), Vector3.new(0, -600, 0), tp)
			if r and PATH[r.Material] then
				return true
			end
		end
		return false
	end
	local placedCover = 0
	local function pass(maxNy: number, pickFn, scaleFn, sinkK: number, pushK: number)
		local cand = {}
		for _, c in cells do
			local rocky = area.coverMaterials == nil or area.coverMaterials[c.m] or c.n.Y < 0.6
			if rocky and c.n.Y < maxNy and c.m ~= Enum.Material.Water and riverDist(c.p) > 22 and not keptOut(area, c.p) then
				table.insert(cand, c)
			end
		end
		table.sort(cand, function(a, b)
			return a.n.Y < b.n.Y
		end)
		local n = 0
		for _, c in cand do
			if area.coverCap and placedCover >= area.coverCap then break end
			if not covered(c.p) then
				local name = pickFn(c)
				local k = kit(name)
				local base0 = k:GetAttribute("BaseSize") or k.Size
				local scale = scaleFn(c) / math.max(base0.X, base0.Z) -- scaleFn gives a target width in studs
				local stretch = Vector3.new(rng:NextNumber(D.Cover.stretchX[1], D.Cover.stretchX[2]), rng:NextNumber(D.Cover.stretchY[1], D.Cover.stretchY[2]), 1)
				local size = base0 * scale * stretch
				local out2 = Vector3.new(c.n.X, 0, c.n.Z)
				out2 = if out2.Magnitude < 0.05 then Vector3.new(rng:NextNumber(-1, 1), 0, rng:NextNumber(-1, 1)).Unit else out2.Unit
				-- the footprint may not reach the river either (big boulders are wide)
				local reach = math.max(size.X, size.Z) * 0.5
				if riverDist(c.p - out2 * (size.Z * pushK)) - reach * 0.6 > 22 and not (c.n.Y > 0.6 and onPath(c.p, reach)) then
					local rot = CFrame.lookAt(Vector3.zero, out2) * CFrame.Angles(0, math.rad(rng:NextNumber(-15, 15)), 0)
					rot = rot * CFrame.Angles(math.rad(rng:NextNumber(-4, 0)), 0, math.rad(rng:NextNumber(-3, 3)))
					local pos = c.p + Vector3.new(0, size.Y / 2 - size.Y * sinkK, 0) - out2 * (size.Z * pushK)
					place(name, out, CFrame.new(pos) * rot, scale, area.name, { stretch = stretch })
					n += 1
					placedCover += 1
					if n % 8 == 0 then
						task.wait()
					end
				end
			end
		end
		return n
	end
	local W = D.Cover
	-- v4b: area.coverMaxNy / area.edgeMaxNy (defaults 0.8 / 0.86). Thinned style (cliff bands on steep ground
	-- only, not a boulder field): coverMaxNy 0.66, edgeMaxNy 0 (no edge pass).
	local n1 = pass(area.coverMaxNy or 0.8, function(c)
		if c.n.Y >= 0.6 and area.extras ~= false and rng:NextNumber() < 0.3 then
			local e = pick(rng, EXTRA_MID)
			if hasKit(e) then return e end
		end
		return if c.n.Y < 0.6 then pick(rng, COVER_STEEP) else pick(rng, COVER_MID)
	end, function(c)
		return if c.n.Y < 0.6 then rng:NextNumber(W.steepW[1], W.steepW[2]) else rng:NextNumber(W.midW[1], W.midW[2])
	end, W.sink, 0.32)
	local n2 = pass(area.edgeMaxNy or 0.86, function(c)
		return pick(rng, COVER_EDGE)
	end, function(c)
		return rng:NextNumber(W.edgeW[1], W.edgeW[2])
	end, W.sink, 0.2)
	return n1, n2
end

-- ------------------------------------------------------------------ terrain repaint: no more faceted rock texture

function D.repaint(area, cells, step: number)
	-- v4: reads and writes all three channels (the v1-v3 WriteVoxels call dropped the liquid in partly solid
	-- voxels and painted the river bed green). Columns with any water, near the river or in a mask are skipped.
	local grid = {}
	for _, c in cells do
		grid[math.floor(c.p.X / step) .. "," .. math.floor(c.p.Z / step)] = c.n.Y
	end
	local B = 64
	local changed = 0
	local x0 = math.floor(area.min.X / 4) * 4
	local z0 = math.floor(area.min.Z / 4) * 4
	local y0, y1 = math.floor(area.min.Y / 4) * 4, math.floor(area.max.Y / 4) * 4
	local CH = { "SolidMaterial", "SolidOccupancy", "LiquidOccupancy" }
	for bx = x0, area.max.X - 1, B do
		for bz = z0, area.max.Z - 1, B do
			local reg = Region3.new(Vector3.new(bx, y0, bz), Vector3.new(bx + B, y1, bz + B))
			local ch = Terrain:ReadVoxelChannels(reg, 4, CH)
			local SM, SO, LO = ch.SolidMaterial, ch.SolidOccupancy, ch.LiquidOccupancy
			local sx, sy, sz = #SM, #SM[1], #SM[1][1]
			local dirty = false
			for ix = 1, sx do
				for iz = 1, sz do
					local wx, wz = bx + (ix - 0.5) * 4, bz + (iz - 0.5) * 4
					local wet = false
					for iy = 1, sy do
						if LO[ix][iy][iz] > 0 then wet = true break end
					end
					local wp = Vector3.new(wx, 0, wz)
					if not wet and riverDist(wp) >= 34 and not keptOut({ keepOut = area.keepOut, waterMask = false }, wp) then
						local ny = grid[math.floor(wx / step) .. "," .. math.floor(wz / step)] or 1
						for iy = 1, sy do
							local m = SM[ix][iy][iz]
							if m == Enum.Material.Rock or m == Enum.Material.Basalt or m == Enum.Material.Slate then
								SM[ix][iy][iz] = if ny <= 0.72 then Enum.Material.LeafyGrass else Enum.Material.Grass
								dirty = true
								changed += 1
							end
						end
					end
				end
			end
			if dirty then
				Terrain:WriteVoxelChannels(reg, 4, { SolidMaterial = SM, SolidOccupancy = SO, LiquidOccupancy = LO })
			end
			task.wait()
		end
	end
	return changed
end

-- ------------------------------------------------------------------ foliage

local function rockOnly(part: BasePart)
	local p = RaycastParams.new()
	p.FilterType = Enum.RaycastFilterType.Include
	p.FilterDescendantsInstances = { part }
	return p
end

-- Ivy (v2): hangs over exposed top edges only. For each big rock: find the top surface just behind the
-- front face, skip it when another rock sits on top of that rim (ray up hits a rock) or the rim is buried
-- (terrain right in front is higher than the rim), then hang the curtain from the rim. Max 2 per rock and
-- area.ivyCap in total (default 160), biggest rocks first.
function D.placeIvy(area, rocks: Folder, out: Folder, rng: Random)
	local rp = RaycastParams.new()
	rp.FilterType = Enum.RaycastFilterType.Include
	rp.FilterDescendantsInstances = { rocks }
	local tp = terrainParams()
	local list = {}
	for _, r in rocks:GetChildren() do
		if r:IsA("MeshPart") and r.Size.Y > 9 then
			table.insert(list, r)
		end
	end
	table.sort(list, function(a, b)
		return a.Size.X * a.Size.Y > b.Size.X * b.Size.Y
	end)
	local cap = area.ivyCap or 160
	local n = 0
	for _, r in list do
		if n >= cap then
			break
		end
		local front = Vector3.new(r.CFrame.LookVector.X, 0, r.CFrame.LookVector.Z).Unit
		local right = r.CFrame.RightVector
		local tries = if r.Size.X > 50 then 4 else 2
		local here = 0
		for i = 1, tries do
			if here >= (area.ivyPerRock or 3) or n >= cap then
				break
			end
			local along = rng:NextNumber(-0.38, 0.38) * r.Size.X
			local probe = r.Position + right * along + front * (r.Size.Z * 0.18) + Vector3.new(0, r.Size.Y, 0)
			local top = workspace:Raycast(probe, Vector3.new(0, -r.Size.Y * 1.5, 0), rockOnly(r))
			if top and top.Normal.Y > 0.55 then
				local y = top.Position.Y
				local face = workspace:Raycast(top.Position + front * r.Size.Z + Vector3.new(0, -1.5, 0), -front * r.Size.Z * 1.3, rockOnly(r))
				local edge = if face then Vector3.new(face.Position.X, y, face.Position.Z) else top.Position
				local above = workspace:Raycast(edge + Vector3.new(0, 1, 0) - front * 1.5, Vector3.new(0, 40, 0), rp)
				local ground = workspace:Raycast(edge + front * 4 + Vector3.new(0, 200, 0), Vector3.new(0, -400, 0), tp)
				local buried = ground ~= nil and ground.Position.Y > y - 6
				if not above and not buried then
					local name = pick(rng, IVY)
					local k = kit(name)
					local s = rng:NextNumber(1.5, 2.3) * math.clamp(r.Size.Y / 28, 0.8, 1.7)
					local size = (k:GetAttribute("BaseSize") or k.Size) * s
					local cf = CFrame.lookAt(edge, edge + front) * CFrame.Angles(0, math.rad(rng:NextNumber(-10, 10)), 0)
					cf = cf * CFrame.new(0, -size.Y / 2 + 0.35 * s, -0.4 * s)
					place(name, out, cf, s, area.name, { noCollide = true })
					n += 1
					here += 1
				end
			end
		end
		if n % 10 == 0 then
			task.wait()
		end
	end
	return n
end

D.Ground = { flowerP = 0.17, flowerDrift = 0.1, flowerScale = { 1.4, 2.1 }, riverBushP = 0.06, scatterP = 0.03, footBush = { 0, 2 } }

function D.placeGround(area, cells, rocks, outs, rng: Random)
	-- bushes at the foot of the cliffs and along the river; flower patches in clumps; scatter rocks; birches
	local G0 = D.Ground
	local k = area.groundScale or 1
	local G = { flowerP = G0.flowerP * k, flowerDrift = G0.flowerDrift, flowerScale = G0.flowerScale, riverBushP = G0.riverBushP * k,
		scatterP = G0.scatterP * k, footBush = G0.footBush }
	local nb, nf, ns, nt = 0, 0, 0, 0
	local params = terrainParams()
	local function ground(x: number, z: number)
		local r = workspace:Raycast(Vector3.new(x, area.max.Y + 200, z), Vector3.new(0, -(area.max.Y + 400), 0), params)
		if r and r.Material ~= Enum.Material.Water and r.Normal.Y > 0.7 then
			return r
		end
		return nil
	end
	local function upright(p: Vector3, nrm: Vector3, tiltK: number)
		local up = Vector3.yAxis:Lerp(nrm, tiltK).Unit
		local fwd = Vector3.new(rng:NextNumber(-1, 1), 0, rng:NextNumber(-1, 1))
		if fwd.Magnitude < 0.1 then
			fwd = Vector3.xAxis
		end
		local right = fwd.Unit:Cross(up).Unit
		local back = right:Cross(up).Unit
		return CFrame.fromMatrix(p, right, up, back)
	end
	-- foot of each cliff
	for _, r in rocks:GetChildren() do
		if r:IsA("MeshPart") and r.Size.X > 25 then
			local front = Vector3.new(r.CFrame.LookVector.X, 0, r.CFrame.LookVector.Z).Unit
			for i = 1, rng:NextInteger(G.footBush[1], G.footBush[2]) do
				local p = r.Position + r.CFrame.RightVector * rng:NextNumber(-0.45, 0.45) * r.Size.X + front * (r.Size.Z * rng:NextNumber(0.45, 0.8))
				local g = ground(p.X, p.Z)
				if g and riverDist(g.Position) > 14 then
					local name = pick(rng, BUSHES)
					local s = rng:NextNumber(1.0, 1.8)
					local size = (kit(name):GetAttribute("BaseSize") or kit(name).Size) * s
					place(name, outs.Bushes, upright(g.Position + Vector3.new(0, size.Y / 2 - 0.4, 0), g.Normal, 0.3), s, area.name, { noCollide = true })
					nb += 1
				end
			end
		end
	end
	task.wait()
	-- meadow: flowers in drifts (noise), bushes along the river, scatter boulders
	local seedx = rng:NextNumber(0, 1000)
	local tick = 0
	for _, c in cells do
		if c.n.Y > 0.82 and c.m ~= Enum.Material.Water and not keptOut(area, c.p) then
			local rd = riverDist(c.p)
			local drift = math.noise(c.p.X / 70, c.p.Z / 70, seedx)
			if rd > 10 and drift > G.flowerDrift and rng:NextNumber() < G.flowerP then
				local x, z = c.p.X + rng:NextNumber(-4, 4), c.p.Z + rng:NextNumber(-4, 4)
				local g = ground(x, z)
				if g then
					local name = if drift > 0.3 then "FL_Lavender" else pick(rng, FLOWERS)
					local s = rng:NextNumber(G.flowerScale[1], G.flowerScale[2])
					local size = (kit(name):GetAttribute("BaseSize") or kit(name).Size) * s
					place(name, outs.Flowers, upright(g.Position + Vector3.new(0, size.Y / 2 - 0.25, 0), g.Normal, 0.5), s, area.name, { noCollide = true, noShadow = true })
					nf += 1
				end
			end
			if rd > 12 and rd < 40 and rng:NextNumber() < G.riverBushP then
				local g = ground(c.p.X, c.p.Z)
				if g then
					local name = pick(rng, BUSHES)
					local s = rng:NextNumber(0.9, 1.6)
					local size = (kit(name):GetAttribute("BaseSize") or kit(name).Size) * s
					place(name, outs.Bushes, upright(g.Position + Vector3.new(0, size.Y / 2 - 0.4, 0), g.Normal, 0.3), s, area.name, { noCollide = true })
					nb += 1
				end
			end
			if rd > 16 and rng:NextNumber() < G.scatterP then
				local g = ground(c.p.X, c.p.Z)
				if g then
					local name = pick(rng, SCATTER)
					local s = rng:NextNumber(0.6, 1.3)
					local size = (kit(name):GetAttribute("BaseSize") or kit(name).Size) * s
					local small = name == "RK_Pebbles" or name == "RK_Rubble"
					place(name, outs.Scatter, upright(g.Position + Vector3.new(0, size.Y / 2 - size.Y * 0.2, 0), g.Normal, 0.6), s, area.name, { noCollide = small })
					ns += 1
				end
			end
		end
		tick += 1
		if tick % 300 == 0 then
			task.wait()
		end
	end
	-- birches in small groups at the edge of the valley floor, from the existing tree models
	local birch = {}
	for _, t in workspace.Nature:GetDescendants() do
		if t:IsA("Model") and (t.Name == "Birch_Slender" or t.Name == "Birch_Twin" or t.Name == "Birch_Lean") and #birch < 6 then
			table.insert(birch, t)
		end
	end
	if #birch > 0 then
		for i = 1, (area.birchGroups or 7) do
			local c = cells[rng:NextInteger(1, #cells)]
			local tries = 0
			while (c.n.Y < 0.9 or riverDist(c.p) < 30 or keptOut(area, c.p)) and tries < 60 do
				c = cells[rng:NextInteger(1, #cells)]
				tries += 1
			end
			if tries < 60 then
				for j = 1, rng:NextInteger(2, 3) do
					local g = ground(c.p.X + rng:NextNumber(-12, 12), c.p.Z + rng:NextNumber(-12, 12))
					if g and riverDist(g.Position) > 20 then
						local t = birch[rng:NextInteger(1, #birch)]:Clone()
						local cf, size = t:GetBoundingBox()
						local pivotToBottom = t:GetPivot().Position.Y - (cf.Position.Y - size.Y / 2)
						t:PivotTo(CFrame.new(g.Position + Vector3.new(0, pivotToBottom - 0.6, 0)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0))
						t:SetAttribute("Dresser", area.name)
						t.Parent = outs.Trees
						nt += 1
					end
				end
			end
		end
	end
	return nb, nf, ns, nt
end

-- ------------------------------------------------------------------ run / undo

function D.run(area, steps)
	steps = steps or { backup = true, remove = true, cover = true, repaint = true, ivy = true, ground = true }
	local log = {}
	local rng = Random.new(area.seed + (steps.seedOffset or 0))
	local art = folder(workspace, "WorldArt")
	local root = art:FindFirstChild(area.name)
	if not root then
		root = Instance.new("Model")
		root.Name = area.name
		root.ModelStreamingMode = Enum.ModelStreamingMode.Default
		root.Parent = art
	end
	local outs = {}
	for _, n in { "Rocks", "Ivy", "Bushes", "Flowers", "Scatter", "Trees" } do
		outs[n] = folder(root, n)
	end
	if steps.backup then
		table.insert(log, D.backup(area))
	end
	if steps.remove then
		table.insert(log, "old rock props moved: " .. D.removeOld(area))
	end
	local cells = D.scan(area, 8)
	table.insert(log, "cells " .. #cells)
	if steps.rocks then
		local placed = D.placeRocks(area, cells, outs.Rocks, rng)
		table.insert(log, "rocks " .. #placed)
	end
	if steps.cover then
		local n1, n2 = D.cover(area, cells, outs.Rocks, rng)
		table.insert(log, string.format("cover big %d edge %d", n1, n2))
	end
	if steps.repaint then
		table.insert(log, "voxels repainted " .. D.repaint(area, cells, 8))
	end
	if steps.ivy then
		table.insert(log, "ivy " .. D.placeIvy(area, outs.Rocks, outs.Ivy, rng))
	end
	if steps.ground then
		local nb, nf, ns, nt = D.placeGround(area, cells, outs.Rocks, outs, rng)
		table.insert(log, string.format("bushes %d flowers %d scatter %d trees %d", nb, nf, ns, nt))
	end
	return table.concat(log, "\n")
end

-- v4: terrain is only restored when restoreTerrain is true. The old default (restore) pasted the whole
-- box back and could undo later terrain work in it (it is how the Brindle River bed got lost once).
function D.undo(areaName: string, restoreTerrain: boolean?)
	local keepTerrain = not restoreTerrain
	local art = workspace:FindFirstChild("WorldArt")
	local root = art and art:FindFirstChild(areaName)
	if root then
		root:Destroy()
	end
	local rem = ServerStorage:FindFirstChild("WorldRemoved_3Nov")
	local f = rem and rem:FindFirstChild(areaName)
	local n = 0
	if f then
		for _, m in f:GetChildren() do
			local path = m:GetAttribute("FromPath")
			local parent = workspace.Nature:FindFirstChild(string.match(path or "", "Nature%.(.+)$") or "")
			if parent then
				m.Parent = parent
				n += 1
			end
		end
	end
	if not keepTerrain then
		local bk = ServerStorage:FindFirstChild("WorldBackup_3Nov")
		local reg = bk and bk:FindFirstChild(areaName)
		if reg then
			local c = reg:GetAttribute("Corner")
			Terrain:PasteRegion(reg, Vector3int16.new(c.X / 4, c.Y / 4, c.Z / 4), true)
		end
	end
	return "undone, props back: " .. n
end


-- ------------------------------------------------------------------ v4: masks, areas, rollout

-- Collects everything rocks and repaint must stay away from, island wide, into D.Masks ({x, z, r}).
-- Sources (each in a pcall, a missing one is reported, not fatal):
--   Quests.Spots (quest places, incl. the Lighthouse Headland, camps, mission spots), r + 25
--   WorldMap.Places / Waystones / Caves: any entry with numeric x and z (or a Vector3/Vector2 position)
--   Missions: every table anywhere in the data with numeric x and z (sneak routes, defend sites), r or 40
--   NpcSpawns: same walker (bandit camps, poachers), r 45
--   workspace.Towns: each child's bounding box as a circle (towns, sets, camps, the lighthouse), + 25
--   SpawnLocations, waystone models in workspace (name contains "Waystone"), r 30
-- Roads and paths are checked per cell by terrain material in D.cover (onPath) and the water mask by voxels.
local function walk(t, out, defR, seen, depth)
	if type(t) ~= "table" or seen[t] or depth > 8 then return end
	seen[t] = true
	local x, z = t.x or t.X, t.z or t.Z
	local pos = t.position or t.pos or t.Position or t.at
	if typeof(pos) == "Vector3" then x, z = pos.X, pos.Z end
	if typeof(pos) == "Vector2" then x, z = pos.X, pos.Y end
	if type(x) == "number" and type(z) == "number" then
		local r = t.r or t.radius or t.R or defR
		if type(r) ~= "number" then r = defR end
		table.insert(out, { x, z, math.min(r, 400), tostring(t.name or t.label or t.id or "") })
	end
	for _, v in t do
		if type(v) == "table" then walk(v, out, defR, seen, depth + 1)
		elseif typeof(v) == "Vector3" and depth > 0 then -- bare position lists
			table.insert(out, { v.X, v.Z, defR, "" })
		end
	end
end

function D.buildMasks(opts)
	opts = opts or {}
	local masks, log = {}, {}
	local RS = game:GetService("ReplicatedStorage")
	local data = RS:FindFirstChild("Shared") and RS.Shared:FindFirstChild("data")
	local function src(name, fn)
		local before = #masks
		local ok, err = pcall(fn)
		table.insert(log, string.format("%s: %s", name, if ok then tostring(#masks - before) else ("FAILED " .. tostring(err))))
	end
	src("Quests.Spots", function()
		local Q = require(data.Quests)
		for name, sp in Q.Spots do
			-- sea and region sized spots (Strait of Lanterns r 1000, the Maelstrom, The Eye) are not places to keep
			-- clear; underground ones (y below 0) do not touch the surface
			if (sp.r or 20) <= 150 and not (sp.y and sp.y < -20) then
				table.insert(masks, { sp.x, sp.z, (sp.r or 20) + 25, name })
			end
		end
	end)
	src("WorldMap", function()
		local W = require(data.WorldMap)
		local tmp = {}
		for _, key in { "Places", "Waystones", "Caves" } do
			if W[key] then walk(W[key], tmp, if key == "Places" then 60 else 35, {}, 0) end
		end
		for _, m in tmp do
			-- big Places (regions) would mask whole biomes: keep only small ones
			if m[3] <= 120 then table.insert(masks, m) end
		end
	end)
	src("Missions", function()
		local tmp = {}
		walk(require(data.Missions), tmp, 40, {}, 0)
		for _, m in tmp do table.insert(masks, { m[1], m[2], math.max(m[3], 30) + 15, m[4] }) end
	end)
	src("NpcSpawns", function()
		local tmp = {}
		walk(require(data.NpcSpawns), tmp, 45, {}, 0)
		for _, m in tmp do table.insert(masks, { m[1], m[2], math.max(m[3], 35), m[4] }) end
	end)
	src("Towns", function()
		local towns = workspace:FindFirstChild("Towns")
		for _, c in (towns and towns:GetChildren() or {}) do
			local ok2, cf, size = pcall(function() if c:IsA("Model") then return c:GetBoundingBox() elseif c:IsA("BasePart") then return c.CFrame, c.Size end return nil end)
			if not (ok2 and cf) and c:IsA("Folder") then
				-- folder of parts/models: bounds of the children
				local mn, mx = Vector3.one * math.huge, -Vector3.one * math.huge
				for _, d in c:GetDescendants() do
					if d:IsA("BasePart") then mn = mn:Min(d.Position) mx = mx:Max(d.Position) end
				end
				if mn.X < math.huge then cf, size = CFrame.new((mn + mx) / 2), mx - mn ok2 = true end
			end
			if ok2 and cf and size then
				local r = math.max(size.X, size.Z) / 2 + 25
				if r <= 220 then
					table.insert(masks, { cf.Position.X, cf.Position.Z, r, "Towns." .. c.Name })
				else
					-- spread-out sets (sea arches, walls along a coast): one circle per child part/model, not one
					-- huge circle that would mask a whole biome
					for _, ch in c:GetChildren() do
						local okc, ccf, cs = pcall(function() if ch:IsA("Model") then return ch:GetBoundingBox() elseif ch:IsA("BasePart") then return ch.CFrame, ch.Size end return nil end)
						if okc and ccf and cs then
							table.insert(masks, { ccf.Position.X, ccf.Position.Z, math.min(math.max(cs.X, cs.Z) / 2 + 20, 220), "Towns." .. c.Name .. "." .. ch.Name })
						end
					end
				end
			end
		end
	end)
	src("Spawns+Waystones", function()
		for _, d in workspace:GetDescendants() do
			if d:IsA("SpawnLocation") then
				table.insert(masks, { d.Position.X, d.Position.Z, 30, d.Name })
			elseif d:IsA("Model") and string.find(d.Name, "Waystone") then
				local p = d:GetPivot().Position
				table.insert(masks, { p.X, p.Z, 30, d.Name })
			end
		end
	end)
	D.Masks = masks
	return masks, table.concat(log, "\n")
end

-- area registry: D.addArea("Highwatch", Vector3 min, Vector3 max, { seed, ivyCap, coverCap, groundScale, birchGroups, keepOut })
function D.addArea(name: string, mn: Vector3, mx: Vector3, opts)
	opts = opts or {}
	local a = {
		name = name, min = mn, max = mx,
		keepOut = opts.keepOut or {},
		seed = opts.seed or (31120 + #name * 977 + math.floor(mn.X + mn.Z)),
		ivyCap = opts.ivyCap or 120,
		coverCap = opts.coverCap,
		groundScale = opts.groundScale or 0.7,
		birchGroups = opts.birchGroups or 0,
		coverMaterials = opts.coverMaterials or { [Enum.Material.Rock] = true, [Enum.Material.Slate] = true, [Enum.Material.Basalt] = true, [Enum.Material.Limestone] = true },
		waterMask = true,
		coverMaxNy = opts.coverMaxNy, edgeMaxNy = opts.edgeMaxNy,
	}
	D.Areas[name] = a
	return a
end

-- one area end to end: terrain backup, old rock props out, cover rocks, repaint (liquid safe), ivy, ground,
-- then the WorldOptimizer passes (cull, ground, thin, settings). Returns a log and the stats line.
-- Needs D.buildMasks() first (it refuses to run with an empty mask list unless opts.noMasks).
function D.rollout(area, opts)
	opts = opts or {}
	assert(#D.Masks > 0 or opts.noMasks, "run D.buildMasks() first")
	D.UseLite = opts.lite == true and ServerStorage:FindFirstChild("RockKitLite") ~= nil
	local t0 = os.clock()
	local log = { D.run(area, { backup = true, remove = true, cover = true, repaint = opts.repaint ~= false, ivy = true, ground = true }) }
	local OptM = ServerStorage:FindFirstChild("DevTools") and ServerStorage.DevTools:FindFirstChild("WorldOptimizer")
	if OptM then
		local O = loadstring(OptM.Source)()
		local root = workspace.WorldArt[area.name]
		table.insert(log, O.cull(root))
		table.insert(log, O.ground(root))
		table.insert(log, O.thinFoliage(root))
		table.insert(log, O.settings(root))
		table.insert(log, O.stats(root))
	end
	table.insert(log, string.format("time %.0f s", os.clock() - t0))
	return table.concat(log, "\n")
end

return D
