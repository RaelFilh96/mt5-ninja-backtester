#! -*- coding: utf-8 -*-
"""Extração OOS via INI para MetaTrader 5 (versão orientada a objetos).

Componentes principais:
- OOSBatchRunner (alias ExtracaoOOS): orquestra múltiplos steps OOS
- Funções utilitárias para parse de ranges a partir d                 # Espera opcional mínima pós-launch
                           print("📋 Passo 2: Carregando arquivo .set via interface...")
                self._load_set_file()
                
                print("⏳ Passo 3: Aguardando 15 segundos antes do clique...")
                time.sleep(15)
                
                print("🎯 Passo 4: Iniciando monitoramento porta 3000...")
                self._monitor.reset()
                self._monitor.start()
                
                print("🔍 Debug: Verificando conexões iniciais...")
                self._debug_active_ports()
                
                print("🖱️ Passo 5: Clicando no botão 'Iniciar backtesting'...")
                self._click_start_backtest()
                
                print("� Aguardando detecção da conexão...")🖱️ Passo 4b: Clicando no botão 'Iniciar backtesting'...")
                self._click_start_backtest()
                
                # Aguardar um pouco após clique para sistema reagir
                print("⏳ Aguardando 3 segundos para sistema reagir ao clique...")
                time.sleep(3)
                
                print("🔍 Verificando conexões após clique...")
                self._debug_active_ports()
                
                # Debug adicional: verificar se há novas conexões
                print("🔍 Monitorando porta por 10 segundos após clique...")
                for i in range(10):
                    finished, _ = self._monitor.poll({'last_log': 0})
                    if finished:
                        print("✅ Backtest detectado rapidamente!")
                        break
                    if i % 2 == 0:  # A cada 2 segundos
                        print(f"  📊 Segundo {i+1}: estado={self._monitor.state}")
                    time.sleep(1)          if self.post_launch_wait > 0:
                     time.sleep(self.post_launch_wait)
                 
                 # Debug: verificar portas ativas do MT5
                 self._debug_active_ports()TML, texto livre ou prompt

Fluxo de cada step (sequência fixa solicitada):
1. Gerar INI (FromDate/ToDate + Report dedicado)
2. Lançar MT5 com /config:INI (sem clicar Start ainda)
3. Aguardar estabilização (post_launch_wait)
4. Iniciar monitoramento porta 3000
5. Clicar botão Start via coordenada (start_button)
6. Aguardar término detectado (porta livre estável) ou timeout
7. Exportar CSV via UI
8. Encerrar MT5

Requer: backtest_core.INIGenerator e backtest_core.BacktestMonitor
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
import re
import subprocess
import time
import configparser

from backtest_core import INIGenerator, BacktestMonitor
from automacao import MT5Automacao

# ---------------------------- Utilidades de Data ---------------------------- #

DATE_BR_REGEX = re.compile(r"^\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})\s*$")


def _br_to_mt5(date_br: str) -> str:
    """Converte dd/mm/yyyy para formato MT5: YYYY.MM.DD HH:MM:SS"""
    d, m, y = date_br.split('/')
    return f"{y}.{m}.{d} 00:00:00"


def _br_to_slug(date_br: str) -> str:
    return date_br.replace('/', '')

# ------------------------ Parsing de Ranges (HTML/TEXTO) -------------------- #


def parse_oos_from_html(html: str) -> List[Tuple[str, str]]:
    """Extrai somente os ranges Out of Sample (3ª coluna) da tabela HTML gerada.

    Evita duplicação dos ranges In Sample. Cada linha <tr> deve conter:
      <td>Step</td><td>IN_SAMPLE</td><td>OUT_SAMPLE</td>

    Fallback: se não achar estrutura tabular, cai para captura global simples
    (mantida) porém ainda filtrando duplicados.
    """
    if not html:
        return []

    # Regex para capturar linhas <tr> ... </tr>
    tr_pattern = re.compile(r"<tr>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
    td_pattern = re.compile(r"<td>(.*?)</td>", re.IGNORECASE | re.DOTALL)
    date_range_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s*[-–]\s*(\d{2}/\d{2}/\d{4})")

    oos_ranges: List[Tuple[str, str]] = []

    rows = tr_pattern.findall(html)
    for row in rows:
        cols = td_pattern.findall(row)
        # Esperado >=3 colunas: Step, In Sample, Out of Sample
        if len(cols) >= 3:
            out_col = cols[2]
            m = date_range_pattern.search(out_col)
            if m:
                oos_ranges.append((m.group(1), m.group(2)))

    if not oos_ranges:
        # Fallback global (antigo comportamento) — pode capturar duplicado, então deduplicar
        found = date_range_pattern.findall(html)
        oos_ranges = [(a.strip(), b.strip()) for a, b in found]

    # Deduplicar preservando ordem
    seen = set()
    unique: List[Tuple[str, str]] = []
    for r in oos_ranges:
        if r not in seen:
            unique.append(r)
            seen.add(r)
    return unique


def parse_oos_from_text(texto: str) -> List[Tuple[str, str]]:
    """Extrai pares de datas de uma linha/arquivo textual.
    Ex: "14/10/2022 - 14/04/2023, 14/04/2023 - 14/10/2023""" 
    if not texto:
        return []
    parts = re.split(r",|;|\n|\|", texto)
    ranges: List[Tuple[str, str]] = []
    for p in parts:
        m = DATE_BR_REGEX.match(p.strip())
        if m:
            ranges.append((m.group(1), m.group(2)))
    return ranges


