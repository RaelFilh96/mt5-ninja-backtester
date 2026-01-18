#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso da nova estrutura organizada de extração OOS

Este script demonstra como usar a arquitetura padronizada
e como customizar quando necessário.
"""

from extracao_oos import (
    create_default_oos_runner,
    OOSBatchRunner,
    list_available_templates,
    list_available_sets,
    get_default_paths,
    parse_oos_from_text
)
from automacao import MT5Automacao

def exemplo_uso_padrao():
    """Exemplo usando configuração padrão"""
    print("📋 Exemplo 1: Uso Padrão")
    print("=" * 50)
    
    # Mostrar caminhos padrão
    paths = get_default_paths()
    print("🗂️ Estrutura padrão:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    
    # Listar arquivos disponíveis
    print(f"\n📄 Templates disponíveis:")
    for template in list_available_templates():
        print(f"  - {template.name}")
        
    print(f"\n⚙️ Arquivos .set disponíveis:")
    for set_file in list_available_sets():
        print(f"  - {set_file.name}")
    
    # Criar runner com padrões
    runner = create_default_oos_runner()
    
    # Exemplo de ranges OOS
    ranges = parse_oos_from_text("14/10/2022 - 14/04/2023, 14/04/2023 - 14/10/2023")
    
    print(f"\n📊 Executaria {len(ranges)} steps OOS")
    # runner.run(ranges)  # Descomentei para executar

def exemplo_uso_customizado():
    """Exemplo com caminhos customizados"""
    print("\n📋 Exemplo 2: Uso Customizado")
    print("=" * 50)
    
    automacao = MT5Automacao()
    
    # Customizar caminhos específicos
    runner = OOSBatchRunner.create_custom(
        automacao=automacao,
        ini_template="C:/meus_templates/custom.ini",    # Template customizado
        set_path="C:/meus_sets/estrategia_x.set",       # SET específico  
        output_dir="C:/resultados_especiais"            # Pasta de saída customizada
    )
    
    print("🎯 Usaria caminhos customizados definidos pelo usuário")

def exemplo_interativo():
    """Exemplo perguntando caminhos ao usuário"""
    print("\n📋 Exemplo 3: Interativo")
    print("=" * 50)
    
    print("Opções:")
    print("1. Usar estrutura padrão")
    print("2. Definir caminhos customizados")
    
    # Simular escolha (na prática seria input())
    escolha = "1"  # input("Escolha (1/2): ")
    
    if escolha == "1":
        print("✅ Usando estrutura padrão organizada")
        runner = create_default_oos_runner()
    else:
        print("📝 Definindo caminhos customizados...")
        # ini_path = input("Caminho do template INI: ")
        # set_path = input("Caminho do arquivo .set: ") 
        # output_path = input("Pasta de saída: ")
        print("(Implementar inputs conforme necessário)")

if __name__ == "__main__":
    exemplo_uso_padrao()
    exemplo_uso_customizado() 
    exemplo_interativo()
    
    print(f"\n✅ Estrutura organizada implementada!")
    print(f"📁 Use create_default_oos_runner() para configuração automática")
    print(f"⚙️ Use OOSBatchRunner.create_custom() para customização")