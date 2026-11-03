--!strict
-- Builds the human fighters and story people: a normal R15 Roblox body (the default blocky proportions,
-- like a player's avatar) with one of our faces, dressed in 3D clothing from the crew kit
-- (ServerStorage.CrewKit: our own Blender meshes, crew_kit.py in mythbound-assets/npc/crew; one Model per
-- piece, one MeshPart per colour role). Every piece is welded to the body part it was modelled on, so it
-- moves with that joint under the animations (CharacterAnimator writes the joints, the clothes follow).
-- The clothes never collide, never take queries or touches and weigh nothing: hit boxes stay the body's.
--
-- The Thrallbinders wear charcoal and crimson with a green binding ring (a ring cut by a line) on the brow,
-- the chest and the buckle; the glow is the rune Cleanse burns out (part "ChestRune"). Roles in the crew:
--   grunt     hood, face wrap, short split cloak, crossbelt, one pauldron
--   archer    hood, face wrap, quiver, no cloak
--   drawer    long hood, rune robe with glowing seams, wide sleeves, chalk satchel (they draw the runes)
--   brute     bald, face wrap, fur mantle, heavy spiked pauldrons, a head bigger
--   leader    hood, carved bone mask with glowing eyes, long tattered cloak, two pauldrons
-- Vane wears her own: a black officer's coat with a high collar and silver buttons, a crimson sash, a
-- porcelain half mask with a red line under the left eye, coat tails and tall boots, her black ponytail.
-- Highwatch knights (the portraits, Knight-Captain Roderic): open helm with a plume, blue surcoat with the
-- lance and wing in gold, steel plate. Rune Knights: the same plate in dark steel with green runes.
--
-- Kinds that a chapter turns into a beast (the Thrallbinder body under a boar, a hound, a crab...) or
-- dresses in its own uniform keep the old plain body (legacy below), so those disguises still fit.
-- Without the kit (before the import) everything falls back to the old part gear.

local Players = game:GetService("Players")
local ServerStorage = game:GetService("ServerStorage")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local NpcFactory = {}

local RUNE = Color3.fromRGB(110, 255, 160)

------------------------------------------------------------------------------------------------------
-- Palettes (colour per role of the kit) and materials

type Palette = { [string]: Color3 }

local function C(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end

local CREW: Palette = {
	Cloth = C(38, 36, 44), Cloth2 = C(64, 60, 68), Lining = C(120, 26, 34), Leather = C(76, 54, 40),
	Metal = C(98, 102, 112), Bone = C(222, 214, 190), Glow = RUNE, Fur = C(86, 74, 64), Wood = C(112, 80, 52),
	Fletch = C(198, 188, 168), Paint = C(140, 24, 30), Gold = C(196, 156, 72),
}
local DRAWER: Palette = table.clone(CREW)
DRAWER.Cloth, DRAWER.Cloth2, DRAWER.Lining = C(30, 30, 38), C(54, 46, 64), C(96, 30, 44)
local LEADER: Palette = table.clone(CREW)
LEADER.Cloth, LEADER.Lining, LEADER.Metal = C(30, 28, 34), C(146, 22, 30), C(70, 72, 80)
local POACHER: Palette = table.clone(CREW)
POACHER.Cloth, POACHER.Cloth2, POACHER.Lining, POACHER.Leather = C(34, 34, 36), C(84, 72, 58), C(70, 56, 44), C(92, 66, 46)
local RUNE_KNIGHT: Palette = table.clone(CREW)
RUNE_KNIGHT.Cloth, RUNE_KNIGHT.Cloth2, RUNE_KNIGHT.Metal, RUNE_KNIGHT.Lining, RUNE_KNIGHT.Gold = C(36, 40, 50), C(44, 58, 82), C(66, 70, 80), C(44, 58, 82), C(150, 156, 168)
local HIGHWATCH: Palette = table.clone(CREW)
HIGHWATCH.Cloth, HIGHWATCH.Cloth2, HIGHWATCH.Metal, HIGHWATCH.Lining, HIGHWATCH.Gold, HIGHWATCH.Leather =
	C(52, 54, 62), C(40, 70, 132), C(176, 182, 192), C(150, 30, 36), C(210, 172, 84), C(92, 64, 44)
local VANE: Palette = table.clone(CREW)
VANE.Cloth, VANE.Cloth2, VANE.Lining, VANE.Leather, VANE.Gold, VANE.Bone, VANE.Paint =
	C(26, 26, 32), C(58, 58, 68), C(150, 22, 30), C(40, 34, 32), C(196, 198, 208), C(242, 238, 230), C(176, 20, 30)

NpcFactory.Palettes = { crew = CREW, drawer = DRAWER, leader = LEADER, poacher = POACHER, runeKnight = RUNE_KNIGHT, highwatch = HIGHWATCH, vane = VANE }

local MATERIAL: { [string]: Enum.Material } = {
	Cloth = Enum.Material.Fabric, Cloth2 = Enum.Material.Fabric, Lining = Enum.Material.Fabric, Leather = Enum.Material.Leather,
	Metal = Enum.Material.Metal, Bone = Enum.Material.SmoothPlastic, Glow = Enum.Material.Neon, Fur = Enum.Material.Fabric,
	Wood = Enum.Material.Wood, Fletch = Enum.Material.Fabric, Paint = Enum.Material.SmoothPlastic, Gold = Enum.Material.Metal,
}

-- the outfits: kit pieces, and the name the piece gets on the model (older code looks for Hood, Mask, Cloak, Pauldron)
local OUTFITS: { [string]: { string } } = {
	grunt = { "Hood", "Wrap", "Tunic", "Cloak", "Belt", "SleeveL", "SleeveR", "BracerL", "BracerR", "GloveL", "GloveR",
		"TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR", "PauldronR" },
	poacher = { "Hood", "Wrap", "Tunic", "Belt", "SleeveL", "SleeveR", "BracerL", "BracerR", "GloveL", "GloveR",
		"TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR" },
	archer = { "Hood", "Wrap", "Tunic", "Quiver", "Belt", "SleeveL", "SleeveR", "BracerL", "BracerR", "GloveL", "GloveR",
		"TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR" },
	drawer = { "HoodLong", "RobeTop", "RobeBelt", "Satchel", "SleeveL", "SleeveR", "BellSleeveL", "BellSleeveR",
		"RobeSkirtL", "RobeSkirtR", "BootL", "BootR", "FootL", "FootR" },
	binder = { "HoodLong", "BoneMask", "RobeTop", "RobeBelt", "Satchel", "SleeveL", "SleeveR", "BellSleeveL", "BellSleeveR",
		"RobeSkirtL", "RobeSkirtR", "BootL", "BootR", "FootL", "FootR" },
	brute = { "Wrap", "BruteTop", "Belt", "PauldronHeavyL", "PauldronHeavyR", "BracerL", "BracerR", "GloveL", "GloveR",
		"TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR" },
	leader = { "Hood", "BoneMask", "Tunic", "CloakLong", "Belt", "PauldronL", "PauldronR", "SleeveL", "SleeveR", "BracerL", "BracerR",
		"GloveL", "GloveR", "TrouserL", "TrouserR", "BootL", "BootR", "FootL", "FootR" },
	-- a crew body for kinds a chapter dresses in its own helmet or uniform (no hood or cloak in the way)
	base = { "Tunic", "Belt", "SleeveL", "SleeveR", "BracerL", "BracerR", "GloveL", "GloveR", "TrouserL", "TrouserR",
		"BootL", "BootR", "FootL", "FootR" },
	knight = { "KnightHelm", "Surcoat", "Belt", "PauldronL", "PauldronR", "SleeveL", "SleeveR", "KnightBracerL", "KnightBracerR",
		"GloveL", "GloveR", "TrouserL", "TrouserR", "KnightBootL", "KnightBootR", "FootL", "FootR" },
	vane = { "VaneMask", "Coat", "SashBelt", "CoatSleeveL", "CoatSleeveR", "CoatCuffL", "CoatCuffR", "GloveL", "GloveR",
		"CoatTailL", "CoatTailR", "TrouserL", "TrouserR", "TallBootL", "TallBootR", "FootL", "FootR" },
}
NpcFactory.Outfits = OUTFITS

local INST_NAME: { [string]: string } = {
	Hood = "Hood", HoodLong = "Hood", Wrap = "Mask", BoneMask = "Mask", VaneMask = "Mask", Cloak = "Cloak", CloakLong = "Cloak",
	PauldronR = "Pauldron", KnightHelm = "Helm",
}

------------------------------------------------------------------------------------------------------
-- The kit

local function crewKit(): Instance?
	return ServerStorage:FindFirstChild("CrewKit")
end

function NpcFactory.kitReady(): boolean
	local k = crewKit()
	return k ~= nil and k:FindFirstChild("Tunic") ~= nil
end

-- Welds one kit piece onto its body part, coloured from the palette. Returns the piece's Model.
function NpcFactory.wearPiece(model: Model, pieceName: string, palette: Palette?, instName: string?): Model?
	local kit = crewKit()
	local src = kit and kit:FindFirstChild(pieceName)
	if not src or not src:IsA("Model") then
		return nil
	end
	local attach = src:GetAttribute("Attach")
	local ref = src:GetAttribute("RefSize")
	local body = if typeof(attach) == "string" then model:FindFirstChild(attach) else nil
	if not body or not body:IsA("BasePart") or typeof(ref) ~= "Vector3" then
		return nil
	end
	local pal = palette or CREW
	local s = Vector3.new(body.Size.X / ref.X, body.Size.Y / ref.Y, body.Size.Z / ref.Z)
	local out = Instance.new("Model")
	out.Name = instName or INST_NAME[pieceName] or pieceName
	out:SetAttribute("CrewPiece", pieceName)
	for _, mp in src:GetChildren() do
		if not mp:IsA("BasePart") then
			continue
		end
		local off = mp.CFrame -- relative to the body part's centre (the kit model sits at the origin)
		local rot = off.Rotation
		local ls = rot:VectorToObjectSpace(s)
		local p = mp:Clone()
		p.Size = mp.Size * Vector3.new(math.abs(ls.X), math.abs(ls.Y), math.abs(ls.Z))
		local at = CFrame.new(off.Position * s) * rot
		p.CFrame = body.CFrame * at
		p.Anchored = false
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Massless = true
		p.CastShadow = p.Size.Magnitude > 0.7
		local role = mp.Name
		local c = pal[role]
		if c then
			p.Color = c
		end
		p.Material = MATERIAL[role] or Enum.Material.SmoothPlastic
		local w = Instance.new("Weld")
		w.Name = "LookWeld"
		w.Part0 = body
		w.Part1 = p
		w.C0 = at
		w.Parent = p
		p.Parent = out
	end
	out.Parent = model
	return out
end

function NpcFactory.wearOutfit(model: Model, outfit: string | { string }, palette: Palette?)
	local list = if type(outfit) == "string" then OUTFITS[outfit] else outfit
	for _, piece in list or {} do
		NpcFactory.wearPiece(model, piece, palette)
	end
	-- the chest rune as its own part on the model (Cleanse and older code look for "ChestRune")
	for _, top in { "Tunic", "RobeTop", "BruteTop" } do
		local m = model:FindFirstChild(top)
		local glow = m and m:FindFirstChild("Glow")
		if glow and glow:IsA("BasePart") then
			glow.Name = "ChestRune"
			glow.Parent = model
		end
	end
end

-- Takes the named pieces (or every kit piece) off a model again
function NpcFactory.strip(model: Model, names: { string }?)
	for _, d in model:GetChildren() do
		if d:IsA("Model") and d:GetAttribute("CrewPiece") ~= nil then
			if not names or table.find(names, d.Name) or table.find(names, d:GetAttribute("CrewPiece") :: string) then
				d:Destroy()
			end
		end
	end
end

------------------------------------------------------------------------------------------------------
-- The body and the face

local SKIN = {
	C(234, 184, 146), C(196, 142, 104), C(150, 100, 70), C(110, 72, 50), C(246, 210, 180), C(214, 160, 120),
}

local function faceDecal(model: Model, kind: string)
	local head = model:FindFirstChild("Head")
	if not head or not head:IsA("BasePart") then
		return
	end
	local ok, FolkLooks = pcall(function()
		return require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("data"):WaitForChild("FolkLooks")) :: any
	end)
	local faces = ok and FolkLooks and FolkLooks.RobloxFaces
	local id = faces and (faces[kind] or faces.stern or faces.neutral)
	if type(id) ~= "string" or id == "" then
		return
	end
	local d = Instance.new("Decal")
	d.Name = "face"
	d.Face = Enum.NormalId.Front
	d.Texture = id
	d.Parent = head
end

local function body(skin: Color3, cloth: Color3, legs: Color3): Model
	local desc = Instance.new("HumanoidDescription")
	desc.HeadColor = skin
	desc.TorsoColor = cloth
	desc.LeftArmColor = cloth
	desc.RightArmColor = cloth
	desc.LeftLegColor = legs
	desc.RightLegColor = legs
	local model = Players:CreateHumanoidModelFromDescription(desc, Enum.HumanoidRigType.R15)
	for _, d in model:GetDescendants() do
		if (d:IsA("Script") or d:IsA("LocalScript")) and d.Name == "Animate" then
			d:Destroy()
		end
	end
	local head = model:FindFirstChild("Head")
	local face = head and head:FindFirstChildOfClass("Decal")
	if face then
		face:Destroy()
	end
	local hum = model:FindFirstChildOfClass("Humanoid") :: Humanoid
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	hum.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	hum.BreakJointsOnDeath = false
	hum.RequiresNeck = false
	return model
end

local function hair(model: Model, name: string, color: Color3)
	local ok, GearFit = pcall(function()
		return require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("gear"):WaitForChild("GearFit")) :: any
	end)
	if not ok or not GearFit then
		return
	end
	local m = GearFit.build(name, model, color)
	if m then
		for _, p in m:GetChildren() do
			if p:IsA("BasePart") and p.Material ~= Enum.Material.Neon then
				p.Color = color
				p.Material = Enum.Material.SmoothPlastic
			end
		end
		m.Name = "Hair"
		m.Parent = model
	end
