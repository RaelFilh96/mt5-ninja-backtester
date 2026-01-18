# -*- coding: utf-8 -*-
"""Núcleo de componentes OOP para automação de backtests MT5.

Classes:
- INIGenerator: Geração de arquivos .ini a partir de template com substituição de datas.
- BacktestMonitor: Monitoramento da porta 3000 para detectar início/fim do backtest.

Foco: reutilização por diferentes fluxos (batch de .set, OOS, etc.)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import configparser
import re
import time
import psutil
from typing import Optional, Tuple

@dataclass
class INIGenerator:
    template_path: Path
    reports_dir: Path

    def __post_init__(self):
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template INI não encontrado: {self.template_path}")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self._encoding: Optional[str] = None
        self._raw_cache: Optional[str] = None

    def _detect_encoding(self):
        if self._encoding:
            return self._encoding
        encodings = ["utf-8", "utf-8-sig", "utf-16", "utf-16-le", "latin-1"]
        last_err = None
        for enc in encodings:
            try:
                data = self.template_path.read_text(encoding=enc)
                self._encoding = enc
                self._raw_cache = data
                return enc
            except UnicodeDecodeError as e:
                last_err = e
        raise UnicodeDecodeError("Falha", b"", 0, 0, f"Não foi possível decodificar {self.template_path}. Último erro: {last_err}")

    def _ensure_loaded(self):
        if self._raw_cache is None:
            self._detect_encoding()

    def build(self, from_mt5: str, to_mt5: str, from_slug: str, to_slug: str, set_file: Path = None) -> Tuple[str, str]:
        """Retorna (conteudo_modificado, encoding)."""
        self._ensure_loaded()
        content = self._raw_cache
        # Substituir linhas
        content = re.sub(r'^FromDate=.*$', f'FromDate={from_mt5}', content, flags=re.MULTILINE)
        content = re.sub(r'^ToDate=.*$', f'ToDate={to_mt5}', content, flags=re.MULTILINE)
        
        # Adicionar relatório se não existir
        if 'Report=' not in content:
            report_path = self.reports_dir / f"OOS_{from_slug}_{to_slug}.html"
            report_norm = str(report_path).replace('\\', '/')
            # Inserir dentro da seção [Tester] ou criar
            if '[Tester]' in content:
                def repl(m):
                    block = m.group(0)
                    if 'Report=' in block:
                        return block
                    additions = f"\nReport={report_norm}\nReplaceReport=1"
                    # Adicionar referência ao .set se fornecido
                    if set_file and set_file.exists():
                        set_norm = str(set_file).replace('\\', '/')
                        additions += f"\nSet={set_norm}"
                    return block + additions
                content = re.sub(r'\[Tester\][^\[]*', repl, content, flags=re.MULTILINE)
            else:
                addition = f"\n[Tester]\nReport={report_norm}\nReplaceReport=1"
                if set_file and set_file.exists():
                    set_norm = str(set_file).replace('\\', '/')
                    addition += f"\nSet={set_norm}"
                content += addition
        return content, self._encoding or 'utf-8'

    def extract_symbol_period(self) -> Tuple[str, str]:
        self._ensure_loaded()
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg.read_string(self._raw_cache)
        sym = cfg.get('Tester', 'Symbol', fallback='SYMBOL')
        per = cfg.get('Tester', 'Period', fallback='TF')
        return sym, per


class BacktestMonitor:
    """Monitor inteligente de backtests MT5 v3.0
    
    Nova lógica: Detecta início via conexão ESTABLISHED na porta 3000,
    depois monitora o processo metatester64 até finalizar (CPU baixa ou processo encerrado).
    
    A conexão na porta 3000 dura apenas ~2 segundos (handshake inicial),
    então usamos ela apenas para detectar INÍCIO, não o fim.
    """
    
    def __init__(self, port: int = 3000, poll_interval: float = 0.1, verbose: bool = True):
        self.port = port
        self.poll_interval = poll_interval
        self.verbose = verbose
        self._start_time: float | None = None
        self._run_start: float | None = None
        self._active = False
        self._state = 'IDLE'  # IDLE | WAITING | RUNNING | FINISHING
        self._finished = False
        
        # Tracking de processo
        self._backtest_pid: int | None = None
        self._low_cpu_start: float | None = None
        self._cpu_threshold = 5.0  # CPU abaixo disso = backtest terminando
        self._low_cpu_duration = 2.0  # segundos com CPU baixa para confirmar fim
        
        # Tracking de conexão (para detectar início)
        self._connection_seen = False
        self._connection_closed_time: float | None = None

    def start(self):
        """Inicia o monitoramento"""
        if self._active:
            if self.verbose:
                print("⚠️ Monitor já ativo - resetando...")
            self.reset()
            
        if self.verbose:
            print(f"🎯 Monitor v3.0 - Detecção híbrida (Porta + CPU)")
            print(f"   Porta: {self.port} | Intervalo: {self.poll_interval}s")
        
        self._start_time = time.time()
        self._run_start = None
        self._active = True
        self._state = 'WAITING'
        self._finished = False
        self._connection_seen = False
        self._backtest_pid = None
        self._low_cpu_start = None

    def _get_metatester_processes(self):
        """Retorna lista de processos metatester64 ativos com CPU"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['name'] and 'metatester64' in proc.info['name'].lower():
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu': proc.cpu_percent(interval=0.05)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def _check_port_activity(self):
        """Verifica atividade na porta 3000 - retorna (has_established, has_any, details)"""
        has_established = False
        has_any = False
        details = []
        
        try:
            for c in psutil.net_connections():
                if c.laddr and c.laddr.port == self.port:
                    has_any = True
                    if c.status == 'ESTABLISHED':
                        has_established = True
                        details.append({
                            'status': c.status,
                            'pid': c.pid,
                            'remote': f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "N/A"
                        })
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Erro ao verificar porta: {e}")
        
        return has_established, has_any, details

    def wait(self, timeout: float = 300) -> bool:
        """Aguarda conclusão do backtest com timeout"""
        if not self._active:
            self.start()
        
        last_log = 0
        while time.time() - self._start_time < timeout:
            finished, last_log = self.poll(log_interval_ref={'last_log': last_log})
            if finished:
                return True
            time.sleep(self.poll_interval)
        
        if self.verbose:
            print("⏰ Timeout no monitoramento")
        self._active = False
        self._state = 'IDLE'
        return False

    def reset(self):
        """Reseta o monitor para novo uso"""
        self._start_time = None
        self._run_start = None
        self._active = False
        self._state = 'IDLE'
        self._finished = False
        self._connection_seen = False
        self._backtest_pid = None
        self._low_cpu_start = None
        self._connection_closed_time = None

    def poll(self, log_interval_ref: dict | None = None):
        """Executa uma iteração de avaliação de estado.
        
        Lógica v3.0:
        1. WAITING: Aguarda conexão ESTABLISHED na porta 3000 (início do backtest)
        2. RUNNING: Monitora CPU do metatester64 - quando cai abaixo do threshold
        3. FINISHING: Confirma fim com CPU baixa por X segundos
        
        Retorna (finished: bool, last_log: float)
        """
        if not self._active:
            return (self._finished, (log_interval_ref or {}).get('last_log', 0.0))
        
        now = time.time()
        last_log = (log_interval_ref or {}).get('last_log', 0.0)
        
        # Obter estado atual
        has_established, has_any, conn_details = self._check_port_activity()
        metatester_procs = self._get_metatester_processes()
        
        # ============ ESTADO: WAITING ============
        if self._state == 'WAITING':
            # Método 1: Detectar conexão ESTABLISHED na porta
            if has_established:
                self._connection_seen = True
                self._run_start = now
                self._state = 'RUNNING'
                
                # Tentar identificar o PID do backtest
                if conn_details:
                    self._backtest_pid = conn_details[0].get('pid')
                
                if self.verbose:
                    print(f"🚀 Backtest INICIADO! (conexão porta {self.port})")
                    if metatester_procs:
                        cpus = [f"PID {p['pid']}: {p['cpu']:.1f}%" for p in metatester_procs]
                        print(f"   MetaTesters ativos: {', '.join(cpus)}")
            
            # Método 2: Detectar aumento de CPU nos metatesters (fallback)
            elif metatester_procs:
                high_cpu_procs = [p for p in metatester_procs if p['cpu'] > 20]
                if high_cpu_procs:
                    self._connection_seen = True
                    self._run_start = now
                    self._state = 'RUNNING'
                    self._backtest_pid = high_cpu_procs[0]['pid']
                    if self.verbose:
                        print(f"🚀 Backtest INICIADO! (CPU alta detectada: PID {self._backtest_pid})")
        
        # ============ ESTADO: RUNNING ============
        elif self._state == 'RUNNING':
            if metatester_procs:
                # Calcular CPU máxima entre metatesters
                max_cpu = max(p['cpu'] for p in metatester_procs)
                
                if max_cpu < self._cpu_threshold:
                    # CPU baixa - pode estar terminando
                    if self._low_cpu_start is None:
                        self._low_cpu_start = now
                        if self.verbose:
                            print(f"📉 CPU baixa detectada ({max_cpu:.1f}%) - verificando...")
                    else:
                        low_duration = now - self._low_cpu_start
                        if low_duration >= self._low_cpu_duration:
                            # Confirmado: backtest terminou
                            total_time = now - (self._run_start or now)
                            if self.verbose:
                                print(f"✅ Backtest FINALIZADO! Duração: {total_time:.1f}s")
                            self._finished = True
                            self._active = False
                            self._state = 'IDLE'
                            return (True, now)
                else:
                    # CPU ainda alta - resetar contador
                    self._low_cpu_start = None
            else:
                # Nenhum metatester encontrado - processo pode ter encerrado
                if self._run_start:
                    total_time = now - self._run_start
                    if self.verbose:
                        print(f"✅ Backtest FINALIZADO! (processo encerrado) Duração: {total_time:.1f}s")
                    self._finished = True
                    self._active = False
                    self._state = 'IDLE'
                    return (True, now)
        
        # Logs periódicos
        if self.verbose and now - last_log > 10:
            if self._state == 'WAITING':
                print(f"⏳ Aguardando início do backtest...")
            elif self._state == 'RUNNING':
                elapsed = now - (self._run_start or now)
                if metatester_procs:
                    max_cpu = max(p['cpu'] for p in metatester_procs)
                    print(f"⏳ Executando... {elapsed:.0f}s | CPU: {max_cpu:.1f}%")
                else:
                    print(f"⏳ Executando... {elapsed:.0f}s | MetaTester não encontrado")
            last_log = now
        
        return (self._finished, last_log)

    @property
    def state(self):
        return self._state

    @property
    def finished(self):
        return self._finished

    @property
    def running(self):
        return self._state == 'RUNNING'

    @property
    def waiting(self):
        return self._state == 'WAITING'
