# FormatAI 🤖✨

[cite\_start]`FormatAI` é uma aplicação web de back-end construída com FastAPI que atua como um "tradutor universal de dados"[cite: 1]. O projeto utiliza a API do Claude da Anthropic, especificamente as ferramentas de Execução de Código e a API de Arquivos, para transformar, mapear e consolidar dados de arquivos de origem (como planilhas) em um novo formato definido por um arquivo de template.

## 🚀 Principais Funcionalidades

  * [cite_start]**Transformação de Dados com IA:** Utiliza o Claude para analisar e converter arquivos de dados de um formato para outro[cite: 11].
  * [cite\_start]**Mapeamento Inteligente:** A IA é instruída a mapear colunas de forma inteligente, mesmo que os nomes não sejam idênticos (ex: "Valor Total" vs "VLR\_TOTAL")[cite: 15].
  * [cite\_start]**Consolidação de Arquivos:** Capaz de processar múltiplos arquivos de origem e consolidá-los em um único arquivo de saída[cite: 19].
  * [cite\_start]**Interface Web Simples:** Fornece uma interface HTML (via Jinja2) para upload de arquivos[cite: 3].
  * [cite\_start]**Reutilização de Arquivos:** Permite que o usuário selecione arquivos já enviados para o workspace do Claude, em vez de fazer o upload novamente[cite: 4, 23].
  * [cite\_start]**Download Direto:** O arquivo processado e formatado é disponibilizado para download imediato (StreamingResponse)[cite: 7].


<img width="591" height="915" alt="image" src="https://github.com/user-attachments/assets/05f182f8-0a2f-4990-a411-7d58b4f418d3" />

## ⚙️ Como Funciona

A aplicação segue um fluxo de orquestração para realizar a formatação dos dados:

1.  [cite\_start]**Interface:** O usuário acessa a rota principal (`/api/v1/transform/`) [cite: 2][cite\_start], que serve uma página HTML (`index.html`)[cite: 3].
2.  [cite\_start]**Envio:** O usuário pode fazer o upload de novos arquivos de origem e um arquivo de template, ou selecionar os IDs de arquivos já existentes no Claude[cite: 4].
3.  [cite\_start]**Upload no Claude:** Os novos arquivos são enviados para a API de Arquivos (Files API) do Claude e recebem um `file_id`[cite: 10, 25].
4.  [cite\_start]**Construção do Prompt:** Um prompt detalhado é montado, instruindo a IA a usar a ferramenta de execução de código (`code_execution`)[cite: 12, 28]. Este prompt inclui os IDs de todos os arquivos de origem e do arquivo de template.
5.  [cite\_start]**Execução do Código:** O Claude é instruído a escrever e executar um script Python (usando `pandas`, `openpyxl`, `xlrd`) [cite: 16, 17] para:
      * [cite\_start]Analisar todos os arquivos[cite: 13].
      * [cite\_start]Mapear os dados das origens para o template[cite: 14].
      * [cite\_start]Consolidar os resultados[cite: 19].
      * [cite\_start]Salvar a saída como `resultado_formatado.xlsx`[cite: 19].
6.  [cite\_start]**Retorno:** A aplicação identifica o `file_id` do arquivo `resultado_formatado.xlsx` gerado na resposta do Claude[cite: 30].
7.  [cite\_start]**Download:** O serviço faz o download do conteúdo desse arquivo [cite: 32] [cite\_start]e o retorna ao usuário como um `StreamingResponse`, iniciando o download no navegador[cite: 7].

## 🛠️ Tecnologias Utilizadas

  * **Back-end:** FastAPI
  * **Servidor ASGI:** Uvicorn (implícito pelo FastAPI)
  * **IA (Core):** Anthropic Claude API
  * **Recursos Beta do Claude:**
      * [cite\_start]`code-execution-2025-08-25` [cite: 10, 28]
      * [cite\_start]`files-api-2025-04-14` [cite: 10]
  * **Bibliotecas Python:**
      * [cite\_start]`anthropic` [cite: 9]
      * [cite\_start]`fastapi` [cite: 1]
      * [cite\_start]`python-dotenv` [cite: 9]
      * [cite\_start]`jinja2` [cite: 3]
  * **Front-end:** HTML5 (via Jinja2 Templates)

## 📦 Estrutura do Projeto

```
FormatAI/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── format.py      # Contém a lógica de roteamento principal
│   │   │   │   └── __init__.py
│   │   │   ├── api.py           # Roteador principal da API v1
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py        # Carrega as variáveis de ambiente (API Key)
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   ├── claude_service.py  # Lógica de negócio (comunicação com Claude)
│   │   └── __init__.py
[cite_start]│   ├── static/                # Arquivos CSS, JS (se houver) [cite: 1]
[cite_start]│   └── main.py                # Ponto de entrada da aplicação FastAPI [cite: 1]
├── templates/
│   └── index.html             # Interface de upload
├── .env                       # Arquivo para variáveis de ambiente (não incluído)
└── README.md
```

## 🚀 Guia de Instalação e Execução

### 1\. Pré-requisitos

  * Python 3.8+
  * [cite\_start]Uma chave de API da Anthropic (Claude) [cite: 9]
  * [cite\_start]Acesso às features beta: `code-execution-2025-08-25` e `files-api-2025-04-14`[cite: 10].

### 2\. Instalação

1.  **Clone o repositório:**

    ```bash
    git clone <url-do-repositorio>
    cd FormatAI
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # (ou .\\venv\\Scripts\\activate no Windows)
    ```

3.  **Instale as dependências:**
    (O projeto não lista um `requirements.txt`, mas com base no código, você precisará de:)

    ```bash
    pip install fastapi "uvicorn[standard]" anthropic python-dotenv jinja2
    ```

4.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto (`FormatAI/`) e adicione sua chave da API:

    ```.env
    ANTHROPIC_API_KEY="sk-..."
    ```

### 3\. Executando a Aplicação

1.  **Inicie o servidor:**

    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Acesse a aplicação:**
    Abra seu navegador e acesse `http://127.0.0.1:8000/`. [cite\_start]Você será redirecionado automaticamente para a página de upload em `http://127.0.0.1:8000/api/v1/transform/`[cite: 2].

## 🔌 Endpoints da API

  * [cite\_start]`GET /api/v1/transform/` [cite: 3]
      * **Descrição:** Serve a página HTML principal (`index.html`) para o upload de arquivos.
  * [cite\_start]`GET /api/v1/transform/files` [cite: 23]
      * **Descrição:** Retorna uma lista de arquivos `.json` que já existem no workspace do Claude.
  * [cite\_start]`POST /api/v1/transform/formatar` [cite: 5]
      * [cite\_start]**Descrição:** Recebe os arquivos (novos ou IDs existentes) [cite: 4][cite\_start], orquestra o processo de formatação com o Claude [cite: 6] [cite\_start]e retorna o arquivo `resultado_formatado.xlsx` para download[cite: 7, 8].