def prompt_oos_steps() -> List[Tuple[str, str]]:
    """Prompt interativo para coletar N ranges OOS."""
    try:
        n = int(input("Quantos steps OOS? ").strip())
    except Exception:
        return []
    out: List[Tuple[str, str]] = []
    for i in range(1, n + 1):
        a = input(f"Step {i} - Data inicial (dd/mm/yyyy): ").strip()
        b = input(f"Step {i} - Data final   (dd/mm/yyyy): ").strip()
        if DATE_BR_REGEX.match(f"{a} - {b}"):
            out.append((a, b))
        else:
            print("⚠️ Formato inválido, ignorando step")
    return out

# ----------------------------- Runner Principal ----------------------------- #

@dataclass
class OOSBatchRunner:
    automacao: MT5Automacao
    ini_template: str | Path = None
    set_path: str | Path = None
    output_dir: str | Path = None
    reports_subdir: str = "reports"      # Mudança: sem underscore
    ini_out_dirname: str = "ini_generated" # Mudança: nome mais claro
    csv_subdir: str = "csv"              # Novo: pasta dedicada para CSVs
    monitor_port: int = 3000
    post_launch_wait: float = 3.0
    window_wait_timeout: float = 20.0

    def __post_init__(self):
        # Definir caminhos padrão se não fornecidos
        base_oos_dir = self._get_default_base_dir()
        
        if self.ini_template is None:
            self.ini_template = base_oos_dir / "templates" / "exemplo.ini"
        else:
            self.ini_template = Path(self.ini_template)
            
        if self.set_path is None:
            self.set_path = self._find_default_set_file(base_oos_dir / "sets")
        else:
            self.set_path = Path(self.set_path)
            
        if self.output_dir is None:
            self.output_dir = base_oos_dir / "output"
        else:
            self.output_dir = Path(self.output_dir)

        # Criar estrutura de pastas
        self.reports_dir = self.output_dir / self.reports_subdir
        self.work_dir = self.output_dir / self.ini_out_dirname
        self.csv_dir = self.output_dir / self.csv_subdir
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        
        self._ini_generator = INIGenerator(self.ini_template, self.reports_dir)
        self._monitor = BacktestMonitor(port=self.monitor_port, verbose=True)
        self._debug_ports = [3000, 443, 80, 8080, 17000, 18000]

        if not self.set_path.exists():
            raise FileNotFoundError(f"Arquivo .set não encontrado: {self.set_path}")
            
        print(f"📁 Estrutura OOS configurada:")
        print(f"  📋 Template INI: {self.ini_template}")
        print(f"  ⚙️ Arquivo SET: {self.set_path}")
        print(f"  📊 Saída CSV: {self.csv_dir}")
        print(f"  📄 Relatórios: {self.reports_dir}")
        print(f"  🔧 INIs gerados: {self.work_dir}")

    def _get_default_base_dir(self) -> Path:
        """Retorna diretório base padrão para extração OOS"""
        current_dir = Path(__file__).parent
        return current_dir.parent / "extracao_OOS"
    
    def _find_default_set_file(self, sets_dir: Path) -> Path:
        """Encontra primeiro arquivo .set na pasta sets/"""
        sets_dir.mkdir(parents=True, exist_ok=True)
        set_files = list(sets_dir.glob("*.set"))
        if not set_files:
            raise FileNotFoundError(f"Nenhum arquivo .set encontrado em: {sets_dir}")
        return set_files[0]  # Retorna primeiro encontrado

    # ---------------------- Construção de INI por Step ---------------------- #
    def _build_ini_file(self, from_br: str, to_br: str) -> Path:
        from_mt5 = _br_to_mt5(from_br)
        to_mt5 = _br_to_mt5(to_br)
        from_slug, to_slug = _br_to_slug(from_br), _br_to_slug(to_br)
        content, enc = self._ini_generator.build(from_mt5, to_mt5, from_slug, to_slug, self.set_path)
        ini_path = self.work_dir / f"OOS_{from_slug}_{to_slug}.ini"
        ini_path.write_text(content, encoding=enc)
        return ini_path

    # --------------------------- Lançar MT5 /config -------------------------- #
    def _launch_mt5_with_ini(self, ini_path: Path):
        terminal_path = Path(self.automacao.mt5_path) / 'terminal64.exe'
        if not terminal_path.exists():
            terminal_path = Path('terminal64.exe')  # fallback PATH
        if terminal_path.exists():
            # Encerrar instâncias anteriores
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and 'terminal64.exe' in proc.info['name'].lower():
                        proc.kill()
                except Exception:
                    pass
            time.sleep(2)
        
        # Construir comando apenas com .ini (o .set será carregado manualmente via UI)
        cmd = [str(terminal_path), f"/config:{ini_path}"]
        
        print(f"▶️ Iniciando MT5: {' '.join(cmd)}")
        print(f"📋 Arquivo .set para carregar manualmente: {self.set_path.name}")
        subprocess.Popen(cmd)

    # ----------------------------- Exportar CSV UI --------------------------- #
    def _export_csv(self, from_br: str, to_br: str):
        csv_name = self._compose_csv_name(from_br, to_br)
        prev_folder = self.automacao.curves_folder
        try:
            # Usar pasta específica para CSVs
            self.automacao.curves_folder = self.csv_dir
            self.automacao.focar_mt5()
            time.sleep(2)
            # Ir para aba gráfico se coordenada existir
            if 'graph_tab' in self.automacao.coords:
                import pyautogui
                pyautogui.click(self.automacao.coords['graph_tab'])
                time.sleep(1)
            self.automacao.exportar_csv(csv_name)
        finally:
            self.automacao.curves_folder = prev_folder

    def _compose_csv_name(self, from_br: str, to_br: str) -> str:
        from_slug, to_slug = _br_to_slug(from_br), _br_to_slug(to_br)
        try:
            sym, per = self._ini_generator.extract_symbol_period()
        except Exception:
            sym, per = 'SYMBOL', 'TF'
        set_stem = self.set_path.stem
        ts = time.strftime('%Y%m%d-%H%M%S')
        return f"{sym}_{per}_{set_stem}_OOS_{from_slug}_{to_slug}_{ts}"

    # ----------------------------- Execução Batch --------------------------- #
    def run(self, ranges: List[Tuple[str, str]]):
        if not ranges:
            print("⚠️ Nenhum range fornecido")
            return
        print(f"\n📋 Executando {len(ranges)} steps OOS...")
        for idx, (from_br, to_br) in enumerate(ranges, 1):
            print(f"\n🧪 Step {idx}: {from_br} -> {to_br}")
            try:
                ini_path = self._build_ini_file(from_br, to_br)
                print(f"📝 INI gerado: {ini_path.name}")
                
                # NOVO FLUXO: 1) Abrir MT5, 2) Monitor, 3) Aguardar 5s, 4) Clicar Start
                print("▶️ Passo 1: Abrindo MT5...")
                pre_launch = time.time()
                self._launch_mt5_with_ini(ini_path)
                
                # Aguardar processo MT5 aparecer
                import psutil
                proc_seen = False
                for _ in range(int(self.window_wait_timeout)):
                    if any((p.info.get('name') or '').lower().startswith('terminal64') for p in psutil.process_iter(['name'])):
                        proc_seen = True
                        break
                    time.sleep(1)
                if proc_seen:
                    print(f"🔎 Processo MT5 detectado em {time.time()-pre_launch:.1f}s")
                else:
                    print("⚠️ Processo MT5 não detectado (seguindo assim mesmo)")
                
                # Espera inicial para MT5 carregar completamente
                if self.post_launch_wait > 0:
                    print(f"⏳ Aguardando MT5 carregar ({self.post_launch_wait}s)...")
                    time.sleep(self.post_launch_wait)
                
                print("🎯 Passo 2: Iniciando monitoramento porta 3000...")
                self._monitor.reset()
                self._monitor.start()
                
                print("⏳ Passo 3: Aguardando 15 segundos antes do clique...")
                time.sleep(15)
                
                print("� Passo 4a: Carregando arquivo .set via interface...")
                self._load_set_file()
                
                print("�🖱️ Passo 4b: Clicando no botão 'Iniciar backtesting'...")
                self._click_start_backtest()
                
                print("🔍 Verificando conexões após clique...")
                self._debug_active_ports()
                
                # ---------------- Loop de monitoramento com fallback ---------------- #
                fallback_report_check_after = 25  # TODO: tornar configurável
                fallback_min_report_size = 5_000   # bytes mínimos para considerar válido (heurística)
                global_timeout = 240              # TODO: tornar configurável
                poll_sleep = 0.5                  # intervalo base de polling
                report_confirmed = False
                start_wait = time.time()
                expected_fragment = f"OOS_{_br_to_slug(from_br)}_{_br_to_slug(to_br)}".lower()
                last_size = 0
                while True:
                    finished, _last_log = self._monitor.poll({'last_log': 0})
                    if finished:
                        break
                    elapsed = time.time() - start_wait
                    # Se ainda em WAITING além de X segundos, checar report como fallback
                    if not report_confirmed and elapsed >= fallback_report_check_after:
                        for fp in self.reports_dir.glob('*.html'):
                            if expected_fragment in fp.name.lower():
                                size = fp.stat().st_size
                                mtime_age = time.time() - fp.stat().st_mtime
                                if size >= fallback_min_report_size and mtime_age < 120:  # modificado recentemente
                                    report_confirmed = True
                                    print("📝 Fallback: Report detectado com tamanho suficiente e modificação recente.")
                                    finished = True
                                    break
                                last_size = size
                    if elapsed >= global_timeout:
                        print("⚠️ Timeout geral sem detecção de término pela porta")
                        break
                    time.sleep(poll_sleep)
                if not finished and report_confirmed:
                    finished = True
                if not finished:
                    print("⚠️ Prosseguindo apesar do timeout (resultado pode estar incompleto)")
                # Exportar CSV
                print("💾 Exportando CSV...")
                self._export_csv(from_br, to_br)
                # Encerrar MT5 p/ próximo step
                print("🛠 Encerrando MT5...")
                self.automacao.encerrar_mt5(silent=True)
                time.sleep(3)
                print("✅ Step concluído")
            except Exception as e:
                print(f"❌ Erro no step {idx}: {e}")
                # Garantir encerramento MT5 antes de seguir
                try:
                    self.automacao.encerrar_mt5(silent=True)
                except Exception:
                    pass
                time.sleep(2)
        print(f"\n✅ Fim! Resultados organizados:")
        print(f"  📊 CSVs: {self.csv_dir}")
        print(f"  📄 Relatórios: {self.reports_dir}")
        print(f"  🔧 INIs: {self.work_dir}")

    @classmethod
    def create_with_defaults(cls, automacao: MT5Automacao):
        """Factory method para criar com configuração padrão"""
        return cls(automacao=automacao)
    
    @classmethod 
    def create_custom(cls, automacao: MT5Automacao, ini_template=None, set_path=None, output_dir=None):
        """Factory method para criar com caminhos customizados"""
        return cls(
            automacao=automacao,
            ini_template=ini_template,
            set_path=set_path,
            output_dir=output_dir
        )

    def _debug_active_ports(self):
        """Debug: mostra portas ativas de processos MT5"""
        import psutil
        print("🔍 Debug - Portas ativas do MT5:")
        try:
            mt5_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'terminal64' in proc.info['name'].lower():
                    mt5_processes.append(proc.info['pid'])
            
            if not mt5_processes:
                print("⚠️ Nenhum processo terminal64.exe encontrado")
                return
            else:
                print(f"✅ Processos MT5 encontrados: {mt5_processes}")
                
            found_any = False
            for port in self._debug_ports:
                connections = []
                for c in psutil.net_connections():
                    if (c.laddr and c.laddr.port == port and 
                        c.pid in mt5_processes):
                        connections.append(f"{c.status}(PID={c.pid})")
                if connections:
                    print(f"  ✅ Porta {port}: {', '.join(connections)}")
                    found_any = True
                    
            if not found_any:
                print("⚠️ Nenhuma conexão encontrada nas portas monitoradas")
                print(f"   Portas verificadas: {self._debug_ports}")
                
        except Exception as e:
            print(f"⚠️ Erro no debug de portas: {e}")

    def _click_start_backtest(self):
        """Clica no botão 'Iniciar backtesting' usando o método já testado da automação"""
        try:
            # Usar o método que já funciona na rotina 1
            print("⚡ Iniciando backtest via método testado...")
            self.automacao.iniciar_backtest()
            
        except Exception as e:
            print(f"❌ Erro ao iniciar backtest: {e}")
            # Fallback: tentar método manual
            try:
                self.automacao.focar_mt5()
                time.sleep(1)
                if 'start_button' in self.automacao.coords:
                    import pyautogui
                    start_coord = self.automacao.coords['start_button']
                    print(f"� Fallback - clicando em ({start_coord[0]}, {start_coord[1]})")
                    pyautogui.click(start_coord[0], start_coord[1])
                    time.sleep(0.5)
            except Exception as e2:
                print(f"❌ Fallback também falhou: {e2}")

    def _load_set_file(self):
        """Carrega arquivo .set via interface do MT5"""
        try:
            # Usar método correto da automação existente
            print(f"📋 Carregando: {self.set_path.name}")
            self.automacao.carregar_set_file(str(self.set_path))
            print(f"✅ Arquivo .set carregado: {self.set_path.name}")
            time.sleep(3)  # Aguardar carregamento completo
            
        except Exception as e:
            print(f"❌ Erro ao carregar .set: {e}")
            print("ℹ️ Continuando sem .set - use configuração padrão")

    # Compatibilidade com interface antiga
    def run_batch(self, ranges: List[Tuple[str, str]]):
        self.run(ranges)

