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

### Seeds worth keeping (full list + config snapshots in `seeds/`)
- `3128558057160963598`: the group liked it in the Phase 2 playtest. It's now the test server's seed for terrain comparisons. Terrain will differ slightly if Tectonic settings change before the real world is made.

### Tectonic config (current: `pack/config/tectonic.json`)
| Setting | Default | **Ours** | Why |
|---|---|---|---|
| Snow start offset | 128 | **256** | Snow line starts higher (from the video) |
| Vertical scale | 1.125 | **2.75** | 3.7 → 3.0 → 2.75 over playtests; compromise between height and sheer range edges |
| Max build height (`max_y`) | 320 | **640** | Headroom above peaks for bigger ranges and building |
| Ocean offset | -0.8 | **-0.65** | First playtest spawned mid-ocean; more land, deep oceans still exist |

Measured peak heights for one mountain range (seed `bankopack`, 256×256 area, 16-block grid; `tools/measure.py`):

| Vertical scale | Median surface | Tallest point |
|---|---|---|
| 3.7 | Y 477 | Y 571 |
| **3.0** | **Y 401** | **Y 485** |
| 2.5 | Y 347 | Y 424 |

- **No floating islands:** Biome Replacer (`config/biome_replacer.properties`) removes Terralith's Skylands biomes (`#terralith:skylands > null`). Verified on the test server: `/locate biome #terralith:skylands` finds nothing. Delete that line to bring them back.
- **Less spiky mountains:** `erosion_scale` 0.25 → **0.10** and `ridge_scale` 0.25 → **0.15** (broader ranges, same height). Measured on seed `3128558057160963598`: average slope 20 → 11 blocks per 16, cliff-like steps (32+ blocks) 20% → 4%, worst single drop 167 → 55. `ultrasmooth` made no measurable difference, so it stays off (its config warns about broken deep oceans).
- **Terrain mix retune ("gradual build-up" toward big peaks, inspired by Tellus/JJThunder).** Measured with `/bankopack terrainstats 8192 256` (noise-only samples over a 16k×16k area, seed `3128558057160963598`). Land share by height above sea:

  | Config | Ocean | Flat 0–20 | Low hills 20–60 | Hills 60–140 | Highlands 140–250 | Mountains 250+ | Max Y |
  |---|---|---|---|---|---|---|---|
  | old (erosion 0.10, flat_skew 0.1, elev_boost 0, ocean −0.5, continents 0.13) | 57% | 36.9% | 13.0% | 15.8% | 16.5% | 17.8% | 500 |
  | **new (erosion 0.20, flat_skew −0.2, elev_boost −0.3, ocean −0.46, continents 0.08)** | 48% | 33.4% | 12.8% | 22.4% | 19.9% | 11.5% | 467 |

  - Negative `elevation_boost` holds back mountains relative to lowlands.
  - Lower `continents_scale` gives longer coast-to-mountain ramps.
  - `ocean_offset` must stay ≤ −0.45 or deep oceans (and ocean monuments) stop generating. Verified at −0.46: deep ocean and YUNG's monuments still `/locate`.
  - `erosion_scale` and `flat_terrain_skew` alone barely change the mix.
  - Trade-off: slopes are slightly steeper than with erosion 0.10.
