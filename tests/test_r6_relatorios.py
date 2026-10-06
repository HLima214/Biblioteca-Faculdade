"""R6 - Relatórios (Aggregation Pipeline)."""
from datetime import timedelta

from biblioteca import tempo


def _ciclo(servicos, isbn, matricula, vezes):
    for _ in range(vezes):
        servicos.emprestimos.emprestar(isbn, matricula)
        servicos.emprestimos.devolver(isbn, matricula)


def test_r6_top_5_livros_mais_emprestados(servicos, novo_livro, novo_aluno):
    matricula = novo_aluno()
    isbns = [novo_livro(titulo=f"Livro {i}") for i in range(1, 7)]
    for isbn, vezes in zip(isbns, [6, 5, 4, 3, 2, 1]):
        _ciclo(servicos, isbn, matricula, vezes)

    top = servicos.relatorios.top_livros()

    assert len(top) == 5                                   # o 6º (1 empréstimo) fica de fora
    assert [t["titulo"] for t in top] == ["Livro 1", "Livro 2", "Livro 3", "Livro 4", "Livro 5"]
    assert [t["total_emprestimos"] for t in top] == [6, 5, 4, 3, 2]


def test_r6_emprestimos_por_curso(servicos, novo_livro, novo_aluno):
    isbn = novo_livro(exemplares=5)
    es1 = novo_aluno(curso="Engenharia de Software")
    es2 = novo_aluno(curso="Engenharia de Software")
    cc = novo_aluno(curso="Ciência da Computação")
    _ciclo(servicos, isbn, es1, 2)
    _ciclo(servicos, isbn, es2, 1)
    _ciclo(servicos, isbn, cc, 1)

    assert servicos.relatorios.emprestimos_por_curso() == [
        {"curso": "Engenharia de Software", "total_emprestimos": 3},
        {"curso": "Ciência da Computação", "total_emprestimos": 1},
    ]


def test_r6_alunos_com_emprestimo_atrasado(servicos, novo_livro, novo_aluno):
    atrasado = novo_aluno(nome="João Souza")
    em_dia = novo_aluno(nome="Maria Silva")
    isbn_a, isbn_b = novo_livro(titulo="Clean Code"), novo_livro(titulo="Dom Casmurro")
    servicos.emprestimos.emprestar(
        isbn_a, atrasado, data_emprestimo=tempo.agora() - timedelta(days=10))
    servicos.emprestimos.emprestar(isbn_b, em_dia)

    assert servicos.relatorios.alunos_atrasados() == [
        {"aluno": "João Souza", "livro": "Clean Code", "dias_atraso": 3}]


def test_r6_total_arrecadado_em_multas(servicos, novo_livro, novo_aluno):
    assert servicos.relatorios.total_multas() == 0          # sem empréstimos
    a1, a2 = novo_aluno(), novo_aluno()
    l1, l2 = novo_livro(), novo_livro()
    servicos.emprestimos.emprestar(l1, a1, data_emprestimo=tempo.agora() - timedelta(days=10))
    servicos.emprestimos.emprestar(l2, a2, data_emprestimo=tempo.agora() - timedelta(days=9))
    servicos.emprestimos.devolver(l1, a1)   # 3 dias -> R$ 6,00
    servicos.emprestimos.devolver(l2, a2)   # 2 dias -> R$ 4,00

    assert servicos.relatorios.total_multas() == 10.0
