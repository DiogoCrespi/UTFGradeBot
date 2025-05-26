# UTFGradeBot - Scraper Grade na Hora UTFPR

Este projeto é um scraper para extrair dados do Grade na Hora da UTFPR e armazená-los em um banco de dados PostgreSQL.

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium instalado
- Docker e Docker Compose (para execução em container)

## Instalação e Configuração do Banco de Dados

### 1. Clone o repositório
```bash
git clone ....
cd ....
```

### 2. Crie e ative um ambiente virtual
```bash
python -m venv venv
# Ative o ambiente virtual:
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instale as dependências do projeto
```bash
pip install -r requirements.txt
pip install -e .  # Instalação em modo editável (recomendado)
```

### 4. Configure o banco de dados PostgreSQL
- Certifique-se de que o PostgreSQL está instalado e rodando na sua máquina.
- Crie o banco de dados (ajuste a senha se necessário):
```bash
psql -U postgres -c "DROP DATABASE IF EXISTS utfgradebot;"
psql -U postgres -c "CREATE DATABASE utfgradebot;"
```

### 5. Configure as variáveis de ambiente
- Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=utfgradebot
DB_USER=postgres
DB_PASSWORD=1597
```

### 6. Crie as tabelas do banco de dados
- Execute as migrações para criar todas as tabelas necessárias:
```bash
python db/run_migrations.py
```
- (Opcional, para garantir que todas as tabelas estejam corretas):
```bash
python db/clean_db.py
```

### 7. Verifique se o banco de dados está correto
```bash
python -m db.check_counts
```

## Uso com Docker

### 1. Construa as imagens Docker
```bash
docker-compose build
```

### 2. Execute o scraper para o curso de Ciência da Computação em Medianeira
```bash
docker-compose up scraper-cc
```

### 3. Execute o filtro de horários
```bash
docker-compose run --rm filtro-cc
```

O script irá:
1. Conectar ao banco de dados
2. Acessar o Grade na Hora
3. Extrair informações do curso de Ciência da Computação em Medianeira
4. Salvar os dados no banco de dados

## Estrutura do Projeto

```
UTFGradeBot/
├── config/
│   └── settings.py      # Configurações do projeto
├── db/
│   ├── schema.sql       # Schema do banco de dados
│   └── queries.py       # Queries SQL
├── scraper/
│   └── main.py         # Código principal do scraper
├── run_scraper_med_CC.py  # Script específico para CC Medianeira
├── run_filtro_horarios.py # Script para filtrar horários
├── requirements.txt     # Dependências do projeto
├── Dockerfile          # Configuração do container Docker
├── docker-compose.yml  # Configuração dos serviços Docker
└── README.md           # Este arquivo
```
### Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
