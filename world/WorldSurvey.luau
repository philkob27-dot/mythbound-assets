--!nonstrict
-- WorldSurvey (3 Nov, world pass): finds the mountain and rocky areas for the rock kit rollout and gives each a
-- budget. Dev tool, Edit mode. It runs in the background (the scan takes longer than one execute call):
--   local S = loadstring(game.ServerStorage.DevTools.WorldSurvey.Source)()
--   S.start()                  -- spawns the scan, results land in _G.WorldSurvey
--   S.status()                 -- "scanning 41%" or "done"
--   S.report()                 -- the area table as text (also _G.WorldSurvey.areas)
-- Method: raycast the terrain every 32 studs over WorldMap.Bounds (fallback X -11200..21600, Z -6900..5100).
-- A cell is "rocky" when its surface is steep (normal Y < 0.8) above the sea (y > 6), not water, or it is
-- Rock/Slate/Basalt/Limestone at any slope above y 40. Old generator rock props (workspace.Nature Cliff_*,
-- Boulder*) count as rocky too. Rocky cells are summed per 128-stud tile; tiles with >= 4 rocky cells are
-- flood filled (8 neighbours) into areas. Each area gets: box, cell counts, height range, material mix,
-- flags (volcanic = Basalt/CrackedLava share, coast = sand/water share, town = overlaps workspace.Towns),
-- the nearest WorldMap place name, and a budget calibrated on Watchstone (the approved sample).

local S = {}
local Terrain = workspace.Terrain
local M = Enum.Material

local ROCKMAT = { [M.Rock] = true, [M.Slate] = true, [M.Basalt] = true, [M.Limestone] = true }
local VOLC = { [M.Basalt] = true, [M.CrackedLava] = true }
local SANDY = { [M.Sand] = true, [M.Sandstone] = true }

-- Watchstone, after optimisation, with the lite kit: 937 parts, ~354k tris, on its rocky tiles (filled in by
-- the scan: S.cal.cells). Budget per rocky 32-stud cell = these totals / Watchstone's rocky cells.
S.WATCH = { name = "Watchstone", min = Vector3.new(-8320, 0, -1280), max = Vector3.new(-7680, 440, -520), parts = 937, tris = 354000, rocks = 409 }
S.CAP_TRIS = 260000 -- per area (one area is about what the client draws at once)
S.CAP_TOTAL = 2600000 -- island total placed (streaming keeps the drawn set far lower)

local function bounds()
	local mn, mx = Vector2.new(-11200, -6900), Vector2.new(21600, 5100)
	pcall(function()
		local W = require(game.ReplicatedStorage.Shared.data.WorldMap)
		local b = W.Bounds
		if b and b.minX and b.maxX and b.minZ and b.maxZ then
			mn, mx = Vector2.new(b.minX, b.minZ), Vector2.new(b.maxX, b.maxZ)
		end
	end)
	return mn, mx
end

local function places()
	local out = {}
	pcall(function()
		local W = require(game.ReplicatedStorage.Shared.data.WorldMap)
		for k, p in (W.Places or {}) do
			local name = p.name or (type(k) == "string" and k) or "?"
			local x, z = p.x or p.X, p.z or p.Z
			local pos = p.position or p.pos
			if typeof(pos) == "Vector3" then x, z = pos.X, pos.Z end
			if type(x) == "number" and type(z) == "number" then table.insert(out, { name = name, x = x, z = z }) end
		end
	end)
	return out
end

local function townBoxes()
	local out = {}
	local towns = workspace:FindFirstChild("Towns")
	for _, c in (towns and towns:GetChildren() or {}) do
		local ok, cf, size = pcall(function() if c:IsA("Model") then return c:GetBoundingBox() end return nil end)
		if ok and cf and size and math.max(size.X, size.Z) < 1800 then
			table.insert(out, { c = Vector2.new(cf.Position.X, cf.Position.Z), r = math.max(size.X, size.Z) / 2, name = c.Name })
		end
	end
	return out
end

