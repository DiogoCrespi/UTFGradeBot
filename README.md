# Turing Bot - Scraper Grade na Hora UTFPR

Este projeto é um scraper para extrair dados do Grade na Hora da UTFPR e armazená-los em um banco de dados PostgreSQL.

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium instalado

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/turing-bot.git
cd turing-bot
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados:
- Crie um banco de dados PostgreSQL
- Execute o script `db/schema.sql` para criar as tabelas

5. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Ajuste as configurações conforme necessário

## Uso

Para executar o scraper:

```bash
python scraper/main.py
```

O script irá:
1. Conectar ao banco de dados
2. Acessar o Grade na Hora
3. Extrair informações dos cursos configurados
4. Salvar os dados no banco de dados

## Estrutura do Projeto

```
turing-bot/
├── config/
│   └── settings.py      # Configurações do projeto
├── db/
│   ├── schema.sql       # Schema do banco de dados
│   └── queries.py       # Queries SQL
├── scraper/
│   └── main.py         # Código principal do scraper
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
```


## API REST

A API REST foi implementada para permitir consultas aos dados do currículo da UTFPR. Ela utiliza FastAPI e oferece endpoints para listar cursos, disciplinas, turmas e carga horária.

### Endpoints

- `GET /api/cursos` - Lista todos os cursos
- `GET /api/cursos/{codigo}` - Retorna detalhes de um curso específico
- `GET /api/cursos/{codigo}/disciplinas` - Lista todas as disciplinas de um curso
- `GET /api/cursos/{codigo}/disciplinas/{periodo}` - Lista disciplinas de um período específico
- `GET /api/cursos/{codigo}/carga-horaria` - Retorna a carga horária total por período
- `GET /api/disciplinas/{codigo}` - Retorna detalhes de uma disciplina
- `GET /api/disciplinas/{codigo}/turmas` - Lista todas as turmas de uma disciplina

### Como executar a API

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o servidor:
   ```bash
   python run_api.py
   ```

3. Acesse a documentação interativa em:
   ```
   http://localhost:8000/docs
   ```
   
## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
