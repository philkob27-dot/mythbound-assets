-- builds the sitters into Workspace.PortraitStage.Cast. Poses are set on the joint attachments (they replicate
-- and the rig solves them in Play). ONLY = a name to rebuild just that one.
return function(ONLY)
local RS = game:GetService("ReplicatedStorage")
local function fresh(mod)
	local c = mod:Clone(); c.Name = mod.Name .. "_ka"; c.Parent = mod.Parent
	local r = require(c); c:Destroy(); return r
end
local NF = fresh(game.ServerScriptService.Server.Combat.Npc.NpcFactory)
local GF = fresh(RS.Shared.gear.GearFit)
local S = workspace.PortraitStage
local cast = S.Cast
local function C(r, g, b) return Color3.fromRGB(r, g, b) end
local SKIN = { C(234, 184, 146), C(196, 142, 104), C(150, 100, 70), C(110, 72, 50), C(246, 210, 180), C(214, 160, 120) }
local HC = { white = C(226, 222, 212), black = C(28, 26, 30), dbrown = C(58, 38, 26), brown = C(96, 62, 38), auburn = C(128, 52, 30),
	red = C(150, 50, 28), sandy = C(196, 158, 100), blonde = C(222, 190, 120), grey = C(150, 146, 140), ash = C(176, 162, 132) }
local HW = NF.Palettes.highwatch
local D = math.rad

local SPECS = {
	{ id = "Portrait_1", seed = 11, pool = "knight", skin = 1, hair = "Folk_Hair_Long", hc = "white", beard = "Folk_Beard_Long", pose = "vigil",
		face = { eyes = "c_calm", brows = "r_heavy", mouth = "c_flat", mark = "" , eyeColor = "grey" } },
	{ id = "Portrait_2", seed = 12, pool = "dame", skin = 4, hair = "Folk_Hair_Braid", hc = "black", pose = "lance",
		face = { eyes = "u_fox", brows = "u_arch", mouth = "c_flat", eyeColor = "amber" } },
	{ id = "Portrait_3", seed = 13, pool = "knight", skin = 6, hair = "Folk_Hair_Crop", hc = "ash", beard = "Folk_Beard_Moustache", pose = "helm",
		face = { eyes = "c03", brows = "c_straight", mouth = "u_smug", mark = "stubble", eyeColor = "hazel" } },
	{ id = "Portrait_4", seed = 14, pool = "dame", skin = 5, hair = "Folk_Hair_Bun", hc = "auburn", pose = "vigil",
		face = { eyes = "c_gentle", brows = "c_soft", mouth = "c_soft", mark = "freckles", eyeColor = "green" } },
	{ id = "Portrait_5", seed = 15, pool = "knight", skin = 2, hair = "Folk_Hair_Topknot", hc = "dbrown", beard = "Folk_Beard_Goatee", pose = "lance",
		face = { eyes = "r_hawk", brows = "r_heavy", mouth = "c01", eyeColor = "brown" } },
	{ id = "Portrait_6", seed = 16, pool = "dame", skin = 3, hair = "Folk_Hair_Long", hc = "black", pose = "helm",
		face = { eyes = "c_calm", brows = "c_thin", mouth = "c02", mark = "beauty_mark", eyeColor = "dark" } },
	{ id = "Portrait_7", seed = 17, pool = "knight", skin = 1, hair = "Folk_Hair_Short", hc = "red", beard = "Folk_Beard_Full", pose = "vigil",
		face = { eyes = "c05", brows = "c03", mouth = "c04", eyeColor = "blue" } },
	{ id = "Portrait_8", seed = 18, pool = "dame", skin = 6, hair = "Folk_Hair_TwinBraids", hc = "sandy", pose = "lance",
		face = { eyes = "u_bright", brows = "c02", mouth = "u_smug", mark = "freckles", eyeColor = "sea" } },
	{ id = "Portrait_9", seed = 19, pool = "knight", skin = 4, hair = "Folk_Hair_Crop", hc = "black", beard = "Folk_Beard_Goatee", pose = "helm",
		face = { eyes = "c_calm", brows = "c01", mouth = "c_flat", mark = "cheek_scar", eyeColor = "dark" } },
	{ id = "Portrait_10", seed = 20, pool = "dame", skin = 3, hair = "Folk_Hair_Curly", hc = "dbrown", pose = "vigil",
		face = { eyes = "c06", brows = "u_arch", mouth = "c_soft", eyeColor = "amber" } },
	{ id = "Portrait_11", seed = 21, pool = "knight", skin = 5, hair = "Folk_Hair_Wild", hc = "ash", pose = "lance",
		face = { eyes = "u02", brows = "u07", mouth = "c_flat", mark = "stubble", eyeColor = "grey" } },
	{ id = "Portrait_12", seed = 22, pool = "dame", skin = 1, hair = "Folk_Hair_Braid", hc = "red", pose = "lance",
		face = { eyes = "c_wide", brows = "c_soft", mouth = "c02", mark = "freckles", eyeColor = "green" } },
	{ id = "Portrait_13", seed = 23, pool = "knight", skin = 2, hair = nil, helmOn = true, beard = "Folk_Beard_Moustache", hc = "brown", pose = "lance",
		face = { eyes = "c_gentle", brows = "c_soft", mouth = "c_soft", eyeColor = "hazel" } },
	{ id = "Portrait_14", seed = 24, pool = "dame", skin = 6, hair = "Folk_Hair_BunLow", hc = "blonde", pose = "vigil",
		face = { eyes = "c_calm", brows = "c_thin", mouth = "c_flat", eyeColor = "blue" } },
}

