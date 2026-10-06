"""Listagens e remoção de alunos (funcionalidades extras do menu)."""
from datetime import timedelta

import pytest

from biblioteca import tempo
from biblioteca.errors import RegraNegocio


def test_listar_alunos_ordenados_por_nome(servicos, novo_aluno):
    novo_aluno(nome="Carlos")
    novo_aluno(nome="Ana")
    novo_aluno(nome="bruno")
    assert [a["nome"] for a in servicos.alunos.listar()] == ["Ana", "bruno", "Carlos"]


def test_remover_aluno_so_sem_emprestimo_em_aberto(servicos, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(), novo_aluno()
    servicos.emprestimos.emprestar(isbn, matricula)
    with pytest.raises(RegraNegocio, match="em aberto"):
        servicos.alunos.remover(matricula)

    servicos.emprestimos.devolver(isbn, matricula)
    servicos.alunos.remover(matricula)
    assert servicos.alunos.buscar(matricula) is None
    with pytest.raises(RegraNegocio, match="não encontrado"):
        servicos.alunos.remover(matricula)


def test_listar_emprestimos_em_aberto_e_devolucoes(servicos, novo_livro, novo_aluno):
    matricula = novo_aluno(nome="Maria")
    aberto, devolvido = novo_livro(titulo="Aberto"), novo_livro(titulo="Devolvido")
    servicos.emprestimos.emprestar(aberto, matricula)
    servicos.emprestimos.emprestar(
        devolvido, matricula, data_emprestimo=tempo.agora() - timedelta(days=1))
    servicos.emprestimos.devolver(devolvido, matricula)

    abertos = servicos.emprestimos.listar_abertos()
    assert [(e["livro"], e["aluno"]) for e in abertos] == [("Aberto", "Maria")]
    devolucoes = servicos.emprestimos.listar_devolucoes()
    assert [(e["livro"], e["aluno"], e["multa"]) for e in devolucoes] == [("Devolvido", "Maria", 0.0)]


def test_historico_de_devolucoes_sobrevive_a_remocao_do_aluno(servicos, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(), novo_aluno()
    servicos.emprestimos.emprestar(isbn, matricula)
    servicos.emprestimos.devolver(isbn, matricula)
    servicos.alunos.remover(matricula)
    assert servicos.emprestimos.listar_devolucoes()[0]["aluno"] == "(aluno removido)"