end

local function finish(model: Model)
	-- the body keeps its own collision, touch and query settings (hit boxes are the body's); the clothes
	-- were made non colliding, non touching and non querying in wearPiece
	model:SetAttribute("CrewLook", true)
end

------------------------------------------------------------------------------------------------------
-- The crew

local FACE_BY_ROLE: { [string]: { string } } = {
	grunt = { "stern", "neutral", "stern" }, poacher = { "neutral", "grin", "stern" }, archer = { "neutral", "stern" },
	drawer = { "stern", "old" }, brute = { "stern", "grin" }, leader = { "stern" }, binder = { "stern" }, base = { "stern", "neutral" },
}

-- A crew member in one of the roles above. seed keeps the made up details (skin, shade, face) the same.
function NpcFactory.crew(role: string, seed: number, paletteName: string?): Model
	local rng = Random.new(seed)
	local skin = SKIN[rng:NextInteger(1, #SKIN)]
	local base = NpcFactory.Palettes[paletteName or ""] or (if role == "drawer" or role == "binder" then DRAWER
		elseif role == "leader" then LEADER elseif role == "poacher" then POACHER else CREW)
	local pal: Palette = table.clone(base)
	-- small differences between crew members: the shade of the cloth and the leather
	local k = rng:NextNumber(-0.06, 0.06)
	pal.Cloth = pal.Cloth:Lerp(if k > 0 then Color3.new(1, 1, 1) else Color3.new(0, 0, 0), math.abs(k))
	local seconds = { pal.Cloth2, C(84, 72, 58), C(58, 62, 52), C(70, 62, 74) }
	if role ~= "drawer" and role ~= "binder" then
		pal.Cloth2 = seconds[rng:NextInteger(1, #seconds)]
	end
	pal.Leather = pal.Leather:Lerp(C(40, 28, 20), rng:NextNumber(0, 0.4))
	local model = body(skin, pal.Cloth, pal.Cloth2)
	NpcFactory.wearOutfit(model, OUTFITS[role] or OUTFITS.grunt, pal)
	local faces = FACE_BY_ROLE[role] or FACE_BY_ROLE.grunt
	faceDecal(model, faces[rng:NextInteger(1, #faces)])
	if role == "brute" then
		model:ScaleTo(1.12)
	elseif role == "leader" then
		model:ScaleTo(1.15)
	end
	model:SetAttribute("CrewRole", role)
	finish(model)
	model.Name = "Thrallbinder"
	return model
end

-- Vane (Captain Ysolde Vane, once "Captain Wren"): her coat, her mask, her ponytail.
-- masked = false leaves the mask off (the reveal, the portrait of the young captain).
function NpcFactory.vane(masked: boolean?): Model
	local model = body(SKIN[2], VANE.Cloth, VANE.Cloth2)
	NpcFactory.wearOutfit(model, OUTFITS.vane, VANE)
	if masked == false then
		NpcFactory.strip(model, { "Mask" })
	end
	hair(model, "Folk_Hair_Ponytail", C(30, 30, 34))
	faceDecal(model, "stern")
	finish(model)
	model.Name = "Vane"
	return model
end

-- A knight of Highwatch (or, rune = true, a Rune Knight of the Thrallbinders)
function NpcFactory.knight(seed: number, rune: boolean?, palette: Palette?): Model
	local rng = Random.new(seed)
	local pal = palette or (if rune then RUNE_KNIGHT else HIGHWATCH)
	local model = body(SKIN[rng:NextInteger(1, #SKIN)], pal.Cloth, pal.Cloth)
	NpcFactory.wearOutfit(model, OUTFITS.knight, pal)
	if rune then
		-- the Rune Knights: heavy spiked pauldrons and a rune on the chest instead of the lance and wing
		NpcFactory.strip(model, { "PauldronL", "Pauldron" })
		NpcFactory.wearPiece(model, "PauldronHeavyL", pal)
		NpcFactory.wearPiece(model, "PauldronHeavyR", pal)
	end
	faceDecal(model, "stern")
	finish(model)
	model.Name = if rune then "RuneKnight" else "Knight"
	return model
end

------------------------------------------------------------------------------------------------------
-- The old part gear (kinds a chapter disguises as a beast or dresses itself, and the fallback without the kit)

local function gear(model: Model, partName: string, name: string, size: Vector3, offset: CFrame, color: Color3, material: Enum.Material?, shape: Enum.PartType?): BasePart?
	local base = model:FindFirstChild(partName)
	if not base or not base:IsA("BasePart") then
		return nil
	end
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = material or Enum.Material.Fabric
	if shape then
		p.Shape = shape
	end
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CFrame = base.CFrame * offset
	local w = Instance.new("WeldConstraint")
	w.Part0 = base
	w.Part1 = p
	w.Parent = p
	p.Parent = model
	return p
end

local function wedgeGear(model: Model, partName: string, name: string, size: Vector3, offset: CFrame, color: Color3)
	local base = model:FindFirstChild(partName)
	if not base or not base:IsA("BasePart") then
		return
	end
	local p = Instance.new("WedgePart")
	p.Name = name
	p.Size = size
	p.Color = color
	p.Material = Enum.Material.Fabric
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
	p.CFrame = base.CFrame * offset
	local w = Instance.new("WeldConstraint")
	w.Part0 = base
	w.Part1 = p
	w.Parent = p
	p.Parent = model
end

-- kept for older callers (the Blender BL_TB kit was never imported)
function NpcFactory.wear(model: Model, pieceName: string, partName: string): boolean
	return NpcFactory.wearPiece(model, pieceName) ~= nil
end

function NpcFactory.legacyThrallbinder(seed: number, archer: boolean): Model
	local rng = Random.new(seed)
	local skin = SKIN[rng:NextInteger(1, 5)]
	local cloth = C(36, 34, 42)
	local model = body(skin, cloth, C(28, 28, 34))
	local bc = model:FindFirstChildOfClass("BodyColors")
	if bc then
		bc.LeftArmColor3 = C(44, 42, 50)
		bc.RightArmColor3 = C(44, 42, 50)
	end
	gear(model, "Head", "Hood", Vector3.new(1.35, 1.35, 1.35), CFrame.new(0, 0.12, 0.08), C(26, 24, 30), Enum.Material.Fabric)
	wedgeGear(model, "Head", "HoodTip", Vector3.new(1.0, 0.6, 0.7), CFrame.new(0, 0.9, 0.35) * CFrame.Angles(0, math.rad(180), 0), C(26, 24, 30))
	gear(model, "Head", "Mask", Vector3.new(1.05, 0.62, 0.12), CFrame.new(0, -0.08, -0.62), C(58, 60, 70), Enum.Material.Metal)
	gear(model, "Head", "EyeL", Vector3.new(0.18, 0.08, 0.05), CFrame.new(-0.22, 0.05, -0.69), RUNE, Enum.Material.Neon)
	gear(model, "Head", "EyeR", Vector3.new(0.18, 0.08, 0.05), CFrame.new(0.22, 0.05, -0.69), RUNE, Enum.Material.Neon)
	gear(model, "UpperTorso", "Cloak", Vector3.new(2.1, 2.3, 0.14), CFrame.new(0, -0.45, 0.58), C(22, 20, 26), Enum.Material.Fabric)
	gear(model, "UpperTorso", "Collar", Vector3.new(2.2, 0.32, 1.2), CFrame.new(0, 0.72, 0.05), C(30, 28, 34), Enum.Material.Fabric)
	gear(model, "RightUpperArm", "Pauldron", Vector3.new(1.2, 0.55, 1.2), CFrame.new(0.08, 0.42, 0), C(62, 64, 74), Enum.Material.Metal)
	gear(model, "RightUpperArm", "PauldronRune", Vector3.new(0.5, 0.12, 0.06), CFrame.new(0.2, 0.42, -0.62), RUNE, Enum.Material.Neon)
	gear(model, "LowerTorso", "Belt", Vector3.new(2.1, 0.26, 1.1), CFrame.new(0, 0.05, 0), C(70, 46, 30), Enum.Material.Leather)
	gear(model, "LowerTorso", "Buckle", Vector3.new(0.34, 0.3, 0.06), CFrame.new(0, 0.05, -0.57), RUNE, Enum.Material.Neon)
	gear(model, "UpperTorso", "ChestRune", Vector3.new(0.12, 0.7, 0.05), CFrame.new(0, 0.1, -0.52), RUNE, Enum.Material.Neon)
	model.Name = if archer then "ThrallbinderMarksman" else "Thrallbinder"
	return model
end

------------------------------------------------------------------------------------------------------
-- The calls the game makes

-- A Thrallbinder (camps, sneak guards, scenes): mostly grunts, now and then a brute; archers get the quiver
function NpcFactory.thrallbinder(seed: number, archer: boolean): Model
	if not NpcFactory.kitReady() then
		return NpcFactory.legacyThrallbinder(seed, archer)
	end
	local roll = Random.new(seed + 77):NextNumber()
	local role = if archer then "archer" elseif roll < 0.18 then "brute" else "grunt"
	local m = NpcFactory.crew(role, seed)
	m.Name = if archer then "ThrallbinderMarksman" else "Thrallbinder"
	return m
end

-- A lieutenant: the masked officer, a head taller, the long cloak and two pauldrons
function NpcFactory.lieutenant(seed: number): Model
	if not NpcFactory.kitReady() then
		local model = NpcFactory.legacyThrallbinder(seed, false)
		model:ScaleTo(1.2)
		model.Name = "ThrallbinderLieutenant"
		return model
	end
	local m = NpcFactory.crew("leader", seed)
	m.Name = "ThrallbinderLieutenant"
	return m
end

-- A Rune Knight (A18), the anchors' keepers
function NpcFactory.runeKnight(seed: number): Model
	if not NpcFactory.kitReady() then
		local model = NpcFactory.legacyThrallbinder(seed, false)
		model:ScaleTo(1.12)
		model.Name = "RuneKnight"
		return model
	end
	local m = NpcFactory.knight(seed, true)
	m:ScaleTo(1.08)
	m.Name = "RuneKnight"
	return m
end

-- kinds a chapter turns into a beast or goblin: the plain old body, so the disguise fits as before
local LEGACY: { [string]: boolean } = {
	MeadowBoar = true, MeadowFox = true, StormHound = true, StormWisp = true, ScrapGoblin = true, BombTinker = true,
	Gloomstalker = true, BoneCrab = true, GloomMatriarch = true, RuneHound = true,
}
-- kinds a chapter dresses in its own helmet or uniform: the crew body without hood, mask or cloak
local DRESSED: { [string]: boolean } = {
	ThrallDiver = true, DrakeRider = true, Tidebinder = true, LumenWarden = true, ForgeWarden = true, SkyLancer = true, Corvid = true,
}
local ROLE_OF: { [string]: string } = {
	HoodedPoacher = "poacher", ThrallbinderMarksman = "archer", StormCaller = "drawer", Binder = "binder",
	ThrallbinderLieutenant = "leader", ShadeScout = "grunt",
}

-- The body for a kind of NpcSpawns (NpcService)
function NpcFactory.forKind(kind: any, seed: number): Model
	local id = kind.id
	if kind.look == "Dummy" then
		return NpcFactory.dummy()
	end
	if not NpcFactory.kitReady() or LEGACY[id] then
		if kind.look == "Lieutenant" then
			return NpcFactory.lieutenant(seed)
		elseif kind.look == "Knight" then
			return NpcFactory.runeKnight(seed)
		end
		return NpcFactory.legacyThrallbinder(seed, kind.brain == "Archer")
	end
	if id == "KnightCaptain" then
		local m = NpcFactory.knight(seed, false)
		m:SetAttribute("Knight", true)
		return m
	end
	if kind.look == "Knight" then
		return NpcFactory.runeKnight(seed)
	end
	if DRESSED[id] then
		return NpcFactory.crew("base", seed)
	end
	if kind.look == "Lieutenant" then
		return NpcFactory.lieutenant(seed)
	end
	local role = ROLE_OF[id]
	if role then
		return NpcFactory.crew(role, seed)
	end
	return NpcFactory.thrallbinder(seed, kind.brain == "Archer")
end

function NpcFactory.dummy(): Model
	local straw = C(214, 180, 104)
	local sack = C(176, 150, 112)
	local model = body(sack, sack, C(120, 86, 52))
	local bc = model:FindFirstChildOfClass("BodyColors")
	if bc then
		bc.LeftArmColor3 = straw
		bc.RightArmColor3 = straw
	end
	gear(model, "Head", "Patch", Vector3.new(0.5, 0.5, 0.06), CFrame.new(0.15, 0.1, -0.52), C(196, 72, 60), Enum.Material.Fabric)
	gear(model, "UpperTorso", "Rope", Vector3.new(2.06, 0.2, 1.06), CFrame.new(0, -0.3, 0), C(150, 120, 80), Enum.Material.Fabric)
	gear(model, "UpperTorso", "Target", Vector3.new(0.06, 0.9, 0.9), CFrame.new(0, 0.2, -0.52) * CFrame.Angles(0, math.rad(90), 0), C(236, 230, 210), Enum.Material.Fabric, Enum.PartType.Cylinder)
	gear(model, "UpperTorso", "Bull", Vector3.new(0.07, 0.36, 0.36), CFrame.new(0, 0.2, -0.53) * CFrame.Angles(0, math.rad(90), 0), C(196, 72, 60), Enum.Material.Fabric, Enum.PartType.Cylinder)
	model.Name = "TrainingDummy"
	return model
end

return NpcFactory
