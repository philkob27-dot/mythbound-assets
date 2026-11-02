# Prints a markdown table of all exported sets (triangles per rarity, largest mesh, mesh count) and checks budgets.
import json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["Envoy", "Kelpfarmer", "Stormcaller", "Bogwitch", "Watcherstone", "Climber", "Racer", "Ledgerwarden", "Songkeeper",
         "Gatekeeper", "Ashknight", "Castaway", "Lumen", "Skylancer", "Ascendant"]
print("| Set | Model | Common | Rare | Epic | Legendary | Grootste mesh | Meshes |")
print("|---|---|---|---|---|---|---|---|")
bad = []
for m in ORDER:
    p = os.path.join(HERE, "export", f"{m}.json")
    if not os.path.exists(p):
        continue
    j = json.load(open(p))
    t = j["tris"]
    print(f"| {j['name']} | {m} | {t['Common']} | {t['Rare']} | {t['Epic']} | {t['Legendary']} | {j['largestMesh'][0]} | {len(j['objects'])} |")
    if t["Legendary"] > 26000 or j["largestMesh"][0] > 5000:
        bad.append(m)
    for o in j["objects"]:
        c = o["center"]
        if max(abs(x) for x in c) > 3.5:
            bad.append(f"{m}:{o['object']} centre {c}")
print("problems:", bad)
