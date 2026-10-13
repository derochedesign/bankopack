"""Collect item/block/entity/dimension/advancement IDs from all mod jars (for validating quest tasks)."""
import json, re, sys, zipfile, pathlib
mods = pathlib.Path(sys.argv[1]); out = {"item": set(), "entity": set(), "dimension": set(), "advancement": set()}
import io
def jars():
    for jar in mods.glob("*.jar"):
        try: z = zipfile.ZipFile(jar)
        except Exception: continue
        yield z
        for n in z.namelist():  # nested jars (jar-in-jar), e.g. Create Aeronautics' bundled modules
            if n.startswith(("META-INF/jarjar/", "META-INF/jars/")) and n.endswith(".jar"):
                try: yield zipfile.ZipFile(io.BytesIO(z.read(n)))
                except Exception: pass
for z in jars():
    for n in z.namelist():
        if re.fullmatch(r"assets/[a-z0-9_.-]+/lang/en_us\.json", n):
            try: d = json.loads(z.read(n).decode("utf-8", "replace"))
            except Exception: continue
            for k in d:
                p = k.split(".")
                if len(p) == 3 and p[0] in ("item", "block"): out["item"].add(f"{p[1]}:{p[2]}")
                if len(p) == 3 and p[0] == "entity": out["entity"].add(f"{p[1]}:{p[2]}")
        elif m := re.fullmatch(r"data/([a-z0-9_.-]+)/dimension/([a-z0-9_/.-]+)\.json", n):
            out["dimension"].add(f"{m.group(1)}:{m.group(2)}")
        elif m := re.fullmatch(r"data/([a-z0-9_.-]+)/advancements?/([a-z0-9_/.-]+)\.json", n):
            out["advancement"].add(f"{m.group(1)}:{m.group(2)}")
out["dimension"] |= {"minecraft:overworld", "minecraft:the_nether", "minecraft:the_end"}
json.dump({k: sorted(v) for k, v in out.items()}, open(sys.argv[2], "w"), indent=0)
print({k: len(v) for k, v in out.items()})
