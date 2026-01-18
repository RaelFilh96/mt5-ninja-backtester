# -*- coding: utf-8 -*-
"""
SISTEMA DE AUTOMAÇÃO MT5 - Arquitetura Orientada a Objetos
"""

from automacao import MT5Automacao
from monitor_mt5 import MonitorMT5
from calibrar import MenuCalibrador
from verificar_config import MenuVerificador
from pathlib import Path
from extracao_oos import ExtracaoOOS, parse_oos_from_html, parse_oos_from_text, prompt_oos_steps
import os
import subprocess
import sys

class SistemaAutomacaoMT5:
    """Sistema principal de automação MT5"""

    def __init__(self, sets_folder=None, curvas_folder=None):
        # Configurar pastas dinamicamente se fornecidas
        # Caminho base do projeto
        self.base_dir = Path(__file__).resolve().parent

        if sets_folder:
            self.sets_folder = Path(sets_folder)
            self.curvas_folder = Path(curvas_folder) if curvas_folder else self.sets_folder / 'curvas'
            self.curvas_folder.mkdir(exist_ok=True)

            # Atualizar config em tempo real
            import configparser
            config = configparser.ConfigParser()
            config.read(self.base_dir / 'config.ini', encoding='utf-8')
            if 'MT5' not in config:
                config.add_section('MT5')
            config['MT5']['sets_folder'] = str(self.sets_folder)
            with open(self.base_dir / 'config.ini', 'w', encoding='utf-8') as f:
                config.write(f)

        # Inicializar componentes
        curvas_param = str(self.curvas_folder) if hasattr(self, 'curvas_folder') else None
        self.automacao = MT5Automacao(curvas_param)
        self.monitor = MonitorMT5()
        self.calibrador = MenuCalibrador()
        self.verificador = MenuVerificador()

    def executar_automacao_completa(self):
        """Executa toda a automação"""
        print("=" * 50)
        print("🚀 EXECUTANDO AUTOMAÇÃO COMPLETA")
        print("=" * 50)

        try:
            self.automacao.executar_automacao_completa()
        except Exception as e:
            print(f"❌ Erro na automação: {e}")

    def verificar_arquivos_set(self):
        """Verifica e lista arquivos .set na pasta configurada"""
        print("\n" + "="*50)
        print("📁 VERIFICAÇÃO DE ARQUIVOS .SET")
        print("="*50)
        
        try:
            # Obter arquivos .set
            arquivos_set = self.automacao.obter_arquivos_set()
            total = len(arquivos_set)
            
            print(f"📂 Pasta: {self.automacao.sets_folder}")
            print(f"📋 Total de arquivos .set: {total}")
            
            if total > 0:
                print("\n📄 Lista de arquivos encontrados:")
                for i, arquivo in enumerate(arquivos_set, 1):
                    nome = arquivo.name
                    tamanho = arquivo.stat().st_size
                    print(f"   {i:2d}. {nome} ({tamanho} bytes)")
                
                print(f"\n✅ {total} arquivos .set prontos para processamento!")
                
                # Verificar se há pasta de curvas
                curvas_path = self.automacao.curves_folder
                if curvas_path.exists():
                    arquivos_csv = list(curvas_path.glob("*.csv"))
                    print(f"📊 Pasta de curvas: {curvas_path}")
                    print(f"📈 CSVs existentes: {len(arquivos_csv)}")
                else:
                    print(f"⚠️ Pasta de curvas não existe: {curvas_path}")
                    
            else:
                print("❌ Nenhum arquivo .set encontrado!")
                print("💡 Verifique se a pasta está correta e contém arquivos .set")
                
        except FileNotFoundError as e:
            print(f"❌ Erro: {e}")
            print("💡 Configure a pasta correta no menu principal")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
        
        input("\nPressione ENTER para continuar...")

    def menu_principal(self):
        """Menu principal do sistema"""
        while True:
            print("\n" + "="*50)
            print("🤖 SISTEMA DE AUTOMAÇÃO MT5")
            print("="*50)
            print("1. ⚡ Executar Automação Completa")
            print("2. 📁 Verificar Arquivos .set")
            print("3. 📍 Calibrar Coordenadas")
            print("4. 📋 Verificar Configuração")
            print("5. 🔍 Testar Monitor MT5")
            print("6. 🧪 Extrair OOS (multi-steps)")
            print("7. 🚪 Sair")
            print("="*50)

            try:
                opcao = input("Opção: ").strip()

                if opcao == "1":
                    self.executar_automacao_completa()
                elif opcao == "2":
                    self.verificar_arquivos_set()
                elif opcao == "3":
                    self.calibrador.executar_menu()
                elif opcao == "4":
                    self.verificador.executar_verificacao()
                elif opcao == "5":
                    self._menu_monitor()
                elif opcao == "6":
                    self._menu_extracao_oos()
                elif opcao == "7":
                    print("👋 Saindo...")
                    break
                else:
                    print("❌ Opção inválida!")

            except KeyboardInterrupt:
                print("\n👋 Cancelado")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

    def _menu_extracao_oos(self):
        """Menu para extrair OOS usando arquivo INI e exportar CSVs."""
        print("\n" + "="*40)
        print("🧪 EXTRAÇÃO OOS VIA INI (monitor robusto por step)")
        print("="*40)

        try:
            import configparser
            cfg = configparser.ConfigParser()
            cfg.read(self.base_dir / 'config.ini', encoding='utf-8')
            oos_default = cfg.get('MT5', 'oos_curvas_folder', fallback=str(self.base_dir.parent / 'extracao_OOS' / 'output'))

            # Caminhos padrão atualizados para nova estrutura organizada
            ini_template = input("Caminho do template INI (ENTER p/ padrão): ").strip() or \
                r"C:\\Users\\Israel Filho\\Documents\\wfa\\auto-backtesting-20250922T001018Z-1-001\\extracao_OOS\\templates\\exemplo.ini"
            set_path = input("Caminho do arquivo .set (ENTER p/ padrão): ").strip() or \
                r"C:\\Users\\Israel Filho\\Documents\\wfa\\auto-backtesting-20250922T001018Z-1-001\\extracao_OOS\\sets\\BB 15 min ccm.set"
            out_dir = input(f"Pasta para salvar CSVs OOS (ENTER p/ {oos_default}): ").strip() or oos_default

            from pathlib import Path

            # ===== Validação Interativa do INI =====
            ini_candidate = Path(ini_template)
            if ini_candidate.is_dir():
                ini_files = sorted(ini_candidate.glob('*.ini'))
                if not ini_files:
                    print(f"❌ Nenhum .ini encontrado em {ini_candidate}")
                    return
                print("\n🗂 Arquivos .ini encontrados:")
                for idx, fp in enumerate(ini_files, 1):
                    print(f"  {idx:2d}. {fp.name}")
                escolha = input("Selecione o número do .ini (ENTER p/ 1): ").strip()
                if escolha.isdigit() and 1 <= int(escolha) <= len(ini_files):
                    ini_template = str(ini_files[int(escolha)-1])
                else:
                    ini_template = str(ini_files[0])
                print(f"✅ INI selecionado: {ini_template}")
            else:
                if not ini_candidate.exists():
                    print(f"❌ Arquivo INI não existe: {ini_candidate}")
                    return

            # ===== Validação Interativa do SET =====
            set_candidate = Path(set_path)
            if set_candidate.is_dir():
                set_files = sorted(set_candidate.glob('*.set'))
                if not set_files:
                    print(f"❌ Nenhum .set encontrado em {set_candidate}")
                    return
                print("\n🗂 Arquivos .set encontrados:")
                for idx, fp in enumerate(set_files, 1):
                    print(f"  {idx:2d}. {fp.name}")
                escolha = input("Selecione o número do .set (ENTER p/ 1): ").strip()
                if escolha.isdigit() and 1 <= int(escolha) <= len(set_files):
                    set_path = str(set_files[int(escolha)-1])
                else:
                    set_path = str(set_files[0])
                print(f"✅ SET selecionado: {set_path}")
            else:
                if not set_candidate.exists():
                    print(f"❌ Arquivo .set não existe: {set_candidate}")
                    return

            # Mostrar resumo antes de prosseguir
            print("\nResumo da Execução:")
            print(f"   Template INI: {ini_template}")
            print(f"   Arquivo SET:  {set_path}")
            print(f"   Pasta CSV OOS: {out_dir}")

            # Persistir nova pasta se diferente
            if 'MT5' not in cfg:
                cfg.add_section('MT5')
            if cfg.get('MT5', 'oos_curvas_folder', fallback='') != out_dir:
                cfg.set('MT5', 'oos_curvas_folder', out_dir)
                with open(self.base_dir / 'config.ini', 'w', encoding='utf-8') as f:
                    cfg.write(f)

            os.makedirs(out_dir, exist_ok=True)

            print("\nSelecione o método de entrada das datas:")
            print("1. HTML da tabela (colar DIV)")
            print("2. Texto com ranges separados por vírgula")
            print("3. Interativo: informar steps e ranges")
            metodo = input("Opção: ").strip()

            if metodo == "1":
                print("Cole o HTML (fim com uma linha vazia):")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
                html = "\n".join(lines)
                ranges = parse_oos_from_html(html)
            elif metodo == "2":
                texto = input("Digite os ranges (ex: 14/10/2022 - 14/04/2023, 14/04/2023 - 14/10/2023):\n").strip()
                ranges = parse_oos_from_text(texto)
            elif metodo == "3":
                ranges = prompt_oos_steps()
            else:
                print("❌ Método inválido")
                return

            if not ranges:
                print("❌ Nenhum range válido encontrado.")
                return

            print(f"\n📆 Ranges detectados ({len(ranges)}):")
            for i, (a, b) in enumerate(ranges, 1):
                print(f"  {i:02d}. {a} -> {b}")

            confirmar = input("Confirmar execução? (s/n): ").strip().lower()
            if confirmar != 's':
                print("🚫 Cancelado")
                return

            executor = ExtracaoOOS(self.automacao, ini_template, set_path, out_dir)
            executor.run_batch(ranges)

        except KeyboardInterrupt:
            print("\n👋 Cancelado")
        except Exception as e:
            print(f"❌ Erro na extração OOS: {e}")

    def _menu_monitor(self):
        """Menu do monitor MT5"""
        while True:
            print("\n" + "="*40)
            print("🎯 MONITOR MT5")
            print("="*40)
            print("1. 🔍 Testar Porta 3000")
            print("2. 🎯 Aguardar Backtest (Inteligente)")
            print("3. ⏳ Aguardar Backtest (Simples)")
            print("4. ↩️ Voltar")
            print("="*40)

            try:
                opcao = input("Opção: ").strip()

                if opcao == "1":
                    if self.monitor.testar_conexao_porta():
                        print("✅ Porta 3000 acessível")
                    else:
                        print("❌ Porta 3000 não acessível")
                elif opcao == "2":
                    self.monitor.aguardar_backtest_inteligente()
                elif opcao == "3":
                    self.monitor.aguardar_backtest_simples()
                elif opcao == "4":
                    break
                else:
                    print("❌ Opção inválida!")

                input("\nPressione ENTER para continuar...")

            except KeyboardInterrupt:
                print("\n👋 Cancelado")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

def main_com_pastas(sets_folder, curvas_folder):
    """Função principal com pastas específicas"""
    try:
        sistema = SistemaAutomacaoMT5(sets_folder, curvas_folder)
        sistema.menu_principal()
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        input("Pressione ENTER para sair...")

def main():
    """Função principal"""
    try:
        sistema = SistemaAutomacaoMT5()
        sistema.menu_principal()
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main()
