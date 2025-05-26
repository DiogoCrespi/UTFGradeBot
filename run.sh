#!/bin/bash

echo "UTF Grade Scraper - Scripts de execução"
echo

if [ $# -eq 0 ]; then
    echo "Uso: ./run.sh [setup|scraper|consulta|servico]"
    echo
    echo "Opções:"
    echo "  setup    - Executa o setup inicial"
    echo "  scraper  - Executa o scraper"
    echo "  consulta - Consulta disciplinas por período"
    echo "  servico  - Executa o serviço de atualização"
    exit 1
fi

case "$1" in
    "setup")
        python scripts/run_all.py --setup
        ;;
    "scraper")
        python scripts/run_all.py --scraper
        ;;
    "consulta")
        if [ -z "$2" ]; then
            echo "Erro: É necessário informar o período."
            echo "Uso: ./run.sh consulta [periodo]"
            exit 1
        fi
        python scripts/run_all.py --consulta "$2"
        ;;
    "servico")
        python scripts/run_all.py --servico
        ;;
    *)
        echo "Erro: Opção inválida."
        echo "Uso: ./run.sh [setup|scraper|consulta|servico]"
        exit 1
        ;;
esac 