function S.start(step: number?)
	step = step or 32
	local st = { progress = 0, done = false, tiles = {}, step = step }
	_G.WorldSurvey = st
	task.spawn(function()
		local mn, mx = bounds()
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { Terrain }
		params.IgnoreWater = false
		local T = 128
		local tiles = st.tiles
		local function tile(x, z)
			local k = math.floor(x / T) .. "," .. math.floor(z / T)
			local t = tiles[k]
			if not t then
				t = { tx = math.floor(x / T), tz = math.floor(z / T), cells = 0, rocky = 0, steep = 0, water = 0, volc = 0, sand = 0, ymin = math.huge, ymax = -math.huge, props = 0 }
				tiles[k] = t
			end
			return t
		end
		local rows = math.ceil((mx.X - mn.X) / step)
		local i = 0
		for x = mn.X + step / 2, mx.X, step do
			for z = mn.Y + step / 2, mx.Y, step do
				local r = workspace:Raycast(Vector3.new(x, 1400, z), Vector3.new(0, -1700, 0), params)
				if r then
					local t = tile(x, z)
					t.cells += 1
					local y, ny, m = r.Position.Y, r.Normal.Y, r.Material
					if m == M.Water then
						t.water += 1
					else
						t.ymin = math.min(t.ymin, y); t.ymax = math.max(t.ymax, y)
						if VOLC[m] then t.volc += 1 end
						if SANDY[m] then t.sand += 1 end
						if ny < 0.6 then t.steep += 1 end
						if y > 6 and (ny < 0.8 or (ROCKMAT[m] and y > 40)) then t.rocky += 1 end
					end
				end
			end
			i += 1
			st.progress = i / rows
			task.wait()
		end
		-- old generator rocks
		local nature = workspace:FindFirstChild("Nature")
		for _, d in (nature and nature:GetDescendants() or {}) do
			if (d:IsA("Model") or d:IsA("BasePart")) and (string.match(d.Name, "^Cliff_") or string.match(d.Name, "^Boulder")) then
				local p = if d:IsA("Model") then d:GetPivot().Position else d.Position
				tile(p.X, p.Z).props += 1
			end
		end
		S.cluster(st)
		st.done = true
	end)
	return "survey started"
end

function S.status()
	local st = _G.WorldSurvey
	if not st then return "not started" end
	if st.done then return "done, areas " .. #st.areas end
	return string.format("scanning %d%%", st.progress * 100)
end

function S.cluster(st)
	local tiles = st.tiles
	local hot = {}
	for k, t in tiles do
		if t.rocky + t.props * 2 >= 4 then hot[k] = t end
	end
	local seen, areas = {}, {}
	for k, t in hot do
		if not seen[k] then
			local q, members = { t }, {}
			seen[k] = true
			while #q > 0 do
				local c = table.remove(q)
				table.insert(members, c)
				for dx = -1, 1 do
					for dz = -1, 1 do
						local nk = (c.tx + dx) .. "," .. (c.tz + dz)
						if hot[nk] and not seen[nk] then
							seen[nk] = true
							table.insert(q, hot[nk])
						end
					end
				end
			end
			if #members >= 3 then
				local a = { tiles = #members, rocky = 0, steep = 0, cells = 0, water = 0, volc = 0, sand = 0, props = 0, ymin = math.huge, ymax = -math.huge,
					min = Vector2.new(math.huge, math.huge), max = Vector2.new(-math.huge, -math.huge) }
				for _, m in members do
					for _, f in { "rocky", "steep", "cells", "water", "volc", "sand", "props" } do a[f] += m[f] end
					a.ymin = math.min(a.ymin, m.ymin); a.ymax = math.max(a.ymax, m.ymax)
					a.min = a.min:Min(Vector2.new(m.tx * 128, m.tz * 128))
					a.max = a.max:Max(Vector2.new(m.tx * 128 + 128, m.tz * 128 + 128))
				end
				table.insert(areas, a)
			end
		end
	end
	-- names, flags, calibration, budgets
	local pl = places()
	local towns = townBoxes()
	local W = S.WATCH
	local calCells = 0
	for _, a in areas do
		local c = (a.min + a.max) / 2
		local best, bd = "?", math.huge
		for _, p in pl do
			local d = (Vector2.new(p.x, p.z) - c).Magnitude
			if d < bd then best, bd = p.name, d end
		end
		a.name = best
		a.volcanic = a.volc / math.max(a.cells - a.water, 1) > 0.25
		a.coast = (a.sand + a.water) / math.max(a.cells, 1) > 0.35
		a.town = {}
		for _, t in towns do
			local cl = Vector2.new(math.clamp(t.c.X, a.min.X, a.max.X), math.clamp(t.c.Y, a.min.Y, a.max.Y))
			if (cl - t.c).Magnitude < t.r then table.insert(a.town, t.name) end
		end
	end
	-- calibration: rocky cells of the tiles inside the Watchstone box (the approved, optimised sample)
	for _, t in tiles do
		local cx, cz = t.tx * 128 + 64, t.tz * 128 + 64
		if cx > W.min.X and cx < W.max.X and cz > W.min.Z and cz < W.max.Z then calCells += t.rocky end
	end
	st.cal = { cells = calCells }
	-- clamped: a tiny or missing calibration (Watchstone scanned with few steep cells) must not blow budgets up
	local perCellTris = math.clamp(if calCells > 0 then W.tris / calCells else 1400, 600, 4000)
	local perCellParts = perCellTris * W.parts / W.tris
	local total = 0
	for _, a in areas do
		a.trisBudget = math.min(S.CAP_TRIS, math.floor(a.rocky * perCellTris))
		a.partsBudget = math.floor(a.trisBudget / perCellTris * perCellParts)
		a.coverCap = math.floor(a.partsBudget * 0.32) -- Watchstone: 292 rocks of 937 parts
		a.ivyCap = math.floor(a.partsBudget * 0.13)
		a.groundScale = math.clamp(a.trisBudget / math.max(a.rocky * perCellTris, 1), 0.3, 1) * 0.8
		total += a.trisBudget
	end
	if total > S.CAP_TOTAL then
		local k = S.CAP_TOTAL / total
		for _, a in areas do
			a.trisBudget = math.floor(a.trisBudget * k); a.partsBudget = math.floor(a.partsBudget * k)
			a.coverCap = math.floor(a.coverCap * k); a.ivyCap = math.floor(a.ivyCap * k)
		end
	end
	table.sort(areas, function(x, y) return x.rocky > y.rocky end)
	st.areas = areas
	st.perCellTris = perCellTris
