# Boot test server and sample biome categories on a grid (no chunk generation needed).
# Usage: landratio.py <server_dir> [spacing] [count]
import subprocess, sys, time, threading
srv = sys.argv[1]; sp = int(sys.argv[2]) if len(sys.argv) > 2 else 500; n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
p = subprocess.Popen(["java", "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.256/win_args.txt", "nogui"],
                     cwd=srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
lines = []; done = threading.Event()
def reader():
    for line in p.stdout:
        lines.append(line)
        if "Done (" in line or "Preparing crash report" in line: done.set()
threading.Thread(target=reader, daemon=True).start()
t0 = time.time()
while not done.is_set() and time.time() - t0 < 600: time.sleep(1)
def cmd(c): p.stdin.write(c + "\n"); p.stdin.flush()
half = n * sp // 2
pts = [(x, z) for x in range(-half, half, sp) for z in range(-half, half, sp)]
res = {"minecraft:is_ocean": 0, "minecraft:is_beach": 0, "minecraft:is_river": 0}
def count(mark): return sum(1 for l in lines[mark:] if "Test passed" in l or "Test failed" in l or "not loaded" in l)
B = 100
for i in range(0, len(pts), B):
    batch = pts[i:i+B]
    for x, z in batch: cmd(f"forceload add {x} {z}")
    for tag in res:  # query until every point in the batch answers passed/failed (not "not loaded")
        while True:
            mark = len(lines)
            for x, z in batch: cmd(f"execute if biome {x} 63 {z} #{tag}")
            while count(mark) < len(batch): time.sleep(0.3)
            if not any("not loaded" in l for l in lines[mark:]): break
            time.sleep(3)
        res[tag] += sum(1 for l in lines[mark:] if "Test passed" in l)
    cmd("forceload remove all"); print(f"  {i+len(batch)}/{len(pts)} points", flush=True)
cmd("stop")
try: p.wait(timeout=180)
except subprocess.TimeoutExpired: p.kill()
tot = len(pts); o, b, r = res["minecraft:is_ocean"], res["minecraft:is_beach"], res["minecraft:is_river"]
print(f"{tot} points over {n*sp}x{n*sp} blocks: ocean {100*o/tot:.0f}%  beach {100*b/tot:.0f}%  river {100*r/tot:.0f}%  land {100*(tot-o-b-r)/tot:.0f}%")
