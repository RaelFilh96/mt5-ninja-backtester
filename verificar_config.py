"""
VERIFICADOR SIMPLES - MT5 AUTOMAÇÃO
Verifica se tudo está pronto para automação
"""

import configparser
import os
import glob
from pathlib import Path

class VerificadorConfiguracao:
    """Classe para verificar configurações MT5"""
    
    def __init__(self):
        self.problemas = []
        self.sucesso = []
    
    def verificar_configuracao(self):
        """Verifica configurações essenciais"""
        
        print("="*60)
        print("  🔍 VERIFICADOR DE CONFIGURAÇÃO")
        print("="*60)
        
        self.problemas = []
        self.sucesso = []
        
        # 1. Verificar config.ini
        print("\n📋 1. VERIFICANDO CONFIG.INI...")
        self._verificar_config_ini()
        
        # 2. Verificar MT5
        print("\n🔧 2. VERIFICANDO METATRADER 5...")
        self._verificar_mt5()
        
        # 3. Verificar arquivos .set
        print("\n📁 3. VERIFICANDO ARQUIVOS .SET...")
        self._verificar_arquivos_set()
        
        # 4. Verificar pasta de curvas
        print("\n📊 4. VERIFICANDO PASTA DE CURVAS...")
        self._verificar_pasta_curvas()
        
        # 5. Resultados finais
        self._mostrar_resultados()
        
        return len(self.problemas) == 0
    
    def _verificar_config_ini(self):
        """Verifica arquivo config.ini"""
        try:
            if not os.path.exists('config.ini'):
                self.problemas.append("❌ Arquivo config.ini não encontrado")
            else:
                config = configparser.ConfigParser()
                config.read('config.ini', encoding='utf-8')
                
                # Verificar seções essenciais
                if 'MT5' not in config:
                    self.problemas.append("❌ Seção [MT5] não encontrada")
                if 'Tester' not in config:
                    self.problemas.append("❌ Seção [Tester] não encontrada")
                    
                if 'MT5' in config and 'Tester' in config:
                    self.sucesso.append("✅ Config.ini válido")
                    
                    # Mostrar configurações
                    print(f"   MT5 Path: {config.get('MT5', 'mt5_path', fallback='NÃO DEFINIDO')}")
                    print(f"   Login: {config.get('MT5', 'login', fallback='NÃO DEFINIDO')}")
                    print(f"   Sets Folder: {config.get('MT5', 'sets_folder', fallback='NÃO DEFINIDO')}")
                    print(f"   Symbol: {config.get('Tester', 'symbol', fallback='NÃO DEFINIDO')}")
                    print(f"   Period: {config.get('Tester', 'period', fallback='NÃO DEFINIDO')}")
                    
        except Exception as e:
            self.problemas.append(f"❌ Erro ao ler config.ini: {e}")
    
    def _verificar_mt5(self):
        """Verifica instalação do MT5"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            if 'MT5' in config:
                mt5_path = config['MT5']['mt5_path']
                terminal_exe = os.path.join(mt5_path, 'terminal64.exe')
                
                if os.path.exists(terminal_exe):
                    self.sucesso.append("✅ Terminal64.exe encontrado")
                    print(f"   Caminho: {terminal_exe}")
                else:
                    self.problemas.append(f"❌ Terminal64.exe não encontrado em: {terminal_exe}")
                    
        except Exception as e:
            self.problemas.append(f"❌ Erro ao verificar MT5: {e}")
    
    def _verificar_arquivos_set(self):
        """Verifica arquivos .set"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            if 'MT5' in config:
                sets_folder = config['MT5']['sets_folder']
                
                if os.path.exists(sets_folder):
                    self.sucesso.append("✅ Pasta de .set encontrada")
                    print(f"   Pasta: {sets_folder}")
                    
                    # Contar arquivos .set
                    set_pattern = os.path.join(sets_folder, "*.set")
                    set_files = glob.glob(set_pattern)
                    
                    if set_files:
                        self.sucesso.append(f"✅ {len(set_files)} arquivos .set encontrados")
                        print(f"   Arquivos .set: {len(set_files)}")
                        
                        # Mostrar primeiros 5
                        print("   Primeiros arquivos:")
                        for i, set_file in enumerate(set_files[:5], 1):
                            print(f"     {i}. {Path(set_file).name}")
                        
                        if len(set_files) > 5:
                            print(f"     ... e mais {len(set_files) - 5}")
                            
                    else:
                        self.problemas.append(f"❌ Nenhum arquivo .set encontrado em: {sets_folder}")
                        
                else:
                    self.problemas.append(f"❌ Pasta de .set não encontrada: {sets_folder}")
                    
        except Exception as e:
            self.problemas.append(f"❌ Erro ao verificar .set: {e}")
    
    def _verificar_pasta_curvas(self):
        """Verifica pasta de curvas"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            if 'MT5' in config:
                sets_folder = config['MT5']['sets_folder']
                curves_folder = os.path.join(sets_folder, 'curvas')
                
                # Criar pasta se não existir
                os.makedirs(curves_folder, exist_ok=True)
                self.sucesso.append("✅ Pasta de curvas pronta")
                print(f"   Pasta curvas: {curves_folder}")
                    
        except Exception as e:
            self.problemas.append(f"❌ Erro com pasta de curvas: {e}")
    
    def _mostrar_resultados(self):
        """Mostra resultados da verificação"""
        print("\n" + "="*60)
        print("  📊 RESULTADO DA VERIFICAÇÃO")
        print("="*60)
        
        if self.sucesso:
            print("\n✅ SUCESSOS:")
            for item in self.sucesso:
                print(f"   {item}")
        
        if self.problemas:
            print("\n❌ PROBLEMAS ENCONTRADOS:")
            for item in self.problemas:
                print(f"   {item}")
            
            print("\n🔧 AÇÕES RECOMENDADAS:")
            print("   1. Corrija os problemas listados")
            print("   2. Execute este verificador novamente")
            print("   3. Quando tudo OK, execute o teste")
            
        else:
            print("\n🎉 CONFIGURAÇÃO PERFEITA!")
            print("   Tudo pronto para automação")
            print("\n📋 PRÓXIMOS PASSOS:")
            print("   1. Execute: python teste_mt5.py")
            print("   2. Se OK, execute: python mt5_automator.py")

class MenuVerificador:
    """Classe para o menu do verificador"""
    
    def __init__(self):
        self.verificador = VerificadorConfiguracao()
    
    def executar_verificacao(self):
        """Executa a verificação"""
        print("Verificador simplificado que checa apenas o essencial:")
        print("- Config.ini válido")
        print("- MT5 instalado")  
        print("- Arquivos .set existem")
        print("- Pasta de curvas pronta\n")
        
        input("Pressione ENTER para verificar...")
        
        tudo_ok = self.verificador.verificar_configuracao()
        
        if tudo_ok:
            print(f"\n🚀 Pronto para automação!")
        else:
            print(f"\n⚠️  Corrija os problemas primeiro")
        
        input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    menu = MenuVerificador()
    menu.executar_verificacao()
