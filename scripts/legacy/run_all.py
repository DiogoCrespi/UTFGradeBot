import os
import sys
import argparse
from pathlib import Path

def executar_setup():
    """Executa o setup inicial"""
    from scripts.setup import setup
    setup()

def executar_scraper():
    """Executa o scraper"""
    from scripts.run_scraper import executar_scraper
    executar_scraper()

def executar_consulta(periodo):
    """Executa a consulta de disciplinas"""
    from scripts.consultar_disciplinas import consultar_disciplinas
    consultar_disciplinas(periodo)

def executar_servico():
    """Executa o serviço de atualização"""
    from scripts.run_service import executar_servico
    executar_servico()

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Turing Bot - Scripts de execução')
    parser.add_argument('--setup', action='store_true', help='Executa o setup inicial')
    parser.add_argument('--scraper', action='store_true', help='Executa o scraper')
    parser.add_argument('--consulta', type=int, help='Consulta disciplinas por período')
    parser.add_argument('--servico', action='store_true', help='Executa o serviço de atualização')
    
    args = parser.parse_args()
    
    # Adiciona o diretório raiz ao PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(root_dir))
    
    if args.setup:
        executar_setup()
    
    if args.scraper:
        executar_scraper()
    
    if args.consulta:
        executar_consulta(args.consulta)
    
    if args.servico:
        executar_servico()
    
    if not any([args.setup, args.scraper, args.consulta, args.servico]):
        parser.print_help()

if __name__ == '__main__':
    main() 