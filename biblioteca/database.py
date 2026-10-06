"""Conexão com o MongoDB e preparação do banco (validações e índices).

`preparar_banco` é idempotente: pode rodar tanto num banco novo (Docker) quanto
num banco já criado manualmente no Atlas/Compass, sem recriar nada que já esteja certo.
"""
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from biblioteca import config

_NUMERO = ["int", "long", "double"]

VALIDADORES = {
    "alunos": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["matricula", "nome", "curso", "email"],
            "properties": {
                "matricula": {"bsonType": "string"},
                "nome": {"bsonType": "string"},
                "curso": {"bsonType": "string"},
                "email": {"bsonType": "string", "pattern": "@"},
            },
        }
    },
    "livros": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["isbn", "titulo", "autor", "ano", "categoria",
                         "exemplares_total", "exemplares_disponiveis"],
            "properties": {
                "isbn": {"bsonType": "string"},
                "titulo": {"bsonType": "string"},
                "autor": {"bsonType": "string"},
                "ano": {"bsonType": _NUMERO},
                "categoria": {"bsonType": "string"},
                "exemplares_total": {"bsonType": _NUMERO, "minimum": 0},
                "exemplares_disponiveis": {"bsonType": _NUMERO, "minimum": 0},
            },
        }
    },
}


def conectar(uri=None, db_name=None):
    """Devolve o banco (objeto Database) configurado."""
    client = MongoClient(uri or config.MONGO_URI, tz_aware=True, serverSelectionTimeoutMS=8000)
    return client[db_name or config.DB_NAME]


def aplicar_validacoes(db):
    existentes = set(db.list_collection_names())
    for nome, validador in VALIDADORES.items():
        opcoes = {"validator": validador, "validationLevel": "moderate",
                  "validationAction": "error"}
        try:
            if nome in existentes:
                db.command("collMod", nome, **opcoes)
            else:
                db.create_collection(nome, **opcoes)
        except OperationFailure as e:
            print(f"Aviso: não foi possível aplicar a validação em '{nome}': {e}")
    if "emprestimos" not in existentes:
        db.create_collection("emprestimos")


def _indice_unico(colecao, campo):
    """Garante um índice ÚNICO em `campo` (recria se existir um índice comum)."""
    for nome, info in colecao.index_information().items():
        if info["key"] == [(campo, 1)]:
            if info.get("unique"):
                return
            print(f"Recriando o índice '{nome}' de {colecao.name} como único.")
            colecao.drop_index(nome)
            break
    colecao.create_index([(campo, 1)], unique=True)


def _indice_apoio(colecao, chaves):
    try:
        colecao.create_index(chaves)
    except OperationFailure as e:
        print(f"Aviso: índice de apoio em {colecao.name} não criado: {e}")


def garantir_indices(db):
    _indice_unico(db["livros"], "isbn")
    _indice_unico(db["alunos"], "matricula")
    # Índices comuns (NÃO únicos): um aluno tem vários empréstimos e um livro também.
    _indice_apoio(db["emprestimos"], [("isbn", 1), ("data_devolucao", 1)])
    _indice_apoio(db["emprestimos"], [("matricula", 1), ("data_devolucao", 1)])


def preparar_banco(db):
    aplicar_validacoes(db)
    garantir_indices(db)
