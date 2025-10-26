import pytest
import json
from app import app as Tradz

@pytest.fixture
def client():
    # Coloca o app em modo de "TESTE"
    Tradz.config['TESTING'] = True
    
    with Tradz.test_client() as client:
        yield client  # 'yield' é como um 'return' para fixtures

def test_traducao_sucesso(client):
    response = client.post('/traduzir', 
                           json={"texto": "Olá mundo", "destino": "en"})
    
    # Pega a resposta JSON
    data = response.get_json()
    assert response.status_code == 200
    assert "texto_traduzido" in data
    # Verifica se o valor é o esperado (ignorando maiúsculas/minúsculas)
    assert data["texto_traduzido"].lower() == "hello world"

def test_texto_vazio(client):
    response = client.post('/traduzir', 
                           json={"texto": "  ", "destino": "en"})
    
    data = response.get_json()
    assert response.status_code == 200
    assert "texto_traduzido" in data
    assert data["texto_traduzido"] == ""

def test_dados_incompletos(client):

    # Teste 1: Faltando a chave "texto"
    response_sem_texto = client.post('/traduzir', 
                                     json={"destino": "en"})
    
    assert response_sem_texto.status_code == 400
    assert "erro" in response_sem_texto.get_json()

    # Teste 2: Faltando a chave "destino"
    response_sem_destino = client.post('/traduzir', 
                                       json={"texto": "Olá"})
    
    assert response_sem_destino.status_code == 400
    assert "erro" in response_sem_destino.get_json()

def test_idioma_invalido(client):
    response = client.post('/traduzir', 
                           json={"texto": "Olá", "destino": "xx"})
    
    # A biblioteca 'deep-translator' vai falhar, e nosso app.py irá capturar a exceção e retornar um erro 500.
    assert response.status_code == 500
    data = response.get_json()
    assert "erro" in data
    assert "Ocorreu um erro no servidor" in data["erro"]

def test_metodo_get_nao_permitido(client):
    """
    Testa se tentar usar o método GET (que não definimos)
    retorna um erro 405 (Method Not Allowed).
    """
    response = client.get('/traduzir')
    assert response.status_code == 405
