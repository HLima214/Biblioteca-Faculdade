"""Dados de exemplo para demonstração (inclui um empréstimo já atrasado)."""
from datetime import timedelta

from biblioteca import tempo
from biblioteca.errors import RegraNegocio

LIVROS = [
    ("9788535902778", "Dom Casmurro", "Machado de Assis", 1899, "Romance", 3),
    ("9788532530783", "Harry Potter e a Pedra Filosofal", "J.K. Rowling", 1997, "Fantasia", 2),
    ("9788576082675", "Clean Code", "Robert C. Martin", 2008, "Tecnologia", 1),
    ("9788575225639", "Introdução a Algoritmos", "Thomas Cormen", 2009, "Tecnologia", 2),
]
ALUNOS = [
    ("2026001", "Maria Silva", "Engenharia de Software", "maria@faculdade.edu.br"),
    ("2026002", "João Souza", "Ciência da Computação", "joao@faculdade.edu.br"),
    ("2026003", "Ana Lima", "Engenharia de Software", "ana@faculdade.edu.br"),
]


def carregar(servicos):
    for livro in LIVROS:
        try:
            servicos.livros.cadastrar(*livro)
        except RegraNegocio:
            pass  # já existe
    for aluno in ALUNOS:
        try:
            servicos.alunos.cadastrar(*aluno)
        except RegraNegocio:
            pass

    # João pegou o Clean Code há 10 dias: o prazo (7 dias) venceu há 3 dias.
    isbn, matricula = "9788576082675", "2026002"
    ja_existe = any(e["isbn"] == isbn and e["matricula"] == matricula
                    for e in servicos.emprestimos.listar_abertos())
    if not ja_existe:
        try:
            servicos.emprestimos.emprestar(
                isbn, matricula, data_emprestimo=tempo.agora() - timedelta(days=10))
        except RegraNegocio:
            pass
