import os
import subprocess
import sys
from pathlib import Path

def executar_comando(comando):
    """Executa um comando no terminal"""
    try:
        subprocess.run(comando, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando '{comando}': {str(e)}")
        sys.exit(1)

def setup():
    """Executa todo o processo de setup"""
    # Obtém o diretório raiz do projeto
    root_dir = Path(__file__).parent.parent
    
    # Cria o ambiente virtual
    print("Criando ambiente virtual...")
    executar_comando(f"python -m venv {root_dir}/venv")
    
    # Ativa o ambiente virtual
    if os.name == 'nt':  # Windows
        activate_script = f"{root_dir}/venv/Scripts/activate"
        executar_comando(f"call {activate_script}")
    else:  # Linux/Mac
        activate_script = f"{root_dir}/venv/bin/activate"
        executar_comando(f"source {activate_script}")
    
    # Instala as dependências
    print("Instalando dependências...")
    executar_comando(f"pip install -r {root_dir}/requirements.txt")
    
    # Inicializa o banco de dados
    print("Inicializando banco de dados...")
    executar_comando(f"python {root_dir}/scripts/init_db.py")
    
    # Executa os testes
    print("Executando testes...")
    executar_comando(f"python {root_dir}/scripts/run_tests.py")
    
    print("\nSetup concluído com sucesso!")
    print("\nPara ativar o ambiente virtual:")
    if os.name == 'nt':  # Windows
        print(f"call {root_dir}/venv/Scripts/activate")
    else:  # Linux/Mac
        print(f"source {root_dir}/venv/bin/activate")

if __name__ == '__main__':
    setup() 