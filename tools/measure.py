# Boot test server, locate a Tectonic mountain range, generate a 256x256 area there,
# sample surface heights on a 16-block grid, and report stats. Usage: measure.py <server_dir> <max_y>
import subprocess, sys, time, threading, re, statistics
srv, max_y = sys.argv[1], int(sys.argv[2])
p = subprocess.Popen(["java", "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.256/win_args.txt", "nogui"],
                     cwd=srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
lines = []; done = threading.Event()
def reader():
    for line in p.stdout:
        lines.append(line)
        if "Done (" in line: done.set()
        if "Preparing crash report" in line: print(line); done.set()
threading.Thread(target=reader, daemon=True).start()
def cmd(c, wait=1.0): p.stdin.write(c + "\n"); p.stdin.flush(); time.sleep(wait)
t0 = time.time()
while not done.is_set() and time.time() - t0 < 600: time.sleep(1)
cmd("tectonic locate mountain_range", 5)
m = next((re.search(r"\[(-?\d+), ~, (-?\d+)\]", l) for l in lines if "mountain_range is at" in l), None)
if not m: print("locate failed"); cmd("stop"); p.wait(); sys.exit(1)
cx, cz = int(m.group(1)), int(m.group(2)); print(f"mountain range at {cx},{cz}")
x0, z0 = cx - 128, cz - 128
cmd(f"forceload add {x0} {z0} {x0+255} {z0+255}", 1)
t1 = time.time(); n0 = len(lines)
# wait for generation: poll by sampling the far corner until it reports a sane height
for _ in range(120):
    time.sleep(5)
    mark = len(lines); cmd(f"execute positioned {x0+250} 0 {z0+250} positioned over world_surface run setblock ~ ~ ~ minecraft:glass", 2)
    if any("Changed the block" in l for l in lines[mark:]): break
gen = int(time.time() - t1)
mark = len(lines)
for x in range(x0, x0 + 256, 16):
    for z in range(z0, z0 + 256, 16):
        cmd(f"execute positioned {x} 0 {z} positioned over world_surface run setblock ~ ~ ~ minecraft:glass", 0.02)
time.sleep(5)
ys = [int(r.group(1)) for l in lines[mark:] if (r := re.search(r"Changed the block at -?\d+, (-?\d+), -?\d+", l))]
cmd("forceload remove all", 1); cmd("stop", 1)
try: p.wait(timeout=180)
except subprocess.TimeoutExpired: p.kill()
ys.sort()
print(f"generated 256 chunks in ~{gen}s; samples={len(ys)}")
if ys:
    q = lambda f: ys[min(len(ys)-1, int(f*len(ys)))]
    print(f"surface Y: min={ys[0]} median={q(.5)} p90={q(.9)} p99={q(.99)} max={ys[-1]}  (build limit {max_y})")
    print(f"samples within 8 blocks of limit: {sum(1 for y in ys if y >= max_y - 9)}")
