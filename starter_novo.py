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
            if not os.path.exists(arquivo):
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
            config.read('config.ini', encoding='utf-8')

            if 'MT5' not in config:
                config.add_section('MT5')

            config['MT5']['sets_folder'] = sets_folder

            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)

            # Armazenar pastas configuradas
            self.pastas_configuradas = (sets_folder, curvas_folder)

            print("✅ config.ini atualizado")
            return True

        except Exception as e:
            print(f"❌ Erro ao atualizar config: {e}")
            return False

    def menu_principal(self):
        """Menu principal simplificado"""
        while True:
            print("\n" + "="*60)
            print("🤖 SISTEMA DE AUTOMAÇÃO MT5 - STARTER")
            print("="*60)
            print("1. 🚀 Iniciar Sistema Completo")
            print("2. ⚙️ Configurar Pastas")
            print("3. 🔍 Verificar Sistema")
            print("4. 📚 Ajuda")
            print("5. 🚪 Sair")
            print("="*60)

            try:
                opcao = input("Escolha uma opção: ").strip()

                if opcao == "1":
                    self.iniciar_sistema()
                elif opcao == "2":
                    pastas = self.configurar_pastas()
                    if pastas:
                        self.atualizar_config(*pastas)
                elif opcao == "3":
                    self.verificar_sistema()
                elif opcao == "4":
                    self.mostrar_ajuda()
                elif opcao == "5":
                    print("\n👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida!")

            except KeyboardInterrupt:
                print("\n👋 Cancelado pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

    def iniciar_sistema(self):
        """Inicia o sistema principal"""
        print("\n🚀 Iniciando Sistema de Automação MT5...")
        try:
            import sistema_principal
            # Passar pastas configuradas se existirem
            if self.pastas_configuradas:
                sistema_principal.main_com_pastas(*self.pastas_configuradas)
            else:
                sistema_principal.main()
        except ImportError:
            print("❌ Erro ao importar sistema_principal.py")
        except Exception as e:
            print(f"❌ Erro ao iniciar: {e}")

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
