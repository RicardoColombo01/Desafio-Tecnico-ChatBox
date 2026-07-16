# backend/test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app, executar_consulta_sql

client = TestClient(app)

# Teste 1: Garante que a conexão com o banco local SQLite está ativa e retornando dados
def test_conexao_banco_de_dados():
    resultado = executar_consulta_sql("SELECT COUNT(*) as total FROM produtos")
    assert isinstance(resultado, list)
    assert "total" in resultado[0]

# Teste 2: Garante que a API responde com erro apropriado a requisições com corpo vazio
def test_mensagem_vazia_retorna_erro():
    response = client.post("/api/chat", json={"mensagem": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "A mensagem não pode ser vazia."