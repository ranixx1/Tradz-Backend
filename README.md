# Mini Tradutor (Back-end)

Este é um servidor back-end simples, criado em Python com Flask, que serve como API para um projeto de tradução de texto.

Ele foi projetado para funcionar com um front-end (como o [seu projeto React](https://github.com/seu-usuario/seu-repo-frontend)) que envia texto e um idioma de destino.

## O que ele faz?

* **Recebe** um JSON com `texto` e `destino` (ex: 'en', 'es').
* **Usa** a biblioteca `deep-translator` (especificamente o Google Translator) para traduzir o texto.
* **Detecta** o idioma original automaticamente.
* **Devolve** um JSON com o `texto_traduzido`.

## Como Rodar

1.  **Clone o repositório** (ou tenha o `app.py` e o `requirements.txt` na mesma pasta).

2.  **Crie um ambiente virtual** (recomendado):
    ```sh
    python -m venv venv
    source venv/bin/activate  # No macOS/Linux
    .\venv\Scripts\activate   # No Windows
    ```

3.  **Instale as dependências**:
    ```sh
    pip install -r requirements.txt
    ```
    *(Isso instalará o `Flask`, `pytest` e outras ferramentas necessárias.)*

4.  **Inicie o servidor**:
    ```sh
    python app.py
    ```

O servidor estará rodando em `http://127.0.0.1:5000`.

## Como Testar

Este projeto usa `pytest` para testes automatizados para garantir que a API funcione como esperado.

1.  Certifique-se de que você já instalou as dependências (passo 3 da seção "Como Rodar").

2.  Na pasta raiz do projeto (`Tradz-Backend`), execute o comando:
    ```sh
    pytest
    ```

3.  O `pytest` irá descobrir automaticamente o arquivo `pytest.ini`, encontrar a pasta `test/`, executar todos os testes e mostrar um relatório.

4.  Se tudo estiver correto, você verá uma mensagem de sucesso:
    ```sh
    ================== 5 passed in X.XXs ==================
    ```

## API

### Endpoint: `/traduzir`

* **Método:** `POST`
* **JSON de Exemplo (Request):**
    ```json
    {
      "texto": "Olá, mundo!",
      "destino": "en"
    }
    ```
* **JSON de Exemplo (Sucesso - Response):**
    ```json
    {
      "texto_traduzido": "Hello World!"
    }
    ```
* **JSON de Exemplo (Erro - Response):**
    ```json
    {
      "erro": "Mensagem de erro aqui."
    }
    ```