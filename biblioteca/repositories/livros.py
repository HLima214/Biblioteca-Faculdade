import re

from pymongo.collation import Collation

# Ordena ignorando maiúsculas/minúsculas e acentos
COLLATION_PT = Collation(locale="pt", strength=2)
SEM_ID = {"_id": 0}


class LivroRepository:
    def __init__(self, db):
        self.col = db["livros"]

    def inserir(self, livro):
        self.col.insert_one(dict(livro))  # cópia: o driver adiciona _id ao dict recebido

    def obter(self, isbn):
        return self.col.find_one({"isbn": isbn}, SEM_ID)

    def listar(self):
        return list(self.col.find({}, SEM_ID).sort("titulo", 1).collation(COLLATION_PT))

    def pesquisar(self, termo="", categoria=""):
        filtro = {}
        if termo:
            rx = {"$regex": re.escape(termo), "$options": "i"}
            filtro["$or"] = [{"titulo": rx}, {"autor": rx}]
        if categoria:
            filtro["categoria"] = {"$regex": f"^{re.escape(categoria)}$", "$options": "i"}
        return list(self.col.find(filtro, SEM_ID).sort("titulo", 1).collation(COLLATION_PT))

    def atualizar(self, isbn, campos, delta_estoque=None):
        """Atualiza campos; se delta_estoque vier, ajusta o estoque disponível junto."""
        filtro = {"isbn": isbn}
        update = {"$set": campos}
        if delta_estoque is not None:
            update["$inc"] = {"exemplares_disponiveis": delta_estoque}
            filtro["exemplares_disponiveis"] = {"$gte": -delta_estoque}  # nunca negativo
        return self.col.update_one(filtro, update).matched_count == 1

    def remover(self, isbn):
        return self.col.delete_one({"isbn": isbn}).deleted_count == 1

    def baixar_estoque(self, isbn):
        """Baixa ATÔMICA: só decrementa se ainda houver exemplar (evita estoque negativo)."""
        res = self.col.update_one(
            {"isbn": isbn, "exemplares_disponiveis": {"$gt": 0}},
            {"$inc": {"exemplares_disponiveis": -1}},
        )
        return res.modified_count == 1

    def repor_estoque(self, isbn):
        self.col.update_one({"isbn": isbn}, {"$inc": {"exemplares_disponiveis": 1}})
