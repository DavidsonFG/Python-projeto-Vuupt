# Integração com API da Vuupt

Projeto simples em Python para integração com a API pública da Vuupt.com, focado em criação de serviços e rotas.

## Funcionalidades

- **Criação de Serviços**:
  - Cadastro de serviços de coleta ou entrega
  - Seleção de destinatários existentes ou criação de novos contatos
  - Geocodificação de endereços utilizando a API do Google Maps

- **Criação de Rotas**:
  - Associação de serviços a rotas
  - Definição de bases operacionais de início e fim
  - Associação opcional a veículos e agentes

## Requisitos

- Python 3.6+
- Flask
- Requests
- python-dotenv

## Instalação

1. Clone este repositório:
```
git clone https://github.com/seu-usuario/vuupt-api-integration.git
cd vuupt-api-integration
```

2. Crie um ambiente virtual e instale as dependências:
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Crie um arquivo `.env` baseado no exemplo:
```
cp .env.example .env
```

4. Edite o arquivo `.env` e adicione suas credenciais:
```
# Configurações da API da Vuupt
VUUPT_TOKEN=seu_token_aqui
VUUPT_BASE_URL=https://api.vuupt.com/api/v1

# Chave API do Google Maps
GOOGLE_MAPS_API_KEY=sua_chave_google_maps_api_aqui
```

## Uso

1. Inicie a aplicação:
```
python app.py
```

2. Acesse a interface web em `http://localhost:5000`

3. Utilize as funcionalidades:
   - Criar serviços com geocodificação automática de endereços
   - Criar rotas associadas aos serviços
   - Visualizar serviços e rotas cadastrados

## Estrutura de Arquivos

```
.
├── app.py              # Aplicação principal
├── .env.example        # Modelo para o arquivo de variáveis de ambiente
├── .gitignore          # Configuração de arquivos ignorados pelo Git
├── requirements.txt    # Dependências do projeto
├── README.md           # Documentação
└── templates/          # Templates HTML
    ├── base.html
    ├── index.html
    ├── servicos/
    │   ├── criar.html
    │   └── listar.html
    └── rotas/
        ├── criar.html
        └── listar.html
```

## Documentação da API

A aplicação utiliza a API pública da Vuupt, documentada em:
https://vuupt.stoplight.io/docs/api