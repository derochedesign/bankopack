# Boot the test server once, generate several 256x256 areas, and report height + steepness stats.
# Areas: the nearest Tectonic mountain range, the nearest badlands plateau, and fixed points.
# Usage: terrainstats.py <server_dir>
import subprocess, sys, time, threading, re, atexit, signal
srv = sys.argv[1]
p = subprocess.Popen(["java", "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.256/win_args.txt", "nogui"],
                     cwd=srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
atexit.register(lambda: p.poll() is None and p.kill())
signal.signal(signal.SIGTERM, lambda *a: sys.exit(1))
lines = []; done = threading.Event()
def reader():
    for line in p.stdout:
        lines.append(line)
        if "Done (" in line or "Preparing crash report" in line: done.set()
threading.Thread(target=reader, daemon=True).start()
def cmd(c, wait=0.0): p.stdin.write(c + "\n"); p.stdin.flush(); time.sleep(wait)
t0 = time.time()
while not done.is_set() and time.time() - t0 < 600: time.sleep(1)

def locate(command):
    mark = len(lines); cmd(command)
    for _ in range(120):
        for l in lines[mark:]:
            if m := re.search(r"is at \[(-?\d+), (?:~|-?\d+), (-?\d+)\]", l): return int(m.group(1)), int(m.group(2))
            if "Couldn't find" in l or "Could not find" in l: return None
        time.sleep(0.5)

def sample(cx, cz):
    x0, z0 = (cx - 128) // 16 * 16, (cz - 128) // 16 * 16   # chunk-aligned: forceload caps at 256 chunks
    cmd(f"forceload add {x0} {z0} {x0+255} {z0+255}")
    for _ in range(120):
        time.sleep(5); mark = len(lines)
        cmd(f"execute positioned {x0+250} 0 {z0+250} positioned over world_surface run setblock ~ ~ ~ minecraft:glass", 2)
        if any("Changed the block" in l for l in lines[mark:]): break
    mark = len(lines)
    for x in range(x0, x0 + 256, 8):          # 8-block grid: catches cliffs a 16-block grid can miss
        for z in range(z0, z0 + 256, 8):
            cmd(f"execute positioned {x} 0 {z} positioned over world_surface run setblock ~ ~ ~ minecraft:glass")
    time.sleep(8)
    pts = {(int(m.group(1)), int(m.group(3))): int(m.group(2)) for l in lines[mark:]
           if (m := re.search(r"Changed the block at (-?\d+), (-?\d+), (-?\d+)", l))}
    cmd("forceload remove all", 1)
    d = [abs(pts[(x, z)] - pts[(x + 8, z)]) for (x, z) in pts if (x + 8, z) in pts] + \
        [abs(pts[(x, z)] - pts[(x, z + 8)]) for (x, z) in pts if (x, z + 8) in pts]
    if not d: return f"no samples ({len(pts)} points)"
    d.sort(); ys = sorted(pts.values())
    return f"Y median={ys[len(ys)//2]} max={ys[-1]} | per 8 blocks: mean={sum(d)/len(d):.1f} p95={d[int(.95*len(d))]} max={d[-1]} | sheer (>=24 per 8, ~70deg): {100*sum(1 for v in d if v >= 24)/len(d):.1f}%"

areas = [("mountain_range", locate("tectonic locate mountain_range")), ("arid_highlands", locate("locate biome terralith:arid_highlands")),
         ("badlands_plateaus", locate("tectonic locate badlands_plateaus")),
         ("random", (3000, -2000))]
for name, c in areas:
    print(f"  {name:18} {sample(*c) if c else 'not found'}", flush=True)
cmd("stop")
try: p.wait(timeout=180)
except subprocess.TimeoutExpired: p.kill()
