# -*- coding: utf-8 -*-
"""
MT5 Automação - Sistema Otimizado
Automação completa para backtests MetaTrader 5
"""

import os
import time
import configparser
import subprocess
import pyautogui
import psutil
from pathlib import Path
import json
import pyperclip  # Para colar texto com caracteres especiais
import logging
from datetime import datetime
# threading/queue removidos após migração para BacktestMonitor
from backtest_core import BacktestMonitor

# Base do projeto (pasta deste arquivo)
BASE_DIR = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════════════════════════
# 📋 SISTEMA DE LOG ESTRUTURADO
# ═══════════════════════════════════════════════════════════════════════════════

class LoggerMT5:
    """Sistema de log estruturado para automação MT5"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Criar pasta de logs
        self.logs_folder = BASE_DIR / 'logs'
        self.logs_folder.mkdir(exist_ok=True)
        
        # Nome do arquivo de log com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'automacao_{timestamp}.log'
        self.log_path = self.logs_folder / log_filename
        
        # Configurar logger
        self.logger = logging.getLogger('MT5Automacao')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console (apenas INFO+)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adicionar handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            # console_handler não adicionado para não duplicar prints
        
        self._initialized = True
        self.logger.info(f"═══ SESSÃO INICIADA ═══")
        self.logger.info(f"Log: {self.log_path}")
    
    def info(self, msg):
        self.logger.info(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def success(self, set_name, duracao):
        self.logger.info(f"✅ SUCESSO | {set_name} | {duracao:.1f}s")
    
    def failure(self, set_name, erro):
        self.logger.error(f"❌ FALHA | {set_name} | {erro}")
    
    def resumo(self, total, sucessos, falhas, duracao_total):
        self.logger.info(f"═══ RESUMO FINAL ═══")
        self.logger.info(f"Total: {total} | Sucessos: {sucessos} | Falhas: {falhas}")
        self.logger.info(f"Taxa de sucesso: {(sucessos/total*100):.1f}%")
        self.logger.info(f"Duração total: {duracao_total:.1f}s")


# Instância global do logger
logger = LoggerMT5()

class MT5Automacao:
    """Automação MT5 - Versão Final Otimizada"""

    def __init__(self, curvas_folder=None):
        self.config = configparser.ConfigParser()
        self.config_path = BASE_DIR / 'config.ini'
        self.config.read(self.config_path, encoding='utf-8')

        if 'MT5' not in self.config:
            raise KeyError("Seção 'MT5' não encontrada em config.ini. Edite " + str(self.config_path))

        self.sets_folder = Path(self.config['MT5'].get('sets_folder', str(BASE_DIR / 'sets')))
        self.mt5_path = self.config['MT5'].get('mt5_path', r"C:\\Program Files\\MetaTrader 5")
        
        # Usar pasta de curvas passada ou padrão
        if curvas_folder:
            self.curves_folder = Path(curvas_folder)
        else:
            self.curves_folder = self.sets_folder / 'curvas'
        
        self.curves_folder.mkdir(exist_ok=True)

        self.coords = self._carregar_coordenadas()

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3

        print(f"📁 Sets: {self.sets_folder}")
        print(f"📊 CSVs: {self.curves_folder}")
        # Instanciar monitor reutilizável
        self._monitor = BacktestMonitor(port=3000, poll_interval=0.5, verbose=True)
    
    def _carregar_coordenadas(self):
        """Carrega coordenadas do arquivo JSON"""
        default_coords = {
            'parameters_tab': (240, 681),
            'parameters_area': (600, 400),
            'menu_abrir': (600, 425),
            'start_button': (1336, 684),
            'graph_tab': (474, 683),
            'graph_area': (548, 460),
            'export_csv': (600, 500)
        }
        
        try:
            coord_path = BASE_DIR / "coordenadas.json"
            if coord_path.exists():
                with open(coord_path, 'r', encoding='utf-8') as f:
                    coords = json.load(f)
                for key, value in coords.items():
                    if hasattr(value, '__len__') and len(value) >= 2:
                        default_coords[key] = (value[0], value[1])
                print(f"✅ Coordenadas carregadas")
        except:
            print("📍 Usando coordenadas padrão")
        
        return default_coords
    
    def obter_arquivos_set(self):
        """Lista arquivos .set"""
        arquivos = list(self.sets_folder.glob("*.set"))
        if not arquivos:
            raise FileNotFoundError(f"Nenhum .set em: {self.sets_folder}")
        return sorted(arquivos)
    
    def garantir_mt5_rodando(self):
        """Verifica/inicia MT5"""
        for proc in psutil.process_iter(['name']):
            if 'terminal64.exe' in proc.info['name'].lower():
                print("✅ MT5 rodando")
                return
        
        print("🚀 Iniciando MT5...")
        terminal_path = os.path.join(self.mt5_path, 'terminal64.exe')
        if not os.path.exists(terminal_path):
            # Fallback para PATH do sistema
            terminal_path = 'terminal64.exe'
        subprocess.Popen([terminal_path])
        time.sleep(8)

    def encerrar_mt5(self, silent: bool = False):
        """Encerra todos os processos terminal64.exe para garantir reinício limpo.

        silent: não imprimir mensagens se True.
        """
        killed = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'terminal64.exe' in proc.info['name'].lower():
                    proc.kill()
                    killed += 1
            except Exception:
                continue
        if not silent:
            if killed:
                print(f"🛑 MT5 finalizado(s): {killed} processo(s)")
            else:
                print("ℹ️ Nenhum processo MT5 ativo para encerrar")
    
    def _encontrar_janela_mt5(self):
        """Encontra a janela do MT5 independente do título da corretora"""
        # Padrões específicos do MT5 (título contém corretora + netting/hedging ou XPMT5)
        # Exemplos: "12656329 - XPMT5-PRD - Netting - XP Investimentos"
        #           "123456 - MetaTrader 5 - Hedging - Clear"
        
        todas_janelas = pyautogui.getAllWindows()
        for janela in todas_janelas:
            titulo = janela.title
            titulo_lower = titulo.lower()
            
            # Padrão 1: Contém "Netting" ou "Hedging" (modo de conta MT5)
            if 'netting' in titulo_lower or 'hedging' in titulo_lower:
                return janela
            
            # Padrão 2: Contém "XPMT5" ou similar
            if 'xpmt5' in titulo_lower or 'mt5-' in titulo_lower:
                return janela
            
            # Padrão 3: Título começa com número (conta) e tem MetaTrader
            if titulo and titulo[0].isdigit() and 'metatrader' in titulo_lower:
                return janela
        
        return None
    
    def focar_mt5(self, forcar=True):
        """Foca janela MT5 com verificação robusta
        
        Args:
            forcar: Se True, tenta múltiplas vezes e levanta exceção se falhar
        
        Returns:
            bool: True se conseguiu focar, False caso contrário
        """
        janela = self._encontrar_janela_mt5()
        
        if not janela:
            if forcar:
                raise Exception("❌ MetaTrader 5 não está aberto! Abra o MT5 primeiro.")
            return False
        
        # Verificar se está minimizada
        if janela.isMinimized:
            print("📌 MT5 estava minimizado, restaurando...")
            janela.restore()
            time.sleep(0.5)
        
        # Tentar ativar múltiplas vezes
        for tentativa in range(3):
            try:
                janela.activate()
                time.sleep(0.3)
                
                # Verificar se realmente está em foco
                if janela.isActive:
                    return True
                    
            except Exception as e:
                if tentativa == 2:
                    print(f"⚠️ Aviso ao focar MT5: {e}")
        
        # Último recurso: Alt+Tab ou clicar na janela
        try:
            # Clicar no centro da janela para garantir foco
            centro_x = janela.left + janela.width // 2
            centro_y = janela.top + 50  # Parte superior (barra de título)
            pyautogui.click(centro_x, centro_y)
            time.sleep(0.3)
            return True
        except:
            pass
        
        if forcar:
            raise Exception("❌ Não foi possível focar a janela do MT5!")
        return False
    
    def verificar_mt5_em_foco(self):
        """Verifica se o MT5 está em primeiro plano"""
        try:
            janela = self._encontrar_janela_mt5()
            if janela and janela.isActive:
                return True
        except:
            pass
        return False
    
    def carregar_set_file(self, set_path):
        """Carrega arquivo .set usando pyperclip para suportar caracteres especiais"""
        # Garantir foco no MT5 antes de interagir
        self.focar_mt5(forcar=True)
        
        print(f"📂 Carregando {Path(set_path).stem}...")
        
        # Ir para aba Parâmetros
        pyautogui.click(self.coords['parameters_tab'])
        time.sleep(1)
        
        # Verificar foco novamente
        if not self.verificar_mt5_em_foco():
            self.focar_mt5(forcar=True)
        
        # Clique direito na área
        pyautogui.rightClick(self.coords['parameters_area'])
        time.sleep(1)
        
        # Abrir diálogo de arquivo: prioriza item 'Abrir'; fallback em 'load_button' ou atalho
        try:
            if 'menu_abrir' in self.coords:
                pyautogui.click(self.coords['menu_abrir'])
            elif 'load_button' in self.coords:
                pyautogui.click(self.coords['load_button'])
            else:
                # Fallback heurístico: item logo abaixo do clique direito
                x, y = self.coords['parameters_area']
                pyautogui.click(x, y + 25)
        except Exception:
            # Último recurso: tentar atalho comum
            pyautogui.hotkey('ctrl', 'o')
        
        time.sleep(1)
        
        # Usar pyperclip para colar caminho (suporta espaços e acentos)
        set_path_str = str(set_path)
        pyperclip.copy(set_path_str)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        
        return True
    
    def iniciar_backtest(self):
        """Inicia backtest"""
        # Garantir foco no MT5
        self.focar_mt5(forcar=True)
        
        print("⚡ Iniciando backtest...")
        pyautogui.click(self.coords['start_button'])
        time.sleep(2)
    
    # Métodos de monitoramento legado removidos (substituídos por BacktestMonitor em backtest_core.py)
    
    def exportar_csv(self, set_name):
        """Exporta resultado para CSV usando pyperclip para suportar caracteres especiais"""
        # Garantir foco no MT5
        self.focar_mt5(forcar=True)
        
        # Preparar nome do arquivo
        csv_filename = f"{set_name}.csv"
        
        # Garantir que pasta de destino existe
        self.curves_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Exportando {set_name}...")
        
        # Ir para aba Gráfico
        pyautogui.click(self.coords['graph_tab'])
        time.sleep(1.5)
        
        # Clique direito e exportar
        pyautogui.rightClick(self.coords['graph_area'])
        time.sleep(1)
        
        if 'export_csv' in self.coords:
            pyautogui.click(self.coords['export_csv'])
        else:
            pyautogui.press('e')
        
        # Aguardar janela "Salvar Como" aparecer
        time.sleep(1.5)
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # PASSO 1: Navegar para a pasta de destino
            # ═══════════════════════════════════════════════════════════════
            
            # Usar Ctrl+L para focar na barra de endereço
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.8)
            
            # Limpar e colar caminho usando pyperclip (suporta espaços e acentos)
            folder_path = str(self.curves_folder).replace('/', '\\')
            print(f"📂 Navegando para: {folder_path}")
            
            pyperclip.copy(folder_path)
            pyautogui.hotkey('ctrl', 'a')  # Selecionar tudo
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')  # Colar caminho
            time.sleep(0.5)
            pyautogui.press('enter')  # Navegar
            time.sleep(2)  # Aguardar navegação completar
            
            # ═══════════════════════════════════════════════════════════════
            # PASSO 2: Focar no campo "Nome do arquivo" e digitar nome
            # ═══════════════════════════════════════════════════════════════
            
            # Alt+N foca diretamente no campo "Nome do arquivo"
            pyautogui.hotkey('alt', 'n')
            time.sleep(0.5)
            
            # Selecionar todo o texto existente no campo
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Colar nome do arquivo usando pyperclip
            print(f"📝 Nome do arquivo: {csv_filename}")
            pyperclip.copy(csv_filename)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # PASSO 3: Salvar (pressionar Enter ou clicar Salvar)
            # ═══════════════════════════════════════════════════════════════
            
            pyautogui.press('enter')
            time.sleep(2)
            
            # Verificar se apareceu diálogo de substituição (arquivo já existe)
            # Se sim, confirmar com Enter novamente
            pyautogui.press('enter')
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Erro na exportação: {e}")
            # Tentar fechar qualquer diálogo aberto
            pyautogui.press('escape')
            time.sleep(0.5)
            return False
        
        # Verificar se arquivo foi criado
        csv_path = self.curves_folder / csv_filename
        time.sleep(1)  # Aguardar escrita em disco
        
        if csv_path.exists():
            size = csv_path.stat().st_size
            print(f"✅ CSV salvo: {csv_filename} ({size:,} bytes)")
            return True
        else:
            print(f"⚠️ Arquivo pode ter sido salvo com outro nome ou local")
            return True  # Não falhar a automação por isso
    
    def _calcular_timeout(self, set_path):
        """Calcula timeout dinâmico baseado no tamanho do arquivo .set"""
        try:
            tamanho = Path(set_path).stat().st_size
            # Base: 240s + 60s a cada 10KB de arquivo
            timeout_base = 240
            timeout_extra = (tamanho // 10240) * 60  # 60s por cada 10KB
            timeout_max = min(timeout_base + timeout_extra, 600)  # Máximo 10 minutos
            return max(timeout_base, timeout_max)
        except:
            return 240  # Fallback para 4 minutos
    
    def processar_set(self, set_path, index, total, tentativa=1, max_tentativas=2):
        """Processamento principal com retry automático e logging"""
        set_name = Path(set_path).stem
        tentativa_str = f" (tentativa {tentativa}/{max_tentativas})" if tentativa > 1 else ""
        print(f"\n🎯 [{index}/{total}] {set_name}{tentativa_str}")
        logger.info(f"Processando: {set_name}{tentativa_str}")
        
        inicio_set = time.time()
        
        try:
            # Verificar foco antes de cada set
            if not self.verificar_mt5_em_foco():
                print("📌 Refocando MT5...")
                self.focar_mt5(forcar=True)
                time.sleep(0.5)
            
            self.carregar_set_file(set_path)
            
            # Iniciar backtest
            self.iniciar_backtest()
            
            # Calcular timeout dinâmico
            timeout = self._calcular_timeout(set_path)
            print(f"⏱️ Timeout configurado: {timeout}s")
            logger.debug(f"Timeout para {set_name}: {timeout}s")
            
            # Monitorar via BacktestMonitor (reinicia estado cada set)
            self._monitor.start()
            terminou = self._monitor.wait(timeout=timeout)
            if not terminou:
                print("⚠️ Timeout aguardando backtest - prosseguindo com export")
                logger.warning(f"Timeout em {set_name}")
            
            self.exportar_csv(set_name)
            
            duracao_set = time.time() - inicio_set
            print(f"✅ {set_name} concluído")
            logger.success(set_name, duracao_set)
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            logger.failure(set_name, str(e))
            
            # Retry automático
            if tentativa < max_tentativas:
                print(f"🔄 Tentando novamente em 5 segundos...")
                logger.info(f"Retry para {set_name}")
                time.sleep(5)
                # Tentar refocar MT5 antes de retry
                try:
                    self.focar_mt5(forcar=True)
                except:
                    pass
                return self.processar_set(set_path, index, total, tentativa + 1, max_tentativas)
            
            return False
    
    def executar_automacao_completa(self):
        """Engine principal com logging completo"""
        print("=" * 40)
        print("🤖 MT5 AUTOMAÇÃO OTIMIZADA")
        print("=" * 40)
        
        logger.info("═══ AUTOMAÇÃO INICIADA ═══")
        
        try:
            # Verificar se MT5 está rodando e em foco
            self.garantir_mt5_rodando()
            
            # Verificar se consegue focar o MT5
            print("\n🔍 Verificando janela do MT5...")
            if not self.focar_mt5(forcar=False):
                print("❌ MT5 não está visível ou acessível!")
                print("💡 Por favor, abra o MetaTrader 5 e deixe visível.")
                logger.error("MT5 não acessível")
                input("\nPressione ENTER para voltar ao menu...")
                return
            
            print("✅ MT5 está em foco")
            logger.info("MT5 em foco")
            
            # Confirmação de segurança
            print("\n" + "="*50)
            print("⚠️  ATENÇÃO: A automação vai começar!")
            print("="*50)
            print("📌 Certifique-se que:")
            print("   1. O MT5 está aberto e visível")
            print("   2. O Strategy Tester está aberto")
            print("   3. Não mexa no mouse/teclado durante a execução")
            print("="*50)
            
            confirma = input("\n🚀 Iniciar automação? (S/n): ").strip().lower()
            if confirma == 'n':
                print("❌ Automação cancelada pelo usuário")
                logger.info("Automação cancelada pelo usuário")
                return
            
            # Focar MT5 novamente após confirmação
            print("\n🎯 Focando MT5...")
            self.focar_mt5(forcar=True)
            time.sleep(1)
            
            arquivos_set = self.obter_arquivos_set()
            total = len(arquivos_set)
            print(f"\n📋 {total} arquivos encontrados")
            logger.info(f"Arquivos .set encontrados: {total}")
            
            sucessos = 0
            falhas_lista = []
            inicio = time.time()
            
            for i, set_file in enumerate(arquivos_set, 1):
                if self.processar_set(set_file, i, total):
                    sucessos += 1
                else:
                    falhas_lista.append(Path(set_file).stem)
                
                if i < total:
                    time.sleep(3)
            
            # Resumo
            duracao = time.time() - inicio
            falhas = total - sucessos
            
            print(f"\n{'=' * 40}")
            print("📊 RESUMO FINAL")
            print(f"{'=' * 40}")
            print(f"✅ Sucessos: {sucessos}/{total}")
            print(f"❌ Falhas: {falhas}/{total}")
            print(f"⏱️ Tempo: {duracao:.1f}s")
            print(f"📁 Local: {self.curves_folder}")
            print(f"📋 Log: {logger.log_path}")
            
            if falhas_lista:
                print(f"\n⚠️ Arquivos com falha:")
                for f in falhas_lista:
                    print(f"   - {f}")
            
            # Log resumo final
            logger.resumo(total, sucessos, falhas, duracao)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            logger.error(f"Erro crítico: {e}")
            import traceback
            traceback.print_exc()
        
        # Sempre pausar no final para ver resultados
        input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    try:
        automacao = MT5Automacao()
        automacao.executar_automacao_completa()
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        input("\nPressione ENTER para sair...")
