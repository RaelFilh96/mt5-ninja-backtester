#!/usr/bin/env python3
"""
BacktestMonitor Híbrido - Combina múltiplas estratégias de detecção
"""

import psutil
import time
from typing import Tuple, Dict, Set

class BacktestMonitorHibrido:
    """
    Monitor híbrido que usa múltiplas estratégias para detectar início/fim de backtest:
    1. Conexões ESTABLISHED (método tradicional)
    2. Mudanças de PID na porta (método alternativo)  
    3. Monitoramento de processos MetaTester64
    """
    
    def __init__(self, port: int = 3000, poll_interval: float = 0.2, verbose: bool = True):
        self.port = port
        self.poll_interval = poll_interval
        self.verbose = verbose
        
        # Estados do monitor
        self._active = False
        self._state = 'IDLE'  # IDLE | WAITING | RUNNING
        self._start_time = None
        self._backtest_start_time = None
        self._finished = False
        
        # Dados de baseline
        self._baseline_pids: Set[int] = set()
        self._baseline_established = 0
        self._current_pids: Set[int] = set()
        
        # Controle de detecção
        self._detection_method = None  # 'established' | 'pid_change' | 'process_monitor'
        self._last_established_time = None
        self._stability_timeout = 1.0  # segundos sem conexão para considerar fim
        
    def start(self):
        """Inicia o monitoramento"""
        if self.verbose:
            print(f"🎯 Monitor híbrido iniciado na porta {self.port}")
            
        self._start_time = time.time()
        self._active = True
        self._state = 'WAITING'
        self._finished = False
        
        # Capturar estado baseline
        baseline_data = self._get_port_snapshot()
        self._baseline_pids = baseline_data['pids']
        self._baseline_established = baseline_data['established_count']
        
        if self.verbose:
            print(f"📊 Baseline: {len(self._baseline_pids)} PIDs, {self._baseline_established} ESTABLISHED")
            
    def _get_port_snapshot(self) -> Dict:
        """Captura snapshot atual da porta"""
        pids = set()
        established_count = 0
        connections = []
        metatester_pids = set()
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port == self.port:
                    connections.append({
                        'status': conn.status,
                        'pid': conn.pid,
                        'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                    })
                    
                    if conn.pid:
                        pids.add(conn.pid)
                        
                        # Verificar se é metatester64
                        try:
                            proc = psutil.Process(conn.pid)
                            if 'metatester64' in proc.name().lower():
                                metatester_pids.add(conn.pid)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    if conn.status == 'ESTABLISHED':
                        established_count += 1
                        
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Erro no snapshot: {e}")
                
        return {
            'pids': pids,
            'established_count': established_count,
            'connections': connections,
            'metatester_pids': metatester_pids
        }
    
    def poll(self) -> Tuple[bool, str]:
        """
        Executa uma verificação do estado
        Retorna (finished, detection_method_used)
        """
        if not self._active:
            return self._finished, self._detection_method or 'none'
            
        now = time.time()
        snapshot = self._get_port_snapshot()
        
        current_pids = snapshot['pids']
        established_count = snapshot['established_count']
        metatester_pids = snapshot['metatester_pids']
        
        # === DETECÇÃO DE INÍCIO ===
        if self._state == 'WAITING':
            detected_start = False
            method_used = None
            
            # Método 1: Nova conexão ESTABLISHED
            if established_count > self._baseline_established:
                detected_start = True
                method_used = 'established'
                if self.verbose:
                    print(f"🚀 Backtest detectado via ESTABLISHED: {established_count} conexões")
            
            # Método 2: Novo PID metatester64
            elif metatester_pids - self._baseline_pids:
                new_metatester = metatester_pids - self._baseline_pids
                detected_start = True
                method_used = 'new_metatester_pid'
                if self.verbose:
                    print(f"🚀 Backtest detectado via novo MetaTester PID: {new_metatester}")
            
            # Método 3: Mudança geral de PIDs
            elif current_pids != self._baseline_pids and current_pids != self._current_pids:
                new_pids = current_pids - self._baseline_pids - self._current_pids
                if new_pids:
                    detected_start = True
                    method_used = 'pid_change'
                    if self.verbose:
                        print(f"🚀 Backtest detectado via mudança de PID: {new_pids}")
            
            if detected_start:
                self._state = 'RUNNING'
                self._backtest_start_time = now
                self._detection_method = method_used
                self._last_established_time = now if established_count > 0 else None
        
        # === DETECÇÃO DE FIM ===
        elif self._state == 'RUNNING':
            detected_end = False
            
            # Método 1: Perda de conexões ESTABLISHED
            if self._detection_method == 'established':
                if established_count > 0:
                    self._last_established_time = now
                elif self._last_established_time and (now - self._last_established_time) >= self._stability_timeout:
                    detected_end = True
                    if self.verbose:
                        duration = now - self._backtest_start_time
                        print(f"✅ Backtest finalizado via ESTABLISHED: {duration:.1f}s de duração")
            
            # Método 2: PID removido
            elif self._detection_method in ['new_metatester_pid', 'pid_change']:
                if not metatester_pids or not current_pids:
                    detected_end = True
                    if self.verbose:
                        duration = now - self._backtest_start_time
                        print(f"✅ Backtest finalizado via PID: {duration:.1f}s de duração")
            
            # Fallback: Timeout por inatividade
            if not detected_end and (now - self._backtest_start_time) > 300:  # 5 minutos
                detected_end = True
                if self.verbose:
                    print(f"⏰ Backtest finalizado por timeout")
            
            if detected_end:
                self._finished = True
                self._active = False
                self._state = 'IDLE'
                return True, self._detection_method
        
        # Atualizar estado atual
        self._current_pids = current_pids.copy()
        
        return self._finished, self._detection_method or 'waiting'
    
    def wait(self, timeout: float = 300) -> bool:
        """Aguarda conclusão do backtest"""
        start_wait = time.time()
        
        while time.time() - start_wait < timeout:
            finished, method = self.poll()
            if finished:
                if self.verbose:
                    print(f"🎉 Backtest concluído! Método: {method}")
                return True
            time.sleep(self.poll_interval)
        
        if self.verbose:
            print("⏰ Timeout no monitoramento híbrido")
        self._active = False
        return False
    
    @property
    def state(self) -> str:
        return self._state
    
    @property
    def finished(self) -> bool:
        return self._finished
    
    @property
    def detection_method(self) -> str:
        return self._detection_method or 'none'

# Teste do monitor híbrido
def teste_monitor_hibrido():
    print("🧪 TESTE DO MONITOR HÍBRIDO")
    print("=" * 60)
    
    monitor = BacktestMonitorHibrido(port=3000, verbose=True)
    monitor.start()
    
    print("🎯 Monitor híbrido ativo!")
    print("   Usa múltiplas estratégias de detecção")
    print("   Execute um backtest para testar")
    print("   Pressione Ctrl+C para parar")
    print("-" * 60)
    
    try:
        success = monitor.wait(timeout=300)
        if success:
            print(f"🎉 SUCESSO! Método usado: {monitor.detection_method}")
        else:
            print("⏰ Timeout")
    except KeyboardInterrupt:
        print("\n🛑 Interrompido")
    
    print(f"📊 Estado final: {monitor.state}")

if __name__ == "__main__":
    teste_monitor_hibrido()