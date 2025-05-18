# Turing Bot UTFPR

Bot para automatizar o acesso ao currículo da UTFPR, extraindo informações sobre cursos, disciplinas, turmas e horários.

## Funcionalidades

- Extração automática de dados do currículo da UTFPR
- Armazenamento em banco de dados PostgreSQL
- API REST para consulta dos dados
- Interface web para visualização
- Bot do Telegram para consultas rápidas

## Requisitos

- Python 3.11+
- PostgreSQL 12+
- Chrome/Chromium (para web scraping)
- ChromeDriver (compatível com sua versão do Chrome)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/MatheusCunha1/Turing-bot-utfpr.git
cd Turing-bot-utfpr
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o banco de dados:
- Crie um banco de dados PostgreSQL
- Copie o arquivo `.env.example` para `.env`
- Edite o arquivo `.env` com suas configurações

4. Execute as migrações:
```bash
python -m db.migrations
```

## Uso

1. Para extrair dados do currículo:
```bash
python -m scraper.main
```

2. Para iniciar a API:
```bash
python -m api.main
```

3. Para iniciar o bot do Telegram:
```bash
python -m bot.main
```

## Estrutura do Projeto

```
turing_bot/
├── api/            # API REST
├── bot/            # Bot do Telegram
├── core/           # Modelos e lógica de negócio
├── db/             # Camada de banco de dados
├── scraper/        # Web scraping
├── tests/          # Testes
└── web/            # Interface web
```

## Testes

Execute os testes com:
```bash
python -m pytest tests/ -v
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
