# UTFGradeBot

Sistema de web scraping e filtragem de horários de aulas da UTFPR - Campus Medianeira.

## 🚀 Scripts Principais

### **run_scraper_docker_fixed.py**
- **Função:** Extrai dados do Grade na Hora e salva no PostgreSQL Docker
- **Curso:** Ciência da Computação (Medianeira)
- **Dados:** 70 disciplinas, turmas e horários
- **Uso:** `python run_scraper_docker_fixed.py`

### **run_filtro_docker.py**
- **Função:** Filtra horários de aulas do banco PostgreSQL Docker
- **Interface:** Menu interativo para busca por horários
- **Uso:** `python run_filtro_docker.py`

## 📁 Estrutura do Projeto

```
UTFGradeBot/
├── run_scraper_docker_fixed.py    # Scraper principal (funcionando)
├── run_filtro_docker.py           # Filtrador principal (funcionando)
├── scripts/
│   ├── legacy/                    # Scripts antigos funcionais
│   ├── test/                      # Scripts de teste
│   └── old/                       # Versões antigas
├── chromedriver/                  # ChromeDriver local
├── config/                        # Configurações
├── db/                           # Scripts de banco
├── docker-compose.yml            # Configuração Docker
└── requirements.txt              # Dependências Python
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Docker e Docker Compose
- Chrome/Chromium
- ChromeDriver (incluído na pasta `chromedriver/`)

### Instalação
```bash
# 1. Clone o repositório
git clone <repository-url>
cd UTFGradeBot

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o Docker
docker-compose up -d

# 4. Execute o scraper
python run_scraper_docker_fixed.py

# 5. Execute o filtrador
python run_filtro_docker.py
```

## 📊 Dados Extraídos

### Curso: Ciência da Computação (Medianeira)
- **Código:** 04219
- **Disciplinas:** 70 disciplinas
- **Carga Horária:** 3.195 horas
- **Data de Atualização:** 31/07/2025 20:35:17

### Exemplo de Dados
```
[CC57A] Sistemas Inteligentes Aplicados (4 aulas/sem)
CC7 — Jorge Aikes Junior [ 3M4(L16) - 3M5(L16) - 5M3(L16) - 5M4(L16) ]

[MAT1002] Estruturas Geométricas E Vetores (3 aulas/sem)
ALI1 — Tatiane Cardoso Batista Flores [ 2M1(I11) - 2M2(I11) - 2M3(I11) ]
```

## 🔧 Configuração Docker

### Banco de Dados PostgreSQL
```yaml
# docker-compose.yml
db:
  image: postgres:12
  environment:
    POSTGRES_DB: utfgradebot
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: 1597
  ports:
    - "5432:5432"
```

### Configuração do Banco
- **Host:** localhost
- **Porta:** 5432
- **Database:** utfgradebot
- **User:** postgres
- **Password:** 1597

## 📋 Funcionalidades

### Scraper (`run_scraper_docker_fixed.py`)
- ✅ Extrai dados do Grade na Hora
- ✅ Salva no PostgreSQL Docker
- ✅ Processa 70 disciplinas
- ✅ Captura turmas e horários
- ✅ Logs detalhados

### Filtrador (`run_filtro_docker.py`)
- ✅ Conecta ao banco Docker
- ✅ Interface interativa
- ✅ Busca por horário específico
- ✅ Busca por múltiplos horários
- ✅ Exibe todos os horários da disciplina

## 🎯 Uso

### 1. Extrair Dados
```bash
python run_scraper_docker_fixed.py
```

### 2. Filtrar Horários
```bash
python run_filtro_docker.py
```

### Opções do Filtrador:
1. **Buscar por horário específico** (ex: 2M1)
2. **Informar horários disponíveis** (ex: 2M1 2M2 3M4 3M5 6M1 6M2)
3. **Sair**

## 📁 Scripts Organizados

### `/scripts/legacy/`
Scripts antigos mas funcionais:
- `run_scraper_med_CC.py` - Scraper original
- `run_scraper_working.py` - Versão funcionando
- `run_filtro_horarios.py` - Filtrador original
- `run_filtro_demo.py` - Versão com dados simulados

### `/scripts/test/`
Scripts de teste:
- `test_chromedriver.py` - Teste do ChromeDriver
- `test_filtro.py` - Teste do filtrador
- `run_tests.py` - Executor de testes

### `/scripts/old/`
Versões antigas:
- `run_scraper_final.py` - Versão final antiga
- `run_scraper_local.py` - Versão local
- `run_scraper_simple.py` - Versão simplificada

## 🔍 Exemplo de Uso

### Buscar disciplinas com horário específico:
```
Opção: 1
Horário: 2M1
```

### Buscar disciplinas com horários disponíveis:
```
Opção: 2
Horários: 2M1 2M2 3M4 3M5 6M1 6M2
```

## 📈 Status do Sistema

- ✅ **Scraper:** Funcionando perfeitamente
- ✅ **Filtrador:** Funcionando perfeitamente
- ✅ **Docker:** Configurado e operacional
- ✅ **Banco de Dados:** PostgreSQL funcionando
- ✅ **ChromeDriver:** Configurado localmente

## 🎉 Sistema 100% Funcional!

O sistema está completamente operacional e pronto para uso. Os dados são extraídos do Grade na Hora e salvos no PostgreSQL Docker, permitindo consultas rápidas e eficientes através do filtrador interativo.
