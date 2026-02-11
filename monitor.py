import os
import json
import time
import subprocess
import requests

# KONFIGURATION
STATS_FILE = "/var/www/html/stats.json"
TARGET_URL = "http://localhost/server-status?auto" # Erfordert mod_status

def get_metrics():
    metrics = {
        "sockets": 0,
        "load": 0.0,
        "ram_used": 0,
        "apache_r": 0,
        "latency": 0,
        "time": time.strftime("%H:%M:%S")
    }

    try:
        # 1. Sockets zählen (ESTABLISHED auf Port 80/443)
        cmd = "ss -ant | grep -E ':80|:443' | grep ESTAB | wc -l"
        metrics["sockets"] = int(subprocess.check_output(cmd, shell=True).decode().strip())

        # 2. CPU Load & RAM
        metrics["load"] = round(os.getloadavg()[0], 2)
        with open('/proc/meminfo', 'r') as f:
            mem = f.readlines()
            total = int(mem[0].split()[1]) / 1024
            free = int(mem[2].split()[1]) / 1024
            metrics["ram_used"] = int(total - free)

        # 3. Apache Worker & Latenz
        start_time = time.time()
        response = requests.get(TARGET_URL, timeout=1)
        metrics["latency"] = round((time.time() - start_time) * 1000)

# Zähle 'R' (Reading) im Scoreboard
        for line in response.text.split('\n'):
            if line.startswith('Scoreboard:'):
                metrics["apache_r"] = line.count('R')

    except Exception as e:
        print(f"Fehler beim Sammeln: {e}")
        metrics["latency"] = -1 # Signalisiert Server-Hänger

    return metrics

print("Stress-Monitor läuft... Drücke Strg+C zum Beenden.")
while True:
    data = get_metrics()
    with open(STATS_FILE, 'w') as f:
        json.dump(data, f)
    time.sleep(1)