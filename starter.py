#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🥷 MT5 NINJA BACKTESTER - Sistema de Automação
Interface CLI Profissional com UI/UX Otimizada
Versão: 4.0 - Design Profissional
"""

import os
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 SISTEMA DE CORES E ESTILOS ANSI
# ═══════════════════════════════════════════════════════════════════════════════

class Cores:
    """Códigos ANSI para cores no terminal"""
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    
    # Cores Texto
    PRETO = '\033[30m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    MAGENTA = '\033[35m'
    CIANO = '\033[36m'
    BRANCO = '\033[37m'
    
    # Cores Texto Brilhantes
    VERMELHO_CLARO = '\033[91m'
    VERDE_CLARO = '\033[92m'
    AMARELO_CLARO = '\033[93m'
    AZUL_CLARO = '\033[94m'
    MAGENTA_CLARO = '\033[95m'
    CIANO_CLARO = '\033[96m'
    BRANCO_CLARO = '\033[97m'
    
    # Cores de Fundo
    BG_PRETO = '\033[40m'
    BG_VERMELHO = '\033[41m'
    BG_VERDE = '\033[42m'
    BG_AMARELO = '\033[43m'
    BG_AZUL = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CIANO = '\033[46m'
    BG_BRANCO = '\033[47m'


class UI:
    """Sistema de Interface do Usuário"""
    
    # Caracteres de Box Drawing
    LINHA_H = '═'
    LINHA_V = '║'
    CANTO_TL = '╔'
    CANTO_TR = '╗'
    CANTO_BL = '╚'
    CANTO_BR = '╝'
    T_DIR = '╠'
    T_ESQ = '╣'
    T_BAIXO = '╦'
    T_CIMA = '╩'
    CRUZ = '╬'
    
    # Largura padrão
    LARGURA = 70
    
    @staticmethod
    def limpar():
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def habilitar_cores_windows():
        """Habilita cores ANSI no Windows"""
        if os.name == 'nt':
            os.system('')  # Hack para habilitar ANSI no Windows
    
    @classmethod
    def linha(cls, char=LINHA_H, largura=None):
        """Desenha uma linha horizontal"""
        l = largura or cls.LARGURA
        return char * l
    
    @classmethod
    def caixa_topo(cls, largura=None):
        """Desenha o topo de uma caixa"""
        l = largura or cls.LARGURA
        return f"{cls.CANTO_TL}{cls.LINHA_H * (l-2)}{cls.CANTO_TR}"
    
    @classmethod
    def caixa_meio(cls, texto="", largura=None, alinhamento='centro', cor=None):
        """Desenha o meio de uma caixa com texto"""
        l = largura or cls.LARGURA
        texto_limpo = texto
        
        # Calcular espaço disponível
        espaco = l - 4  # 2 para bordas + 2 para espaço
        
        if alinhamento == 'centro':
            texto_formatado = texto_limpo.center(espaco)
        elif alinhamento == 'esquerda':
            texto_formatado = texto_limpo.ljust(espaco)
        else:
            texto_formatado = texto_limpo.rjust(espaco)
        
        if cor:
            return f"{cls.LINHA_V} {cor}{texto_formatado}{Cores.RESET} {cls.LINHA_V}"
        return f"{cls.LINHA_V} {texto_formatado} {cls.LINHA_V}"
    
    @classmethod
    def caixa_base(cls, largura=None):
        """Desenha a base de uma caixa"""
        l = largura or cls.LARGURA
        return f"{cls.CANTO_BL}{cls.LINHA_H * (l-2)}{cls.CANTO_BR}"
    
    @classmethod
    def caixa_divisor(cls, largura=None):
        """Desenha um divisor de caixa"""
        l = largura or cls.LARGURA
        return f"{cls.T_DIR}{cls.LINHA_H * (l-2)}{cls.T_ESQ}"
    
    @staticmethod
    def sucesso(msg):
        """Mensagem de sucesso"""
        print(f"{Cores.VERDE_CLARO}  ✓ {msg}{Cores.RESET}")
    
    @staticmethod
    def erro(msg):
        """Mensagem de erro"""
        print(f"{Cores.VERMELHO_CLARO}  ✗ {msg}{Cores.RESET}")
    
    @staticmethod
    def aviso(msg):
        """Mensagem de aviso"""
        print(f"{Cores.AMARELO_CLARO}  ⚠ {msg}{Cores.RESET}")
    
    @staticmethod
    def info(msg):
        """Mensagem informativa"""
        print(f"{Cores.CIANO_CLARO}  ℹ {msg}{Cores.RESET}")
    
    @staticmethod
    def destaque(msg):
        """Mensagem em destaque"""
        print(f"{Cores.MAGENTA_CLARO}{Cores.BOLD}  ★ {msg}{Cores.RESET}")
    
    @staticmethod
    def progresso(atual, total, texto=""):
        """Barra de progresso"""
        largura_barra = 40
        preenchido = int(largura_barra * atual / total) if total > 0 else 0
        barra = '█' * preenchido + '░' * (largura_barra - preenchido)
        percent = (atual / total * 100) if total > 0 else 0
        print(f"\r  {Cores.CIANO}{barra}{Cores.RESET} {percent:5.1f}% {texto}", end='', flush=True)
    
    @staticmethod
    def loading(msg="Carregando", duracao=1):
        """Animação de loading"""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        end_time = time.time() + duracao
        i = 0
        while time.time() < end_time:
            print(f"\r  {Cores.CIANO}{frames[i % len(frames)]} {msg}...{Cores.RESET}", end='', flush=True)
            time.sleep(0.1)
            i += 1
        print(f"\r  {Cores.VERDE}✓ {msg}... OK{Cores.RESET}      ")
    
    @staticmethod
    def input_styled(prompt, cor=None):
        """Input estilizado com tratamento de erro"""
        try:
            cor_prompt = cor or Cores.AMARELO_CLARO
            return input(f"{cor_prompt}  → {prompt}: {Cores.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
    
    @staticmethod
    def confirmar(msg):
        """Pede confirmação S/N"""
        try:
            resp = input(f"{Cores.AMARELO}  ? {msg} (S/n): {Cores.RESET}").strip().lower()
            return resp != 'n'
        except (EOFError, KeyboardInterrupt):
            return False
    
    @staticmethod
    def pausar(msg="Pressione ENTER para continuar"):
        """Pausa e aguarda ENTER"""
        try:
            input(f"\n{Cores.DIM}  {msg}...{Cores.RESET}")
        except (EOFError, KeyboardInterrupt):
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🛡️ SISTEMA DE TRATAMENTO DE ERROS
# ═══════════════════════════════════════════════════════════════════════════════

class ErrorHandler:
    """Gerenciador centralizado de erros"""
    
    @staticmethod
    def handle(func):
        """Decorator para tratamento de erros"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print(f"\n{Cores.AMARELO}  ⚠ Operação cancelada pelo usuário{Cores.RESET}")
                return None
            except ImportError as e:
                UI.erro(f"Módulo não encontrado: {e.name}")
                UI.info("Execute: pip install <modulo>")
                return None
            except FileNotFoundError as e:
                UI.erro(f"Arquivo não encontrado: {e.filename}")
                return None
            except PermissionError as e:
                UI.erro(f"Sem permissão: {e.filename}")
                return None
            except ConnectionError as e:
                UI.erro(f"Erro de conexão: {e}")
                return None
            except Exception as e:
                UI.erro(f"Erro inesperado: {type(e).__name__}")
                UI.erro(f"Detalhes: {str(e)}")
                print(f"\n{Cores.DIM}{'─'*60}")
                print("  TRACEBACK COMPLETO:")
                print('─'*60)
                traceback.print_exc()
                print(f"{'─'*60}{Cores.RESET}\n")
                return None
        return wrapper
    
    @staticmethod
    def safe_import(module_name):
        """Importação segura de módulos"""
        try:
            return __import__(module_name)
        except ImportError:
            UI.erro(f"Módulo '{module_name}' não instalado")
            return None
    
    @staticmethod
    def safe_call(func, *args, default=None, **kwargs):
        """Chamada segura de função"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            UI.erro(f"Erro em {func.__name__}: {e}")
            return default


# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 SISTEMA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

# Base do projeto
BASE_DIR = Path(__file__).resolve().parent


class MT5NinjaBacktester:
    """Sistema Principal do MT5 Ninja Backtester"""
    
    VERSION = "4.1.0"
    
    def __init__(self):
        UI.habilitar_cores_windows()
        self.pastas_configuradas = None
        self.status = {
            'dependencias': False,
            'arquivos': False,
            'mt5': False,
            'coordenadas': False
        }
    
    def exibir_header(self):
        """Exibe o cabeçalho do sistema"""
        print(f"{Cores.MAGENTA_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio(""))
        print(UI.caixa_meio("🥷  M T 5   N I N J A   B A C K T E S T E R  🥷"))
        print(UI.caixa_meio(f"Versão {self.VERSION} - Automação Profissional"))
        print(UI.caixa_meio(""))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
    
    def exibir_status_bar(self):
        """Exibe barra de status do sistema"""
        deps = f"{Cores.VERDE}●{Cores.RESET}" if self.status['dependencias'] else f"{Cores.VERMELHO}●{Cores.RESET}"
        arqs = f"{Cores.VERDE}●{Cores.RESET}" if self.status['arquivos'] else f"{Cores.VERMELHO}●{Cores.RESET}"
        mt5 = f"{Cores.VERDE}●{Cores.RESET}" if self.status['mt5'] else f"{Cores.VERMELHO}●{Cores.RESET}"
        coords = f"{Cores.VERDE}●{Cores.RESET}" if self.status['coordenadas'] else f"{Cores.VERMELHO}●{Cores.RESET}"
        
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        print(f"{Cores.DIM}  ┌─ STATUS ─────────────────────────────────────────────────────┐{Cores.RESET}")
        print(f"{Cores.DIM}  │ {deps} Deps  {arqs} Arquivos  {mt5} MT5  {coords} Coords   │  📅 {data_hora} │{Cores.RESET}")
        print(f"{Cores.DIM}  └──────────────────────────────────────────────────────────────┘{Cores.RESET}")
    
    def exibir_menu(self):
        """Exibe o menu principal"""
        print()
        print(f"{Cores.CIANO_CLARO}  ┌─────────────────────────────────────────────────────────────┐{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.BOLD}                    📋 MENU PRINCIPAL                        {Cores.RESET}{Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  ├─────────────────────────────────────────────────────────────┤{Cores.RESET}")
        
        # Operacional
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}  {Cores.VERDE_CLARO}▸ OPERACIONAL{Cores.RESET}                                            {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[1]{Cores.RESET} 🚀 Executar Automação Completa                    {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[2]{Cores.RESET} 📂 Verificar Arquivos .set                        {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[3]{Cores.RESET} 🧪 Extrair OOS (Multi-Steps)                      {Cores.CIANO_CLARO}│{Cores.RESET}")
        
        print(f"{Cores.CIANO_CLARO}  ├─────────────────────────────────────────────────────────────┤{Cores.RESET}")
        
        # Configuração
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}  {Cores.AMARELO_CLARO}▸ CONFIGURAÇÃO{Cores.RESET}                                           {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[4]{Cores.RESET} ⚙️  Configurar Pastas                              {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[5]{Cores.RESET} 📍 Calibrar Coordenadas                            {Cores.CIANO_CLARO}│{Cores.RESET}")
        
        print(f"{Cores.CIANO_CLARO}  ├─────────────────────────────────────────────────────────────┤{Cores.RESET}")
        
        # Diagnóstico
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}  {Cores.MAGENTA_CLARO}▸ DIAGNÓSTICO{Cores.RESET}                                            {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[6]{Cores.RESET} 🔍 Verificar Sistema                               {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[7]{Cores.RESET} 📋 Verificar Configuração                          {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[8]{Cores.RESET} 🎯 Testar Monitor MT5                              {Cores.CIANO_CLARO}│{Cores.RESET}")
        
        print(f"{Cores.CIANO_CLARO}  ├─────────────────────────────────────────────────────────────┤{Cores.RESET}")
        
        # Sistema
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}  {Cores.AZUL_CLARO}▸ SISTEMA{Cores.RESET}                                                {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[9]{Cores.RESET} 📚 Ajuda e Documentação                            {Cores.CIANO_CLARO}│{Cores.RESET}")
        print(f"{Cores.CIANO_CLARO}  │{Cores.RESET}    {Cores.BRANCO_CLARO}[0]{Cores.RESET} 🚪 Sair                                            {Cores.CIANO_CLARO}│{Cores.RESET}")
        
        print(f"{Cores.CIANO_CLARO}  └─────────────────────────────────────────────────────────────┘{Cores.RESET}")
        print()
    
    @ErrorHandler.handle
    def verificar_dependencias(self, silencioso=False):
        """Verifica se as dependências estão instaladas"""
        if not silencioso:
            print(f"\n{Cores.CIANO}  ● Verificando dependências...{Cores.RESET}")
        
        deps = ['pyautogui', 'psutil', 'PIL']
        todas_ok = True
        
        for dep in deps:
            try:
                if dep == 'PIL':
                    __import__('PIL')
                else:
                    __import__(dep)
                if not silencioso:
                    UI.sucesso(f"{dep}")
            except ImportError:
                todas_ok = False
                if not silencioso:
                    UI.erro(f"{dep} - NÃO INSTALADO")
        
        self.status['dependencias'] = todas_ok
        return todas_ok
    
    @ErrorHandler.handle
    def verificar_arquivos(self, silencioso=False):
        """Verifica arquivos essenciais"""
        if not silencioso:
            print(f"\n{Cores.CIANO}  ● Verificando arquivos...{Cores.RESET}")
        
        arquivos = [
            ('sistema_principal.py', 'Sistema Principal'),
            ('automacao.py', 'Automação'),
            ('monitor_mt5.py', 'Monitor MT5'),
            ('calibrar.py', 'Calibrador'),
            ('config.ini', 'Configuração'),
            ('coordenadas.json', 'Coordenadas')
        ]
        
        todos_ok = True
        for arquivo, desc in arquivos:
            existe = (BASE_DIR / arquivo).exists()
            if existe:
                if not silencioso:
                    UI.sucesso(f"{desc} ({arquivo})")
            else:
                todos_ok = False
                if not silencioso:
                    UI.erro(f"{desc} ({arquivo}) - NÃO ENCONTRADO")
        
        self.status['arquivos'] = todos_ok
        return todos_ok
    
    @ErrorHandler.handle
    def verificar_mt5(self, silencioso=False):
        """Verifica se MT5 está rodando (por processo, não por título)"""
        if not silencioso:
            print(f"\n{Cores.CIANO}  ● Verificando MetaTrader 5...{Cores.RESET}")
        
        try:
            import psutil
            
            # Procurar pelo processo terminal64.exe (MT5)
            mt5_processos = ['terminal64.exe', 'terminal.exe', 'metatrader64.exe', 'metatrader.exe']
            mt5_encontrado = False
            processo_nome = None
            
            for proc in psutil.process_iter(['name']):
                try:
                    nome = proc.info['name'].lower()
                    if nome in mt5_processos:
                        mt5_encontrado = True
                        processo_nome = proc.info['name']
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if mt5_encontrado:
                self.status['mt5'] = True
                if not silencioso:
                    UI.sucesso(f"MT5 encontrado: {processo_nome}")
                return True
            else:
                self.status['mt5'] = False
                if not silencioso:
                    UI.aviso("MT5 não está aberto (processo terminal64.exe não encontrado)")
                return False
        except Exception as e:
            self.status['mt5'] = False
            if not silencioso:
                UI.erro(f"Erro ao verificar MT5: {e}")
            return False
    
    @ErrorHandler.handle
    def verificar_coordenadas(self, silencioso=False):
        """Verifica se coordenadas estão calibradas"""
        if not silencioso:
            print(f"\n{Cores.CIANO}  ● Verificando coordenadas...{Cores.RESET}")
        
        coord_file = BASE_DIR / 'coordenadas.json'
        if coord_file.exists():
            try:
                import json
                with open(coord_file, 'r') as f:
                    coords = json.load(f)
                
                # Verificar se tem as coordenadas principais
                coords_necessarias = ['parameters_tab', 'start_button', 'parameters_area']
                faltando = [c for c in coords_necessarias if c not in coords]
                
                if not faltando:
                    self.status['coordenadas'] = True
                    if not silencioso:
                        UI.sucesso(f"Coordenadas OK ({len(coords)} pontos)")
                    return True
                else:
                    self.status['coordenadas'] = False
                    if not silencioso:
                        UI.aviso(f"Faltam coordenadas: {', '.join(faltando)}")
                    return False
            except Exception as e:
                self.status['coordenadas'] = False
                if not silencioso:
                    UI.erro(f"Erro ao ler coordenadas: {e}")
                return False
        else:
            self.status['coordenadas'] = False
            if not silencioso:
                UI.aviso("Arquivo de coordenadas não existe")
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🎯 FUNÇÕES DO MENU
    # ═══════════════════════════════════════════════════════════════════════════
    
    @ErrorHandler.handle
    def executar_automacao(self):
        """Executa a automação completa"""
        UI.limpar()
        
        print(f"\n{Cores.VERDE_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("🚀 AUTOMAÇÃO COMPLETA"))
        print(UI.caixa_meio("Sistema de Backtest Automatizado"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        # Verificações pré-execução
        print(f"\n{Cores.AMARELO}  ▸ Verificações Pré-Execução:{Cores.RESET}")
        
        # 1. Verificar MT5
        if not self.verificar_mt5():
            UI.erro("MT5 não está aberto!")
            UI.info("Abra o MetaTrader 5 antes de continuar")
            UI.pausar()
            return
        
        # 2. Verificar coordenadas
        if not self.verificar_coordenadas():
            UI.erro("Coordenadas não calibradas!")
            UI.info("Use a opção 5 para calibrar coordenadas")
            UI.pausar()
            return
        
        # 3. Verificar sets
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')
            sets_folder = config.get('MT5', 'sets_folder', fallback='')
            
            if not sets_folder or not Path(sets_folder).exists():
                UI.erro("Pasta de sets não configurada!")
                UI.info("Use a opção 4 para configurar pastas")
                UI.pausar()
                return
            
            sets_count = len(list(Path(sets_folder).glob("*.set")))
            if sets_count == 0:
                UI.erro(f"Nenhum arquivo .set na pasta!")
                UI.info(f"Pasta: {sets_folder}")
                UI.pausar()
                return
            
            UI.sucesso(f"{sets_count} arquivos .set encontrados")
        except Exception as e:
            UI.erro(f"Erro na verificação: {e}")
            UI.pausar()
            return
        
        # Confirmação
        print(f"\n{Cores.AMARELO}")
        print("  ╔════════════════════════════════════════════════════════════╗")
        print("  ║              ⚠️  ATENÇÃO - LEIA COM CUIDADO                 ║")
        print("  ╠════════════════════════════════════════════════════════════╣")
        print("  ║  A automação vai controlar mouse e teclado.                ║")
        print("  ║                                                            ║")
        print("  ║  CERTIFIQUE-SE DE:                                         ║")
        print("  ║  • MT5 está aberto e visível                               ║")
        print("  ║  • Strategy Tester está aberto na aba correta              ║")
        print("  ║  • Não mexa no computador durante a execução               ║")
        print("  ║                                                            ║")
        print("  ║  Para CANCELAR a qualquer momento: Ctrl+C                  ║")
        print("  ╚════════════════════════════════════════════════════════════╝")
        print(f"{Cores.RESET}")
        
        if not UI.confirmar("Iniciar automação agora"):
            UI.aviso("Automação cancelada pelo usuário")
            UI.pausar()
            return
        
        # Executar
        print(f"\n{Cores.VERDE_CLARO}  ▸ Iniciando automação...{Cores.RESET}\n")
        
        try:
            import sistema_principal
            if self.pastas_configuradas:
                sistema = sistema_principal.SistemaAutomacaoMT5(*self.pastas_configuradas)
            else:
                sistema = sistema_principal.SistemaAutomacaoMT5()
            
            sistema.executar_automacao_completa()
            
        except Exception as e:
            UI.erro(f"Erro durante automação: {e}")
            traceback.print_exc()
        
        UI.pausar()
    
    @ErrorHandler.handle
    def verificar_arquivos_set(self):
        """Verifica arquivos .set disponíveis"""
        UI.limpar()
        
        print(f"\n{Cores.AZUL_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("📂 VERIFICAR ARQUIVOS .SET"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')
            sets_folder = config.get('MT5', 'sets_folder', fallback='')
            
            if not sets_folder:
                UI.erro("Pasta de sets não configurada")
                UI.info("Use a opção 4 para configurar pastas")
                UI.pausar()
                return
            
            sets_path = Path(sets_folder)
            if not sets_path.exists():
                UI.erro(f"Pasta não existe: {sets_path}")
                UI.pausar()
                return
            
            arquivos_set = sorted(list(sets_path.glob("*.set")))
            total = len(arquivos_set)
            
            print(f"\n{Cores.CIANO}  ▸ Pasta: {Cores.BRANCO}{sets_path}{Cores.RESET}")
            print(f"{Cores.CIANO}  ▸ Total: {Cores.VERDE_CLARO}{total}{Cores.RESET} arquivos .set\n")
            
            if total > 0:
                print(f"  {Cores.DIM}{'─'*60}{Cores.RESET}")
                print(f"  {Cores.BOLD}{'#':>3}  {'Nome do Arquivo':<40} {'Tamanho':>10}{Cores.RESET}")
                print(f"  {Cores.DIM}{'─'*60}{Cores.RESET}")
                
                tamanho_total = 0
                for i, arquivo in enumerate(arquivos_set, 1):
                    tamanho = arquivo.stat().st_size
                    tamanho_total += tamanho
                    cor = Cores.VERDE if i % 2 == 0 else Cores.RESET
                    print(f"  {cor}{i:>3}  {arquivo.name:<40} {tamanho:>8,} B{Cores.RESET}")
                
                print(f"  {Cores.DIM}{'─'*60}{Cores.RESET}")
                print(f"  {Cores.BOLD}     {'TOTAL':<40} {tamanho_total:>8,} B{Cores.RESET}")
                
                # Verificar pasta de curvas
                curvas_path = sets_path / 'curvas'
                if curvas_path.exists():
                    csvs = len(list(curvas_path.glob("*.csv")))
                    print(f"\n{Cores.MAGENTA}  📊 Curvas exportadas: {csvs} arquivos CSV{Cores.RESET}")
            else:
                UI.aviso("Nenhum arquivo .set encontrado na pasta")
        
        except Exception as e:
            UI.erro(f"Erro: {e}")
            traceback.print_exc()
        
        UI.pausar()
    
    @ErrorHandler.handle
    def extrair_oos(self):
        """Extração de OOS"""
        UI.limpar()
        
        print(f"\n{Cores.MAGENTA_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("🧪 EXTRAÇÃO OOS"))
        print(UI.caixa_meio("Out-of-Sample Multi-Steps"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        try:
            import sistema_principal
            sistema = sistema_principal.SistemaAutomacaoMT5()
            sistema._menu_extracao_oos()
        except Exception as e:
            UI.erro(f"Erro na extração: {e}")
            traceback.print_exc()
        
        UI.pausar()
    
    @ErrorHandler.handle
    def configurar_pastas(self):
        """Configura pastas do sistema"""
        UI.limpar()
        
        print(f"\n{Cores.AMARELO_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("⚙️  CONFIGURAR PASTAS"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        print(f"\n{Cores.CIANO}  Configure os diretórios para os arquivos .set e curvas:{Cores.RESET}\n")
        
        # Ler configuração atual
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')
            sets_atual = config.get('MT5', 'sets_folder', fallback='')
            if sets_atual:
                print(f"  {Cores.DIM}Pasta atual: {sets_atual}{Cores.RESET}\n")
        except:
            sets_atual = ''
        
        # Pasta dos sets
        sets_folder = UI.input_styled("Pasta dos arquivos .set (ENTER para manter)")
        if not sets_folder:
            if sets_atual:
                sets_folder = sets_atual
            else:
                UI.aviso("Nenhuma pasta definida")
                UI.pausar()
                return None
        
        # Verificar/criar pasta
        if not os.path.exists(sets_folder):
            if UI.confirmar(f"Pasta não existe. Criar '{sets_folder}'"):
                try:
                    os.makedirs(sets_folder, exist_ok=True)
                    UI.sucesso("Pasta criada")
                except Exception as e:
                    UI.erro(f"Erro ao criar pasta: {e}")
                    UI.pausar()
                    return None
            else:
                UI.aviso("Configuração cancelada")
                UI.pausar()
                return None
        
        # Pasta das curvas
        curvas_default = os.path.join(sets_folder, "curvas")
        print(f"\n  {Cores.DIM}Sugestão: {curvas_default}{Cores.RESET}")
        curvas_folder = UI.input_styled("Pasta para curvas (ENTER para sugestão)")
        if not curvas_folder:
            curvas_folder = curvas_default
        
        os.makedirs(curvas_folder, exist_ok=True)
        
        # Salvar configuração
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')
            
            if 'MT5' not in config:
                config.add_section('MT5')
            
            config['MT5']['sets_folder'] = sets_folder
            
            with open(BASE_DIR / 'config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.pastas_configuradas = (sets_folder, curvas_folder)
            
            print(f"\n{Cores.VERDE}")
            print("  ╔════════════════════════════════════════════════════════════╗")
            print("  ║               ✓ CONFIGURAÇÃO SALVA                         ║")
            print("  ╠════════════════════════════════════════════════════════════╣")
            print(f"  ║  Sets:   {sets_folder[:50]:<50} ║")
            print(f"  ║  Curvas: {curvas_folder[:50]:<50} ║")
            print("  ╚════════════════════════════════════════════════════════════╝")
            print(f"{Cores.RESET}")
            
        except Exception as e:
            UI.erro(f"Erro ao salvar: {e}")
        
        UI.pausar()
        return (sets_folder, curvas_folder)
    
    @ErrorHandler.handle
    def calibrar_coordenadas(self):
        """Calibra coordenadas do MT5"""
        UI.limpar()
        
        print(f"\n{Cores.AMARELO_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("📍 CALIBRAR COORDENADAS"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        try:
            import calibrar
            calibrador = calibrar.MenuCalibrador()
            calibrador.executar_menu()
        except ImportError:
            UI.erro("Módulo de calibração não encontrado")
        except Exception as e:
            UI.erro(f"Erro: {e}")
            traceback.print_exc()
        
        # Reler status das coordenadas
        self.verificar_coordenadas(silencioso=True)
        UI.pausar()
    
    @ErrorHandler.handle
    def verificar_sistema(self):
        """Verifica status completo do sistema"""
        UI.limpar()
        
        print(f"\n{Cores.MAGENTA_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("🔍 VERIFICAÇÃO DO SISTEMA"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        # Verificar tudo
        self.verificar_dependencias()
        self.verificar_arquivos()
        self.verificar_mt5()
        self.verificar_coordenadas()
        
        # Resumo
        total_checks = len(self.status)
        total_ok = sum(self.status.values())
        
        print(f"\n  {Cores.DIM}{'─'*60}{Cores.RESET}")
        
        if total_ok == total_checks:
            print(f"\n{Cores.VERDE_CLARO}")
            print("  ╔════════════════════════════════════════════════════════════╗")
            print("  ║         🎉 SISTEMA 100% OPERACIONAL! 🎉                    ║")
            print("  ╚════════════════════════════════════════════════════════════╝")
            print(f"{Cores.RESET}")
        else:
            print(f"\n{Cores.AMARELO}")
            print(f"  ⚠️  Status: {total_ok}/{total_checks} verificações OK")
            print(f"  Resolva os itens marcados com ✗ antes de usar o sistema")
            print(f"{Cores.RESET}")
        
        UI.pausar()
    
    @ErrorHandler.handle
    def verificar_configuracao(self):
        """Exibe configuração detalhada"""
        UI.limpar()
        
        print(f"\n{Cores.AZUL_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("📋 CONFIGURAÇÃO DO SISTEMA"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        # Config.ini
        print(f"\n{Cores.AMARELO}  ▸ CONFIG.INI:{Cores.RESET}")
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')
            
            for section in config.sections():
                print(f"\n    {Cores.CIANO}[{section}]{Cores.RESET}")
                for key, value in config[section].items():
                    # Truncar valores longos
                    val_display = value if len(value) < 50 else value[:47] + "..."
                    print(f"      {key}: {Cores.BRANCO}{val_display}{Cores.RESET}")
        except Exception as e:
            UI.erro(f"Erro ao ler config.ini: {e}")
        
        # Coordenadas
        print(f"\n{Cores.AMARELO}  ▸ COORDENADAS:{Cores.RESET}")
        try:
            import json
            coord_file = BASE_DIR / 'coordenadas.json'
            if coord_file.exists():
                with open(coord_file, 'r') as f:
                    coords = json.load(f)
                
                for key, value in coords.items():
                    print(f"      {key}: {Cores.BRANCO}{value}{Cores.RESET}")
            else:
                UI.aviso("Arquivo coordenadas.json não existe")
        except Exception as e:
            UI.erro(f"Erro ao ler coordenadas: {e}")
        
        UI.pausar()
    
    @ErrorHandler.handle
    def testar_monitor(self):
        """Testa o monitor MT5"""
        UI.limpar()
        
        print(f"\n{Cores.CIANO_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("🎯 TESTAR MONITOR MT5"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        try:
            import sistema_principal
            sistema = sistema_principal.SistemaAutomacaoMT5()
            sistema._menu_monitor()
        except Exception as e:
            UI.erro(f"Erro: {e}")
            traceback.print_exc()
        
        UI.pausar()
    
    def mostrar_ajuda(self):
        """Exibe ajuda detalhada"""
        UI.limpar()
        
        print(f"\n{Cores.AZUL_CLARO}")
        print(UI.caixa_topo())
        print(UI.caixa_meio("📚 AJUDA E DOCUMENTAÇÃO"))
        print(UI.caixa_base())
        print(f"{Cores.RESET}")
        
        print(f"""
{Cores.VERDE_CLARO}  ▸ COMO USAR O SISTEMA:{Cores.RESET}

    1. {Cores.BOLD}Primeira execução:{Cores.RESET}
       • Verifique o sistema (opção 6)
       • Configure as pastas (opção 4)
       • Calibre as coordenadas (opção 5)

    2. {Cores.BOLD}Executar automação:{Cores.RESET}
       • Abra o MetaTrader 5
       • Abra o Strategy Tester (Ctrl+R)
       • Execute a automação (opção 1)

