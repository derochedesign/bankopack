# Wait for the Minecraft client to exit, then resolve keybind conflicts in the Prism instance's options.txt.
import subprocess, time, os, re, sys
opts = os.path.expandvars(r"%APPDATA%\PrismLauncher\instances\Bankopack\minecraft\options.txt")
UNBIND = ["key_key.ftbchunks.map",                    # M: keep Xaero's world map
          "key_key.constructionwand.void_sack_toggle", # M
          "key_iris.keybind.shaderPackSelection",      # O: conflicts with Cobblemon hide party
          "key_iris.keybind.reload"]                   # R: Cobblemon throw
def running():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process -Filter \"Name='javaw.exe' or Name='java.exe'\" | Where-Object { $_.CommandLine -match 'net.minecraft.client.main.Main' } | Measure-Object | % Count"],
        capture_output=True, text=True).stdout.strip()
    return out not in ("", "0")
while running(): time.sleep(10)
time.sleep(3)
s = open(opts, encoding="utf-8").read()
for k in UNBIND:
    s, n = re.subn(rf"(?m)^{re.escape(k)}:.*$", f"{k}:key.keyboard.unknown", s)
    print(f"{k}: {'unbound' if n else 'not found'}")
open(opts, "w", encoding="utf-8").write(s)
