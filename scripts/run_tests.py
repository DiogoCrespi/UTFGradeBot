import pytest
import os
import sys

def executar_testes():
    """Executa os testes do projeto"""
    try:
        # Adiciona o diretório raiz ao PYTHONPATH
        sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        
        # Executa os testes
        pytest.main(['-v', 'tests/'])
        
    except Exception as e:
        print(f"Erro ao executar testes: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    executar_testes() 