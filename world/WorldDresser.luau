--!nonstrict
-- WorldDresser (3 Nov, world pass): dresses a terrain area with the self-made RockKit and FoliageKit in the
-- style of Philip's reference shots. Dev tool, Edit mode only (run through execute_luau or the command bar):
--   local D = require(game.ServerStorage.DevTools.WorldDresser)
--   D.run(D.Areas.Watchstone)        -- backup, remove old cliff props, rocks, terrain repaint, foliage
--   D.undo("Watchstone")             -- removes everything it placed and puts the old props + terrain back
-- Kits: ServerStorage.RockKit (RK_*) and ServerStorage.FoliageKit (FL_*), MeshParts with SurfaceAppearance and
-- an attribute BaseSize (the size in studs the piece was modelled at).
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
		-- keep clear: river polyline (x, z) and radius; story spots (x, z, r)
		keepOut = { { -8100, -1100, 70 } }, -- the stone circle on the top
		seed = 3112026,
	},
}

local ROCK_STEEP = { "RK_CliffWall_A", "RK_CliffWall_B", "RK_CliffWall_C", "RK_CliffWall_A", "RK_CliffWall_B", "RK_CliffCorner", "RK_Outcrop_Tall" }
local ROCK_MID = { "RK_MountainFace", "RK_CliffTop_A", "RK_CliffTop_B", "RK_Stack_A", "RK_Stack_B", "RK_Ledge_A", "RK_Ledge_B", "RK_Outcrop_A", "RK_Outcrop_B", "RK_MountainFace" }
local SCATTER = { "RK_Boulder_A", "RK_Boulder_B", "RK_Boulder_C", "RK_Boulder_Flat", "RK_Pebbles", "RK_Rubble", "RK_Slab_Tilted", "RK_Pebbles" }
local FLOWERS = { "FL_Lavender", "FL_Lavender", "FL_Lavender", "FL_PinkFlowers", "FL_PinkFlowers", "FL_WhiteFlowers", "FL_BlueFlowers" }
local BUSHES = { "FL_Bush_A", "FL_Bush_B", "FL_Bush_Low" }
local IVY = { "FL_Ivy_A", "FL_Ivy_B" }
local OLD_ROCK_NAMES = { "^Cliff_", "^Boulder" }

local function kit(name: string): MeshPart
	local k = ServerStorage:FindFirstChild("RockKit"):FindFirstChild(name) or ServerStorage:FindFirstChild("FoliageKit"):FindFirstChild(name)
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

local function keptOut(area, p: Vector3): boolean
	for _, k in area.keepOut do
		local dx, dz = p.X - k[1], p.Z - k[2]
		if dx * dx + dz * dz < k[3] * k[3] then
			return true
		end
	end
	return false
end

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
	-- steepest first so the cliffs get the best spots
	local cand = {}
	for _, c in cells do
		if c.n.Y < 0.82 and c.m ~= Enum.Material.Water and riverDist(c.p) > 24 and not keptOut(area, c.p) then
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
		if free(c.p, footprint) then
			local out2 = Vector3.new(c.n.X, 0, c.n.Z)
			if out2.Magnitude < 0.05 then
				out2 = Vector3.new(1, 0, 0)
			end
			out2 = out2.Unit
			local yaw = math.rad(rng:NextNumber(-14, 14))
			local look = CFrame.lookAt(Vector3.zero, out2) * CFrame.Angles(0, yaw, 0)
			-- lean back into the hill a little (more on gentler slopes)
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

-- Cover pass (v2): walks the slope cells steepest first and drops a piece wherever the terrain is not yet
-- under a kit rock (ray from above), so steep faces end up built from stacked rocks instead of a sprinkle.
-- v2: wide flat-topped pieces (CliffTop, MountainFace, Ledge) dominate, every piece is stretched wider and
-- squatter (stretch X 1.15..1.45, Y 0.7..0.9) and never pitched forward, so the faces read as horizontal
-- layers like the refs instead of spiky columns. Pass 2 fills edges and gaps with medium pieces.
-- v3: no column pieces (CliffWall, Outcrop_Tall, Spire) any more: the refs are big rounded boulders and
-- flat-topped blocks packed together. Boulders get scaled way up (scale is chosen from a target width).
local COVER_STEEP = { "RK_CliffTop_A", "RK_CliffTop_B", "RK_Boulder_A", "RK_Boulder_B", "RK_MountainFace", "RK_CliffTop_B", "RK_Boulder_C", "RK_Outcrop_B" }
local COVER_MID = { "RK_MountainFace", "RK_CliffTop_A", "RK_CliffTop_B", "RK_Boulder_A", "RK_Boulder_B", "RK_Stack_B", "RK_Outcrop_B" }
local COVER_EDGE = { "RK_Ledge_A", "RK_Ledge_B", "RK_Stack_A", "RK_Stack_B", "RK_Boulder_Flat", "RK_Outcrop_B", "RK_Boulder_C", "RK_Boulder_A", "RK_Slab_Tilted" }

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
	local function pass(maxNy: number, pickFn, scaleFn, sinkK: number, pushK: number)
		local cand = {}
		for _, c in cells do
			if c.n.Y < maxNy and c.m ~= Enum.Material.Water and riverDist(c.p) > 22 and not keptOut(area, c.p) then
				table.insert(cand, c)
			end
		end
		table.sort(cand, function(a, b)
			return a.n.Y < b.n.Y
		end)
		local n = 0
		for _, c in cand do
			if not covered(c.p) then
				local name = pickFn(c)
				local k = kit(name)
				local base0 = k:GetAttribute("BaseSize") or k.Size
				local scale = scaleFn(c) / math.max(base0.X, base0.Z) -- scaleFn gives a target width in studs
				local stretch = Vector3.new(rng:NextNumber(1.15, 1.45), rng:NextNumber(0.7, 0.9), 1)
				local size = (k:GetAttribute("BaseSize") or k.Size) * scale * stretch
				local out2 = Vector3.new(c.n.X, 0, c.n.Z)
				out2 = if out2.Magnitude < 0.05 then Vector3.new(rng:NextNumber(-1, 1), 0, rng:NextNumber(-1, 1)).Unit else out2.Unit
				if not (c.n.Y > 0.6 and onPath(c.p, math.max(size.X, size.Z) * 0.5)) then
					local rot = CFrame.lookAt(Vector3.zero, out2) * CFrame.Angles(0, math.rad(rng:NextNumber(-15, 15)), 0)
					rot = rot * CFrame.Angles(math.rad(rng:NextNumber(-4, 0)), 0, math.rad(rng:NextNumber(-3, 3)))
					local pos = c.p + Vector3.new(0, size.Y / 2 - size.Y * sinkK, 0) - out2 * (size.Z * pushK)
					place(name, out, CFrame.new(pos) * rot, scale, area.name, { stretch = stretch })
					n += 1
					if n % 8 == 0 then
						task.wait()
					end
				end
			end
		end
		return n
	end
	local n1 = pass(0.8, function(c)
		return if c.n.Y < 0.6 then pick(rng, COVER_STEEP) else pick(rng, COVER_MID)
	end, function(c)
		return if c.n.Y < 0.6 then rng:NextNumber(55, 85) else rng:NextNumber(38, 60)
	end, 0.3, 0.32)
	local n2 = pass(0.86, function(c)
		return pick(rng, COVER_EDGE)
	end, function(c)
		return rng:NextNumber(18, 34)
	end, 0.3, 0.2)
	return n1, n2
