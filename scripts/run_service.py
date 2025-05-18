import os
import sys
from pathlib import Path
from scripts.update_data import main as update_main

def executar_servico():
    """Executa o serviço de atualização"""
    try:
        # Adiciona o diretório raiz ao PYTHONPATH
        root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(root_dir))
        
        print("Iniciando serviço de atualização...")
        update_main()
        
    except KeyboardInterrupt:
        print("\nServiço interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro ao executar serviço: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    executar_servico() 