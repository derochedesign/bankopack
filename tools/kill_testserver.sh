#!/usr/bin/env bash
# Stop any test-server JVMs (identified by NeoForge's win_args launch file) and wait until they're gone.
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -match 'win_args' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" >/dev/null 2>&1
for _ in $(seq 30); do
  n=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -match 'win_args' } | Measure-Object).Count")
  [ "${n//[$'\r\n ']/}" = "0" ] && exit 0; sleep 1
done
