@echo off
echo Turing Bot - Scripts de execução
echo.

if "%1"=="" (
    echo Uso: run.bat [setup^|scraper^|consulta^|servico]
    echo.
    echo Opções:
    echo   setup    - Executa o setup inicial
    echo   scraper  - Executa o scraper
    echo   consulta - Consulta disciplinas por período
    echo   servico  - Executa o serviço de atualização
    exit /b 1
)

if "%1"=="setup" (
    python scripts/run_all.py --setup
) else if "%1"=="scraper" (
    python scripts/run_all.py --scraper
) else if "%1"=="consulta" (
    if "%2"=="" (
        echo Erro: É necessário informar o período.
        echo Uso: run.bat consulta [periodo]
        exit /b 1
    )
    python scripts/run_all.py --consulta %2
) else if "%1"=="servico" (
    python scripts/run_all.py --servico
) else (
    echo Erro: Opção inválida.
    echo Uso: run.bat [setup^|scraper^|consulta^|servico]
    exit /b 1
) 