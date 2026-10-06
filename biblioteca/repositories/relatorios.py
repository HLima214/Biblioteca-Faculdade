"""R6 - Relatórios com Aggregation Pipeline."""


class RelatorioRepository:
    def __init__(self, db):
        self.col = db["emprestimos"]

    def top_livros(self, limite=5):
        return list(self.col.aggregate([
            {"$group": {"_id": "$isbn", "total_emprestimos": {"$sum": 1}}},
            {"$sort": {"total_emprestimos": -1, "_id": 1}},
            {"$limit": limite},
            {"$lookup": {"from": "livros", "localField": "_id",
                         "foreignField": "isbn", "as": "livro"}},
            {"$unwind": "$livro"},
            {"$project": {"_id": 0, "isbn": "$_id", "titulo": "$livro.titulo",
                          "total_emprestimos": 1}},
            {"$sort": {"total_emprestimos": -1, "isbn": 1}},
        ]))

    def emprestimos_por_curso(self):
        return list(self.col.aggregate([
            {"$lookup": {"from": "alunos", "localField": "matricula",
                         "foreignField": "matricula", "as": "aluno"}},
            {"$unwind": "$aluno"},
            {"$group": {"_id": "$aluno.curso", "total_emprestimos": {"$sum": 1}}},
            {"$sort": {"total_emprestimos": -1, "_id": 1}},
            {"$project": {"_id": 0, "curso": "$_id", "total_emprestimos": 1}},
        ]))

    def alunos_atrasados(self):
        return list(self.col.aggregate([
            {"$match": {"data_devolucao": None,
                        "$expr": {"$lt": ["$data_prevista", "$$NOW"]}}},
            {"$lookup": {"from": "alunos", "localField": "matricula",
                         "foreignField": "matricula", "as": "aluno"}},
            {"$lookup": {"from": "livros", "localField": "isbn",
                         "foreignField": "isbn", "as": "livro"}},
            {"$unwind": "$aluno"},
            {"$unwind": "$livro"},
            {"$project": {
                "_id": 0,
                "aluno": "$aluno.nome",
                "livro": "$livro.titulo",
                "dias_atraso": {"$dateDiff": {"startDate": "$data_prevista",
                                              "endDate": "$$NOW", "unit": "day"}},
            }},
            {"$sort": {"dias_atraso": -1, "aluno": 1}},
        ]))

    def total_multas(self):
        resultado = list(self.col.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$multa"}}},
        ]))
        return resultado[0]["total"] if resultado else 0
