# -*- coding: utf-8 -*-
"""Monitor simples de portas MT5 para capturar aberturas/fechamentos"""

import psutil
import time
from collections import defaultdict
from datetime import datetime

print("="*70)
print("🔍 MONITORANDO TODAS AS PORTAS MT5 - Inicie o backtest agora!")
print("="*70)
print("⏱️  Monitorando por 90 segundos...")
print()

port_history = defaultdict(list)
state_changes = []
all_ports_seen = set()
established_ports = set()

start_time = time.time()
last_snapshot = {}
iteration = 0

while time.time() - start_time < 90:
    iteration += 1
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Buscar processos MT5
    mt5_pids = {}
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = proc.info["name"].lower() if proc.info["name"] else ""
            if any(x in name for x in ["terminal64", "metatester"]):
                mt5_pids[proc.info["pid"]] = proc.info["name"]
        except:
            continue
    
    # Buscar conexões
    current = {}
    for conn in psutil.net_connections():
        try:
            if conn.pid and conn.pid in mt5_pids:
                port = conn.laddr.port if conn.laddr else 0
                key = (conn.pid, port, conn.status)
                current[key] = {
                    "pid": conn.pid,
                    "process": mt5_pids[conn.pid],
                    "port": port,
                    "status": conn.status,
                    "remote": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                }
                all_ports_seen.add(port)
                if conn.status == "ESTABLISHED":
                    established_ports.add(port)
        except:
            continue
    
    # Detectar mudanças
    for key, conn in current.items():
        if key not in last_snapshot:
            emoji = "🟢" if conn["status"] == "ESTABLISHED" else "🔵" if conn["status"] == "LISTEN" else "🟡"
            print(f"{emoji} [{timestamp}] NOVA: {conn['process']} | Porta {conn['port']} | {conn['status']} | Remote: {conn['remote']}")
            state_changes.append(("NEW", conn))
    
    for key in last_snapshot:
        if key not in current:
            old = last_snapshot[key]
            print(f"🔴 [{timestamp}] FECHOU: {old['process']} | Porta {old['port']} | {old['status']}")
            state_changes.append(("CLOSED", old))
    
    last_snapshot = current
    time.sleep(0.3)

print()
print("="*70)
print("📊 RELATÓRIO FINAL")
print("="*70)
print(f"Portas vistas: {sorted(all_ports_seen)}")
print(f"Portas com ESTABLISHED: {sorted(established_ports)}")
print(f"Total de mudanças: {len(state_changes)}")
print()
print("💡 MUDANÇAS DETECTADAS:")
for change_type, conn in state_changes:
    marker = "➕" if change_type == "NEW" else "➖"
    print(f"   {marker} {change_type}: Porta {conn['port']} ({conn['status']}) - {conn['process']}")

print()
print("="*70)
if established_ports:
    print(f"✅ RECOMENDAÇÃO: Use a porta {min(established_ports)} para monitoramento!")
else:
    print("⚠️ Nenhuma conexão ESTABLISHED detectada durante o backtest")
    print("   O MT5 pode estar usando outro método de comunicação")
print("="*70)
