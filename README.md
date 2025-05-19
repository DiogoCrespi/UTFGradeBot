# UTFGradeBot

Este projeto é um bot para o WhatsApp que permite consultar informações sobre o currículo da UTFPR.

## Colaboradores

- [Diogo Crespi](https://github.com/DiogoCrespi)

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

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
