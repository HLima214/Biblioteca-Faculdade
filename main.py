"""Ponto de entrada: python main.py"""
from pymongo.errors import PyMongoError

from biblioteca import config
from biblioteca.cli import executar_menu
from biblioteca.database import conectar, preparar_banco
from biblioteca.fabrica import criar_servicos


def main():
    db = conectar()
    try:
        db.client.admin.command("ping")
    except PyMongoError as e:
        print(f"Não foi possível conectar ao MongoDB ({config.MONGO_URI.split('@')[-1]}).")
        print("Local: suba o banco com 'docker compose up -d'.")
        print("Atlas: confira MONGO_URI, a liberação do seu IP (Network Access) e se o cluster está ativo.")
        print(f"Detalhe: {str(e)[:200]}")
        return
    try:
        preparar_banco(db)
    except PyMongoError as e:
        print(f"Não foi possível preparar o banco (índices/validações): {str(e)[:300]}")
        return
    executar_menu(criar_servicos(db))


if __name__ == "__main__":
    main()
