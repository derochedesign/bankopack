"""Generate the pack's default keybinds (config/defaultoptions/keybindings.txt for Default Options).

Usage: python tools/gen_keybinds.py <options.txt from a full client> <output keybindings.txt>

Starts from every keybind in the given options.txt (so all mods are covered) and applies LAYOUT below.
Default Options only changes the *default* of each key: new players get it automatically, existing
players get it via Controls -> Reset Keys.

Rules used for the layout:
- Global actions (usable any time) each get their own key.
- Situational actions (only in a GUI, only while riding, only while holding/wearing a specific item,
  only in a transformed form) may share a key, but only with other situational actions whose
  situations can't overlap, or with a global action that is harmless to trigger at the same time.
- Modifier combos work: NeoForge only fires the plain X binding when no Alt/Ctrl/Shift+X binding
  matches, so Alt+1 does not also switch to hotbar slot 1. A LAYOUT value may be (key, "ALT").
"""
import re, sys
from collections import defaultdict

U = "key.keyboard.unknown"
def k(name): return "key.keyboard." + name

LAYOUT = {
    # --- Global, own key ---------------------------------------------------------------------
    "key.cobblemon.throwpartypokemon": k("r"),          # Cobblemon default; its HUD prompts say R
    "keybinds.combat_roll.roll": k("c"),
    "key.irons_spellbooks.spellbook_cast": k("v"),
    "key.irons_spellbooks.spell_wheel": k("g"),
    "key.irons_spellbooks.spell_bar_modifier": U,       # alt+scroll clashed with Relics; use the wheel (G)
    # Spell Engine (RPG Series classes): hold Alt + 1-9 to cast; plain 1-9 always stay the hotbar.
    # pack/config/spell_engine/client.json5 turns off its fallback to the plain number keys.
    **{f"keybindings.spell_engine.spell_hotbar_{i}": (k(str(i)), "ALT") for i in range(1, 10)},
    "keybindings.spell_engine.bypass_spell_hotbar": U,     # held, it blocks casting (would cancel Alt+N)
    "key.cobblemon.summary": k("h"),
    "key.cobblemon.hideparty": k("o"),
    "key.puffish_skills.open": k("k"),
    "accessories.key.open_accessories_screen": k("j"),
    "key.aether.open_accessories.desc": k("i"),
    "key.travelersbackpack.inventory": k("b"),
    "gui.xaero_open_map": k("m"),
    "gui.xaero_waypoints_key": k("u"),
    "gui.xaero_new_waypoint": k("n"),
    "gui.xaero_minimap_settings": U,                    # rare; Mods menu -> Xaero's Minimap
    "gui.xaero_enlarge_map": U,                         # rare; Z is needed for helmet abilities
    "gui.xaero_open_settings": U,                       # rare; settings button on the world map
    "key.relics.active_abilities_list": k("left.alt"),  # Relics default (hold + scroll)
    "key.toms_storage.open_terminal": k("0"),
    "iris.keybind.toggleShaders": k("f6"),

    # --- Armor abilities: one key per armor slot (you can't wear two helmets) ----------------
    "key.cataclysm.helmet_ability": k("z"),
    "key.legendary_monsters.helmet_ability": k("z"),
    "key.legendary_monsters.roar_ability": k("z"),      # assumed helmet-style ability
    "key.cataclysm.chestplate_ability": k("x"),
    "key.legendary_monsters.mossy_chestplate_ability": k("x"),
    "key.ad_astra.toggle_suit_flight": k("x"),           # jet suit chestplate
    "key.deep_aether.stratus_dash_ability.desc": k("x"), # stratus armor
    "key.cataclysm.boots_ability": k("y"),
    "key.legendary_monsters.fiery_boots_ability": k("y"),
    "key.deep_aether.slider_eye_ability": k("y"),        # Slider Slam (accessory)

    # --- Held weapon/item ability (only the item you're holding reacts) ----------------------
    "key.cataclysm.ability": k("apostrophe"),
    "key.deeperdarker.transmit": k("apostrophe"),
    "key.twilightforest.item_display_map_cycle": k("apostrophe"),
    "key.twilightforest.swap_hotbar": k("apostrophe"),
    "key.twilightforest.zoom": k("apostrophe"),
    # Simply Swords keeps ; (offhand) and ' (mainhand)
    "key.pipeorgans.midi_config": U,                     # freed ; for Simply Swords

    # --- Vehicles / mounts (you only ride one thing at a time) -------------------------------
    "key.immersive_aircraft.boost": k("left.control"),   # sprint does nothing while riding/flying
    "key.deeperdarker.boost": k("left.control"),         # Soul Elytra boost
    "key.goety.mount.roar": k("left.control"),
    "key.immersive_aircraft.dismount": k("caps.lock"),
    "key.ad_astra.open_radio": k("caps.lock"),
    "key.goety.mount.freeRoam": k("caps.lock"),
    # Bumblezone beehemoth down stays on Caps Lock, up on Space; Cobblemon ride free-look on Left Alt
    "key.travelersbackpack.cycle_tool": k("caps.lock"),  # hold + scroll while holding a tool

    # --- Goety (necromancy) -------------------------------------------------------------------
    "key.goety.focusCircle": k("period"),
    "key.goety.bag": k("minus"),
    "key.goety.ceaseFire": k("backslash"),
    "key.goety.activate_curio": k("equal"),
    "key.goety.wand": k("f8"),
    # Lich and Witch forms: keypad, shared between the two forms
    "key.goety.lich.lichForm": k("keypad.6"),
    "key.goety.lich.magnet": k("keypad.7"),
    "key.goety.lich.nightVision": k("keypad.8"),
    "key.goety.lich.laugh": k("keypad.9"),
    "key.goety.witch.robe": k("keypad.6"),
    "key.goety.witch.brewCircle": k("keypad.7"),
    "key.goety.witch.brewBag": k("keypad.8"),
    "key.goety.witch.extractPotions": k("keypad.9"),
    "placebo.toggleWings": U,                        # supporter cosmetics; freed keypad 8/9
    "placebo.toggleTrails": U,

    # --- Misc ---------------------------------------------------------------------------------
    "key.constructionwand.wand_undo": k("backspace"),    # only while holding a wand; JEI uses it in GUIs
    "key.aether.invisibility_toggle.desc": k("f7"),      # visual toggles
    "key.deep_aether.toggle_skyjade_transparency": k("f7"),
    "crafting_on_a_stick.key.open_curios": U,        # right-click the item instead
    "key.evilcraft.exaltedCrafting": U,                  # right-click the item instead
    "key.evilcraft.fart": U,
    "key.ftbchunks.minimap.zoomIn": U,                   # FTB minimap is disabled (Xaero's is used)
    "key.ftbchunks.minimap.zoomOut": U,

    # --- Weavers Paradise (clothing) ----------------------------------------------------------
    "weaversparadise.keybind.open_upper_wear": k("f9"),   # default [ (RFTools)
    "weaversparadise.keybind.trinket_sound": k("f10"),    # default X (chestplate abilities)
}

