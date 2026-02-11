import os
import json
import time
import subprocess

# Pfad zur Web-Statistik
STATS_FILE = "/var/www/html/stats.json"

def get_stats():
    # 1. Sockets zählen (ESTABLISHED auf Port 80)
    cmd = "ss -ant | grep :80 | grep ESTAB | wc -l"
    sockets = subprocess.check_output(cmd, shell=True).decode().strip()

    # 2. CPU Load (1 Min Durchschnitt)
    load = os.getloadavg()[0]

    # 3. RAM Verbrauch (in MB)
    with open('/proc/meminfo', 'r') as f:
        mem = f.readlines()
        total = int(mem[0].split()[1]) / 1024
        free = int(mem[2].split()[1]) / 1024
        used = total - free

    return {
        "sockets": sockets,
        "load": round(load, 2),
        "ram_used": round(used, 2),
        "time": time.strftime("%H:%M:%S")
    }

print("Monitoring gestartet... (Strg+C zum Beenden)")
while True:
    data = get_stats()
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f)
    time.sleep(1) # Jede Sekunde aktualisieren