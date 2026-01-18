#!/usr/bin/env python3
"""
Monitor Alternativo - Detecta backtest por mudanças de processo
Funciona mesmo quando não há conexões ESTABLISHED
"""

import psutil
import time
from datetime import datetime
from collections import defaultdict

class BacktestMonitorAlternativo:
    def __init__(self, port=3000, poll_interval=0.2, verbose=True):
        self.port = port
        self.poll_interval = poll_interval
        self.verbose = verbose
        self._active = False
        self._state = 'IDLE'  # IDLE | WAITING | RUNNING
        self._start_time = None
        self._baseline_pids = set()
        self._current_pids = set()
        self._last_change_time = None
        self._backtest_detected = False
        self._finished = False
        
    def _get_port_processes(self):
        """Retorna conjunto de PIDs que estão usando a porta"""
        pids = set()
        process_info = {}
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == self.port:
                    if conn.pid:
                        pids.add(conn.pid)
                        if conn.pid not in process_info:
                            try:
                                proc = psutil.Process(conn.pid)
                                process_info[conn.pid] = {
                                    'name': proc.name(),
                                    'status': conn.status,
                                    'create_time': proc.create_time()
                                }
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                process_info[conn.pid] = {
                                    'name': 'Unknown',
                                    'status': conn.status,
                                    'create_time': time.time()
                                }
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Erro ao obter processos: {e}")
                
        return pids, process_info
    
    def start(self):
        """Inicia o monitoramento"""
        if self.verbose:
            print(f"🎯 Iniciando monitor alternativo porta {self.port}...")
        
        self._start_time = time.time()
        self._active = True
        self._state = 'WAITING'
        self._finished = False
        
        # Capturar baseline de processos
        self._baseline_pids, baseline_info = self._get_port_processes()
        
        if self.verbose:
            print(f"📊 Baseline: {len(self._baseline_pids)} processo(s) na porta {self.port}")
            for pid, info in baseline_info.items():
                print(f"   └─ PID {pid}: {info['name']} [{info['status']}]")
    
    def poll(self):
        """Verifica uma vez o estado atual"""
        if not self._active:
            return self._finished
            
        now = time.time()
        current_pids, current_info = self._get_port_processes()
        
        # Detectar mudanças nos processos
        novos_pids = current_pids - self._baseline_pids - self._current_pids
        pids_removidos = self._current_pids - current_pids
        
        # Detectar início de backtest
        if self._state == 'WAITING':
            if novos_pids:
                # Verificar se é metatester64
                for pid in novos_pids:
                    if pid in current_info and 'metatester64' in current_info[pid]['name'].lower():
                        if self.verbose:
                            print(f"🚀 NOVO MetaTester64 detectado: PID {pid}")
                        self._state = 'RUNNING'
                        self._backtest_detected = True
                        self._last_change_time = now
                        break
                        
            # Fallback: detectar mudança em processos existentes (status change)
            if not self._backtest_detected:
                status_changes = []
                for pid in current_pids & self._baseline_pids:
                    if pid in current_info:
                        status_changes.append(current_info[pid]['status'])
                
                # Se viu alguma mudança de status, pode ser início de backtest
                if 'ESTABLISHED' in status_changes and self._last_change_time is None:
                    if self.verbose:
                        print(f"🎯 Mudança de status detectada na porta {self.port}")
                    self._state = 'RUNNING'
                    self._backtest_detected = True
                    self._last_change_time = now
        
        # Detectar fim de backtest
        elif self._state == 'RUNNING':
            # Método 1: PID foi removido
            if pids_removidos:
                metatester_removido = False
                for pid in pids_removidos:
                    # Verificar se era um metatester64 que foi removido
                    try:
                        # Se PID ainda existe mas não está mais na porta
                        if psutil.pid_exists(pid):
                            proc = psutil.Process(pid)
                            if 'metatester64' in proc.name().lower():
                                metatester_removido = True
                                break
                    except:
                        # PID não existe mais = processo terminou
                        metatester_removido = True
                        break
                
                if metatester_removido or pids_removidos:
                    duracao = now - (self._last_change_time or now)
                    if self.verbose:
                        print(f"✅ Backtest finalizado: processo removido após {duracao:.1f}s")
                    self._finished = True
                    self._active = False
                    self._state = 'IDLE'
                    return True
            
            # Método 2: Timeout por inatividade (fallback)
            if self._last_change_time and (now - self._last_change_time) > 30:
                if self.verbose:
                    print(f"⏰ Backtest considerado finalizado por timeout")
                self._finished = True
                self._active = False
                self._state = 'IDLE'
                return True
        
        # Atualizar estado atual
        self._current_pids = current_pids.copy()
        
        # Log periódico
        if self.verbose and now % 10 < 0.5:  # A cada ~10 segundos
            print(f"📊 Estado: {self._state} | PIDs ativos: {len(current_pids)}")
        
        return self._finished
    
    def wait(self, timeout=300):
        """Aguarda conclusão do backtest"""
        start_wait = time.time()
        
        while time.time() - start_wait < timeout:
            if self.poll():
                return True
            time.sleep(self.poll_interval)
        
        if self.verbose:
            print("⏰ Timeout no monitoramento alternativo")
        
        self._active = False
        self._state = 'IDLE'
        return False
    
    @property
    def state(self):
        return self._state
    
    @property
    def finished(self):
        return self._finished

def testar_monitor_alternativo():
    print("🧪 TESTE DO MONITOR ALTERNATIVO")
    print("=" * 50)
    
    monitor = BacktestMonitorAlternativo(port=3000, verbose=True)
    monitor.start()
    
    print("🎯 Monitor alternativo ativo - Execute um backtest!")
    print("   Detecta mudanças de processo em vez de conexões")
    print("   Pressione Ctrl+C para parar")
    print("-" * 50)
    
    try:
        success = monitor.wait(timeout=300)
        if success:
            print("🎉 BACKTEST DETECTADO E FINALIZADO!")
        else:
            print("⏰ Timeout sem detecção")
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    
    print(f"\n📊 Status final: {monitor.state}")

if __name__ == "__main__":
    testar_monitor_alternativo()