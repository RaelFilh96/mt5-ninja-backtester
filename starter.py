#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 STARTER - Sistema de Automação MT5
Ponto de entrada simplificado para o sistema
Versão: 2.0 - Arquitetura Orientada a Objetos
"""

import os
import sys
from pathlib import Path

# Base do projeto (pasta deste arquivo)
BASE_DIR = Path(__file__).resolve().parent


class StarterSistemaMT5:
    """Classe principal do starter do sistema MT5"""

    def __init__(self):
        self.pastas_configuradas = None

    def verificar_dependencias(self):
        """Verifica se as dependências estão instaladas"""
        try:
            import pyautogui
            import psutil
            print("✅ Dependências OK")
            return True
        except ImportError as e:
            print(f"❌ Dependência faltando: {e}")
            print("💡 Execute: pip install pyautogui psutil")
            return False

    def verificar_arquivos(self):
        """Verifica arquivos essenciais"""
        arquivos_essenciais = [
            'sistema_principal.py',
            'automacao.py',
            'monitor_mt5.py',
            'config.ini'
        ]

        faltando = []
        for arquivo in arquivos_essenciais:
            if not (BASE_DIR / arquivo).exists():
                faltando.append(arquivo)

        if faltando:
            print("❌ Arquivos faltando:")
            for arquivo in faltando:
                print(f"   - {arquivo}")
            return False

        print("✅ Arquivos essenciais OK")
        return True

    def configurar_pastas(self):
        """Configura pastas dos sets e curvas"""
        print("\n" + "="*50)
        print("📁 CONFIGURAÇÃO DE PASTAS")
        print("="*50)

        # Pasta dos sets
        sets_padrao = "C:/Users/israel.filho/Documents/WFA/PORTFOLIO B3/SETS EM LIVE"
        sets_folder = input(f"📂 Pasta dos arquivos .set: ").strip()
        if not sets_folder:
            sets_folder = sets_padrao

        # Verificar se pasta existe
        if not os.path.exists(sets_folder):
            print(f"⚠️ Pasta não existe: {sets_folder}")
            criar = input("Criar pasta? (s/n): ").strip().lower()
            if criar == 's':
                os.makedirs(sets_folder, exist_ok=True)
                print("✅ Pasta criada")
            else:
                print("❌ Configuração cancelada")
                return None

        # Pasta das curvas
        curvas_padrao = os.path.join(sets_folder, "curvas")
        curvas_folder = input(f"📊 Pasta para salvar curvas: ").strip()
        if not curvas_folder:
            curvas_folder = curvas_padrao

        # Criar pasta de curvas se não existir
        os.makedirs(curvas_folder, exist_ok=True)

        print("\n✅ Configuração concluída:")
        print(f"   Sets: {sets_folder}")
        print(f"   Curvas: {curvas_folder}")

        return sets_folder, curvas_folder

    def atualizar_config(self, sets_folder, curvas_folder):
        """Atualiza config.ini com as novas pastas"""
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')

            if 'MT5' not in config:
                config.add_section('MT5')

            config['MT5']['sets_folder'] = sets_folder

            with open(BASE_DIR / 'config.ini', 'w', encoding='utf-8') as f:
                config.write(f)

            # Armazenar pastas configuradas
            self.pastas_configuradas = (sets_folder, curvas_folder)

            print("✅ config.ini atualizado")
            return True

        except Exception as e:
            print(f"❌ Erro ao atualizar config: {e}")
            return False

    def menu_principal(self):
        """Menu principal unificado e conciso"""
        while True:
            print("\n" + "="*60)
            print("🤖 SISTEMA DE AUTOMAÇÃO MT5 v2.0")
            print("="*60)
            print("┌─ OPERACIONAL ───────────────────────────────────┐")
            print("│ 1. 🚀 Executar Automação Completa               │")
            print("│ 2. 📁 Verificar Arquivos .set                  │")
            print("│ 3. 🧪 Extrair OOS (multi-steps monitor robusto) │")
            print("└─ CONFIGURAÇÃO ──────────────────────────────────┘")
            print("│ 4. ⚙️ Configurar Pastas                        │")
            print("│ 5. 📍 Calibrar Coordenadas                     │")
            print("└─ DIAGNÓSTICO ───────────────────────────────────┘")
            print("│ 6. 🔍 Verificar Sistema                        │")
            print("│ 7. 📋 Verificar Configuração                   │")
            print("│ 8. 🎯 Testar Monitor MT5                       │")
            print("└─ SISTEMA ───────────────────────────────────────┘")
            print("│ 9. 📚 Ajuda                                   │")
            print("│ 10. 🚪 Sair                                   │")
            print("="*60)

            try:
                opcao = input("Escolha uma opção (1-10): ").strip()

                if opcao == "1":
                    self.iniciar_sistema_completo()
                elif opcao == "2":
                    self.verificar_arquivos_set()
                elif opcao == "3":
                    self.extrair_oos_via_ini()
                elif opcao == "4":
                    pastas = self.configurar_pastas()
                    if pastas:
                        self.atualizar_config(*pastas)
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
                elif opcao == "10":
                    print("\n👋 Obrigado por usar o Sistema de Automação MT5!")
                    break
                else:
                    print("❌ Opção inválida! Digite um número de 1 a 9.")

            except KeyboardInterrupt:
                print("\n👋 Sistema interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                input("Pressione ENTER para continuar...")

    def iniciar_sistema_completo(self):
        """Executa diretamente a automação completa"""
        print("\n🚀 EXECUTANDO AUTOMAÇÃO COMPLETA...")
        print("=" * 50)

        try:
            import sistema_principal
            # Passar pastas configuradas se existirem
            if self.pastas_configuradas:
                sistema = sistema_principal.SistemaAutomacaoMT5(*self.pastas_configuradas)
            else:
                sistema = sistema_principal.SistemaAutomacaoMT5()

            # Executar automação completa diretamente
            sistema.executar_automacao_completa()

        except ImportError:
            print("❌ Erro ao importar sistema_principal.py")
        except Exception as e:
            print(f"❌ Erro na automação: {e}")
            input("Pressione ENTER para continuar...")

    def verificar_arquivos_set(self):
        """Verifica arquivos .set disponíveis"""
        print("\n📁 VERIFICAÇÃO DE ARQUIVOS .SET")
        print("-" * 35)

        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(str(BASE_DIR / 'config.ini'), encoding='utf-8')
            sets_folder = config.get('MT5', 'sets_folder', fallback='')

            if not sets_folder:
                print("❌ Pasta de sets não configurada")
                print("💡 Use a opção 3 para configurar pastas")
                input("Pressione ENTER para continuar...")
                return

            import os
            from pathlib import Path
            sets_path = Path(sets_folder)

            if not sets_path.exists():
                print(f"❌ Pasta não existe: {sets_path}")
                input("Pressione ENTER para continuar...")
                return

            arquivos_set = list(sets_path.glob("*.set"))
            total = len(arquivos_set)

            print(f"📂 Pasta: {sets_path}")
            print(f"📋 Arquivos .set encontrados: {total}")

            if total > 0:
                print("\n📄 Lista de arquivos:")
                for i, arquivo in enumerate(sorted(arquivos_set), 1):
                    tamanho = arquivo.stat().st_size
                    print(f"   {i:2d}. {arquivo.name} ({tamanho:,} bytes)")

                # Verificar pasta de curvas
                curvas_path = sets_path / 'curvas'
                if curvas_path.exists():
                    arquivos_csv = list(curvas_path.glob("*.csv"))
                    print(f"\n📊 Pasta de curvas: {len(arquivos_csv)} CSVs salvos")
                else:
                    print(f"\n⚠️ Pasta de curvas não existe: {curvas_path}")

            print(f"\n✅ {total} arquivos .set prontos para processamento!")

        except Exception as e:
            print(f"❌ Erro na verificação: {e}")

        input("\nPressione ENTER para continuar...")

    def extrair_oos_via_ini(self):
        """Atalho no starter para abrir o menu de extração OOS do sistema principal."""
        print("\n🧪 EXTRAÇÃO OOS VIA INI")
        print("-" * 28)
        try:
            import sistema_principal
            sistema = sistema_principal.SistemaAutomacaoMT5()
            sistema._menu_extracao_oos()
        except Exception as e:
            print(f"❌ Erro: {e}")
        input("Pressione ENTER para continuar...")

    def calibrar_coordenadas(self):
        """Abre o sistema de calibração de coordenadas"""
        print("\n📍 CALIBRAÇÃO DE COORDENADAS")
        print("-" * 30)
        try:
            import calibrar
            calibrador = calibrar.MenuCalibrador()
            calibrador.executar_menu()
        except ImportError:
            print("❌ Módulo de calibração não encontrado")
        except Exception as e:
            print(f"❌ Erro na calibração: {e}")
        input("Pressione ENTER para continuar...")

    def verificar_configuracao(self):
        """Verifica configuração completa do sistema"""
        print("\n📋 VERIFICAÇÃO DE CONFIGURAÇÃO")
        print("-" * 32)

        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')

            print("📄 CONFIG.INI:")
            if 'MT5' in config:
                for key, value in config['MT5'].items():
                    print(f"   {key}: {value}")
            else:
                print("   ❌ Seção MT5 não encontrada")

            print("\n🔧 MT5:")
            mt5_path = config.get('MT5', 'mt5_path', fallback='')
            if mt5_path and os.path.exists(os.path.join(mt5_path, 'terminal64.exe')):
                print("   ✅ MetaTrader 5 encontrado")
            else:
                print("   ❌ MetaTrader 5 não encontrado")

            print("\n📁 ARQUIVOS:")
            sets_folder = config.get('MT5', 'sets_folder', fallback='')
            if sets_folder and os.path.exists(sets_folder):
                arquivos_set = len(list(Path(sets_folder).glob("*.set")))
                print(f"   ✅ Pasta de sets: {arquivos_set} arquivos .set")
            else:
                print("   ❌ Pasta de sets não configurada")

        except Exception as e:
            print(f"❌ Erro na verificação: {e}")

        input("\nPressione ENTER para continuar...")

    def testar_monitor(self):
        """Testa o sistema de monitoramento MT5"""
        print("\n🎯 TESTE DO MONITOR MT5")
        print("-" * 25)

        try:
            import sistema_principal
            sistema = sistema_principal.SistemaAutomacaoMT5()
            sistema._menu_monitor()
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            input("Pressione ENTER para continuar...")

    def verificar_sistema(self):
        """Verifica status do sistema"""
        print("\n🔍 VERIFICANDO SISTEMA...")
        print("-" * 30)

        # Verificar dependências
        deps_ok = self.verificar_dependencias()

        # Verificar arquivos
        arqs_ok = self.verificar_arquivos()

        # Verificar MT5
        mt5_ok = False
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            mt5_path = config.get('MT5', 'mt5_path', fallback='')
            if mt5_path and os.path.exists(os.path.join(mt5_path, 'terminal64.exe')):
                mt5_ok = True
                print("✅ MetaTrader 5 encontrado")
            else:
                print("❌ MetaTrader 5 não encontrado")
        except:
            print("❌ Erro ao verificar MT5")

        # Status geral
        if deps_ok and arqs_ok and mt5_ok:
            print("\n🎉 SISTEMA PRONTO!")
        else:
            print("\n⚠️ SISTEMA INCOMPLETO - Verifique os itens acima")

    def mostrar_ajuda(self):
        """Mostra ajuda do sistema"""
        print("\n" + "="*60)
        print("📚 AJUDA - Sistema de Automação MT5")
        print("="*60)
        print("""
