"""Generate the Bankopack FTB Quests book from the readable spec below.

Usage: python quests/build_quests.py <ids.json> <output quests dir>
  ids.json   - registry of known IDs (quests/collect_ids.py) used to validate every task/reward
  output dir - normally pack/config/ftbquests/quests

Design: every chapter is optional and independent (no cross-chapter gating), so players can ignore
whole systems (e.g. Cobblemon). Quests inside a chapter form simple chains. Text is written to
lang/en_us.snbt (FTB Quests 2101 stores titles/descriptions there).
"""
import hashlib, json, pathlib, re, sys

# ---------------------------------------------------------------------------------------------
# Task / reward helpers
# ---------------------------------------------------------------------------------------------
def item(i, count=1): return {"type": "item", "item": i, "count": count}
def kill(e, n=1): return {"type": "kill", "entity": e, "value": n}
def dim(d): return {"type": "dimension", "dimension": d}
def adv(a): return {"type": "advancement", "advancement": a}
def check(): return {"type": "checkmark"}
def give(i, n=1): return {"type": "item", "item": i, "count": n}
def xp(n): return {"type": "xp", "xp": n}

# Quest: (key, title, [tasks], [rewards], [description lines], deps=[keys], optional=False)
def Q(key, title, tasks, rewards, desc, deps=(), optional=False, icon=None):
    return dict(key=key, title=title, tasks=tasks, rewards=rewards, desc=desc, deps=list(deps),
                optional=optional, icon=icon)