- **Range-edge cliffs** (e.g. lowland → mountain in `terralith:arid_highlands`) come from the vertical stretch, not plateaus. On seed `3128558057160963598`, the share of near-vertical steps (24+ blocks rise per 8 blocks) at that spot was 6.6% at scale 3.0, 5.3% at 2.75 and 4.5% at 2.5. `flat_terrain_skew` 0.5 didn't help there and made badlands steeper, so it stays at 0.1. Measured with `tools/terrainstats.py`.
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
| More Mob Variants | ~~`more-mob-variants-modernized`~~ **dropped**: broken on 1.21.1 (1.21.5+ data format) | Vanilla wolf variants only |
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
- **Pro Placer**: reach-around placement (place blocks under/behind the block you're standing on) + Bedrock-style accurate placement. Client-only.
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
- **Carry On** + its Aeronautics compat (optional, not added).
- Added: Default Options (ships default keybinds). Note: Sable: Physics Compat logs one Aether-related data error; re-check in Phase 6 when Aether is added.

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

**Phase 3 build notes:**
- **Dropped More Mob Variants Modernized:** its "1.21.1" build ships 1.21.5+ wolf-variant data and stops the world from loading. Vanilla 1.21.1 already has wolf variants.
- **Added Spell Power Attributes:** Skill Tree and Spell Engine require it, but it isn't declared on Modrinth.
- **Naturalist left out:** too much overlap with Alex's Mobs.
- **Combat rework (after playtest):** removed Better Combat (cosmetic; ReArm reworks swords directly, so the two would collide). Added **Combat Roll** (dodge), **ReArm** (bow/crossbow/sword/axe/shield mechanics + armor/protection rebalance), **Zombie Improvements**, **Simple Mob Buff System**.
- **Iron's Spells 'n Spellbooks** added; it needs **Iron's Lib 2.x** (pinned 1.21.1-2.2.0), which isn't declared on Modrinth.
- **Class-based combat (RPG Series):** Wizards, Paladins & Priests, Rogues & Warriors, Archers, Jewelry, plus community classes Berserker, Forcemaster, Witcher, Elemental Wizards and Bard (More RPG Library). Skill Tree (RPG Series) is built for these classes. Death Knights has no NeoForge 1.21.1 build.
- **Better Combat is back:** the classes need it for dual-wielding and two-handed weapons. ReArm's sword changes are switched off in `config/rearm/config.toml` so they don't conflict; its bow, crossbow, axe, shield and armor features stay on.
- **Spell Engine pinned to 1.10.7** (`packwiz pin`): Witcher 3.1.4 crashes on 1.10.8+ (`NoSuchMethodError` in `LootHelper.configure`). Unpin once Witcher updates.
- **Iron's Spells stays** as a second, separate magic path, with its own mana and spellbooks.
- **Harmless log noise:** Bard recipes for BetterEnd's aeternium; these resolve once BetterEnd is added in Phase 6.
- **Keybind watch:** ReArm's action key defaults to Left Alt, the same as Cobblemon's riding free-look. Combat Roll and Iron's add keys too, so capture them in Default Options.
- **Harmless log noise:** Simply Swords recipe errors for Mythic Metals (an optional mod we don't have).

**Checklist:**
- Better Combat swing animations and Eating Animation don't fight (both animate the player).
- Mob spawn density is sane. Many mob mods stack, so tune spawn weights.

### Phase 4 — Magic & gear
- Apotheosis (+ Apothic Attributes, Apothic Enchanting, Apothic Spawners, Placebo, Patchouli)
- Goety
- ~~Mahou Tsukai~~ (dropped by group decision)
- EvilCraft (+ Cyclops Core)
- Silent Gear (+ Silent Lib)

**Checklist:**
- Apotheosis enchanting doesn't clash with Grind Enchantments or Enchantment Descriptions.
- Stat interactions between Apothic Attributes, Better Combat and Skill Tree behave.

**Phase 4 build notes:** added Apotheosis (+ Apothic Attributes / Enchanting / Spawners, Placebo, Patchouli), Goety, EvilCraft (+ Cyclops Core). Boots clean. **Silent Gear removed** after playtest (group didn't want it; nothing depended on it). Harmless log noise: Silent Gear recipes for Woodcutter / Bonsai Trees (not installed) and one Farmer's Delight × Silent Gear cutting recipe.

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

**Phase 5 build notes:**
- **Added:**
  - Chipped (+ Athena), Handcrafted
  - Macaw's Windows / Fences & Walls / Bridges / Doors / Roofs / Stairs
  - Rechiseled + Rechiseled: Create, Fusion, Glassential Renewed, Exposure
  - YUNG's API, Better Mineshafts / Strongholds / Ocean Monuments / Desert Temples / Jungle Temples / Witch Huts / Dungeons, Extras, Bridges, Menu Tweaks (client-only), Cave Biomes
- **TerraBlender added:** YUNG's Cave Biomes needs it, but it isn't declared on Modrinth.
- **Every YUNG's structure type `/locate`s** in the Tectonic world (test seed). Still to do: playtest how they sit on steep terrain.
- **Crit-tuning fix:** Apotheosis requires affix ranges in whole 0.01 steps, so the scaled values are rounded (Bankopack Tweaks 1.3.1).

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

**Phase 6 build notes:**
- **Added:**
  - BetterNether / BetterEnd: New Dawn (+ BCLib, WunderLib, WorldWeaver)
  - YUNG's Better Nether Fortresses + Better End Island
  - Deeper and Darker, Eternal Starlight, The Bumblezone
  - The Aether + Deep Aether (+ owo-lib)
  - Twilight Forest (CF)
  - Enhanced Celestials (+ CorgiLib, Data Anchor)
- **True Ending** ships as a datapack, loaded globally by **Paxi**. `pack.toml` sets `datapack-folder = "config/paxi/datapacks"`, so packwiz puts datapacks there. Confirmed in `/datapack list`.
- **Roguelike runs: The Birth of Steve, REMOVED for now (revisit later).** Playtest: the journal tabs (Story / Archive Run / Abilities) don't switch, and the Extract/Continue choice never appeared, so a floor's reward cache stays sealed and runs can't be finished. It's v0.10 and young. To re-add: `packwiz mr add https://modrinth.com/mod/the-birth-of-steve/version/<neoforge id>`; our Bankopack Tweaks placement fixes still apply (inert while it's absent). Original notes: **The Birth of Steve** (`tbos`, pinned to the NeoForge 0.10.1 build; plain `packwiz mr add` grabbed an old Fabric jar). Opt-in: an adventure leads to *Echoes of the Past*, a replayable procedural multi-floor dungeon dimension.
  - You bring your own gear; loot is per player.
  - Scaling: `healthPerDifficulty` / `damagePerDifficulty` in `config/tbos-common.json`. Raise these if it's too easy with modded gear.
- **Harmless log noise:**
  - BetterEnd/BetterNether Patchouli guidebooks fail to load (old book format).
  - BCLib "failed fixing level.dat" on brand-new worlds.
  - Bumblezone compat entries for Goety and Legendary Monsters entities.
- **Removed YUNG's Better End Island:** its own page rates True Ending "not recommended", and in testing the 4 summoning crystals in its central tower stayed invulnerable and kept healing the dragon. True Ending was the group's explicit pick.
- **Traversal (after playtest, for the steep terrain):** **Paragliders** (glide down; campfire updrafts) and **Yori3o's Grappling Hooks** (material-tiered hooks, climb ropes, Sable-compatible). Waystones rejected (everyone would skip other travel); ParCool rejected (too invasive).
- **Content additions (gameplay-gap review):**
  - **Towns and Towers** (+ Cristel Lib), **When Dungeons Arise**, **L_Ender's Cataclysm** (+ Lionfish API). Every Cataclysm boss structure `/locate`s in its dimension, including the Ruined Citadel despite BetterEnd.
  - Frosted Prison was about 20k blocks away (Terralith makes snowy plains rare); Bankopack Tweaks 1.7.1 adds snowy taiga, ice spikes and Terralith wintry lowlands, snowy shield and wintry forest to `#cataclysm:has_structure/frosted_prison_biomes`, bringing it to about 9.6k.
  - **Cobblemon: Mega Showdown 1.2.0** (built for Cobblemon 1.8.1; pinned, since 1.3.0 needs Cobblemon 1.8.2). It brings **Accessories**, a second accessory system next to Curios.
- **Cataclysm boss tuning** (`pack/config/cataclysm-common.toml`, server-side): every boss's `damage_cap` ×1.5 and `dps_cap` ×2 (Ignis 20/14 → 30/28). Boss `health_multiplier` ×1.25 (Ignis 450 → 562.5 HP); Ignis life steal `healing_multiplier` 1.0 → 0.5; nature heal unchanged. The default caps were built for near-vanilla gear, and the DPS cap is shared, so groups didn't kill any faster.
  - Boss music plays on the **Jukebox/Note Blocks** slider (not Music); set that to about 30% in the Default Options capture.
  - Ignis tips: hit him from the side or behind (his shield blocks frontal melee), knock his blue Abyss fireballs back to break the shield (3 hits), and don't hit during his counter stance.
- **Added Gateways to Eternity** (wave-based arenas opened with Gate Pearls; by the Apotheosis author). Replaces Birth of Steve as the opt-in "test your gear" activity.

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

**Phase 7 build notes:**
- **Added:**
  - AmbientSounds (+ CreativeCore), Sound Physics Remastered, Create: Sound of Steam
  - Particle Rain, Subtle Effects
  - EMF + ETF + **Fresh Animations** (resource pack in `pack/resourcepacks/`; enable it in Resource Packs, then capture it in Default Options so new players get it on)
  - Not Enough Animations, First-person Model
  - Serene Seasons (+ GlitchCore), Snow! Real Magic! (+ Kiwi)
  - Chat Heads, Legendary Tooltips (+ Iceberg, Prism), Visual Workbench
- **Phase 7 playtest tweaks:**
  - Subtle Effects frosty breath: `seasons = "OFF"` (with Serene Seasons, the default showed breath in every biome during late autumn, winter and early spring, and new worlds start in early spring). Own breath is still shown, but only in actually cold biomes.
  - Subtle Effects item rarity particles → `NOT_COMMON` (every dropped item sparkled white; now only uncommon+ loot sparkles).
  - Sound Physics `reverb_gain` 1.0 → 0.55 and `default_block_reflectivity` 0.5 → 0.35 (small rooms sounded like caves).
  - Added **Mouse Tweaks** (shift-drag and scroll item moving, like ATM10).
  - The configs are shipped in `pack/config/` and overwrite players' copies on sync.
- **First-person Model REMOVED:** its body model lunges forward during Better Combat attacks while the camera stays fixed (you see your own neck/body move). Better Combat's own first-person animations are used instead.
- **Better Combat client config shipped** (`config/bettercombat/client.json5`): crosshair highlight off, `firstPersonAnimations = AUTO`.
- **Performance pass (spark profiles in a jungle):**
  - Main costs: shaders (Iris, ~15%, mostly the shadow pass), DH (~8%), Cobblemon models (~8%), Xaero World Map + Minimap (~7%), Subtle Effects (~5%). Phase 7 overall is ~8%.
  - The F3 screen alone cost ~11% of each frame, so don't judge FPS with F3 open.
  - Jungle fixes: added **More Culling** (hidden leaf faces aren't drawn; client-only) and Falling Leaves `leafSpawnRate` 10 → 4 (shipped config).
  - Profile analysis scripts live in the session scratchpad; spark's "Sources" view gives the same per-mod breakdown.
- **Enhanced Celestials 2 join prompts:**
  - Added **EC2 Shader Support** (client-only), so lunar-event moon colours work with Iris.
  - Shipped `config/enhancedcelestials2core/translations.json` with `Translation_Mode = DISABLED`. This hides the "/ecc translate config" prompt and stops the translation download that caused the HTTP timeouts in logs; English is built in.
- **Better Clouds skipped:** Complementary draws its own clouds.
- **Client-only mods** are marked automatically by packwiz from Modrinth's metadata.
- **Harmless log noise:** an HTTP connect timeout from an update check.

### Phase 8 — Optional / later
- Dynamic Trees (if not done in Phase 5)
- Waystones (fast travel across very big terrain)
- Alex's Caves (unofficial port)

---

## Multiplayer server (the pack's end goal)
The pack is built to run on a dedicated server. Every phase is boot-tested on `testserver/`, and client-only mods are marked `side = "client"` so the server skips them.

- **World settings live on the server.** Tectonic's and Biome Replacer's configs are server-side, so terrain comes out the same for everyone. Lock them before the real world is generated.
- **Distant Horizons on the server:** DH can generate LODs on the server and send them to players. That makes the long-range view far smoother for friends exploring new terrain. Pre-generate with `/dh pregen` before opening the server.
- **Server RAM:** about 8–10 GB for this mod list, more as phases add up.
- **Getting the pack to friends:**
  1. Push this repo to GitHub.
  2. Each friend creates a Prism instance whose pre-launch command points `packwiz-installer-bootstrap` at the repo's `pack.toml` URL.
  3. Every launch then auto-updates their mods, the same way it works for you now.
  The other route is a `.mrpack` export, but CurseForge-only mods (the FTB mods, Twilight Forest) can't be bundled in one.
- **Default keybinds:** the Default Options mod ships our conflict-free keybinds to new players. It applies on first launch only, so anyone can still rebind afterward.
- **Claims and protection:** FTB Chunks (claims + force-loading), FTB Teams, FTB Essentials (homes, TPA, etc.).
- **Hosting:** TBD (rented host vs. a home PC). Decide before Phase 6 or so.

---

## Custom mods (source in `mods-src/`)
### Bankopack Tweaks (`bankopack`, source in `mods-src/bankopack`)
A client-only mod. Config: `config/bankopack-client.toml`.
- **Per-dimension shaders:** turns Iris shaders off in listed dimensions and back on when you leave. It only re-enables shaders it turned off itself, and does nothing if Iris isn't installed.
  - Why: shader packs draw their own sky over Ad Astra planets (overworld clouds, a second sun). The existing per-dimension shader mods are Fabric 1.21.11 only.
  - `[shaders] dimensions = ["ad_astra:*", "the_bumblezone:the_bumblezone", "eternal_starlight:starlight"]`: use full IDs (`ad_astra:moon`) or `namespace:*`. Shipped in `pack/config/bankopack-client.toml`; shaders render the Bumblezone and Eternal Starlight far too dark.
- **JEI mod aliases:** `@rpg` in JEI lists items from every RPG Series mod (classes, community classes, Jewelry, Spell Engine, Runes, Skill Tree). This uses JEI's `addModAliases` API.
  - `[jei] mod_aliases = ["rpg=wizards,paladins,..."]`: add more groups as `alias=modid1,modid2`. Restart the game after editing.
- **Simply Swords → Skill Tree weapon branches (data):** all 133 Simply Swords weapons are added to `minecraft:swords` / `rpg_series:weapon_type/*` tags, so Skill Tree's weapon branches recognise them. They're sorted by name keyword, then by Better Combat archetype:
  - longsword, katana, rapier, chakram → sword
  - claymores, lichblades, heavy uniques → claymore
  - greataxe → double_axe
  - greathammer, Mjolnir → hammer
  - glaive, warglaive, halberd, twinblade, scythe → glaive
  - spear → spear
  - sai → dagger
  - cutlass → sickle
  - Regenerate with `tools/gen_simplyswords_tags.py <simplyswords.jar> src/main/resources` after Simply Swords updates. Verified with `execute if items` on the test server.
- **Crit tuning (data + config):** the pack has two independent crit systems, Critical Strike (RPG Series) and Apothic Attributes (Apotheosis), so both are toned down:
  - Critical Strike innate crit: 5% → **2%** (`pack/config/critical_strike/server_config.json`).
  - *Critical Hit* enchantment: 4% → **3%** per level.
  - Apotheosis *Intricate* affix and *Samurai* gem crit values ×**0.75** (perfect Samurai: 50% → 37.5%).
  - The enchantment, affix and gem values are overridden by this mod's data, which loads after Apotheosis and Critical Strike. Regenerate with `tools/gen_crit_tuning.py <mods dir> src/main/resources`. In-game check: Critical Hit III should show +9% (was +12%).
- **Fix: The Birth of Steve archive buried at the bottom of the world (mixin).** Using the Archive Survey Map builds the Meridian Archive about 384 blocks away via `AdventureWorldManager.findDrySurface`, which calls `level.getHeight`. For unloaded chunks vanilla returns the world's minimum height, so the archive landed at about Y -63. `mixin/tbos/AdventureWorldManagerMixin` redirects both `getHeight` calls to load the chunk first. It's optional (`required: false`), so it's a no-op if TBoS is absent, and it was verified applied on the dedicated server via `-Dmixin.debug.export=true`. Already-placed archives don't move; on an affected world they stay at the bottom.
- **Fix: TBoS shrines and archive placed on water (mixin, 1.5.0).** The original `findDrySurface` tries only 12 spots within ±24 blocks and then falls back to the target even if it's water. Our `@Inject` at HEAD searches rings out to 256 blocks using `ChunkGenerator.getBaseHeight(OCEAN_FLOOR_WG)` (noise only, no chunk generation) for ground above sea level, then loads just that chunk and checks for surface water. This also replaces most of the 1.4.0 chunk loading that caused a ~10 s hitch on first Survey Map use. If no land is found, it falls back to the original logic (still covered by the redirect).
- **TBoS gameplay notes (by design):**
  - Cantor Cache chests stay sealed until the floor's lesser warden or guardians are defeated ("%s still binds this seal").
  - The in-run **Waystone** binds your floor checkpoint and sends you out; "Your Archive run is already active" means rejoin through a Waystone, not the Lens. Waystones are craftable (Chronicle Bronze + 3 Archive Stone + Lenswork Crystal).
- **`/bankopack terrainstats <radius> <step>`** (op, 1.6.0+): samples terrain height from the generator's noise (no chunk generation) and reports ocean / flat / hills / highlands / mountains shares and local relief. The mod now runs on the server too; its client-only parts still only load on clients.
- **Build:** `cd mods-src/bankopack && ./gradlew build`, then copy `build/libs/bankopack-<version>.jar` into `pack/mods/` (removing the old jar) and run `packwiz refresh`.
- **History:** v1.0.0 was named `dimshaders` (shader switching only).
---

## Quest book (FTB Quests)
- **Source of truth:** `quests/build_quests.py` (readable Python spec) generates `pack/config/ftbquests/quests/` (chapters, `lang/en_us.snbt` for all text, `data.snbt`).
- **Validation:** every task/reward ID is checked against a registry built by `quests/collect_ids.py` from all mod jars, including nested jar-in-jar mods. Unknown IDs fail the build.
- **Regenerate:** `python quests/collect_ids.py <instance>/mods ids.json` (plus vanilla IDs), then `python quests/build_quests.py ids.json pack/config/ftbquests/quests`, then `packwiz refresh`.
- **Design:** 7 independent, optional chapters (Welcome, Pokémon, Create & Flight, Classes & Magic, Gear & World Tiers, Beyond the Overworld, Bosses). No cross-chapter gating, so any system can be ignored. Small rewards.
- **Status:** verified on the test server ("Loaded 7 chapters, 63 quests"). In-game edits made with FTB's editor would be overwritten by the next generated sync, so change `build_quests.py` instead, or switch to hand-editing the SNBT files and retire the generator.

---

## Side packs
### Worldgen tests (never shipped to players)
For comparing other big-terrain generators with DH + Iris. Each has DH, Sodium, Iris, ModernFix, FerriteCore, Lithium, ImmediatelyFast, Entity Culling, Xaero's maps and JEI.
- **`packs/worldgen-tellus/`** → Prism "Bankopack Worldgen Test (Tellus)": Tellus 0.8.3. Pick the Tellus world preset when creating a world (needs internet). Stock DH, so leave Tellus's "1:1 / increased height" off (that needs the author's DH fork).
- **`packs/worldgen-jjthunder/`** → Prism "Bankopack Worldgen Test (JJThunder)": JJThunder To The Max 0.6.0, a datapack loaded globally via Paxi. Use the default world type.
- **They must stay separate:** JJThunder's datapack replaces `minecraft:dimension/overworld` and `dimension_type/overworld`, plus 35 vanilla biomes. Loaded globally, it would override the Tellus world preset, and its biome edits would leak into Tellus worlds.

---

## Resource budget
Your PC: Ryzen 7 3700X, 32 GB RAM, RTX 3070 Ti → give the client **10–12 GB** heap. For a dedicated server with this list: 8–10 GB. Pregenerate with Chunky. Tectonic at vertical scale 3.7 with the higher build limit is noticeably slower to generate than vanilla.
