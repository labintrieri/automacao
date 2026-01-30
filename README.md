# Portfólio Automatizado

Site de portfólio pessoal com funcionalidades de automação, incluindo raspagem de dados e integração com Telegram.

**Trabalho final da disciplina Algoritmos de Automação** — [Master em Jornalismo de Dados, Insper](https://www.insper.edu.br/pos-graduacao/master-em-jornalismo-de-dados-automacao-e-data-storytelling/)

## Sobre o Projeto

Este projeto foi desenvolvido para reunir em um só lugar:
- Publicações jornalísticas
- Projetos em jornalismo de dados
- Informações profissionais de contato

### Funcionalidades

- **Página dinâmica de eventos do Sesc**: Exibe automaticamente os próximos eventos culturais do Sesc SP, com dados raspados e armazenados em MongoDB
- **Bot do Telegram** *(atualmente desativado)*: Respondia com a programação do Sesc quando acionado

## Tecnologias

- **Backend**: Python, Flask
- **Banco de dados**: MongoDB
- **Deploy**: Render
- **Integrações**: API do Telegram (webhook)

## Estrutura do Projeto

```
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências Python
├── templates/
│   ├── index.html      # Página inicial
│   ├── infos.html      # Informações de contato
│   ├── projetos.html   # Projetos de jornalismo de dados
│   ├── publicacoes.html # Publicações na imprensa
│   └── sesc.html       # Página dinâmica com eventos do Sesc
└── static/             # Arquivos estáticos (CSS, imagens)
```

## Demo

> **Nota**: A demo pode estar offline devido às limitações do plano gratuito do Render (o serviço "adormece" após inatividade).

- Site: https://automacao-rby3.onrender.com/
- Página dinâmica: https://automacao-rby3.onrender.com/sesc

## Executando Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/labintrieri/automacao.git
   cd automacao
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```bash
   export MONGO_URI="sua_uri_mongodb"
   export MONGO_ID="nome_do_banco"
   export TELEGRAM_BOT_TOKEN="seu_token"  # opcional
   ```

4. Execute a aplicação:
   ```bash
   python app.py
   ```

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
