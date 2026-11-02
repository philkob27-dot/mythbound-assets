# De 15 nieuwe armorsets in Blender (2 november)

Alle 15 sets uit NEW_CONTENT_DESIGN_2NOV.md (sectie 2) zijn gemodelleerd, geëxporteerd en bekeken op een blokkige R15 dummy. Niets is in Studio veranderd; alles staat klaar om te importeren.

Overzicht van alle sets naast elkaar: `review/lineup_sets15.png`. Per set is er een reviewblad met voor, achter, twee keer driekwart (Legendary) en een driekwart van de Common versie: `review/<Set>_review.png`.

## Wat er per set in zit

Elke set volgt de huisstijl van de gear: lagen stof, leer en plaat, een accentstof, trim op de randen, een hangende familie (capes, linten, kralen, veren, tasjes), het embleem op borst, riem of knie, glow pas vanaf Epic en een hoofd dat de helft van het verhaal vertelt. Watcherstone, Lumen Warden en Eyrie Ascendant zijn symmetrisch; de rest niet.

- **Accord Envoy:** zeegroene mantel met parelknopen, kraag van schelpjes, sjerp met drie zegels, diplomatentas met lakzegels op de rechterheup, schelpschouder links.
- **Kelpfarmer:** oliejas, brede strohoed met drijvers, sikkel aan de riem, mand met kelp op de rug, rubberlaarzen tot het dijbeen.
- **Storm Caller Regalia:** hoge kap met koperen spoelen, cape die in regenrafels eindigt, glazen bollen aan de riem, lege stafkoker op de rug.
- **Bogwitch:** geitenschedel met rieten vlechten, omslagdoek vol kruidenzakjes, ketel op de heup, botkettingen.
- **Watcherstone:** stenen platen met mos in de naden, glad stenen masker, groene glazen oogsteen op de borst, stenen ogen op de knieën.
- **Thunderhead Climber:** leren vliegerskap met windbril, klimharnas met karabiners, touw over de schouder, veren op de schouders, klauwhandschoenen.
- **Midnight Racer:** wijnrode racezijde, windkap met vizier, groot nummer 07 op de rug, linten aan de schouders.
- **Ledgerwarden:** grijze archivarismantel, kettingslot met hangslot om het middel, sleutelbos, leeslamp op de rechterschouder, inktvlekken op de handschoenen, groot grootboek op de rug.
- **Coral Songkeeper:** koraalkroon, parelsnoeren voor het gezicht, rok en rug van zeewierstroken, schelphoorn op de heup.
- **Abyss Gatekeeper:** parelmoeren platen, borstplaat als poort met slot, kreeftschouders met een schaar links, cape van kelp.
- **Ashfall Knight:** verbrande ridderplaat, gebroken lans als embleem, halve geschroeide cape links, as op de schouders, grandguard.
- **Castaway:** zeildoek en touw, ribbenkooi als borstplaat, schedeltje aan de riem, blote enkels met touw, klein zeiltje op het hoofd (Legendary).
- **Lumen Warden:** wit en goud, glad masker zonder mond, gouden ring achter het hoofd, groene runelijnen, lange gewaden.
- **Sky Lancer:** gouden duikhelm met kam, smalle vleugelplaten op de schouders, zon met lans als embleem, lange rijlaarzen met sporen.
- **Eyrie Ascendant:** botplaten over pelgrimswol, verenmantel, trap van botten naar een oog op de kap, gouden klauwen aan de laarzen.

## Driehoeken

Totaal per volledige outfit, opgeteld tot en met die rarity. Het budget was 26.000 voor Legendary en 5.000 voor de grootste losse mesh; elke set blijft daar ruim onder.

| Set | Model | Common | Rare | Epic | Legendary | Grootste mesh | Meshes |
|---|---|---|---|---|---|---|---|
| Accord Envoy | Envoy | 2284 | 7620 | 8056 | 8776 | 1364 | 80 |
| Kelpfarmer | Kelpfarmer | 1996 | 4200 | 4500 | 4832 | 280 | 69 |
| Storm Caller Regalia | Stormcaller | 2560 | 6108 | 6440 | 6760 | 564 | 68 |
| Bogwitch | Bogwitch | 2612 | 6488 | 6592 | 7468 | 400 | 71 |
| Watcherstone | Watcherstone | 2084 | 4548 | 5060 | 5500 | 472 | 93 |
| Thunderhead Climber | Climber | 2088 | 5208 | 5356 | 5696 | 308 | 101 |
| Midnight Racer | Racer | 1932 | 4216 | 4472 | 4544 | 708 | 58 |
| Ledgerwarden | Ledgerwarden | 2964 | 6376 | 6448 | 6908 | 896 | 65 |
| Coral Songkeeper | Songkeeper | 2960 | 8746 | 9174 | 9918 | 864 | 69 |
| Abyss Gatekeeper | Gatekeeper | 2776 | 5512 | 5692 | 6012 | 388 | 71 |
| Ashfall Knight | Ashknight | 2280 | 4796 | 4868 | 4996 | 288 | 67 |
| Castaway | Castaway | 3556 | 5866 | 5950 | 6098 | 1148 | 71 |
| Lumen Warden | Lumen | 2524 | 4816 | 5188 | 5792 | 528 | 79 |
| Sky Lancer | Skylancer | 1872 | 4020 | 4156 | 4588 | 304 | 78 |
| Eyrie Ascendant | Ascendant | 2876 | 6756 | 7356 | 7796 | 360 | 92 |