# Text style: plain facts only, no flavour lines or joke titles. Never write a bare "&" - FTB Quests
# reads "&" as a formatting code (&b colour, &r reset) and flags the text as invalid. Write "and".
CHAPTERS = [
  dict(key="welcome", title="Welcome to Bankopack", icon="ftbquests:book",
       subtitle=["Start here. Every chapter is optional."],
       quests=[
    Q("welcome", "Welcome", [check()], [xp(50)], [
      "This book covers the pack's main systems: classes and spells, Create airships, Pokémon,",
      "dimensions and bosses. None of it is required.",
      "",
      "&eUseful to know:&r",
      "- &bJEI&r (right side of your inventory) shows every recipe. Type &a@rpg&r to see all class/RPG items.",
      "- &bXaero's World Map&r opens with &aM&r. FTB Chunks lets you claim land from the map.",
      "- Hold the &bUltimine&r key (default &a`&r) while mining to mine whole veins.",
      "- Hover a Create item and hold &aW&r to watch its Ponder tutorial."]),
    Q("backpack", "Traveler's Backpack", [item("travelersbackpack:standard")], [give("minecraft:leather", 4)], [
      "Extra storage plus two fluid tanks. Worn in the back slot; press its keybind to open it."], deps=["welcome"]),
    Q("glider", "Paraglider", [item("paraglider:paraglider")], [give("minecraft:feather", 8)], [
      "Gliding uses stamina. Campfires and other heat sources create &bupdrafts&r that lift you."], deps=["welcome"]),
    Q("hook", "Grappling Hook", [item("yo_hooks:iron_grappling_hook")], [give("minecraft:iron_ingot", 4)], [
      "Grappling hooks pull you up cliffs. Climb or descend the rope with your movement keys and jump to let go.",
      "Higher tiers (gold, diamond, netherite) have a longer rope."], deps=["glider"]),
    Q("compass", "Nature's Compass", [item("naturescompass:naturescompass")], [xp(100)], [
      "Points you to any biome you choose."], deps=["welcome"]),
    Q("calendar", "Seasons", [item("sereneseasons:calendar")], [give("minecraft:wheat_seeds", 16)], [
      "Seasons are on. Some crops only grow in certain seasons.",
      "A calendar shows the current season and how long it lasts."], deps=["compass"]),
    Q("kitchen", "Cooking Pot", [item("farmersdelight:cooking_pot")], [give("minecraft:bread", 8)], [
      "Farmer's Delight meals restore more hunger and give effects.",
      "Cooking pots need a fire or campfire underneath. Check JEI for recipes."], deps=["welcome"]),
    Q("graves", "Gravestones", [check()], [xp(50)], [
      "When you die, your items (including accessories and backpack) go into a &bgravestone&r",
      "where you died. Open it to get everything back."], deps=["welcome"]),
  ]),

  dict(key="pokemon", title="Pokémon", icon="cobblemon:poke_ball",
       subtitle=["Cobblemon. Optional - skip this chapter if you don't want Pokémon."],
       quests=[
    Q("starter", "Choose a Starter", [check()], [give("cobblemon:poke_ball", 5)], [
      "Press your &bPokémon summary&r key (see Controls) to pick a starter Pokémon.",
      "To catch wild Pokémon, weaken them in battle, then throw a Poké Ball."]),
    Q("balls", "Poké Balls", [item("cobblemon:poke_ball", 5)], [give("cobblemon:poke_ball", 5)], [
      "Poké Balls are crafted from apricorns, which grow on apricorn trees."], deps=["starter"]),
    Q("healer", "Healing Machine", [item("cobblemon:healing_machine")], [xp(150)], [
      "Fully heals your party. It recharges over time."], deps=["starter"]),
    Q("pc", "PC", [item("cobblemon:pc")], [xp(150)], [
      "Stores the Pokémon that aren't in your party."], deps=["healer"]),
    Q("pokedex", "Pokédex", [item("cobblemon:pokedex_red")], [xp(150)], [
      "Tracks the Pokémon you've seen and caught. Any colour counts."], deps=["balls"]),
    Q("pasture", "Pasture", [item("cobblemon:pasture")], [xp(150)], [
      "Lets your Pokémon roam freely near your base."], deps=["pc"]),
    Q("trainers", "Trainer Battles", [check()], [give("cobblemon:poke_ball", 10)], [
      "NPC &btrainers&r (Radical Cobblemon Trainers) spawn around the world and will challenge you."], deps=["balls"]),
    Q("mega", "Mega Evolution", [item("mega_showdown:mega_bracelet")], [xp(500)], [
      "Mega Showdown adds Mega Evolution, Z-Moves, Terastallization and Dynamax.",
      "Wear a Mega Bracelet in its &baccessory&r slot and give a compatible Pokémon its Mega Stone.",
      "In battle, after picking Fight, toggle the Mega button next to Back, then choose a move."],
      deps=["trainers"], optional=True),
  ]),

  dict(key="create", title="Create and Flight", icon="create:cogwheel",
       subtitle=["Machines, trains and airships. Hold W over any Create item for a tutorial."],
       quests=[
    Q("alloy", "Andesite Alloy", [item("create:andesite_alloy", 8)], [give("create:andesite_alloy", 8)], [
      "Most early Create machines are made from andesite alloy."]),
    Q("wheel", "Water Wheel", [item("create:water_wheel")], [give("create:shaft", 16)], [
      "Turns flowing water into rotation. Connect machines with shafts and cogwheels."], deps=["alloy"]),
    Q("press", "Mechanical Press", [item("create:mechanical_press")], [give("minecraft:iron_ingot", 8)], [
      "Makes plates, and with a basin underneath it compacts items."], deps=["wheel"]),
    Q("brass", "Precision Mechanism", [item("create:precision_mechanism")], [give("create:brass_ingot", 8)], [
      "Needed for Create's more advanced machines."], deps=["press"]),
    Q("steam", "Steam Engine", [item("create:steam_engine")], [xp(300)], [
      "A boiler (fluid tanks heated by a blaze burner) with steam engines on it gives a lot of power."], deps=["brass"]),
    Q("assembler", "Physics Assembler", [item("simulated:physics_assembler")], [xp(200)], [
      "Create Aeronautics turns builds into physics objects. Glue your build with Super Glue,",
      "then use a Physics Assembler on it. Hold W over any Aeronautics block to see how it works."], deps=["press"]),
    Q("balloon", "Hot Air Balloon", [item("aeronautics:adjustable_burner"), item("aeronautics:white_envelope", 16)],
      [give("minecraft:coal", 16)], [
      "Hot Air Burners fill an enclosed balloon of Envelope blocks with hot air to give lift.",
      "Power the burner with redstone (a lever works)."], deps=["assembler"]),
    Q("propeller", "Propellers", [item("aeronautics:propeller_bearing"), item("simulated:white_portable_engine")],
      [xp(300)], [
      "A Propeller Bearing with sails (or a ready-made propeller) driven by a Portable Engine moves your ship.",
      "Use a wrench on the bearing to reverse thrust."], deps=["balloon"]),
    Q("helm", "Steering Wheel", [item("simulated:steering_wheel")], [xp(300)], [
      "Steering wheels and throttle levers control your ship."], deps=["propeller"]),
    Q("trains", "Trains", [item("create:track_station")], [xp(300)], [
      "Create trains run on tracks between stations, following schedules."], deps=["brass"]),
    Q("plane", "Immersive Aircraft", [item("immersive_aircraft:biplane")], [xp(300)], [
      "Ready-made planes and airships, separate from Create."], deps=["alloy"], optional=True),
  ]),

  dict(key="classes", title="Classes and Magic", icon="spell_engine:spell_binding",
       subtitle=["Combat classes, skill trees and Iron's spellcasting."],
       quests=[
    Q("binding", "Spell Binding Table", [item("spell_engine:spell_binding")], [give("minecraft:lapis_lazuli", 16)], [
      "Classes are built around &bspell books&r. Craft a Spell Binding Table (surround it with bookshelves)",
      "to make your class's spell book and unlock its spells."]),
    Q("pick", "Choose a Class", [check()], [xp(200)], [
      "Classes: &bWizard&r (arcane, fire, frost), &bPaladin&r, &bPriest&r, &bRogue&r, &bWarrior&r, &bArcher&r,",
      "&bBerserker&r, &bForcemaster&r, &bWitcher&r, &bElemental Wizard&r and &bBard&r.",
      "Equip the spell book and hold a weapon to cast. Type &a@rpg&r in JEI to see all class items."], deps=["binding"]),
    Q("runes", "Rune Crafting", [item("runes:crafting_altar")], [xp(150)], [
      "Wizard spells use &brunes&r as ammunition, like arrows for a bow."], deps=["pick"], optional=True),
    Q("skills", "Skill Trees", [check()], [xp(200)], [
      "Open the &bSkill Tree&r screen (see Controls). Class skills grant stats and spells.",
      "Weapon skill branches only apply while holding that weapon type (daggers, glaives, claymores...)."], deps=["pick"]),
    Q("irons", "Inscription Table", [item("irons_spellbooks:inscription_table")], [give("irons_spellbooks:common_ink", 4)], [
      "Iron's Spells 'n Spellbooks is a separate magic system with its own mana.",
      "Inscribe scrolls into a spell book at the Inscription Table."], optional=True),
    Q("scrolls", "Scroll Forge", [item("irons_spellbooks:scroll_forge")], [xp(200)], [
      "Makes new spell scrolls from ink and focus items."], deps=["irons"], optional=True),
  ]),

  dict(key="gear", title="Gear and World Tiers", icon="apotheosis:reforging_table",
       subtitle=["Apotheosis loot, enchanting and world-tier gateways."],
       quests=[
    Q("shelves", "Hellshelf", [item("apothic_enchanting:hellshelf")], [xp(200)], [
      "Apotheosis changes enchanting: each shelf type adds different amounts of power, quanta (randomness)",
      "and arcana (rarity). The enchanting table shows the totals."]),
    Q("reforge", "Reforging Table", [item("apotheosis:reforging_table")], [xp(200)], [
      "Looted gear can have &baffixes&r with rarities. The Reforging Table rerolls them."], deps=["shelves"]),
    Q("salvage", "Salvaging Table", [item("apotheosis:salvaging_table")], [xp(150)], [
      "Breaks affix gear down into rarity materials."], deps=["reforge"]),
    Q("augment", "Augmenting Table", [item("apotheosis:augmenting_table")], [xp(200)], [
      "Upgrades or rerolls individual affixes. Gems are socketed at a smithing table."], deps=["salvage"]),
    Q("frontier", "World Tier: Frontier", [adv("apotheosis:gateways/frontier")], [give("minecraft:diamond", 2)], [
      "Rare loot is gated by &bWorld Tier&r. Each tier has a Gateway: craft its Gate Pearl (see JEI),",
      "throw it, and survive the waves. Clearing it unlocks the next tier."], deps=["reforge"]),
    Q("ascent", "World Tier: Ascent", [adv("apotheosis:gateways/ascent")], [give("minecraft:diamond", 4)], [
      "The Gateway of the Sunlit Ascent. Lives are shared between everyone fighting."], deps=["frontier"]),
    Q("summit", "World Tier: Summit", [adv("apotheosis:gateways/summit")], [give("minecraft:diamond", 6)], [
      "Enemies spawn with their own affix gear."], deps=["ascent"]),
    Q("pinnacle", "World Tier: Pinnacle", [adv("apotheosis:gateways/pinnacle")], [give("minecraft:netherite_ingot", 1)], [
      "The final tier. After this, the Endless Invader gateway is the hardest challenge."], deps=["summit"]),
  ]),

  dict(key="dimensions", title="Dimensions", icon="minecraft:ender_eye",
       subtitle=["Every dimension in the pack, in any order."],
       quests=[
    Q("nether", "The Nether", [dim("minecraft:the_nether")], [xp(200)], [
      "Better Nether adds biomes, and fortresses are redesigned."]),
    Q("end", "The End", [dim("minecraft:the_end")], [xp(300)], [
      "True Ending overhauls the dragon fight. The outer islands have new biomes."], deps=["nether"]),
    Q("aether", "The Aether", [dim("aether:the_aether")], [xp(300)], [
      "Build a portal frame from &bglowstone&r and pour in a water bucket.",
      "Deep Aether adds extra biomes."]),
    Q("twilight", "The Twilight Forest", [dim("twilightforest:twilight_forest")], [xp(300)], [
      "Make a small pool of water surrounded by flowers or grass and throw a &bdiamond&r into it.",
      "Its bosses are meant to be fought in order."]),
    Q("bumblezone", "The Bumblezone", [dim("the_bumblezone:the_bumblezone")], [xp(300)], [
      "Throw an &bender pearl&r at a bee nest or beehive to enter."]),
    Q("otherside", "The Otherside", [dim("deeperdarker:otherside")], [xp(400)], [
      "Deeper and Darker's dimension. The portal is in an &bAncient City&r; check JEI for how to activate it."]),
    Q("starlight", "Eternal Starlight", [dim("eternal_starlight:starlight")], [xp(400)], [
      "A dimension with its own bosses and gear. Check JEI for how to get there."]),
    Q("moon", "The Moon", [dim("ad_astra:moon")], [xp(500)], [
      "Build a Tier 1 rocket at a NASA Workbench, fuel it, place it on a launch pad and launch.",
      "You need a space suit: there's no air."]),
  ]),

  dict(key="bosses", title="Bosses", icon="cataclysm:ignitium_ingot",
       subtitle=["Major boss fights."],
       quests=[
    Q("wither", "The Wither", [kill("minecraft:wither")], [give("minecraft:diamond", 3)], [
      "Summoned with soul sand and three wither skeleton skulls."]),
    Q("dragon", "The Ender Dragon", [kill("minecraft:ender_dragon")], [give("minecraft:diamond", 5)], [
      "True Ending gives the dragon new attacks and phases. Destroy the crystals first."]),
    Q("naga", "The Naga", [kill("twilightforest:naga")], [xp(300)], ["The first Twilight Forest boss, in the Naga Courtyard."]),
    Q("lich", "The Lich", [kill("twilightforest:lich")], [xp(400)], ["At the top of the Lich Tower."], deps=["naga"]),
    Q("hydra", "The Hydra", [kill("twilightforest:hydra")], [give("minecraft:diamond", 3)], ["In the Fire Swamp."], deps=["lich"]),
    Q("slider", "The Slider", [kill("aether:slider")], [xp(300)], ["Boss of the Aether's bronze dungeons."]),
    Q("monstrosity", "Netherite Monstrosity", [kill("cataclysm:netherite_monstrosity")], [give("minecraft:netherite_scrap", 2)], [
      "In the Nether's &bSoul Blacksmith&r."], deps=["wither"]),
    Q("ignis", "Ignis", [kill("cataclysm:ignis")], [give("minecraft:netherite_scrap", 2)], [
      "In the &bBurning Arena&r in the Nether."], deps=["monstrosity"]),
    Q("ender_guardian", "Ender Guardian", [kill("cataclysm:ender_guardian")], [give("minecraft:netherite_scrap", 2)], [
      "In the &bRuined Citadel&r in the End."], deps=["dragon"]),
    Q("harbinger", "The Harbinger", [kill("cataclysm:the_harbinger")], [give("minecraft:netherite_scrap", 2)], [
      "Underground in the &bAncient Factory&r."]),
    Q("leviathan", "The Leviathan", [kill("cataclysm:the_leviathan")], [give("minecraft:netherite_scrap", 3)], [
      "In the &bSunken City&r in deep ocean."], deps=["harbinger"]),
    Q("remnant", "Ancient Remnant", [kill("cataclysm:ancient_remnant")], [give("minecraft:netherite_scrap", 3)], [
      "In the &bCursed Pyramid&r in the desert."], deps=["harbinger"]),
    Q("maledictus", "Maledictus", [kill("cataclysm:maledictus")], [give("minecraft:netherite_scrap", 3)], [
      "In the &bFrosted Prison&r in snowy biomes."], deps=["harbinger"]),
    Q("scylla", "Scylla", [kill("cataclysm:scylla")], [give("minecraft:netherite_scrap", 3)], [
      "At the &bAcropolis&r in warm ocean."], deps=["leviathan"]),
  ]),
]

