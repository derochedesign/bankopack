# Boot the test server, wait for "Done" (or crash/timeout), optionally run commands, then stop.
import subprocess, sys, time, threading, os
srv = sys.argv[1]; cmds = sys.argv[2:]; timeout = 900
p = subprocess.Popen(["java", "@user_jvm_args.txt", "@libraries/net/neoforged/neoforge/21.1.256/win_args.txt", "nogui"],
                     cwd=srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
done = threading.Event(); crashed = threading.Event(); start = time.time()
def reader():
    for line in p.stdout:
        if any(k in line for k in ("ERROR", "Exception", "FATAL", "Done (", "WARN] [mixin", "Crash")):
            print(line.rstrip()[:300], flush=True)
        if "Done (" in line: done.set()
        if "Preparing crash report" in line: crashed.set()
threading.Thread(target=reader, daemon=True).start()
while not done.is_set() and not crashed.is_set() and p.poll() is None and time.time() - start < timeout: time.sleep(1)
if done.is_set():
    for c in cmds:
        p.stdin.write(c + "\n"); p.stdin.flush()
        if c.startswith("wait"): time.sleep(int(c.split()[1]))
        else: time.sleep(2)
    p.stdin.write("stop\n"); p.stdin.flush()
if crashed.is_set(): time.sleep(5); p.kill()
try: p.wait(timeout=180)
except subprocess.TimeoutExpired: p.kill(); print("KILLED after stop timeout")
print(f"exit={p.returncode} booted={done.is_set()} crashed={crashed.is_set()} elapsed={int(time.time()-start)}s")