end

function S.report()
	local st = _G.WorldSurvey
	if not (st and st.done) then return S.status() end
	local lines = { string.format("calibration: Watchstone rocky cells %d, tris per rocky cell %.0f", st.cal.cells, st.perCellTris),
		"# name | box x0,z0..x1,z1 | tiles | rocky | steep | props | y | flags | budget tris/parts/cover/ivy" }
	for i, a in st.areas do
		local flags = {}
		if a.volcanic then table.insert(flags, "VOLCANIC") end
		if a.coast then table.insert(flags, "COAST") end
		if #a.town > 0 then table.insert(flags, "TOWN:" .. table.concat(a.town, "+")) end
		table.insert(lines, string.format("%d %s | %d,%d..%d,%d | %d | %d | %d | %d | %.0f..%.0f | %s | %d/%d/%d/%d",
			i, a.name, a.min.X, a.min.Y, a.max.X, a.max.Y, a.tiles, a.rocky, a.steep, a.props, a.ymin, a.ymax,
			table.concat(flags, " "), a.trisBudget, a.partsBudget, a.coverCap, a.ivyCap))
	end
	return table.concat(lines, "\n")
end

-- Watchstone-sized pieces: boxes over ~700 studs a side are split into tiles of at most 640 (TerrainRegion
-- backups stay small, runs stay under a minute each). Returns D.addArea-ready definitions.
function S.split(a, maxSide: number?)
	maxSide = maxSide or 640
	local out = {}
	local nx = math.max(1, math.ceil((a.max.X - a.min.X) / maxSide))
	local nz = math.max(1, math.ceil((a.max.Y - a.min.Y) / maxSide))
	local wx, wz = (a.max.X - a.min.X) / nx, (a.max.Y - a.min.Y) / nz
	for i = 0, nx - 1 do
		for j = 0, nz - 1 do
			local mn = Vector3.new(a.min.X + i * wx, math.max(0, math.floor((a.ymin - 30) / 4) * 4), a.min.Y + j * wz)
			local mx = Vector3.new(a.min.X + (i + 1) * wx, math.ceil((a.ymax + 120) / 4) * 4, a.min.Y + (j + 1) * wz)
			table.insert(out, { name = (a.name:gsub("%W", "")) .. (if nx * nz > 1 then ("_" .. i .. j) else ""), min = mn, max = mx,
				coverCap = math.ceil(a.coverCap / (nx * nz)), ivyCap = math.ceil(a.ivyCap / (nx * nz)), groundScale = a.groundScale })
		end
	end
	return out
end

return S