# Bindings that only work inside a screen/tooltip or while holding a modifier: sharing is fine.
CONTEXT = re.compile(r"ftbquests\.gui|jei\.|trashslot|ponder|simplytooltips|legendarytooltips|guideme|"
                     r"jade\.show_details|apotheosis\.compare|relics\.research|_modifier|ae2\.|"
                     r"ToolbarActivator|mtr\.train|beehemoth|yo_hooks|gravitite|ridingfreelook|"
                     r"upshiftparty|downshiftparty|ftbultimine\.change_shape|immersiveengineering|"
                     r"simulated\.keyinfo|Destination|mtr\.lift|xaero_quick_confirm")

def main(src, dst):
    binds = {}
    for line in open(src, encoding="utf-8"):
        m = re.match(r"key_([^:]+):([^:\s]+)(?::(\S*))?", line.strip())
        if m: binds[m.group(1)] = (m.group(2), m.group(3) or "")
    # Mods added after the options.txt snapshot was taken; their binds are written even if absent from it.
    newer = ("weaversparadise.",)
    missing = [n for n in LAYOUT if n not in binds and not n.startswith(newer)]
    if missing: sys.exit("not in options.txt (renamed or removed mod?): " + ", ".join(missing))
    for n, key in LAYOUT.items(): binds[n] = key if isinstance(key, tuple) else (key, "")
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        for n in sorted(binds):
            key, mods = binds[n]
            f.write(f"key_{n}:{key}:{mods}\n")
    # Report keys still shared by more than one non-situational binding
    by = defaultdict(list)
    for n, (key, mods) in binds.items():
        if key != U: by[(key, mods)].append(n)
    for (key, mods), names in sorted(by.items()):
        hard = [n for n in names if not CONTEXT.search(n)]
        if len(names) > 1:
            print(f"{key.replace('key.keyboard.', '')}{'+' + mods if mods else ''}: "
                  + ", ".join(n + ("" if n in hard else "*") for n in names))
    print(f"wrote {len(binds)} bindings -> {dst}  (* = situational)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