local function wearGear(model, name, color)
	local m = GF.build(name, model, color)
	if not m then return nil end
	for _, p in m:GetDescendants() do
		if p:IsA("BasePart") and p.Material ~= Enum.Material.Neon then
			p.Color = color; p.Material = Enum.Material.SmoothPlastic
		end
	end
	m.Parent = model
	return m
end

local function rot(model, partName, jointName, cf)
	local p = model:FindFirstChild(partName)
	local j = p and p:FindFirstChild(jointName)
	if j then j.Attachment0.CFrame = j.Attachment0.CFrame * cf end
end

local function mkPart(parent, name, size, color, mat, shape)
	local p = Instance.new("Part")
	p.Name = name; p.Size = size; p.Color = color; p.Material = mat or Enum.Material.SmoothPlastic
	if shape then p.Shape = shape end
	p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Massless = true; p.Anchored = false
	p.Parent = parent
	return p
end
local function weldTo(base, p, c0)
	p.CFrame = base.CFrame * c0
	local w = Instance.new("Weld"); w.Part0 = base; w.Part1 = p; w.C0 = c0; w.Parent = p
end

-- a lance: the shaft runs along the hand's local Z (the hand is pitched 90 degrees up by the pose)
local function lance(model)
	local hand = model.RightHand
	local m = Instance.new("Model"); m.Name = "Lance"; m.Parent = model
	local shaft = mkPart(m, "Shaft", Vector3.new(0.22, 0.22, 11), C(92, 64, 40), Enum.Material.Wood)
	weldTo(hand, shaft, CFrame.new(0, -0.15, -3.2))
	local grip = mkPart(m, "Grip", Vector3.new(0.3, 0.3, 1.2), C(60, 40, 28), Enum.Material.Leather)
	weldTo(shaft, grip, CFrame.new(0, 0, 3.2))
	local ring = mkPart(m, "Ring", Vector3.new(0.34, 0.34, 0.12), HW.Gold, Enum.Material.Metal)
	weldTo(shaft, ring, CFrame.new(0, 0, 2.5))
	local tipBase = mkPart(m, "TipBase", Vector3.new(0.3, 0.3, 0.5), HW.Metal, Enum.Material.Metal)
	weldTo(shaft, tipBase, CFrame.new(0, 0, -5.6))
	local tip = Instance.new("WedgePart"); tip.Name = "Tip"; tip.Size = Vector3.new(0.12, 1.6, 0.36); tip.Color = HW.Metal
	tip.Material = Enum.Material.Metal; tip.CanCollide = false; tip.CanQuery = false; tip.Massless = true; tip.Parent = m
	-- two wedges back to back make a leaf blade
	weldTo(shaft, tip, CFrame.new(0, 0, -6.6) * CFrame.Angles(D(90), 0, 0) * CFrame.new(0, 0, -0.18))
	local tip2 = tip:Clone(); tip2.Parent = m; tip2:FindFirstChildOfClass("Weld"):Destroy()
	weldTo(shaft, tip2, CFrame.new(0, 0, -6.6) * CFrame.Angles(D(90), D(180), 0) * CFrame.new(0, 0, -0.18))
	-- the pennon: Highwatch blue with a gold stripe, two tails
	local pen = mkPart(m, "Pennon", Vector3.new(0.05, 1.4, 1.1), HW.Cloth2, Enum.Material.Fabric)
	weldTo(shaft, pen, CFrame.new(0, 0.8, -4.4))
	local stripe = mkPart(m, "Stripe", Vector3.new(0.06, 0.18, 1.12), HW.Gold, Enum.Material.Fabric)
	weldTo(pen, stripe, CFrame.new(0, 0.1, 0))
end

