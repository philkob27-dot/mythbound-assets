-- Run in Edit after File > Import of MB_CrewKit.glb: turns the imported MeshParts into ServerStorage.CrewKit
-- (one Model per piece at the origin, MeshParts named by colour role, CFrame relative to the body part centre).
local BODY = {
	Head = { c = Vector3.new(0.0, 0.0, 4.54), s = Vector3.new(1.159, 1.161, 1.182) },
	UpperTorso = { c = Vector3.new(0.0, 0.0, 3.15), s = Vector3.new(1.943, 1.004, 1.698) },
	LowerTorso = { c = Vector3.new(0.0, 0.0, 2.15), s = Vector3.new(1.991, 1.004, 0.401) },
	LeftUpperArm = { c = Vector3.new(1.472, 0.0, 3.38), s = Vector3.new(1.001, 1.002, 1.242) },
	LeftLowerArm = { c = Vector3.new(1.472, 0.0, 2.71), s = Vector3.new(1.001, 1.002, 1.118) },
	LeftHand = { c = Vector3.new(1.472, 0.0, 2.11), s = Vector3.new(0.984, 1.028, 0.316) },
	RightUpperArm = { c = Vector3.new(-1.472, 0.0, 3.38), s = Vector3.new(1.001, 1.002, 1.242) },
	RightLowerArm = { c = Vector3.new(-1.472, 0.0, 2.71), s = Vector3.new(1.001, 1.002, 1.118) },
	RightHand = { c = Vector3.new(-1.472, 0.0, 2.11), s = Vector3.new(0.984, 1.028, 0.316) },
	LeftUpperLeg = { c = Vector3.new(0.497, 0.0, 1.38), s = Vector3.new(0.993, 0.973, 1.363) },
	LeftLowerLeg = { c = Vector3.new(0.497, 0.0, 0.8), s = Vector3.new(0.993, 0.973, 1.301) },
	LeftFoot = { c = Vector3.new(0.497, 0.0, 0.156), s = Vector3.new(1.009, 1.001, 0.312) },
	RightUpperLeg = { c = Vector3.new(-0.497, 0.0, 1.38), s = Vector3.new(0.993, 0.973, 1.363) },
	RightLowerLeg = { c = Vector3.new(-0.497, 0.0, 0.8), s = Vector3.new(0.993, 0.973, 1.301) },
	RightFoot = { c = Vector3.new(-0.497, 0.0, 0.156), s = Vector3.new(1.009, 1.001, 0.312) },
}
local ATTACH = {
	BellSleeveL = "LeftLowerArm",
	BellSleeveR = "RightLowerArm",
	Belt = "LowerTorso",
	BoneMask = "Head",
	BootL = "LeftLowerLeg",
	BootR = "RightLowerLeg",
	BracerL = "LeftLowerArm",
	BracerR = "RightLowerArm",
	BruteTop = "UpperTorso",
	Cloak = "UpperTorso",
	CloakLong = "UpperTorso",
	Coat = "UpperTorso",
	CoatCuffL = "LeftLowerArm",
	CoatCuffR = "RightLowerArm",
	CoatSleeveL = "LeftUpperArm",
	CoatSleeveR = "RightUpperArm",
	CoatTailL = "LeftUpperLeg",
	CoatTailR = "RightUpperLeg",
	FootL = "LeftFoot",
	FootR = "RightFoot",
	GloveL = "LeftHand",
	GloveR = "RightHand",
	Hood = "Head",
	HoodLong = "Head",
	KnightBootL = "LeftLowerLeg",
	KnightBootR = "RightLowerLeg",
	KnightBracerL = "LeftLowerArm",
	KnightBracerR = "RightLowerArm",
	KnightHelm = "Head",
	PauldronHeavyL = "LeftUpperArm",
	PauldronHeavyR = "RightUpperArm",
	PauldronL = "LeftUpperArm",
	PauldronR = "RightUpperArm",
	Quiver = "UpperTorso",
	RobeBelt = "LowerTorso",
	RobeSkirtL = "LeftUpperLeg",
	RobeSkirtR = "RightUpperLeg",
	RobeTop = "UpperTorso",
	SashBelt = "LowerTorso",
	Satchel = "LowerTorso",
	SleeveL = "LeftUpperArm",
	SleeveR = "RightUpperArm",
	Surcoat = "UpperTorso",
	TallBootL = "LeftLowerLeg",
	TallBootR = "RightLowerLeg",
	TrouserL = "LeftUpperLeg",
	TrouserR = "RightUpperLeg",
	Tunic = "UpperTorso",
	VaneMask = "Head",
	Wrap = "Head",
}
local src = workspace:FindFirstChild("SceneCrewKitImport") or workspace:FindFirstChild("CrewKitImport")
assert(src, "import not found")
local function get(n) local p = src:FindFirstChild(n, true) assert(p, n) return p.Position end
local A, B, Cc, D = get("CK_RefA"), get("CK_RefB"), get("CK_RefC"), get("CK_RefD")
local s = (B - A).Magnitude / 10
local eZ = (B - A).Unit       -- Blender +Z (up)
local eX = (Cc - A).Unit      -- Blender +X (character left)
local eY = -(D - A).Unit      -- Blender +Y (back)
local Rbody = CFrame.fromMatrix(Vector3.zero, -eX, eZ, eY) -- body frame (right, up, back) in world
local kit = game.ServerStorage:FindFirstChild("CrewKit")
if kit then kit:Destroy() end
kit = Instance.new("Folder") kit.Name = "CrewKit"
local n = 0
for _, mp in src:GetDescendants() do
	if mp:IsA("MeshPart") then
		local piece, role = string.match(mp.Name, "^CK_(.-)__(.+)$")
		if piece then
			role = string.gsub(role, "%.%d+$", "")
			local attach = ATTACH[piece]
			local b = BODY[attach]
			local w = mp.Position - A
			local bp = Vector3.new(w:Dot(eX), w:Dot(eY), w:Dot(eZ)) / s
			local d = bp - b.c
			local off = Vector3.new(-d.X, d.Z, d.Y)
			local rel = Rbody:Inverse() * (mp.CFrame - mp.CFrame.Position)
			local m = kit:FindFirstChild(piece)
			if not m then
				m = Instance.new("Model") m.Name = piece
				m:SetAttribute("Attach", attach)
				m:SetAttribute("RefSize", Vector3.new(b.s.X, b.s.Z, b.s.Y))
				m.Parent = kit
			end
			local c = mp:Clone()
			c.Name = role
			c.Size = mp.Size / s
			c.Anchored = true
			c.CanCollide = false c.CanQuery = false c.CanTouch = false
			c.CFrame = CFrame.new(off) * rel
			for _, ch in c:GetChildren() do if not ch:IsA("SurfaceAppearance") then ch:Destroy() end end
			c.Parent = m
			n += 1
		end
	end
end
kit.Parent = game.ServerStorage
return "kit parts " .. n .. " scale " .. s .. " eX " .. tostring(eX) .. " eY " .. tostring(eY) .. " eZ " .. tostring(eZ)
