-- builds Workspace.PortraitStage: a closed dark box with a green screen on the back wall and a light rig
local old = workspace:FindFirstChild("PortraitStage")
if old then old:Destroy() end
local S = Instance.new("Model")
S.Name = "PortraitStage"
S.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local O = Vector3.new(-21000, 800, -21000)
local function part(name, size, pos, color, mat)
	local p = Instance.new("Part")
	p.Name = name; p.Anchored = true; p.Size = size; p.Position = O + pos
	p.Color = color or Color3.fromRGB(30, 30, 34); p.Material = mat or Enum.Material.SmoothPlastic
	p.CastShadow = false
	p.Parent = S
	return p
end
local W = 70
part("Floor", Vector3.new(W, 1, W), Vector3.new(0, -0.5, 0))
part("Ceil", Vector3.new(W, 1, W), Vector3.new(0, 36, 0))
local back = part("Back", Vector3.new(W, 36, 1), Vector3.new(0, 18, 32))
part("Front", Vector3.new(W, 36, 1), Vector3.new(0, 18, -33))
part("L", Vector3.new(1, 36, W), Vector3.new(-33, 18, 0))
part("R", Vector3.new(1, 36, W), Vector3.new(33, 18, 0))
-- the green screen, unlit (keyed out later)
local g = Instance.new("SurfaceGui")
g.Face = Enum.NormalId.Front; g.LightInfluence = 0; g.Brightness = 1; g.CanvasSize = Vector2.new(64, 32)
g.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
local f = Instance.new("Frame"); f.Size = UDim2.fromScale(1, 1); f.BackgroundColor3 = Color3.fromRGB(0, 255, 0); f.BorderSizePixel = 0; f.Parent = g
g.Parent = back
-- also green floor/ceiling patches far behind are not needed: the camera only sees the back wall
local function light(name, pos, aim, color, bright, range, angle, shadows)
	local p = part(name, Vector3.new(0.2, 0.2, 0.2), pos)
	p.Transparency = 1; p.CanCollide = false; p.CanQuery = false
	p.CFrame = CFrame.lookAt(O + pos, O + aim)
	local l = Instance.new("SpotLight")
	l.Face = Enum.NormalId.Front; l.Color = color; l.Brightness = bright; l.Range = range; l.Angle = angle; l.Shadows = shadows
	l.Parent = p
	return p
end
local head = Vector3.new(0, 4.6, 0)
light("Key", Vector3.new(-5, 8.5, -6.5), head, Color3.fromRGB(255, 222, 186), 5, 22, 50, true)
light("Fill", Vector3.new(6, 4, -7), head - Vector3.new(0, 0.8, 0), Color3.fromRGB(140, 160, 215), 1.1, 22, 70, false)
light("RimL", Vector3.new(-4.5, 7.5, 4.5), head, Color3.fromRGB(255, 196, 132), 7, 14, 45, false)
light("RimR", Vector3.new(4.5, 7, 4), head, Color3.fromRGB(190, 210, 255), 5, 14, 45, false)
light("Top", Vector3.new(0, 11, 2), head, Color3.fromRGB(255, 236, 210), 2.5, 14, 40, false)
local cast = Instance.new("Folder"); cast.Name = "Cast"; cast.Parent = S
local mark = part("Mark", Vector3.new(1, 0.2, 1), Vector3.new(0, 0.1, 0)); mark.Transparency = 1; mark.CanCollide = false
S.Parent = workspace
return "stage ok"
