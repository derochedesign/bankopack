# Bankopack — Mod Plan

**Platform:** Minecraft **1.21.1** · **NeoForge** (21.1.240+). Java 21.
**Worldgen:** **Tectonic + Terralith** (replaces Tellus — see "Worldgen decision" below).
**Sinytra Connector: not needed.** Every Fabric-only mod on the list has a native NeoForge port, a datapack version, or a native replacement.

Researched 2026-10-07 against the Modrinth API + CurseForge. Source column: **MR** = Modrinth, **CF** = CurseForge-only.

---

## Worldgen decision

**Tellus was dropped** because of an open conflict with **Sable**, the physics library that Create Aeronautics and Propulsion depend on ([Tellus #42](https://github.com/Yucareux/Tellus/issues/42), [#56](https://github.com/Yucareux/Tellus/issues/56)). Its other limits went with it:
- vanilla-only overworld biomes
- no world creation on a dedicated server
- terrain data streamed live from the internet

**Tectonic** (mod version, NeoForge) has Terralith support built in, so no separate Terratonic datapack is needed. It works with TerraBlender biome mods, structure mods, Cobblemon and Distant Horizons.

### Tectonic config (current: `pack/config/tectonic.json`)
| Setting | Default | **Ours** | Why |
|---|---|---|---|
| Snow start offset | 128 | **256** | Snow line starts higher (from the video) |
| Vertical scale | 1.125 | **3.0** | Was 3.7 in the first playtest; group wanted it lower |
| Max build height (`max_y`) | 320 | **640** | Headroom above peaks for bigger ranges and building |
| Ocean offset | -0.8 | **-0.65** | First playtest spawned mid-ocean; more land, deep oceans still exist |

Measured peak heights for one mountain range (seed `bankopack`, 256×256 area, 16-block grid; `tools/measure.py`):

| Vertical scale | Median surface | Tallest point |
|---|---|---|
| 3.7 | Y 477 | Y 571 |
| **3.0** | **Y 401** | **Y 485** |
| 2.5 | Y 347 | Y 424 |

- **No floating islands:** Biome Replacer (`config/biome_replacer.properties`) removes Terralith's Skylands biomes (`#terralith:skylands > null`). Verified on the test server: `/locate biome #terralith:skylands` finds nothing. Delete that line to bring them back.
- Other knobs worth trying: `continents_scale` (lower = bigger continents), `erosion_scale` (lower = broader ranges), biome noise (large biomes).
- **Lock the config before the real world is created.** Changing terrain settings afterward leaves cliff seams where new chunks meet old ones.
- **Ocean monuments:** Tectonic sinks vanilla monuments 30 blocks (`monument_offset`) to match its deeper oceans, and the monument's water box cuts a sheer pit into the seabed. Re-check after YUNG's Better Ocean Monuments (Phase 5) replaces them.
- **DH while exploring:** LODs fill in as terrain generates. Pre-generate with `/dh pregen` (tab-complete for the arguments) instead of Chunky.
- **Create Aeronautics models air pressure by altitude.** Check how airships handle Y 400–640.

---|---|---|---|
| Snow start offset | — | **256** | 512 |
| Vertical scale | 1.125 | **3.7** | 2.5 |
| Increased height | off (Y −64→320) | **ON** (Y −64→640) | Y −64→768 |
| Continents scale (lower = bigger) | 0.13 | try 0.10 | 0.10 |
| Erosion scale (lower = broader ranges) | 0.25 | try 0.08–0.15 | 0.08 |
| Biome noise | default | try large_biomes (0.06) | 0.1 |

- At vertical scale 3.7 the peaks may clip against the 640 ceiling. Generate a test seed and fly the tallest ranges. If the tops are flat, raise `max_y` (the config takes custom min/max) or lower the scale.
- **Lock the config before the real world is created.** Changing terrain settings afterward leaves cliff seams at chunk borders.
- **Create Aeronautics models air pressure by altitude.** Check how airships handle Y 400–640 with the increased build height.

---

## Verdict on the original list

### ❌ Won't work — drop
| Mod | Why | Substitute |
|---|---|---|
| Tellus | Breaks Sable/Aeronautics | **Tectonic + Terralith** |
| Species | 1.20.1 only, no port | Friends & Foes (`friends-and-foes-forge`) |
| More Critters | 1.20.1 Forge only | Critters and Companions |
| Blue Skies | Newest is 1.20.4 (2024); no longer maintained | Covered by the other dimension mods (Eternal Starlight, Aether, Twilight Forest) |

### 🔁 Doesn't work as-is — replace with equivalent
| Original | Replacement (NeoForge 1.21.1) | Notes |
|---|---|---|
| Alex's Mobs | **Alex's Mobs 1.21.1 Port** (Raguto, CF) + Citadel | Unofficial; install only ONE port. Fallback: Naturalist |
| More Mob Variants | `more-mob-variants-modernized` (MR) | Small project — test |
| Simply Skills | **Skill Tree (RPG Series)** (`skill-tree`) — same family as Better Combat. Lighter alt: Pufferfish's Skills (`skills`) + default trees datapack | Skill Tree pulls in Spell Engine, Ranged Weapon API and Critical Strike |
| Construction Wand | `construction-wands-revived` (MR) | MIT fork of the original |
| Eating Animation (Fabric) | **Eating Animation Neo/Forge port** (matyrobbrt, CF) + GroovyModLoader | Native, no Connector |
| True Ending (no NeoForge 1.21.1 jar) | **True Ending datapack** (`true-ending-v1.1.2d.zip`, MR) loaded via Paxi/Open Loader | Alt: Ender Dragon Fight Remastered (`edf-remastered`) |
| Cobblemon Trainer Battle (Fabric only) | **Radical Cobblemon Trainers** (`rctmod` + `rctapi`) | Native NeoForge, actively updated |
| BetterNether / BetterEnd | **BetterNether: New Dawn** / **BetterEnd: New Dawn** (`-neoforge` slugs) | Need BCLib/WunderLib/WorldWeaver (neoforge) |
| Falling Leaves (Fabric) | `fallingleavesforge` (NeoForge port) | |
| Dynamic Lights | **LambDynamicLights** (needs Forgified Fabric API — a native NeoForge library, not Connector) | Alt: Sodium Dynamic Lights |
| Iris needs a renderer | **Sodium** (official NeoForge build) — not Embeddium (no updates since Jan 2025) | |

### ✅ Works natively — everything else
All other mods have current NeoForge 1.21.1 builds. Notes:
- **Simply Swords + Better Combat**: yes, Simply Swords ships Better Combat weapon attributes.
- **Apotheosis** on 1.21 is split into several mods (all needed): Apotheosis + Apothic Attributes + Apothic Enchanting + Apothic Spawners + Placebo + Patchouli.
- **Create Propulsion**: the 1.21.1 version is `create-propulsion-simulated` (built on Sable + Aeronautics).
- **Twilight Forest** and the **FTB mods** are CurseForge-only (TF 4.8.x; FTB 2101.x — all fine).
- **MTR** 4.1 is beta on 1.21.1. **Ad Astra** works (1.16.26, Sep 2026).
- **"Everything needed for Curios"**: Curios API (+ Caelus for Elytra Slot, + Gravestone x Curios compat).
- **Dynamic Trees** + Terralith has a compat addon: `dynamic-trees-terralith`.

---

## Phases

Each phase:
1. Add the phase's mods.
2. Launch the client and create a fresh test world.
3. Run the checklist.
4. Check `logs/latest.log` for errors.
5. Only then start the next phase.

Keep one long-running "real" test world too, to catch updates that break saves.

### Phase 0 — Foundation (worldgen, rendering, performance)
| Mod | Src | Role |
|---|---|---|
| Tectonic (+ Lithostitched) | MR | Terrain shape |
| Terralith | MR | ~100 biomes (Tectonic has built-in compat) |
| Distant Horizons | MR | LODs |
| Sodium | MR | Renderer |
| Iris Shaders | MR | Shaders (use a DH-compatible pack: Complementary, Bliss, etc.) |
| ModernFix, FerriteCore | MR | Startup time / memory |
| Lithium (NeoForge) | MR | Server tick perf (replaces Radium, which hasn't been updated since 2024) |
| ImmediatelyFast, Entity Culling | MR | Client perf |
| Spark | MR | Profiler — essential for diagnosing lag |
| ~~Chunky~~ | MR | **Removed after testing:** DH 3.3.3 + Chunky 1.4.23 crash the server during spawn generation (DH's Chunky hook calls Chunky before it has loaded). Use DH's own pregen for now and re-test Chunky on future DH updates |
| Xaero's Minimap + World Map | MR | Maps |
| JEI, Jade, AppleSkin | MR | Info overlays |
| Mod Menu (NeoForge Edition) | MR | Config access |

**Do not add:** C2ME (alpha on NeoForge), Moonrise (beta, replaces the chunk system), Radium, Embeddium.
**Checklist:**
- Tectonic config applied (increased height on, vertical scale 3.7).
- Fly the biggest mountain ranges and check for clipped peaks.
- DH LODs render to the horizon with shaders on.
- Chunk generation speed while flying fast (no pregen tool yet; see the Chunky note).
- Check FPS and RAM in spark.

### Phase 1 — Cobblemon + core QoL
**Cobblemon**
- Cobblemon (+ Kotlin for Forge)
- Radical Cobblemon Trainers (+ RCT API)
- Lootr + Lootrmon (Lootr × Cobblemon)

**Inventory & equipment**
- Curios API
- Traveler's Backpack
- Elytra Slot (+ Caelus)
- TrashSlot
- Crafting on a Stick

**Death**
- GraveStone Mod (+ Gravestone x Curios compat, which also needs **BaguetteLib**; its Modrinth page doesn't list it)

**Movement & interaction**
- Double Doors
- Jump Over Fences
- Harvest with Ease
- Construction Wands Revived
- **FTB Ultimine** (chosen over Veinminer, which would add a second Kotlin language library next to Cobblemon's)

**Visuals & UI**
- Dark Mode Everywhere
- Colorful Hearts
- 3D Skin Layers
- Falling Leaves (NeoForge port)
- LambDynamicLights (+ Forgified Fabric API)

**Utilities**
- Nature's Compass
- Fuel Goes Here
- Magnum Torch
- Enchantment Descriptions
- Grind Enchantments
- AI Improvements

**Server tools**
- FTB Library, Teams, Chunks and Essentials

**Checklist:**
- Pokémon spawn in Terralith biomes (Cobblemon tags cover many of them; check a few exotic ones).
- Trainers spawn.
- Backpack and curio slots work.
- Graves keep curios.

**Note:** FTB Chunks has its own minimap. Disable it in config and keep Xaero's.

### Phase 2 — Tech
**Create**
- Create
- Create Aeronautics (+ Sable)
- Create Propulsion: Simulated
- Sable Physics Compat

**Storage & machines**
- AE2
- Tom's Simple Storage
- Iron Furnaces
- Immersive Engineering
- Industrial Foregoing (+ Titanium)
- XNet (+ McJtyLib, RFTools Base)

**Transport**
- Immersive Aircraft
- Minecraft Transit Railway

**Space**
- Ad Astra (+ Resourceful Lib, Resourceful Config, Common Storage Lib)

**Compat adds:**
- **Almost Unified**: merges duplicate copper/lead/silver/etc. across Create, IE, IF, Ad Astra and Silent Gear.
- **Polymorph**: lets you pick between conflicting recipes.
- **Carry On** + its Aeronautics compat (optional).

**Checklist:**
- Ores from each mod generate (zinc, IE ores, AE2 meteorites).
- Create contraptions render with shaders on.
- An Aeronautics airship flies at high altitude.
- MTR trains run across mountain terrain.
- Ad Astra planets load.

### Phase 3 — Mobs, food, combat
**Mobs**
- Legendary Monsters
- Enderman Overhaul (+ GeckoLib)
- Nyf's Spiders
- Wither Skeleton Tweaks
- More Mob Variants Modernized
- Friends & Foes
- Critters and Companions
- Naturalist (optional)
- Alex's Mobs 1.21.1 Port (+ Citadel). *Add last in this phase; it's the riskiest.*

**Food**
- Farmer's Delight
- Mama's Herbs and Harvest
- Eating Animation (Neo port + GroovyModLoader)

**Combat**
- Better Combat (+ playerAnimator, Cloth Config)
- Simply Swords (+ Architectury, Fzzy Config, Simply Tooltips)
- Immersive Armors
- Relics (+ ShatterByte Lib)
- Skill Tree (RPG Series) (+ its deps)

**Checklist:**
- Better Combat swing animations and Eating Animation don't fight (both animate the player).
- Mob spawn density is sane. Many mob mods stack, so tune spawn weights.

### Phase 4 — Magic & gear
- Apotheosis (+ Apothic Attributes, Apothic Enchanting, Apothic Spawners, Placebo, Patchouli)
- Goety
- Mahou Tsukai
- EvilCraft (+ Cyclops Core)
- Silent Gear (+ Silent Lib)

**Checklist:**
- Apotheosis enchanting doesn't clash with Grind Enchantments or Enchantment Descriptions.
- Stat interactions between Apothic Attributes, Better Combat and Skill Tree behave.

### Phase 5 — Building & overworld structures
**Building**
- Chipped (+ Athena)
- Handcrafted
- Macaw's: Windows, Fences & Walls, Bridges, Doors, Roofs, Stairs, Trapdoors, Paths, Lights
- Rechiseled (+ Fusion) and Rechiseled: Create
- Glassential Renewed
- Exposure
- **Connected textures:** use **Fusion** (native; Rechiseled already requires it) plus Fusion resource packs: Fusion Connected Glass, Fusion Connected Blocks, Midnighttigger's Default Connected Textures. *Continuity* is not an option: its NeoForge 1.21.1 build requires Sinytra Connector.

**Structures**
- YUNG's API
- YUNG's Better: Mineshafts, Strongholds, Ocean Monuments, Desert Temples, Jungle Temples, Witch Huts, Dungeons
- YUNG's Extras, Bridges, Menu Tweaks, **Cave Biomes** (works again without Tellus)
- *Optional:* Dynamic Trees + Dynamic Trees: Terralith (TPS cost; test)

**Checklist:**
- Structures sit well on steep Tectonic terrain.
- Villages aren't spawning on cliffs (if they are, add *Improved Village Placement*).

### Phase 6 — Dimensions & sky
**Nether & End**
- BetterNether: New Dawn and BetterEnd: New Dawn (+ BCLib, WunderLib, WorldWeaver)
- YUNG's Better Nether Fortresses and Better End Island
- True Ending (datapack)

**Other dimensions**
- Deeper and Darker
- Eternal Starlight
- Twilight Forest (CF)
- The Bumblezone
- The Aether and Deep Aether (+ TerraBlender)

**Sky**
- Enhanced Celestials

**Don't add** Incendium or Nullscape: they rework the same dimensions as BetterNether and BetterEnd.
**Checklist:**
- Each portal works.
- DH renders in each dimension.
- The dragon fight works: BetterEnd, YUNG's End Island and True Ending all touch the End.

### Phase 7 — Immersion (all native NeoForge 1.21.1)
**Sound**

| Mod | What it adds | Notes |
|---|---|---|
| **AmbientSounds** (+ CreativeCore) | Biome/time/weather/cave ambience | Updated Oct 2026 |
| **Sound Physics Remastered** | Reverb in caves, sound muffled by walls | Some CPU cost; tune reverb |
| Create: Sound of Steam | Better Create machine sounds | |

**Visual atmosphere**

| Mod | What it adds | Notes |
|---|---|---|
| **Particle Rain** | Rain/snow particles, splashes, fog in storms | |
| **Subtle Effects** | Lots of small ambient particles (fireflies, steam, sparks…) | Updated today |
| Better Clouds (+ YACL) | Volumetric-looking clouds | Pick one: shaders may already handle clouds |

**Animation & first-person**

| Mod | What it adds | Notes |
|---|---|---|
| **Entity Model Features + Entity Texture Features** | Required for the **Fresh Animations** resource pack (mobs blink, breathe, move naturally) | Fresh Animations is a resource pack, not a mod |
| Not Enough Animations | Third-person animations for maps, eating, ladders | Test alongside Better Combat |
| First-person Model | See your own body in first person | Test alongside Better Combat / Eating Animation |

**World & seasons**

| Mod | What it adds | Notes |
|---|---|---|
| **Serene Seasons** (+ GlitchCore) | Seasons: color shifts, snow, crop seasons | Interacts with Farmer's Delight / Mama's crops |
| Snow! Real Magic! | Snow layers on plants, fences, etc. | |

**UI & small touches**

| Mod | What it adds | Notes |
|---|---|---|
| Chat Heads | Player heads in chat | |
| Legendary Tooltips | Fancier item tooltips | Simply Swords has its own tooltips; check overlap |
| Visual Workbench | Items stay on the crafting table | |

Not available on NeoForge 1.21.1: Presence Footsteps, Wakes, Visuality, Extra Sounds (Fabric only), and Dynamic Surroundings.

### Phase 8 — Optional / later
- Dynamic Trees (if not done in Phase 5)
- Waystones (fast travel across very big terrain)
- Alex's Caves (unofficial port)

---

## Resource budget
Your PC: Ryzen 7 3700X, 32 GB RAM, RTX 3070 Ti → give the client **10–12 GB** heap. For a dedicated server with this list: 8–10 GB. Pregenerate with Chunky. Tectonic at vertical scale 3.7 with the higher build limit is noticeably slower to generate than vanilla.
