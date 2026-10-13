"""Generate the Bankopack FTB Quests book from the readable spec below.

Usage: python quests/build_quests.py <ids.json> <output quests dir>
  ids.json   - registry of known IDs (quests/collect_ids.py) used to validate every task/reward
  output dir - normally pack/config/ftbquests/quests

Design: every chapter is optional and independent (no cross-chapter gating), so players can ignore
whole systems (e.g. Cobblemon). Quests inside a chapter form simple chains. Text is written to
lang/en_us.snbt (FTB Quests 2101 stores titles/descriptions there).
"""
import hashlib, json, pathlib, sys

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

CHAPTERS = [
  dict(key="welcome", title="Welcome to Bankopack", icon="ftbquests:book",
       subtitle=["Start here. Every chapter is optional - follow whatever interests you."],
       quests=[
    Q("welcome", "Welcome!", [check()], [xp(50)], [
      "Bankopack is a big, exploration-heavy pack: huge terrain, classes and spells, Create airships,",
      "Pokémon, dimensions and bosses. None of it is required - use this book as a map, not a checklist.",
      "",
      "&eUseful to know:&r",
      "- &bJEI&r (right side of your inventory) shows every recipe. Type &a@rpg&r to see all class/RPG items.",
      "- &bXaero's World Map&r opens with &aM&r. FTB Chunks lets you claim land from the map.",
      "- Hold the &bUltimine&r key (default &a`&r) while mining to mine whole veins.",
      "- Hover a Create item and hold &aW&r to watch its Ponder tutorial."]),
    Q("backpack", "Pack Up", [item("travelersbackpack:standard")], [give("minecraft:leather", 4)], [
      "A Traveler's Backpack gives you lots of extra storage plus two fluid tanks.",
      "It's worn on your back - press its keybind to open it while you walk."], deps=["welcome"]),
    Q("glider", "Ride the Wind", [item("paraglider:paraglider")], [give("minecraft:feather", 8)], [
      "The terrain here is &lvertical&r. A paraglider turns every cliff into a shortcut.",
      "Gliding uses stamina. Campfires (and other heat) create &bupdrafts&r you can ride upward."], deps=["welcome"]),
    Q("hook", "Get a Grip", [item("yo_hooks:copper_grappling_hook")], [give("minecraft:copper_ingot", 8)], [
      "Grappling hooks pull you up cliffs. Climb or descend the rope with your movement keys and jump off it.",
      "Better materials (iron, gold, diamond, netherite) give a longer rope."], deps=["glider"]),
    Q("compass", "Biome Hunter", [item("naturescompass:naturescompass")], [xp(100)], [
      "Nature's Compass points you to any biome you choose - handy with this many of them."], deps=["welcome"]),
    Q("calendar", "Seasons Change", [item("sereneseasons:calendar")], [give("minecraft:wheat_seeds", 16)], [
      "Seasons are on. Some crops only grow in certain seasons, and winter gets cold.",
      "A calendar tells you the season and how long it lasts."], deps=["compass"]),
    Q("kitchen", "A Proper Kitchen", [item("farmersdelight:cooking_pot")], [give("minecraft:bread", 8)], [
      "Farmer's Delight cooking gives much better food with useful effects.",
      "Cooking pots work over a fire or campfire. Check JEI for recipes."], deps=["welcome"]),
    Q("graves", "Death Happens", [check()], [xp(50)], [
      "When you die, your items (including curios and backpack contents) go into a &bgravestone&r",
      "where you fell. Go back and open it to get everything back."], deps=["welcome"]),
  ]),

  dict(key="pokemon", title="Pokémon", icon="cobblemon:poke_ball",
       subtitle=["Cobblemon - completely optional. Ignore this chapter if Pokémon aren't your thing."],
       quests=[
    Q("starter", "Choose Your Starter", [check()], [give("cobblemon:poke_ball", 5)], [
      "Press your &bPokémon summary&r key (see Controls) to pick a starter Pokémon.",
      "Wild Pokémon roam the world - weaken them in battle, then throw a Poké Ball."]),
    Q("balls", "Gotta Catch 'Em", [item("cobblemon:poke_ball", 5)], [give("cobblemon:poke_ball", 5)], [
      "Craft Poké Balls from apricorns, which grow on apricorn trees around the world."], deps=["starter"]),
    Q("healer", "Pokémon Center", [item("cobblemon:healing_machine")], [xp(150)], [
      "The Healing Machine fully heals your party. It recharges over time."], deps=["starter"]),
    Q("pc", "Box Storage", [item("cobblemon:pc")], [xp(150)], [
      "A PC stores the Pokémon you aren't carrying in your party."], deps=["healer"]),
    Q("pokedex", "Gotta Log 'Em All", [item("cobblemon:pokedex_red")], [xp(150)], [
      "The Pokédex tracks what you've seen and caught. Any colour works."], deps=["balls"]),
    Q("pasture", "Ranch Life", [item("cobblemon:pasture")], [xp(150)], [
      "Pastures let your Pokémon roam freely near your base."], deps=["pc"]),
    Q("trainers", "Trainer Battles", [check()], [give("cobblemon:poke_ball", 10)], [
      "NPC &btrainers&r wander the world (Radical Cobblemon Trainers) and will challenge you.",
      "Beat them to climb the trainer ranks - your Trainer Card tracks progress."], deps=["balls"]),
    Q("mega", "Mega Evolution", [item("mega_showdown:mega_bracelet")], [xp(500)], [
      "Mega Showdown adds Mega Evolution, Z-Moves, Terastallization and Dynamax.",
      "Wear a Mega Bracelet (it goes in an &baccessory&r slot), set a Key Stone in it,",
      "and give a compatible Pokémon its Mega Stone."], deps=["trainers"], optional=True),
  ]),

  dict(key="create", title="Create & Flight", icon="create:cogwheel",
       subtitle=["Machines, trains and airships. Hold W over any Create item for a tutorial."],
       quests=[
    Q("alloy", "Andesite Alloy", [item("create:andesite_alloy", 8)], [give("create:andesite_alloy", 8)], [
      "Almost every early Create machine starts with andesite alloy."]),
    Q("wheel", "Rotational Power", [item("create:water_wheel")], [give("create:shaft", 16)], [
      "Water wheels turn flowing water into rotation. Connect machines with shafts and cogwheels."], deps=["alloy"]),
    Q("press", "Under Pressure", [item("create:mechanical_press")], [give("minecraft:iron_ingot", 8)], [
      "The mechanical press makes plates and, with a basin, mixes and compacts."], deps=["wheel"]),
    Q("brass", "Brass Age", [item("create:precision_mechanism")], [give("create:brass_ingot", 8)], [
      "Precision mechanisms unlock Create's more advanced machines."], deps=["press"]),
    Q("steam", "Full Steam", [item("create:steam_engine")], [xp(300)], [
      "A boiler made from fluid tanks, a blaze burner and steam engines is serious power."], deps=["brass"]),
    Q("assembler", "Physics!", [item("simulated:physics_assembler")], [xp(200)], [
      "Create Aeronautics turns builds into real physics objects. Glue your build with Super Glue,",
      "then use a Physics Assembler on it. Hold W over any Aeronautics block to see how it works."], deps=["press"]),
    Q("balloon", "Up, Up and Away", [item("aeronautics:adjustable_burner"), item("aeronautics:white_envelope", 16)],
      [give("minecraft:coal", 16)], [
      "Hot Air Burners fill an enclosed balloon of Envelope blocks with hot air to give lift.",
      "Power the burner with redstone - a lever works."], deps=["assembler"]),
    Q("propeller", "Thrust", [item("aeronautics:propeller_bearing"), item("simulated:white_portable_engine")],
      [xp(300)], [
      "A Propeller Bearing with sails (or a ready-made propeller) driven by a Portable Engine moves your ship.",
      "Use a wrench on the bearing to reverse thrust."], deps=["balloon"]),
    Q("helm", "Captain's Wheel", [item("simulated:steering_wheel")], [xp(300)], [
      "Steering wheels and throttle levers give your ship proper controls."], deps=["propeller"]),
    Q("trains", "All Aboard", [item("create:track_station")], [xp(300)], [
      "Create trains run on tracks with stations and schedules - great on this huge terrain."], deps=["brass"]),
    Q("plane", "Prop Plane", [item("immersive_aircraft:biplane")], [xp(300)], [
      "Prefer something simpler? Immersive Aircraft has ready-to-fly planes and airships."], deps=["alloy"], optional=True),
  ]),

  dict(key="classes", title="Classes & Magic", icon="spell_engine:spell_binding",
       subtitle=["Pick a combat class, learn its skills, or study Iron's spellcasting."],
       quests=[
    Q("binding", "The Spell Binding Table", [item("spell_engine:spell_binding")], [give("minecraft:lapis_lazuli", 16)], [
      "Classes are built around &bspell books&r. Craft a Spell Binding Table (surround it with bookshelves)",
      "to create your class's spell book and unlock its spells."]),
    Q("pick", "Choose a Class", [check()], [xp(200)], [
      "Classes: &bWizard&r (arcane/fire/frost), &bPaladin&r & &bPriest&r, &bRogue&r & &bWarrior&r, &bArcher&r,",
      "plus &bBerserker&r, &bForcemaster&r, &bWitcher&r, &bElemental Wizard&r and &bBard&r.",
      "Equip the spell book and hold a weapon to cast. Type &a@rpg&r in JEI to browse everything."], deps=["binding"]),
    Q("runes", "Rune Crafting", [item("runes:crafting_altar")], [xp(150)], [
      "Wizard-style spells use &brunes&r as ammunition, much like arrows for a bow."], deps=["pick"], optional=True),
    Q("skills", "Skill Trees", [check()], [xp(200)], [
      "Open the &bSkill Tree&r screen (see Controls). Class skills grant stats and spells;",
      "Weapon Skills branches unlock while holding that weapon type (daggers, glaives, claymores...)."], deps=["pick"]),
    Q("irons", "Iron's Spellcasting", [item("irons_spellbooks:inscription_table")], [give("irons_spellbooks:common_ink", 4)], [
      "Iron's Spells 'n Spellbooks is a separate magic system with its own mana.",
      "Inscribe scrolls into a spell book at the Inscription Table."], optional=True),
    Q("scrolls", "Scroll Forge", [item("irons_spellbooks:scroll_forge")], [xp(200)], [
      "Forge new spell scrolls from ink and focus items."], deps=["irons"], optional=True),
  ]),

  dict(key="gear", title="Gear & World Tiers", icon="apotheosis:reforging_table",
       subtitle=["Apotheosis loot, enchanting and the world-tier gateways."],
       quests=[
    Q("shelves", "Better Bookshelves", [item("apothic_enchanting:hellshelf")], [xp(200)], [
      "Apotheosis reworks enchanting: different shelves change power, quanta (randomness) and arcana (rarity).",
      "The enchanting table shows the stats your shelves give."]),
    Q("reforge", "Reforging", [item("apotheosis:reforging_table")], [xp(200)], [
      "Looted gear can roll &baffixes&r with rarities. The Reforging Table rerolls them."], deps=["shelves"]),
    Q("salvage", "Salvage", [item("apotheosis:salvaging_table")], [xp(150)], [
      "Break unwanted affix gear down into rarity materials."], deps=["reforge"]),
    Q("augment", "Augmenting", [item("apotheosis:augmenting_table")], [xp(200)], [
      "Improve and reroll individual affixes on your favourite gear. Gems can be socketed at a smithing table."],
      deps=["salvage"]),
    Q("frontier", "Leave the Frontier", [adv("apotheosis:gateways/frontier")], [give("minecraft:diamond", 2)], [
      "Rare loot is gated by &bWorld Tier&r. Each tier has a matching Gateway: craft its Gate Pearl (see JEI),",
      "throw it, and survive the waves. Clearing it is how you progress to the next tier."], deps=["reforge"]),
    Q("ascent", "Finish Your Ascent", [adv("apotheosis:gateways/ascent")], [give("minecraft:diamond", 4)], [
      "The Gateway of the Sunlit Ascent. Bring friends - lives are shared."], deps=["frontier"]),
    Q("summit", "The Thundering Summit", [adv("apotheosis:gateways/summit")], [give("minecraft:diamond", 6)], [
      "Tougher invaders with real gear of their own."], deps=["ascent"]),
    Q("pinnacle", "The Apothic Pinnacle", [adv("apotheosis:gateways/pinnacle")], [give("minecraft:netherite_ingot", 1)], [
      "The final tier. After this, the Endless Invader gateway is the ultimate test."], deps=["summit"]),
  ]),

  dict(key="dimensions", title="Beyond the Overworld", icon="minecraft:ender_eye",
       subtitle=["Every dimension in the pack. Visit them in any order."],
       quests=[
    Q("nether", "Into the Nether", [dim("minecraft:the_nether")], [xp(200)], [
      "Better Nether biomes and redesigned fortresses await."]),
    Q("end", "The End", [dim("minecraft:the_end")], [xp(300)], [
      "The dragon fight is overhauled (True Ending) - come prepared. The outer islands are full of new biomes."],
      deps=["nether"]),
    Q("aether", "The Aether", [dim("aether:the_aether")], [xp(300)], [
      "Build a portal frame from &bglowstone&r and pour in a water bucket.",
      "Floating islands, dungeons and the Deep Aether's extra biomes."]),
    Q("twilight", "The Twilight Forest", [dim("twilightforest:twilight_forest")], [xp(300)], [
      "Make a small pool of water ringed with flowers or grass and throw a &bdiamond&r into it.",
      "A progression of bosses lives here."]),
    Q("bumblezone", "The Bumblezone", [dim("the_bumblezone:the_bumblezone")], [xp(300)], [
      "Throw an &bender pearl&r at a bee nest or beehive. A giant enclosed hive - mind the bees."]),
    Q("otherside", "The Otherside", [dim("deeperdarker:otherside")], [xp(400)], [
      "Deeper and Darker's dimension is reached through a portal in an &bAncient City&r.",
      "Check JEI and the mod's items for how to activate it."]),
    Q("starlight", "Eternal Starlight", [dim("eternal_starlight:starlight")], [xp(400)], [
      "A starry dimension with its own bosses and gear. Check JEI for how to get there."]),
    Q("moon", "Fly Me to the Moon", [dim("ad_astra:moon")], [xp(500)], [
      "Build a Tier 1 rocket at a NASA Workbench, fuel it, place it on a launch pad and launch.",
      "Bring a space suit - there's no air up there."]),
  ]),

  dict(key="bosses", title="Bosses", icon="cataclysm:ignitium_ingot",
       subtitle=["The big fights. Gear up first - and bring friends."],
       quests=[
    Q("wither", "The Wither", [kill("minecraft:wither")], [give("minecraft:diamond", 3)], [
      "Classic, but still dangerous."]),
    Q("dragon", "The Ender Dragon", [kill("minecraft:ender_dragon")], [give("minecraft:diamond", 5)], [
      "With True Ending the dragon has new attacks and phases. Destroy the crystals first."]),
    Q("naga", "The Naga", [kill("twilightforest:naga")], [xp(300)], ["The first Twilight Forest boss, in a courtyard."]),
    Q("lich", "The Lich", [kill("twilightforest:lich")], [xp(400)], ["Atop the Lich Tower."], deps=["naga"]),
    Q("hydra", "The Hydra", [kill("twilightforest:hydra")], [give("minecraft:diamond", 3)], ["In the fire swamp."], deps=["lich"]),
    Q("slider", "The Slider", [kill("aether:slider")], [xp(300)], ["Guardian of the Aether's bronze dungeons."]),
    Q("monstrosity", "Netherite Monstrosity", [kill("cataclysm:netherite_monstrosity")], [give("minecraft:netherite_scrap", 2)], [
      "Found in the Nether's &bSoul Blacksmith&r. The first big Cataclysm boss."], deps=["wither"]),
    Q("ignis", "Ignis", [kill("cataclysm:ignis")], [give("minecraft:netherite_scrap", 2)], [
      "Waits in the &bBurning Arena&r in the Nether."], deps=["monstrosity"]),
    Q("ender_guardian", "Ender Guardian", [kill("cataclysm:ender_guardian")], [give("minecraft:netherite_scrap", 2)], [
      "Guards the &bRuined Citadel&r in the End."], deps=["dragon"]),
    Q("harbinger", "The Harbinger", [kill("cataclysm:the_harbinger")], [give("minecraft:netherite_scrap", 2)], [
      "Deep underground in the &bAncient Factory&r."]),
    Q("leviathan", "The Leviathan", [kill("cataclysm:the_leviathan")], [give("minecraft:netherite_scrap", 3)], [
      "Beneath the waves, in the &bSunken City&r of a deep ocean."], deps=["harbinger"]),
    Q("remnant", "Ancient Remnant", [kill("cataclysm:ancient_remnant")], [give("minecraft:netherite_scrap", 3)], [
      "Buried in the desert's &bCursed Pyramid&r."], deps=["harbinger"]),
    Q("maledictus", "Maledictus", [kill("cataclysm:maledictus")], [give("minecraft:netherite_scrap", 3)], [
      "Imprisoned in the snowy &bFrosted Prison&r."], deps=["harbinger"]),
    Q("scylla", "Scylla", [kill("cataclysm:scylla")], [give("minecraft:netherite_scrap", 3)], [
      "Rises over the warm-ocean &bAcropolis&r."], deps=["leviathan"]),
  ]),
]

# ---------------------------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------------------------
def oid(*parts):
    h = hashlib.sha1("/".join(parts).encode()).hexdigest()[:16].upper()
    return h if int(h, 16) else "0000000000000001"

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