-- a sword held point down, both hands on the pommel (welded to the right hand)
local function sword(model)
	local hand = model.RightHand
	local m = Instance.new("Model"); m.Name = "Sword"; m.Parent = model
	local grip = mkPart(m, "Grip", Vector3.new(0.2, 0.2, 0.9), C(60, 40, 28), Enum.Material.Leather)
	weldTo(hand, grip, CFrame.new(-0.25, -0.25, 0.1))
	local pommel = mkPart(m, "Pommel", Vector3.new(0.34, 0.34, 0.34), HW.Gold, Enum.Material.Metal, Enum.PartType.Ball)
	weldTo(grip, pommel, CFrame.new(0, 0, -0.55))
	local guard = mkPart(m, "Guard", Vector3.new(1.5, 0.16, 0.18), HW.Gold, Enum.Material.Metal)
	weldTo(grip, guard, CFrame.new(0, 0, 0.5))
	local blade = mkPart(m, "Blade", Vector3.new(0.34, 0.07, 4.2), C(200, 204, 212), Enum.Material.Metal)
	weldTo(grip, blade, CFrame.new(0, 0, 2.65))
	local fuller = mkPart(m, "Fuller", Vector3.new(0.08, 0.075, 3.4), C(150, 156, 168), Enum.Material.Metal)
	weldTo(blade, fuller, CFrame.new(0, 0, -0.3))
end

-- the helm carried under the left arm: the worn helm's parts move from the head to the left forearm
local function carryHelm(model)
	local helm = model:FindFirstChild("Helm")
	local arm = model.LeftLowerArm
	if not helm then return end
	for _, p in helm:GetChildren() do
		local w = p:FindFirstChild("LookWeld")
		if w then
			local rel = w.C0 -- relative to the head
			w.Part0 = arm
			w.C0 = CFrame.new(0.55, -0.1, -0.6) * CFrame.Angles(0, D(-75), D(-90)) * rel
		end
	end
end

local POSES = {
	lance = function(m)
		rot(m, "RightUpperArm", "RightShoulder", CFrame.Angles(D(12), 0, D(8)))
		rot(m, "RightLowerArm", "RightElbow", CFrame.Angles(D(78), 0, 0))
		rot(m, "LeftUpperArm", "LeftShoulder", CFrame.Angles(D(4), 0, D(-4)))
		rot(m, "LeftLowerArm", "LeftElbow", CFrame.Angles(D(10), 0, 0))
		lance(m)
	end,
	vigil = function(m)
		rot(m, "RightUpperArm", "RightShoulder", CFrame.Angles(D(32), 0, D(-14)))
		rot(m, "RightLowerArm", "RightElbow", CFrame.Angles(D(52), 0, D(-12)))
		rot(m, "LeftUpperArm", "LeftShoulder", CFrame.Angles(D(32), 0, D(14)))
		rot(m, "LeftLowerArm", "LeftElbow", CFrame.Angles(D(52), 0, D(12)))
		sword(m)
	end,
	helm = function(m)
		rot(m, "LeftUpperArm", "LeftShoulder", CFrame.Angles(D(10), 0, D(-12)))
		rot(m, "LeftLowerArm", "LeftElbow", CFrame.Angles(D(85), 0, 0))
		rot(m, "RightUpperArm", "RightShoulder", CFrame.Angles(D(4), 0, D(5)))
		rot(m, "RightLowerArm", "RightElbow", CFrame.Angles(D(14), 0, 0))
		carryHelm(m)
	end,
}

local function build(spec)
	local m = NF.knight(spec.seed)
	local skin = SKIN[spec.skin]
	m.Head.Color = skin
	local bc = m:FindFirstChildOfClass("BodyColors"); if bc then bc.HeadColor3 = skin end
	local fh = m.Head:FindFirstChild("FaceHead"); if fh then fh.Color = skin end
	local hc = HC[spec.hc] or HC.brown
	NF.face(m, spec.pool, spec.seed, hc, spec.face)
	if not spec.helmOn and spec.pose ~= "helm" then NF.strip(m, { "Helm" }) end
	if spec.hair and not spec.helmOn then wearGear(m, spec.hair, hc) end
	if spec.beard then wearGear(m, spec.beard, hc) end
	-- a captain's cloak in Highwatch blue over the shoulders for everyone (the hall honours them)
	NF.wearPiece(m, "Cloak", HW)
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") and d.Material == Enum.Material.Neon then d.Color = HW.Gold; d.Material = Enum.Material.Metal end
	end
	-- turn three quarters to the camera, the head back toward it, chin a touch up
	rot(m, "Head", "Neck", CFrame.Angles(D(spec.chin or 3), D(spec.look or -14), D(spec.tilt or 2)))
	rot(m, "UpperTorso", "Waist", CFrame.Angles(0, D(-6), 0))
	POSES[spec.pose](m)
	m.Name = spec.id
	m.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
	m:SetAttribute("Yaw", spec.yaw or 26)
	-- parked below the stage floor until the server moves it onto the mark
	m:PivotTo(CFrame.new(-21000, 760, -21000))
	local hum = m:FindFirstChildOfClass("Humanoid"); if hum then hum.PlatformStand = true end
	m.HumanoidRootPart.Anchored = true
	m.Parent = cast
	return m
end

local n = 0
for _, spec in SPECS do
	if ONLY == nil or ONLY == spec.id then
		local old = cast:FindFirstChild(spec.id); if old then old:Destroy() end
		build(spec); n += 1
		task.wait()
	end
end
return "built " .. n
end
