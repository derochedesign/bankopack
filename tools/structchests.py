# Boot the test server, locate a structure in a dimension, generate the area, and count chest-type
# blocks in it (vanilla chests vs Lootr chests etc.) using non-destructive "clone ... filtered" tricks.
# Usage: structchests.py <server_dir> <dimension> <structure_id> [radius] [y_min] [y_max]
import subprocess, sys, time, threading, re, atexit, signal

srv, dim, structure = sys.argv[1], sys.argv[2], sys.argv[3]
radius = int(sys.argv[4]) if len(sys.argv) > 4 else 48
y_min = int(sys.argv[5]) if len(sys.argv) > 5 else 0
y_max = int(sys.argv[6]) if len(sys.argv) > 6 else 160
BLOCKS = ["minecraft:chest", "minecraft:trapped_chest", "minecraft:barrel", "minecraft:shulker_box",
          "lootr:lootr_chest", "lootr:lootr_trapped_chest", "lootr:lootr_barrel", "lootr:lootr_shulker",
          "minecraft:end_rod", "minecraft:purpur_block"]

p = subprocess.Popen(["java", "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.256/win_args.txt", "nogui"],
                     cwd=srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, encoding="utf-8", errors="replace")
atexit.register(lambda: p.poll() is None and p.kill())
signal.signal(signal.SIGTERM, lambda *a: sys.exit(1))
lines, done = [], threading.Event()
def reader():
    for line in p.stdout:
        lines.append(line)
        if "Done (" in line or "Preparing crash report" in line: done.set()
threading.Thread(target=reader, daemon=True).start()
def cmd(c, wait=0.0): p.stdin.write(c + "\n"); p.stdin.flush(); time.sleep(wait)
def wait_for(pred, timeout=120):
    t = time.time()
    while time.time() - t < timeout:
        for l in list(lines):
            r = pred(l)
            if r: return r
        time.sleep(0.5)

t0 = time.time()
while not done.is_set() and time.time() - t0 < 600: time.sleep(1)

mark = len(lines)
cmd(f"execute in {dim} run locate structure {structure}")
loc = None
for _ in range(240):
    for l in lines[mark:]:
        if m := re.search(r"is at \[(-?\d+), (?:~|-?\d+), (-?\d+)\]", l): loc = (int(m.group(1)), int(m.group(2)))
        if "Could not find" in l: loc = "none"
    if loc: break
    time.sleep(0.5)
print("located:", loc, flush=True)
if not isinstance(loc, tuple): cmd("stop"); p.wait(); sys.exit(1)

cx, cz = loc
x0, z0 = (cx - radius) // 16 * 16, (cz - radius) // 16 * 16
x1, z1 = x0 + 2 * radius + 15, z0 + 2 * radius + 15
cmd(f"execute in {dim} run forceload add {x0} {z0} {x1} {z1}", 2)
# wait for generation: probe the far corner
for _ in range(120):
    mark = len(lines)
    cmd(f"execute in {dim} positioned {x1} 0 {z1} run fill ~ {y_max} ~ ~ {y_max} ~ minecraft:air", 3)
    if any("filled" in l or "No blocks were filled" in l for l in lines[mark:]): break
time.sleep(5)

# Count each block type: "fill <box> structure_void replace <block>" reports how many blocks matched.
# The test world is thrown away afterwards, so nothing is restored.
def is_reply(l): return "Successfully filled" in l or "No blocks were filled" in l or "Too many blocks" in l
for b in BLOCKS:
    boxes = [f"{xs} {y} {zs} {min(xs+31, x1)} {min(y+7, y_max)} {min(zs+31, z1)}"
             for y in range(y_min, y_max, 8) for xs in range(x0, x1 + 1, 32) for zs in range(z0, z1 + 1, 32)]
    mark = len(lines)
    for box in boxes:
        cmd(f"execute in {dim} run fill {box} minecraft:structure_void replace {b}")
    t = time.time()
    while sum(1 for l in lines[mark:] if is_reply(l)) < len(boxes) and time.time() - t < 120: time.sleep(0.3)
    total = sum(int(m.group(1)) for l in lines[mark:] if (m := re.search(r"Successfully filled (\d+) block", l)))
    print(f"  {b:28} {total}", flush=True)

cmd("forceload remove all", 1); cmd("stop")
try: p.wait(timeout=180)
except subprocess.TimeoutExpired: p.kill()
