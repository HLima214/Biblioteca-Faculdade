"""Fixtures dos testes.

Os testes usam um MongoDB REAL, o do docker-compose:
    docker compose up -d --wait
    pytest
Eles trabalham num banco separado (biblioteca_teste), apagado a cada teste,
e nunca tocam no banco da aplicação nem no Atlas.
"""
import os

import pytest
from pymongo import MongoClient

from biblioteca.database import preparar_banco
from biblioteca.fabrica import criar_servicos

URI_TESTE = os.environ.get("MONGO_URI_TESTE", "mongodb://localhost:27017")
DB_TESTE = "biblioteca_teste"


@pytest.fixture(scope="session")
def client():
    if URI_TESTE.startswith("mongodb+srv"):
        pytest.exit("Os testes não rodam no Atlas. Use o MongoDB do docker-compose.", returncode=2)
    cliente = MongoClient(URI_TESTE, tz_aware=True, serverSelectionTimeoutMS=3000)
    try:
        cliente.admin.command("ping")
    except Exception as e:
        pytest.exit(
            "MongoDB indisponível para os testes.\n"
            "Suba o banco com: docker compose up -d --wait\n"
            f"Detalhe: {str(e)[:150]}",
            returncode=2,
        )
    yield cliente
    cliente.drop_database(DB_TESTE)
    cliente.close()


@pytest.fixture
def db(client):
    client.drop_database(DB_TESTE)
    banco = client[DB_TESTE]
    preparar_banco(banco)  # mesmas validações e índices da aplicação
    return banco


@pytest.fixture
def servicos(db):
    return criar_servicos(db)


@pytest.fixture
def novo_livro(servicos):
    contador = {"n": 0}

    def _criar(isbn=None, titulo="Livro Teste", autor="Autor Teste", ano=2020,
               categoria="Geral", exemplares=1):
        contador["n"] += 1
        isbn = isbn or f"978000000{contador['n']:04d}"
        servicos.livros.cadastrar(isbn, titulo, autor, ano, categoria, exemplares)
        return isbn

    return _criar


@pytest.fixture
def novo_aluno(servicos):
    contador = {"n": 0}

    def _criar(matricula=None, nome="Aluno Teste", curso="Engenharia de Software",
               email="aluno@faculdade.edu.br"):
        contador["n"] += 1
        matricula = matricula or f"2026{contador['n']:03d}"
        servicos.alunos.cadastrar(matricula, nome, curso, email)
        return matricula

    return _criar
