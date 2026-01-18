# -*- coding: utf-8 -*-
"""
🔍 DETECTOR DE PORTAS MT5 - Script de Diagnóstico
Monitora todas as conexões de rede usadas pelo MetaTrader 5 e MetaTester
"""

import psutil
import time
from collections import defaultdict
from datetime import datetime

def get_mt5_connections():
    """Obtém todas as conexões de rede relacionadas ao MT5"""
    connections = []
    mt5_processes = {}
    
    # Primeiro, encontrar todos os processos MT5/metatester
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            if any(x in name for x in ['terminal64', 'metatester', 'metaeditor', 'metatrader']):
                mt5_processes[proc.info['pid']] = {
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent']
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Agora buscar conexões desses processos
    try:
        for conn in psutil.net_connections():
            if conn.pid and conn.pid in mt5_processes:
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                
                connections.append({
                    'pid': conn.pid,
                    'process': mt5_processes[conn.pid]['name'],
                    'cpu': mt5_processes[conn.pid]['cpu'],
                    'status': conn.status,
                    'local': local_addr,
                    'remote': remote_addr,
                    'local_port': conn.laddr.port if conn.laddr else 0,
                    'family': 'IPv4' if conn.family.name == 'AF_INET' else 'IPv6'
                })
    except (psutil.AccessDenied, Exception) as e:
        print(f"⚠️ Erro ao acessar conexões: {e}")
    
    return connections, mt5_processes

def monitor_mt5_activity(duration=60, interval=1):
    """Monitora atividade de rede do MT5 por um período"""
    print("="*70)
    print("🔍 DETECTOR DE PORTAS MT5 - MONITORAMENTO EM TEMPO REAL")
    print("="*70)
    print(f"⏱️  Duração: {duration} segundos | Intervalo: {interval}s")
    print("="*70)
    
    # Histórico para análise
    port_history = defaultdict(list)  # porta -> lista de status
    state_changes = []  # mudanças de estado
    all_ports_seen = set()
    established_ports = set()
    
    start_time = time.time()
    last_snapshot = {}
    iteration = 0
    
    print("\n🚀 Inicie o backtest agora para capturar as conexões!\n")
    print("-"*70)
    
    while time.time() - start_time < duration:
        iteration += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        connections, processes = get_mt5_connections()
        
        # Mostrar processos MT5 ativos
        if iteration == 1 or iteration % 10 == 0:
            print(f"\n📋 [{timestamp}] Processos MT5 detectados:")
            for pid, info in processes.items():
                print(f"   PID {pid}: {info['name']} (CPU: {info['cpu']:.1f}%)")
        
        # Agrupar por processo e status
        current_snapshot = {}
        for conn in connections:
            key = (conn['pid'], conn['local_port'], conn['status'])
            current_snapshot[key] = conn
            all_ports_seen.add(conn['local_port'])
            
            # Registrar histórico
            port_history[conn['local_port']].append({
                'time': timestamp,
                'status': conn['status'],
                'process': conn['process'],
                'remote': conn['remote']
            })
            
            # Detectar ESTABLISHED
            if conn['status'] == 'ESTABLISHED':
                established_ports.add(conn['local_port'])
        
        # Detectar mudanças
        for key, conn in current_snapshot.items():
            if key not in last_snapshot:
                state_changes.append({
                    'time': timestamp,
                    'type': 'NEW',
                    'conn': conn
                })
                emoji = "🟢" if conn['status'] == 'ESTABLISHED' else "🔵"
                print(f"{emoji} [{timestamp}] NOVA: {conn['process']} | "
                      f"Porta {conn['local_port']} | {conn['status']} | "
                      f"Remote: {conn['remote']}")
        
        for key in last_snapshot:
            if key not in current_snapshot:
                old_conn = last_snapshot[key]
                state_changes.append({
                    'time': timestamp,
                    'type': 'CLOSED',
                    'conn': old_conn
                })
                print(f"🔴 [{timestamp}] FECHOU: {old_conn['process']} | "
                      f"Porta {old_conn['local_port']} | {old_conn['status']}")
        
        last_snapshot = current_snapshot
        
        # Status resumido a cada 5 segundos
        if iteration % 5 == 0:
            active_established = [c for c in connections if c['status'] == 'ESTABLISHED']
            active_listen = [c for c in connections if c['status'] == 'LISTEN']
            print(f"📊 [{timestamp}] Status: {len(active_listen)} LISTEN | "
                  f"{len(active_established)} ESTABLISHED | "
                  f"Portas vistas: {sorted(all_ports_seen)}")
        
        time.sleep(interval)
    
    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO FINAL DE ANÁLISE")
    print("="*70)
    
    print(f"\n🔢 Total de portas detectadas: {len(all_ports_seen)}")
    print(f"   Portas: {sorted(all_ports_seen)}")
    
    print(f"\n🟢 Portas com ESTABLISHED: {len(established_ports)}")
    if established_ports:
        print(f"   Portas: {sorted(established_ports)}")
    else:
        print("   ⚠️ NENHUMA PORTA ESTABELECEU CONEXÃO!")
    
    print(f"\n📝 Total de mudanças de estado: {len(state_changes)}")
    
    # Análise por porta
    print("\n📈 ANÁLISE POR PORTA:")
    print("-"*70)
    for port in sorted(all_ports_seen):
        history = port_history[port]
        statuses = set(h['status'] for h in history)
        processes = set(h['process'] for h in history)
        
        had_established = 'ESTABLISHED' in statuses
        marker = "✅" if had_established else "❌"
        
        print(f"   {marker} Porta {port}:")
        print(f"      Processos: {', '.join(processes)}")
        print(f"      Estados vistos: {', '.join(statuses)}")
        print(f"      Ocorrências: {len(history)}")
    
    # Recomendação
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÃO:")
    print("="*70)
    
    if established_ports:
        best_port = max(established_ports, key=lambda p: 
            len([h for h in port_history[p] if h['status'] == 'ESTABLISHED']))
        print(f"   ✅ Use a porta {best_port} para detecção!")
        print(f"   Esta porta teve conexões ESTABLISHED durante o backtest.")
    else:
        # Verificar se há portas que aparecem/desaparecem
        changing_ports = [p for p, h in port_history.items() if len(h) > 5]
        if changing_ports:
            print(f"   ⚠️ Portas com atividade: {sorted(changing_ports)}")
            print("   Considere monitorar essas portas ou usar CPU/processo.")
        else:
            print("   ❌ Não foi detectada nenhuma conexão ESTABLISHED!")
            print("   Sugestões:")
            print("   1. Verifique se o backtest realmente iniciou")
            print("   2. O MT5 pode não usar conexões TCP para backtests locais")
            print("   3. Considere usar detecção por CPU ou processo")
    
    return {
        'all_ports': all_ports_seen,
        'established_ports': established_ports,
        'state_changes': state_changes,
        'port_history': dict(port_history)
    }

def quick_scan():
    """Scan rápido das conexões atuais"""
    print("="*70)
    print("🔍 SCAN RÁPIDO - Conexões MT5 Atuais")
    print("="*70)
    
    connections, processes = get_mt5_connections()
    
    if not processes:
        print("❌ Nenhum processo MT5 encontrado!")
        print("   Certifique-se que o MetaTrader 5 está aberto.")
        return
    
    print(f"\n📋 Processos MT5 ({len(processes)}):")
    for pid, info in processes.items():
        print(f"   PID {pid}: {info['name']}")
    
    if not connections:
        print("\n❌ Nenhuma conexão de rede encontrada!")
        return
    
    print(f"\n🌐 Conexões ({len(connections)}):")
    print("-"*70)
    print(f"{'PID':<8} {'Processo':<18} {'Status':<12} {'Local':<22} {'Remote':<22}")
    print("-"*70)
    
    for conn in sorted(connections, key=lambda x: (x['process'], x['local_port'])):
        print(f"{conn['pid']:<8} {conn['process']:<18} {conn['status']:<12} "
              f"{conn['local']:<22} {conn['remote']:<22}")
    
    # Resumo por porta
    ports = defaultdict(list)
    for conn in connections:
        ports[conn['local_port']].append(conn['status'])
    
    print(f"\n📊 Resumo por Porta:")
    for port in sorted(ports.keys()):
        statuses = ports[port]
        print(f"   Porta {port}: {', '.join(set(statuses))} ({len(statuses)}x)")

def monitor_during_backtest():
    """Modo especial: monitora durante um backtest completo"""
    print("="*70)
    print("🎯 MODO BACKTEST - Detecção Automática de Porta")
    print("="*70)
    print("\n⚡ Este modo vai detectar qual porta o MT5 usa durante backtest")
    print("📋 Instruções:")
    print("   1. Tenha o MT5 aberto com Strategy Tester")
    print("   2. Pressione ENTER para começar a monitorar")
    print("   3. INICIE o backtest manualmente no MT5")
    print("   4. Aguarde o backtest terminar")
    print("   5. Veja o relatório de portas usadas")
    print("-"*70)
    
    input("\n🔔 Pressione ENTER para iniciar o monitoramento...")
    
    print("\n⏳ Capturando estado ANTES do backtest...")
    before_conns, _ = get_mt5_connections()
    before_ports = set(c['local_port'] for c in before_conns)
    before_established = set(c['local_port'] for c in before_conns if c['status'] == 'ESTABLISHED')
    
    print(f"   Portas ativas: {sorted(before_ports)}")
    print(f"   Com ESTABLISHED: {sorted(before_established)}")
    
    print("\n🚀 INICIE O BACKTEST AGORA!")
    print("⏱️  Monitorando por 120 segundos (ou Ctrl+C para parar)...\n")
    
    try:
        result = monitor_mt5_activity(duration=120, interval=0.5)
        
        # Comparar
        new_established = result['established_ports'] - before_established
        if new_established:
            print(f"\n🎯 PORTAS NOVAS COM ESTABLISHED: {sorted(new_established)}")
            print("   USE UMA DESSAS PORTAS NO MONITOR!")
    except KeyboardInterrupt:
        print("\n\n⚠️ Monitoramento interrompido pelo usuário")

def main():
    """Menu principal"""
    while True:
        print("\n" + "="*50)
        print("🔍 DETECTOR DE PORTAS MT5")
        print("="*50)
        print("1. 📷 Scan rápido (estado atual)")
        print("2. ⏱️  Monitorar por 30 segundos")
        print("3. ⏱️  Monitorar por 60 segundos")
        print("4. 🎯 Modo Backtest (detectar porta ideal)")
        print("5. 🚪 Sair")
        print("="*50)
        
        try:
            opcao = input("Opção: ").strip()
            
            if opcao == "1":
                quick_scan()
            elif opcao == "2":
                monitor_mt5_activity(duration=30, interval=0.5)
            elif opcao == "3":
                monitor_mt5_activity(duration=60, interval=0.5)
            elif opcao == "4":
                monitor_during_backtest()
            elif opcao == "5":
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida!")
            
            input("\nPressione ENTER para continuar...")
            
        except KeyboardInterrupt:
            print("\n👋 Interrompido!")
            break

if __name__ == "__main__":
    main()
