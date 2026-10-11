"""Generate data overrides that tone down crit chance from the two crit systems in the pack.

The pack has two independent crit systems: Critical Strike (RPG Series) and Apothic Attributes
(Apotheosis). This copies the relevant JSON from each mod's jar, scales the crit-chance values, and
writes them into this mod's resources at the same paths, so they override the originals (this mod
declares ordering AFTER both mods). The innate Critical Strike bonus is a config value, shipped
separately in pack/config/critical_strike/server_config.json.

Usage: python gen_crit_tuning.py <mods dir> <output resources dir>
"""
import glob
import json
import pathlib
import sys
import zipfile

APOTH_SCALE = 0.75          # Apotheosis crit affix + gem values
CRIT_ENCHANT_PER_LEVEL = 0.03  # Critical Strike "Critical Hit" enchantment (default 0.04 per level)

APOTH_FILES = [
    "data/apotheosis/affixes/melee/attribute/intricate.json",
    "data/apotheosis/gems/core/samurai.json",
]
CRIT_ENCHANT = "data/critical_strike/enchantment/chance.json"


def jar(mods_dir, pattern):
    matches = glob.glob(str(pathlib.Path(mods_dir) / pattern))
    if len(matches) != 1:
        sys.exit(f"expected one jar for {pattern}, found {matches}")
    return zipfile.ZipFile(matches[0])


def scale_crit_values(node):
    """Scale every number under 'values' of entries whose attribute is apothic_attributes:crit_chance."""
    if isinstance(node, dict):
        if node.get("attribute") == "apothic_attributes:crit_chance" and "values" in node:
            node["values"] = scale_numbers(node["values"])
        for v in node.values():
            scale_crit_values(v)
    elif isinstance(node, list):
        for v in node:
            scale_crit_values(v)


def scale_numbers(node):
    if isinstance(node, dict):
        if "min" in node and "max" in node:
            # Apotheosis interpolates ranges in 0.01 steps, so (max - min) must be a multiple of 0.01.
            return {**node, "min": round(node["min"] * APOTH_SCALE, 2), "max": round(node["max"] * APOTH_SCALE, 2)}
        return {k: scale_numbers(v) for k, v in node.items()}
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        return round(node * APOTH_SCALE, 4)
    return node


def write(out_dir, path, data):
    target = pathlib.Path(out_dir) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("wrote", path)


def main(mods_dir, out_dir):
    with jar(mods_dir, "Apotheosis-*.jar") as apoth:
        for path in APOTH_FILES:
            data = json.loads(apoth.read(path))
            scale_crit_values(data)
            write(out_dir, path, data)

    with jar(mods_dir, "critical_strike-*.jar") as crit:
        data = json.loads(crit.read(CRIT_ENCHANT))
        for effect in data["effects"]["minecraft:attributes"]:
            if effect["attribute"] == "critical_strike:chance":
                effect["amount"]["base"] = CRIT_ENCHANT_PER_LEVEL
                effect["amount"]["per_level_above_first"] = CRIT_ENCHANT_PER_LEVEL
        write(out_dir, CRIT_ENCHANT, data)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