{Cores.AMARELO_CLARO}  ▸ REQUISITOS:{Cores.RESET}

    • Python 3.8+
    • MetaTrader 5 instalado
    • Bibliotecas: pyautogui, psutil, Pillow

{Cores.MAGENTA_CLARO}  ▸ ATALHOS IMPORTANTES:{Cores.RESET}

    • {Cores.BOLD}Ctrl+C{Cores.RESET} - Cancelar operação atual
    • {Cores.BOLD}ENTER{Cores.RESET}  - Confirmar / Continuar
    • {Cores.BOLD}N{Cores.RESET}      - Negar confirmação

{Cores.CIANO_CLARO}  ▸ RESOLUÇÃO DE PROBLEMAS:{Cores.RESET}

    • MT5 não detectado → Verifique se está aberto
    • Coordenadas erradas → Recalibre (opção 5)
    • Erros de permissão → Execute como Admin

{Cores.DIM}  ─────────────────────────────────────────────────────────────

  Versão: {self.VERSION}
  GitHub: https://github.com/RaelFilh96/mt5-ninja-backtester{Cores.RESET}
""")
        
        UI.pausar()
    
    def sair(self):
        """Encerra o programa"""
        UI.limpar()
        print(f"\n{Cores.MAGENTA_CLARO}")
        print("  ╔════════════════════════════════════════════════════════════╗")
        print("  ║                                                            ║")
        print("  ║       🥷 Obrigado por usar o MT5 Ninja Backtester! 🥷      ║")
        print("  ║                                                            ║")
        print("  ║              Até a próxima! Bons trades! 📈                ║")
        print("  ║                                                            ║")
        print("  ╚════════════════════════════════════════════════════════════╝")
        print(f"{Cores.RESET}\n")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🎮 LOOP PRINCIPAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def executar(self):
        """Loop principal do programa"""
        
        # Verificações iniciais silenciosas
        self.verificar_dependencias(silencioso=True)
        self.verificar_arquivos(silencioso=True)
        self.verificar_mt5(silencioso=True)
        self.verificar_coordenadas(silencioso=True)
        
        while True:
            try:
                UI.limpar()
                self.exibir_header()
                self.exibir_status_bar()
                self.exibir_menu()
                
                opcao = UI.input_styled("Escolha uma opção")
                
                if opcao is None:  # Ctrl+C ou EOF
                    break
                
                if opcao == "1":
                    self.executar_automacao()
                elif opcao == "2":
                    self.verificar_arquivos_set()
                elif opcao == "3":
                    self.extrair_oos()
                elif opcao == "4":
                    self.configurar_pastas()
                elif opcao == "5":
                    self.calibrar_coordenadas()
                elif opcao == "6":
                    self.verificar_sistema()
                elif opcao == "7":
                    self.verificar_configuracao()
                elif opcao == "8":
                    self.testar_monitor()
                elif opcao == "9":
                    self.mostrar_ajuda()
                elif opcao in ["0", "10"]:
                    self.sair()
                    break
                else:
                    UI.erro("Opção inválida! Digite um número de 0-9")
                    time.sleep(1)
                
                # Atualizar status após cada operação
                self.verificar_mt5(silencioso=True)
                self.verificar_coordenadas(silencioso=True)
                
            except KeyboardInterrupt:
                print(f"\n{Cores.AMARELO}  Operação cancelada{Cores.RESET}")
                if UI.confirmar("Deseja sair do programa"):
                    self.sair()
                    break
            except Exception as e:
                UI.erro(f"Erro inesperado: {e}")
                traceback.print_exc()
                UI.pausar()


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Função principal"""
    app = MT5NinjaBacktester()
    app.executar()


if __name__ == "__main__":
    main()
