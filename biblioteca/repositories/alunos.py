from biblioteca.repositories.livros import COLLATION_PT, SEM_ID


class AlunoRepository:
    def __init__(self, db):
        self.col = db["alunos"]

    def inserir(self, aluno):
        self.col.insert_one(dict(aluno))

    def obter(self, matricula):
        return self.col.find_one({"matricula": matricula}, SEM_ID)

    def listar(self):
        return list(self.col.find({}, SEM_ID).sort("nome", 1).collation(COLLATION_PT))

    def remover(self, matricula):
        return self.col.delete_one({"matricula": matricula}).deleted_count == 1
