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
# threading/queue removidos após migração para BacktestMonitor
from backtest_core import BacktestMonitor

# Base do projeto (pasta deste arquivo)
BASE_DIR = Path(__file__).resolve().parent

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
    
    def focar_mt5(self, forcar=True):
        """Foca janela MT5 com verificação robusta
        
        Args:
            forcar: Se True, tenta múltiplas vezes e levanta exceção se falhar
        
        Returns:
            bool: True se conseguiu focar, False caso contrário
        """
        janelas_mt5 = pyautogui.getWindowsWithTitle('MetaTrader 5')
        
        if not janelas_mt5:
            if forcar:
                raise Exception("❌ MetaTrader 5 não está aberto! Abra o MT5 primeiro.")
            return False
        
        janela = janelas_mt5[0]
        
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
            janelas_mt5 = pyautogui.getWindowsWithTitle('MetaTrader 5')
            if janelas_mt5 and janelas_mt5[0].isActive:
                return True
        except:
            pass
        return False
    
    def carregar_set_file(self, set_path):
        """Carrega arquivo .set"""
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
        
        # Digitar caminho e confirmar
        pyautogui.typewrite(str(set_path), interval=0.02)
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
        """Exporta resultado para CSV"""
        # Garantir foco no MT5
        self.focar_mt5(forcar=True)
        
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
        
        time.sleep(1)
        
        # Método corrigido para navegação no Explorer
        try:
            # Aguardar janela do Explorer aparecer
            time.sleep(1)
            
            # Usar Ctrl+L para focar na barra de endereço (não na pesquisa)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(1.2)
            
            # Limpar campo completamente
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            # Digitar caminho mais devagar para garantir captura
            folder_path = str(self.curves_folder).replace('/', '\\')  # Forçar barras do Windows
            print(f"🔧 Navegando para: {folder_path}")
            pyautogui.typewrite(folder_path, interval=0.08)  # Mais devagar
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(3)  # Aguardar navegação
            
            # Aguardar carregar pasta completamente
            time.sleep(2)
            
            # Focar no campo nome do arquivo usando F2 ou clicue na área de nome
            # Método mais confiável: usar atalho Alt+N (Nome do arquivo)
            pyautogui.hotkey('alt', 'n')
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Erro na navegação: {e}")
            # Fallback mais simples - aguardar e tentar Tab
            print("🔧 Usando fallback - Tab para campo nome")
            time.sleep(2)
            # Pressionar Tab múltiplas vezes para chegar ao campo nome
            for _ in range(3):
                pyautogui.press('tab')
                time.sleep(0.3)

        # Método mais direto: focar e limpar campo nome
        try:
            # Garantir que estamos no campo nome, não na barra de endereço
            pyautogui.hotkey('alt', 'n')  # Forçar foco no campo nome
            time.sleep(0.5)
            
            # Limpar qualquer texto no campo nome
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)            # Garantir foco no campo nome do arquivo
            csv_filename = f"{set_name}.csv"
            full_path = self.curves_folder / csv_filename
            
            # Se pasta de destino não existe, criar
            self.curves_folder.mkdir(parents=True, exist_ok=True)
            
            # Método mais confiável: usar F2 para renomear/focar campo nome
            time.sleep(0.5)
            pyautogui.press('f2')  # Ativa modo de edição de nome
            time.sleep(0.5)
            
            # Limpar e digitar nome
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            print(f"💾 Digitando nome do arquivo: {csv_filename}")
            pyautogui.typewrite(csv_filename, interval=0.04)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Se F2 não funcionou, fallback com foco direto
            if not full_path.exists():
                print("🔧 Tentando método alternativo...")
                # Clicar no campo nome e tentar novamente
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                pyautogui.typewrite(csv_filename, interval=0.04)
                time.sleep(0.8)
                pyautogui.press('enter')
                time.sleep(2)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar: {e}")
            time.sleep(2)
        
        # Verificar criação
        csv_path = self.curves_folder / csv_filename
        if csv_path.exists():
            size = csv_path.stat().st_size
            print(f"✅ CSV: {csv_filename} ({size} bytes)")
        else:
            print(f"⚠️ CSV processado")
        
        return True
    
    def processar_set(self, set_path, index, total):
        """Processamento principal"""
        set_name = Path(set_path).stem
        print(f"\n🎯 [{index}/{total}] {set_name}")
        
        try:
            # Verificar foco antes de cada set
            if not self.verificar_mt5_em_foco():
                print("📌 Refocando MT5...")
                self.focar_mt5(forcar=True)
                time.sleep(0.5)
            
            self.carregar_set_file(set_path)
            
            # Iniciar backtest
            self.iniciar_backtest()
            # Monitorar via BacktestMonitor (reinicia estado cada set)
            self._monitor.start()
            terminou = self._monitor.wait(timeout=240)
            if not terminou:
                print("⚠️ Timeout aguardando backtest - prosseguindo com export (resultado pode estar incompleto)")
            self.exportar_csv(set_name)
            print(f"✅ {set_name} concluído")
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def executar_automacao_completa(self):
        """Engine principal"""
        print("=" * 40)
        print("🤖 MT5 AUTOMAÇÃO OTIMIZADA")
        print("=" * 40)
        
        try:
            # Verificar se MT5 está rodando e em foco
            self.garantir_mt5_rodando()
            
            # Verificar se consegue focar o MT5
            print("\n🔍 Verificando janela do MT5...")
            if not self.focar_mt5(forcar=False):
                print("❌ MT5 não está visível ou acessível!")
                print("💡 Por favor, abra o MetaTrader 5 e deixe visível.")
                input("\nPressione ENTER para voltar ao menu...")
                return
            
            print("✅ MT5 está em foco")
            
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
                return
            
            # Focar MT5 novamente após confirmação
            print("\n🎯 Focando MT5...")
            self.focar_mt5(forcar=True)
            time.sleep(1)
            
            arquivos_set = self.obter_arquivos_set()
            total = len(arquivos_set)
            print(f"\n📋 {total} arquivos encontrados")
            
            sucessos = 0
            inicio = time.time()
            
            for i, set_file in enumerate(arquivos_set, 1):
                if self.processar_set(set_file, i, total):
                    sucessos += 1
                
                if i < total:
                    time.sleep(3)
            
            # Resumo
            duracao = time.time() - inicio
            print(f"\n{'=' * 40}")
            print("📊 RESUMO FINAL")
            print(f"{'=' * 40}")
            print(f"✅ Sucessos: {sucessos}/{total}")
            print(f"❌ Falhas: {total - sucessos}/{total}")
            print(f"⏱️ Tempo: {duracao:.1f}s")
            print(f"📁 Local: {self.curves_folder}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
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