COMO USAR:

1. 🚀 INICIAR SISTEMA:
   - Execute este arquivo (starter.py)
   - Escolha opção 1 para iniciar

2. ⚙️ CONFIGURAR PASTAS:
   - Defina onde estão seus arquivos .set
   - Defina onde salvar as curvas exportadas

3. 🔍 VERIFICAR SISTEMA:
   - Checa se tudo está configurado corretamente

4. 📋 FUNCIONALIDADES:
   - Automação completa de backtests
   - Monitoramento inteligente via porta 3000
   - Calibração automática de coordenadas
   - Verificação de configuração

5. 🎯 OTIMIZAÇÕES:
   - Detecção automática de fim de backtest
   - Redução de 40% no tempo de processamento
   - Interface orientada a objetos

SUPORTE:
- Certifique-se que MT5 está instalado
- Configure as coordenadas na primeira execução
- Verifique se a porta 3000 está acessível

""")

    def executar(self):
        """Executa o starter"""
        print("🤖 Bem-vindo ao Sistema de Automação MT5!")
        print("Versão: 2.0 - Otimizada")
        print("="*50)

        # Verificações iniciais
        if not self.verificar_dependencias():
            input("Pressione ENTER para sair...")
            return

        if not self.verificar_arquivos():
            input("Pressione ENTER para sair...")
            return

        # Iniciar menu
        self.menu_principal()


def main():
    """Função principal para compatibilidade"""
    starter = StarterSistemaMT5()
    starter.executar()


if __name__ == "__main__":
    main()
