"""R2 (alunos)."""
from pymongo.errors import DuplicateKeyError

from biblioteca.errors import RegraNegocio


class AlunoService:
    def __init__(self, alunos, emprestimos):
        self.alunos = alunos
        self.emprestimos = emprestimos

    def cadastrar(self, matricula, nome, curso, email):
        if not matricula or not nome or not curso:
            raise RegraNegocio("Matrícula, nome e curso são obrigatórios.")
        if "@" not in email:
            raise RegraNegocio("E-mail inválido: precisa conter @.")
        try:
            self.alunos.inserir(
                {"matricula": matricula, "nome": nome, "curso": curso, "email": email}
            )
        except DuplicateKeyError:
            raise RegraNegocio("Já existe um aluno com essa matrícula.")

    def buscar(self, matricula):
        return self.alunos.obter(matricula)

    def listar(self):
        return self.alunos.listar()

    def remover(self, matricula):
        if self.emprestimos.contar_abertos_do_aluno(matricula) > 0:
            raise RegraNegocio("Aluno com empréstimo em aberto não pode ser removido.")
        if not self.alunos.remover(matricula):
            raise RegraNegocio("Aluno não encontrado.")