## Waar de bestanden staan

In de repo mythbound-assets onder `gear/sets15/`:

- `export/<Set>.fbx`: alle meshes van de set, standaard FBX-assen (Y omhoog, voorkant -Z).
- `export/<Set>.json`: manifest per mesh (slot, lichaamsdeel, rarity, sway, kleur, materiaal, glowkleur, midden en maat in studs ten opzichte van het lichaamsdeel, en het referentielichaamsdeel).
- `export/<Set>_GearMeshes.luau`: de entries voor GearMeshes, klaar om te plakken.
- `export/<Set>.blend`: het Blender-bestand met de dummy erbij.
- `export/GEARKIT_SOLID_PATCH.luau`: de drie kleine code-aanpassingen die nodig zijn (zie hieronder).
- `scripts/`: de kit `mbkit2.py`, een script per set (`set_<id>.py`), `lineup.py` en `summary.py`. Een set opnieuw bouwen: `python3 set_<id>.py` (bpy als Python-module).
- `review/`: de reviewbladen en de lineup.

## Hoe het in elkaar zit

Namen volgen het bestaande patroon: entry `Armor_<Model>_<Stuk>` met de stukken Helm, Chest, Belt, PauldronL/R, BracerL/R en GreaveL/R, plus drie nieuwe soorten stukken: GloveL/R (handen), ThighL/R (bovenbenen) en BootL/R (voeten). Zo buigt alles met het juiste gewricht. Capes zitten in de Chest-entry (UpperTorso), rokken, tassen en tassets in de Belt-entry (LowerTorso).

Een MeshPart in de FBX heet `Armor_<Model>_<Stuk>_<Kleur>[Sway]_<Rarity>`, bijvoorbeeld `Armor_Envoy_Chest_MantleSway_Common`. Dat is precies wat GearKitSetup zoekt (entrynaam plus partnaam). Glow is een eigen part, `..._Glow_Epic` of `..._Glow_Legendary`.

Anders dan de oude sets hebben deze meshes geen palet-texture. Elk part heeft een eigen kleur en materiaal (role "solid" in de entry), en een rarity: het part is zichtbaar vanaf die rarity. Een Common item toont dus alleen de Common parts, een Legendary alles.

## Importeren in Studio

1. Importeer de 15 FBX-bestanden: File > Import 3D per bestand, of in een keer via Asset Manager > Bulk Import. Standaardinstellingen zijn prima; de schaal maakt niet uit, de maten komen uit het manifest.
2. Zet de drie aanpassingen uit `GEARKIT_SOLID_PATCH.luau` in de code: vier optionele velden in het type MeshPart van GearMeshes, een tak voor role "solid" in GearKitSetup, en een optionele rarity in GearFit.build.
3. Plak de inhoud van elk `<Set>_GearMeshes.luau` in de tabel M van ReplicatedStorage.Shared.data.GearMeshes.
4. Draai in de command bar `require(game.ServerStorage.DevTools.art.GearKitSetup).run({ cleanup = true })`. Die zoekt elke MeshPart op naam, zet maat, positie, kleur en materiaal, en zet per entry een Model `Armor_<Model>_<Stuk>` in ReplicatedStorage.LookKit. Wie het met de hand doet: dezelfde structuur, een Model per entry met de MeshParts erin, hernoemd naar de partnaam (bijvoorbeeld `Robe_Common`).
5. Voeg de sets toe in Gear.luau. De helper set() maakt nu negen modellen per set; de nieuwe sets hebben er meer. De lijst per slot staat in de vierde regel van elk luau-bestand ("Pieces per slot").

## Eerlijke kanttekeningen

- Niet in Studio getest; ik had alleen leestoegang. De eerste import is dus ook de eerste echte test. Kijk vooral of GearKitSetup "axes swapped" meldt; dat zou betekenen dat de importer de assen anders draait dan bij de oude gear-FBX.
- De dummy gebruikt de referentiematen uit GearMeshes, maar waar de delen precies zitten heb ik zelf gestapeld. Per lichaamsdeel klopt het, de aansluiting tussen bijvoorbeeld dijplaat en scheenplaat kan in Studio een fractie anders uitvallen.
- Sway-parts hangen nog vast aan hun lichaamsdeel. Ze zijn wel apart gehouden zodat er later beweging op kan.
- De Mythic-herkleuringen uit het ontwerp zijn niet gemaakt.
- Goud en donker metaal ogen in de renders donkerder dan ze in Roblox zullen zijn (het metaal weerkaatst de grijze achtergrond).
- Lange rokken en mantels zitten vast aan de LowerTorso of UpperTorso; bij lopen steken de benen erdoorheen, net als bij de bestaande sets.
