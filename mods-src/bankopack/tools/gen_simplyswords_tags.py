"""Generate RPG Series weapon-type tags for Simply Swords weapons.

Skill Tree (RPG Series) unlocks its weapon branches via item tags (rpg_series:weapon_type/*,
minecraft:swords, ...). Simply Swords only tags its weapons as c:swords, so none of them count.
This reads Simply Swords' Better Combat weapon_attributes files from its jar and sorts every
weapon into a branch: by name keyword first, then by Better Combat archetype.

Usage: python gen_simplyswords_tags.py <simplyswords.jar> <output resources dir>
"""
import json
import pathlib
import sys
import zipfile
from collections import defaultdict

# First matching keyword in the item name wins.
NAME_RULES = [
    ("greathammer", "hammer"), ("mjolnir", "hammer"),
    ("greataxe", "double_axe"),
    ("claymore", "claymore"), ("lichblade", "claymore"),
    ("warglaive", "glaive"), ("glaive", "glaive"), ("halberd", "glaive"),
    ("twinblade", "glaive"), ("scythe", "glaive"),
    ("spear", "spear"),
    ("sai", "dagger"),
    ("cutlass", "sickle"), ("sickle", "sickle"),
    ("longsword", "sword"), ("katana", "sword"), ("rapier", "sword"),
    ("chakram", "sword"), ("estoc", "sword"),
]

# Fallback for uniquely named weapons, keyed by Better Combat archetype (namespace stripped).
ARCHETYPE_RULES = {
    "heavy_axe": "claymore", "claymore": "claymore",
    "sword": "sword", "katana": "sword", "rapier": "sword", "chakram": "sword",
    "glaive": "glaive", "warglaive": "glaive", "halberd": "glaive",
    "battlestaff": "glaive", "scythe": "glaive",
    "trident": "spear", "spear": "spear",
    "soul_knife": "dagger",
    "sickle": "sickle",
    "mace": "mace",
}

# Branch -> tag file. Skill Tree's sword branch checks minecraft:swords; the rest are RPG Series tags.
TAG_FILES = {
    "sword": "data/minecraft/tags/item/swords.json",
    **{t: f"data/rpg_series/tags/item/weapon_type/{t}.json"
       for t in ("claymore", "double_axe", "hammer", "glaive", "spear", "dagger", "sickle", "mace")},
}


def name_match(name):
    # Match whole underscore-separated words, so "sai" doesn't hit e.g. "saint".
    words = name.split("_")
    for keyword, branch in NAME_RULES:
        if keyword in words or (len(keyword) > 4 and keyword in name):
            return branch
    return None


def main(jar_path, out_dir):
    tags = defaultdict(list)
    unmapped = []
    with zipfile.ZipFile(jar_path) as jar:
        for entry in sorted(jar.namelist()):
            parts = entry.split("/")
            # data/simplyswords/weapon_attributes/<item>.json (skip compat subfolders for other mods)
            if len(parts) != 4 or parts[0] != "data" or parts[2] != "weapon_attributes" or not entry.endswith(".json"):
                continue
            item = f"{parts[1]}:{parts[3][:-5]}"
            attrs = json.loads(jar.read(entry))
            archetype = (attrs.get("parent") or attrs.get("attributes", {}).get("category") or "").split(":")[-1]
            branch = name_match(parts[3][:-5]) or ARCHETYPE_RULES.get(archetype)
            if branch:
                tags[branch].append(item)
            else:
                unmapped.append(f"{item} ({archetype})")

    out = pathlib.Path(out_dir)
    for branch, items in sorted(tags.items()):
        path = out / TAG_FILES[branch]
        path.parent.mkdir(parents=True, exist_ok=True)
        values = [{"id": i, "required": False} for i in items]
        path.write_text(json.dumps({"replace": False, "values": values}, indent=2) + "\n", encoding="utf-8")
        print(f"{branch:11} {len(items):3}  -> {TAG_FILES[branch]}")
    if unmapped:
        print("UNMAPPED:", ", ".join(unmapped))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
