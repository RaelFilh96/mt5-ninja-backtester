#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CALIBRADOR DE COORDENADAS MT5 - VERSÃO FUNCIONAL
"""

import pyautogui
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class CalibradorMT5:
    """Classe para calibração de coordenadas MT5"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.coords = {}
    
    def calibrar(self):
        """Calibra coordenadas"""
        print("\n🎯 INICIANDO CALIBRAÇÃO")
        print("📋 Instruções:")
        print("• Abra o MT5 e Strategy Tester")
        print("• Posicione mouse no elemento")
        print("• Pressione ENTER para capturar")
        print("• Digite 's' para pular")
        
        # Pontos para calibrar (alinhados com a automação)
        pontos = [
            ('parameters_tab', 'Aba Parâmetros do Strategy Tester'),
            ('parameters_area', 'Área de parâmetros (clique direito)'),
            ('menu_abrir', "Item 'Abrir' no menu de contexto"),
            ('load_button', 'Botão Load/Carregar parâmetros (opcional)'),
            ('start_button', 'Botão Start para iniciar backtest'),
            ('graph_tab', 'Aba Gráfico do Strategy Tester'),
            ('graph_area', 'Área do gráfico para clique direito'),
            ('export_csv', 'Opção Exportar CSV no menu')
        ]
        
        for nome, desc in pontos:
            print(f"\n📍 {desc}")
            choice = input("ENTER para capturar, 's' para pular: ").strip().lower()
            
            if choice == 's':
                print(f"⏭️ {nome}: Pulado")
                continue
            
            print("⏳ Capturando em 3 segundos...")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            
            try:
                x, y = pyautogui.position()
                self.coords[nome] = [x, y]  # Lista para JSON
                print(f"✅ {nome}: ({x}, {y})")
            except Exception as e:
                print(f"❌ Erro ao capturar {nome}: {e}")
        
        # Salvar coordenadas
        if self.coords:
            try:
                with open(BASE_DIR / 'coordenadas.json', 'w', encoding='utf-8') as f:
                    json.dump(self.coords, f, indent=2)
                print(f"\n✅ Calibração concluída!")
                print(f"📁 Coordenadas salvas: {BASE_DIR / 'coordenadas.json'}")
                print(f"🎯 Total: {len(self.coords)} pontos")
            except Exception as e:
                print(f"❌ Erro ao salvar: {e}")
        else:
            print("⚠️ Nenhuma coordenada foi calibrada")

class VisualizadorCoordenadas:
    """Classe para mostrar coordenadas salvas"""
    
    def mostrar_coordenadas(self):
        """Mostra coordenadas salvas"""
        try:
            with open(BASE_DIR / 'coordenadas.json', 'r', encoding='utf-8') as f:
                coords = json.load(f)

            print("\n📋 COORDENADAS SALVAS:")
            print("-" * 40)
            for nome, pos in coords.items():
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    print(f"{nome}: ({pos[0]}, {pos[1]})")
                elif isinstance(pos, dict) and 'x' in pos and 'y' in pos:
                    print(f"{nome}: ({pos['x']}, {pos['y']})")
                else:
                    print(f"{nome}: {pos}")

            print(f"\nTotal: {len(coords)} coordenadas")

        except FileNotFoundError:
            print("❌ Arquivo coordenadas.json não encontrado")
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")

class MenuCalibrador:
    """Classe para o menu do calibrador"""
    
    def __init__(self):
        self.calibrador = CalibradorMT5()
        self.visualizador = VisualizadorCoordenadas()
    
    def executar_menu(self):
        """Executa o menu principal"""
        print("="*50)
        print("🎯 CALIBRADOR DE COORDENADAS MT5")
        print("="*50)
        
        try:
            while True:
                print("\n" + "="*40)
                print("📍 CALIBRADOR DE COORDENADAS")
                print("="*40)
                print("1. 🎯 Calibrar Coordenadas")
                print("2. 📋 Ver Coordenadas")
                print("3. 🚪 Sair")
                print("="*40)
                
                opcao = input("Opção: ").strip()
                
                if opcao == "1":
                    self.calibrador.calibrar()
                elif opcao == "2":
                    self.visualizador.mostrar_coordenadas()
                elif opcao == "3":
                    print("👋 Saindo...")
                    break
                else:
                    print("❌ Opção inválida!")
                    
        except KeyboardInterrupt:
            print("\n👋 Interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    menu = MenuCalibrador()
    menu.executar_menu()
