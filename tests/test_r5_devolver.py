"""R5 - Devolver livro."""
from datetime import timedelta

import pytest

from biblioteca import tempo
from biblioteca.errors import RegraNegocio


def test_r5_devolucao_no_prazo_repoe_estoque_sem_multa(
        servicos, db, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(exemplares=1), novo_aluno()
    servicos.emprestimos.emprestar(isbn, matricula)

    resultado = servicos.emprestimos.devolver(isbn, matricula)

    assert resultado == {"dias_atraso": 0, "multa": 0.0}
    assert servicos.livros.buscar(isbn)["exemplares_disponiveis"] == 1
    assert db.emprestimos.find_one({"isbn": isbn})["data_devolucao"] is not None


def test_r5_devolucao_atrasada_cobra_2_reais_por_dia(
        servicos, db, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(), novo_aluno()
    servicos.emprestimos.emprestar(
        isbn, matricula, data_emprestimo=tempo.agora() - timedelta(days=10))  # 3 dias de atraso

    resultado = servicos.emprestimos.devolver(isbn, matricula)

    assert resultado["dias_atraso"] == 3
    assert resultado["multa"] == 6.0
    assert db.emprestimos.find_one({"isbn": isbn})["multa"] == 6.0


def test_r5_devolver_duas_vezes_gera_erro(servicos, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(exemplares=1), novo_aluno()
    servicos.emprestimos.emprestar(isbn, matricula)
    servicos.emprestimos.devolver(isbn, matricula)

    with pytest.raises(RegraNegocio, match="já foi devolvido"):
        servicos.emprestimos.devolver(isbn, matricula)
    assert servicos.livros.buscar(isbn)["exemplares_disponiveis"] == 1  # não repôs de novo


def test_r5_emprestimo_inexistente(servicos, novo_livro, novo_aluno):
    with pytest.raises(RegraNegocio, match="não encontrado"):
        servicos.emprestimos.devolver(novo_livro(), novo_aluno())
