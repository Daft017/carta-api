#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUIA RÁPIDO - Carta Contemplada API
====================================

Este script oferece um menu interativo para iniciar o projeto.
Execute: python guia_rapido.py
"""

import os
import sys
import subprocess
from pathlib import Path

def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu():
    """Mostra menu principal."""
    limpar_tela()
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          🏠 CARTA CONTEMPLADA API - GUIA RÁPIDO 🏠              ║
╚══════════════════════════════════════════════════════════════════╝

O QUE VOCÊ DESEJA FAZER?

1️⃣  Instalar dependências (primeira vez)
2️⃣  Criar arquivo de dados de exemplo
3️⃣  Iniciar Backend (FastAPI)
4️⃣  Ver status da API
5️⃣  Abrir documentação (Swagger)
6️⃣  Ver instruções completas (README)
7️⃣  Sair

═══════════════════════════════════════════════════════════════════
    """)

def instalar_dependencias():
    """Instala dependências Python."""
    print("\n📦 Instalando dependências...")
    print("   Isso pode levar alguns minutos...\n")
    
    backend_dir = Path(__file__).parent / "backend"
    requirements = backend_dir / "requirements.txt"
    
    if not requirements.exists():
        print("❌ Arquivo requirements.txt não encontrado!")
        input("\nPressione ENTER para voltar...")
        return
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
            cwd=str(backend_dir)
        )
        print("\n✅ Dependências instaladas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao instalar: {e}")
    
    input("\nPressione ENTER para voltar...")

def criar_dados_exemplo():
    """Executa script de criação de dados."""
    print("\n📝 Criando arquivo de dados de exemplo...\n")
    
    script = Path(__file__).parent / "backend" / "criar_exemplo_cotas.py"
    
    if not script.exists():
        print("❌ Script de criação não encontrado!")
        input("\nPressione ENTER para voltar...")
        return
    
    try:
        subprocess.run([sys.executable, str(script)])
        print("\n✅ Arquivo de dados criado com sucesso!")
        print(f"   Localização: dados/cotas.xlsx")
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
    
    input("\nPressione ENTER para voltar...")

def iniciar_backend():
    """Inicia o backend FastAPI."""
    print("\n🚀 Iniciando Backend FastAPI...\n")
    print("   A API estará disponível em: http://localhost:8000")
    print("   Documentação: http://localhost:8000/docs")
    print("\n   ⚠️  Pressione CTRL+C para parar o servidor\n")
    
    backend_main = Path(__file__).parent / "backend" / "main.py"
    
    if not backend_main.exists():
        print("❌ Arquivo main.py não encontrado!")
        input("\nPressione ENTER para voltar...")
        return
    
    try:
        os.chdir(Path(__file__).parent / "backend")
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Backend parado.")
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
    
    input("\nPressione ENTER para voltar...")

def ver_status():
    """Verifica status da API."""
    print("\n🔍 Verificando status da API...\n")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API ONLINE\n")
            print(f"   Status: {data['status']}")
            print(f"   Cache ativo: {data['cache']['ativo']}")
            print(f"   Duração cache: {data['cache']['duracao_segundos']}s")
            print(f"   Arquivo: {data['arquivo_dados']}")
            print(f"   Arquivo existe: {data['arquivo_existe']}")
        else:
            print(f"❌ API retornou erro: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ NÃO CONSEGUIU CONECTAR")
        print("   Backend não está rodando em http://localhost:8000")
        print("   Execute a opção 3 para iniciar!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione ENTER para voltar...")

def abrir_swagger():
    """Abre documentação Swagger."""
    print("\n📚 Abrindo documentação Swagger...\n")
    
    import webbrowser
    try:
        webbrowser.open("http://localhost:8000/docs")
        print("✅ Documentação aberta no navegador!")
        print("   URL: http://localhost:8000/docs")
    except Exception as e:
        print(f"❌ Erro ao abrir: {e}")
        print("   Acesse manualmente: http://localhost:8000/docs")
    
    input("\nPressione ENTER para voltar...")

def mostrar_readme():
    """Mostra conteúdo do README."""
    readme = Path(__file__).parent / "README.md"
    
    if not readme.exists():
        print("❌ README.md não encontrado!")
        input("\nPressione ENTER para voltar...")
        return
    
    limpar_tela()
    with open(readme, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Mostrar em paginação
    linhas = conteudo.split('\n')
    pagina = 0
    linhas_por_pagina = 20
    
    while True:
        limpar_tela()
        inicio = pagina * linhas_por_pagina
        fim = inicio + linhas_por_pagina
        
        print('\n'.join(linhas[inicio:fim]))
        
        if fim < len(linhas):
            print(f"\n[Página {pagina + 1}] Digite 's' para próxima ou 'q' para sair: ", end='')
            opcao = input().lower()
            if opcao == 's':
                pagina += 1
            elif opcao == 'q':
                break
        else:
            input("\nFim do arquivo. Pressione ENTER para voltar...")
            break

def main():
    """Loop principal."""
    while True:
        mostrar_menu()
        
        opcao = input("Digite sua escolha (1-7): ").strip()
        
        if opcao == "1":
            instalar_dependencias()
        elif opcao == "2":
            criar_dados_exemplo()
        elif opcao == "3":
            iniciar_backend()
        elif opcao == "4":
            ver_status()
        elif opcao == "5":
            abrir_swagger()
        elif opcao == "6":
            mostrar_readme()
        elif opcao == "7":
            print("\n👋 Até logo!\n")
            break
        else:
            print("\n❌ Opção inválida! Tente novamente.")
            input("Pressione ENTER...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido.")
