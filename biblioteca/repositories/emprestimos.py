class EmprestimoRepository:
    def __init__(self, db):
        self.col = db["emprestimos"]

    def inserir(self, emprestimo):
        self.col.insert_one(dict(emprestimo))

    def contar_abertos_do_aluno(self, matricula):
        return self.col.count_documents({"matricula": matricula, "data_devolucao": None})

    def contar_abertos_do_livro(self, isbn):
        return self.col.count_documents({"isbn": isbn, "data_devolucao": None})

    def existe_atrasado(self, matricula, agora):
        return self.col.find_one({
            "matricula": matricula, "data_devolucao": None,
            "data_prevista": {"$lt": agora},
        }) is not None

    def obter_aberto(self, isbn, matricula):
        return self.col.find_one({"isbn": isbn, "matricula": matricula, "data_devolucao": None})

    def existe_historico(self, isbn, matricula):
        return self.col.find_one({"isbn": isbn, "matricula": matricula}) is not None

    def registrar_devolucao(self, emprestimo_id, data_devolucao, multa):
        """O filtro data_devolucao=None garante que só UMA devolução seja registrada."""
        res = self.col.update_one(
            {"_id": emprestimo_id, "data_devolucao": None},
            {"$set": {"data_devolucao": data_devolucao, "multa": multa}},
        )
        return res.modified_count == 1

    def _detalhados(self, filtro, ordem):
        """Empréstimos com nome do aluno e título do livro (via $lookup)."""
        pipeline = [
            {"$match": filtro},
            {"$sort": ordem},
            {"$lookup": {"from": "alunos", "localField": "matricula",
                         "foreignField": "matricula", "as": "aluno"}},
            {"$lookup": {"from": "livros", "localField": "isbn",
                         "foreignField": "isbn", "as": "livro"}},
            {"$project": {
                "_id": 0, "isbn": 1, "matricula": 1, "data_emprestimo": 1,
                "data_prevista": 1, "data_devolucao": 1, "multa": 1,
                "aluno": {"$ifNull": [{"$arrayElemAt": ["$aluno.nome", 0]}, "(aluno removido)"]},
                "livro": {"$ifNull": [{"$arrayElemAt": ["$livro.titulo", 0]}, "(livro removido)"]},
            }},
        ]
        return list(self.col.aggregate(pipeline))

    def listar_abertos(self):
        return self._detalhados({"data_devolucao": None}, {"data_prevista": 1})

    def listar_devolucoes(self):
        return self._detalhados({"data_devolucao": {"$ne": None}}, {"data_devolucao": -1})