end

-- ------------------------------------------------------------------ terrain repaint: no more faceted rock texture

function D.repaint(area, cells, step: number)
	-- normal per (x, z) grid cell from the scan
	local grid = {}
	for _, c in cells do
		grid[math.floor(c.p.X / step) .. "," .. math.floor(c.p.Z / step)] = c.n.Y
	end
	local B = 64
	local changed = 0
	local x0 = math.floor(area.min.X / 4) * 4
	local z0 = math.floor(area.min.Z / 4) * 4
	local y0, y1 = math.floor(area.min.Y / 4) * 4, math.floor(area.max.Y / 4) * 4
	for bx = x0, area.max.X - 1, B do
		for bz = z0, area.max.Z - 1, B do
			local reg = Region3.new(Vector3.new(bx, y0, bz), Vector3.new(bx + B, y1, bz + B))
			local mats, occ = Terrain:ReadVoxels(reg, 4)
			local sx, sy, sz = mats.Size.X, mats.Size.Y, mats.Size.Z
			local dirty = false
			for ix = 1, sx do
				for iz = 1, sz do
					local wx, wz = bx + (ix - 0.5) * 4, bz + (iz - 0.5) * 4
					local ny = grid[math.floor(wx / step) .. "," .. math.floor(wz / step)] or 1
					local riverNear = riverDist(Vector3.new(wx, 0, wz)) < 18
					for iy = 1, sy do
						local m = mats[ix][iy][iz]
						if m == Enum.Material.Rock or m == Enum.Material.Basalt or m == Enum.Material.Slate then
							local new
							-- (MB_Ground reads as flagstones in this place, so slopes go green: grass between the rocks)
							if riverNear or ny <= 0.72 then
								new = Enum.Material.LeafyGrass
							else
								new = Enum.Material.Grass
							end
							mats[ix][iy][iz] = new
							dirty = true
							changed += 1
						end
					end
				end
			end
			if dirty then
				Terrain:WriteVoxels(reg, 4, mats, occ)
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
		local tries = if r.Size.X > 50 then 3 else 2
		local here = 0
		for i = 1, tries do
			if here >= 2 or n >= cap then
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
					local s = rng:NextNumber(1.0, 1.6) * math.clamp(r.Size.Y / 28, 0.8, 1.7)
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

function D.placeGround(area, cells, rocks, outs, rng: Random)
	-- bushes at the foot of the cliffs and along the river; flower patches in clumps; scatter rocks; birches
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
			for i = 1, rng:NextInteger(1, 3) do
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
			if rd > 10 and drift > 0.12 and rng:NextNumber() < 0.25 then
				local x, z = c.p.X + rng:NextNumber(-4, 4), c.p.Z + rng:NextNumber(-4, 4)
				local g = ground(x, z)
				if g then
					local name = if drift > 0.3 then "FL_Lavender" else pick(rng, FLOWERS)
					local s = rng:NextNumber(1.0, 1.6)
					local size = (kit(name):GetAttribute("BaseSize") or kit(name).Size) * s
					place(name, outs.Flowers, upright(g.Position + Vector3.new(0, size.Y / 2 - 0.25, 0), g.Normal, 0.5), s, area.name, { noCollide = true, noShadow = true })
					nf += 1
				end
			end
			if rd > 12 and rd < 40 and rng:NextNumber() < 0.09 then
				local g = ground(c.p.X, c.p.Z)
				if g then
					local name = pick(rng, BUSHES)
					local s = rng:NextNumber(0.9, 1.6)
					local size = (kit(name):GetAttribute("BaseSize") or kit(name).Size) * s
					place(name, outs.Bushes, upright(g.Position + Vector3.new(0, size.Y / 2 - 0.4, 0), g.Normal, 0.3), s, area.name, { noCollide = true })
					nb += 1
				end
			end
			if rd > 16 and rng:NextNumber() < 0.035 then
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
		for i = 1, 7 do
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
	local root = folder(art, area.name)
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

function D.undo(areaName: string, keepTerrain: boolean?)
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

return D