# ---------------------------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------------------------
def oid(*parts):
    # FTB Quests re-assigns IDs that read as negative longs, so keep the top bit clear.
    # (IDs starting 0-7 are unchanged by this, so existing progress on those is kept.)
    n = int(hashlib.sha1("/".join(parts).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return f"{n or 1:016X}"

def s(v): return json.dumps(v, ensure_ascii=False)  # SNBT-compatible quoted string

def stack(i, n=1): return f'{{ count: {n}, id: {s(i)} }}'

def snbt_task(t, tid):
    base = f'id: {s(tid)}, type: {s(t["type"])}'
    if t["type"] == "item":
        extra = f', item: {stack(t["item"])}' + (f', count: {t["count"]}L' if t["count"] > 1 else "")
    elif t["type"] == "kill":
        extra = f', entity: {s(t["entity"])}, value: {t["value"]}L'
    elif t["type"] == "dimension":
        extra = f', dimension: {s(t["dimension"])}'
    elif t["type"] == "advancement":
        extra = f', advancement: {s(t["advancement"])}, criterion: ""'
    else:
        extra = ""
    return "{ " + base + extra + " }"

def snbt_reward(r, rid):
    if r["type"] == "item":
        return f'{{ id: {s(rid)}, type: "item", item: {stack(r["item"], r["count"])} }}'
    return f'{{ id: {s(rid)}, type: "xp", xp: {r["xp"]} }}'

def validate(ids):
    known = {k: set(v) for k, v in ids.items()}
    problems = []
    for ch in CHAPTERS:
        texts = [ch["title"], *ch["subtitle"]] + [x for q in ch["quests"] for x in [q["title"], *q["desc"]]]
        for txt in texts:
            if re.search(r"&(?![0-9a-fk-or])", txt): problems.append(f'{ch["key"]}: bare "&" in {txt!r}')
        keys = {q["key"] for q in ch["quests"]}
        icons = [ch["icon"]] + [q["icon"] for q in ch["quests"] if q["icon"]]
        for i in icons:
            if i not in known["item"]: problems.append(f'{ch["key"]}: icon {i}')
        for q in ch["quests"]:
            for d in q["deps"]:
                if d not in keys: problems.append(f'{ch["key"]}/{q["key"]}: unknown dependency {d}')
            for t in q["tasks"]:
                kind = {"item": "item", "kill": "entity", "dimension": "dimension", "advancement": "advancement"}.get(t["type"])
                val = t.get("item") or t.get("entity") or t.get("dimension") or t.get("advancement")
                if kind and val not in known[kind]: problems.append(f'{ch["key"]}/{q["key"]}: unknown {kind} {val}')
            for r in q["rewards"]:
                if r["type"] == "item" and r["item"] not in known["item"]: problems.append(f'{ch["key"]}/{q["key"]}: unknown reward {r["item"]}')
    return problems

def layout(quests):
    """Place quests by dependency depth (columns) and order (rows)."""
    depth = {}
    def d(q):
        if q["key"] in depth: return depth[q["key"]]
        byk = {x["key"]: x for x in quests}
        depth[q["key"]] = 0 if not q["deps"] else 1 + max(d(byk[k]) for k in q["deps"])
        return depth[q["key"]]
    for q in quests: d(q)
    rows = {}
    pos = {}
    for q in quests:
        col = depth[q["key"]]
        row = rows.get(col, 0); rows[col] = row + 1
        pos[q["key"]] = (col * 2.0, row * 1.5)
    return pos

def main(ids_path, out_dir):
    ids = json.load(open(ids_path))
    problems = validate(ids)
    if problems:
        print("VALIDATION FAILED:"); [print("  " + p) for p in problems]; sys.exit(1)

    out = pathlib.Path(out_dir); (out / "chapters").mkdir(parents=True, exist_ok=True); (out / "lang").mkdir(exist_ok=True)
    for old in (out / "chapters").glob("*.snbt"): old.unlink()
    lang = {}
    for order, ch in enumerate(CHAPTERS):
        cid = oid("chapter", ch["key"])
        lang[f"chapter.{cid}.title"] = ch["title"]
        lang[f"chapter.{cid}.chapter_subtitle"] = ch["subtitle"]
        pos = layout(ch["quests"])
        qs = []
        for q in ch["quests"]:
            qid = oid("quest", ch["key"], q["key"])
            lang[f"quest.{qid}.title"] = q["title"]
            lang[f"quest.{qid}.quest_desc"] = q["desc"]
            tasks = ", ".join(snbt_task(t, oid("task", ch["key"], q["key"], str(n))) for n, t in enumerate(q["tasks"]))
            rewards = ", ".join(snbt_reward(r, oid("reward", ch["key"], q["key"], str(n))) for n, r in enumerate(q["rewards"]))
            deps = ", ".join(s(oid("quest", ch["key"], d)) for d in q["deps"])
            x, y = pos[q["key"]]
            fields = [f"id: {s(qid)}", f"x: {x}d", f"y: {y}d", f"dependencies: [{deps}]", f"tasks: [{tasks}]", f"rewards: [{rewards}]"]
            if q["optional"]: fields.append("optional: true")
            if q["icon"]: fields.append(f"icon: {stack(q['icon'])}")
            qs.append("\t\t{\n\t\t\t" + "\n\t\t\t".join(fields) + "\n\t\t}")
        chapter = "\n".join([
            "{",
            f"\tdefault_hide_dependency_lines: false",
            f'\tdefault_quest_shape: ""',
            f"\tfilename: {s(ch['key'])}",
            f'\tgroup: ""',
            f"\ticon: {stack(ch['icon'])}",
            f"\tid: {s(cid)}",
            f"\torder_index: {order}",
            "\tquest_links: [ ]",
            "\tquests: [\n" + "\n".join(qs) + "\n\t]",
            "}", ""])
        (out / "chapters" / f"{ch['key']}.snbt").write_text(chapter, encoding="utf-8")

    (out / "data.snbt").write_text("\n".join([
        "{",
        "\tdefault_autoclaim_rewards: \"disabled\"",
        "\tdefault_consume_items: false",
        "\tdefault_quest_disable_jei: false",
        "\tdefault_quest_shape: \"circle\"",
        "\tdefault_reward_team: false",
        "\tdetection_delay: 20",
        "\tdisable_gui: false",
        "\tdrop_book_on_death: false",
        "\tdrop_loot_crates: false",
        "\tfallback_locale: \"en_us\"",
        "\tgrid_scale: 0.5d",
        "\tlock_message: \"\"",
        "\tpause_game: false",
        "\tprogression_mode: \"linear\"",
        "}", ""]), encoding="utf-8")
    (out / "chapter_groups.snbt").write_text("{\n\tchapter_groups: [ ]\n}\n", encoding="utf-8")

    def lang_val(v):
        return "[" + ", ".join(s(x) for x in v) + "]" if isinstance(v, list) else s(v)
    (out / "lang" / "en_us.snbt").write_text("{\n" + "\n".join(f"\t{s(k)}: {lang_val(v)}" for k, v in sorted(lang.items())) + "\n}\n", encoding="utf-8")
    n = sum(len(c["quests"]) for c in CHAPTERS)
    print(f"wrote {len(CHAPTERS)} chapters, {n} quests -> {out}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