# Alias para manter import existente (from extracao_oos import ExtracaoOOS)
ExtracaoOOS = OOSBatchRunner

# ----------------------- Funções Utilitárias de Conveniência ----------------------- #

def create_default_oos_runner() -> OOSBatchRunner:
    """Cria runner OOS com configuração padrão da estrutura organizada"""
    from automacao import MT5Automacao
    automacao = MT5Automacao()
    return OOSBatchRunner.create_with_defaults(automacao)

def list_available_templates() -> List[Path]:
    """Lista templates INI disponíveis"""
    base_dir = Path(__file__).parent.parent / "extracao_OOS" / "templates"
    return list(base_dir.glob("*.ini"))

def list_available_sets() -> List[Path]:
    """Lista arquivos .set disponíveis"""
    base_dir = Path(__file__).parent.parent / "extracao_OOS" / "sets"
    return list(base_dir.glob("*.set"))

def get_default_paths() -> dict:
    """Retorna dicionário com todos os caminhos padrão"""
    base_dir = Path(__file__).parent.parent / "extracao_OOS"
    return {
        'base': base_dir,
        'templates': base_dir / "templates",
        'sets': base_dir / "sets", 
        'output': base_dir / "output",
        'csv': base_dir / "output" / "csv",
        'reports': base_dir / "output" / "reports",
        'ini_generated': base_dir / "output" / "ini_generated"
    }

__all__ = [
    'OOSBatchRunner',
    'ExtracaoOOS',
    'parse_oos_from_html',
    'parse_oos_from_text',
    'prompt_oos_steps',
    'create_default_oos_runner',
    'list_available_templates',
    'list_available_sets',
    'get_default_paths'
]
