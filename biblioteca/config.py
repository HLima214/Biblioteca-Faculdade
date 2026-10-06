"""Configuração da aplicação.

A conexão vem de variáveis de ambiente (ou de um arquivo .env), nunca do código.
- Docker local (padrão): mongodb://localhost:27017
- MongoDB Atlas: defina MONGO_URI com a string de conexão do cluster.
"""
import os

try:  # python-dotenv é opcional: se existir, lê o arquivo .env
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "Biblioteca_Faculdade")

# Regras de negócio
PRAZO_DIAS = 7
LIMITE_EMPRESTIMOS = 3
MULTA_POR_DIA = 2.00
