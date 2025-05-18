# Turing Bot

Bot para extração e consulta de grades curriculares da UTFPR.

## 🚀 Funcionalidades

- Extração automática de grades curriculares da UTFPR
- Armazenamento em banco de dados PostgreSQL
- Consulta de disciplinas por período
- Cálculo de carga horária total por período
- Atualização automática dos dados

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- Chrome/Chromium (para o Selenium)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/turing_bot.git
cd turing_bot
```

2. Execute o script de setup:
```bash
# Windows
run.bat setup

# Linux/Mac
chmod +x run.sh
./run.sh setup
```

O script de setup irá:
- Criar um ambiente virtual
- Instalar as dependências
- Configurar o banco de dados
- Executar os testes

## 🎮 Uso

O projeto possui scripts para facilitar a execução das funcionalidades:

### Windows
```bash
# Executar o scraper
run.bat scraper

# Consultar disciplinas do 1º período
run.bat consulta 1

# Executar o serviço de atualização
run.bat servico
```

### Linux/Mac
```bash
# Executar o scraper
./run.sh scraper

# Consultar disciplinas do 1º período
./run.sh consulta 1

# Executar o serviço de atualização
./run.sh servico
```

## 🧪 Testes

Os testes são executados automaticamente durante o setup. Para executar os testes manualmente:

```bash
# Windows
python scripts/run_tests.py

# Linux/Mac
python3 scripts/run_tests.py
```

## 📝 Estrutura do Projeto

```
turing_bot/
├── core/                  # Lógica de negócio
├── scraper/              # Módulo de scraping
├── db/                   # Persistência
├── bot/                  # Integração com WhatsApp
├── config/               # Configurações
├── scripts/              # Scripts utilitários
└── tests/                # Testes
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 