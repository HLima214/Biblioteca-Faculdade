"""R4 - Emprestar livro."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest

from biblioteca import tempo
from biblioteca.errors import RegraNegocio


def test_r4_emprestar_baixa_estoque_e_define_prazo_de_7_dias(
        servicos, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(exemplares=2), novo_aluno()
    emprestimo = servicos.emprestimos.emprestar(isbn, matricula)

    assert servicos.livros.buscar(isbn)["exemplares_disponiveis"] == 1
    assert emprestimo["data_prevista"] - emprestimo["data_emprestimo"] == timedelta(days=7)
    assert emprestimo["data_devolucao"] is None


def test_r4_sem_exemplar_disponivel_nao_empresta(servicos, novo_livro, novo_aluno):
    isbn = novo_livro(exemplares=1)
    servicos.emprestimos.emprestar(isbn, novo_aluno())
    with pytest.raises(RegraNegocio, match="exemplares"):
        servicos.emprestimos.emprestar(isbn, novo_aluno())
    assert servicos.livros.buscar(isbn)["exemplares_disponiveis"] == 0


def test_r4_maximo_de_3_emprestimos_em_aberto(servicos, novo_livro, novo_aluno):
    matricula = novo_aluno()
    isbns = [novo_livro() for _ in range(4)]
    for isbn in isbns[:3]:
        servicos.emprestimos.emprestar(isbn, matricula)
    with pytest.raises(RegraNegocio, match="3 empréstimos"):
        servicos.emprestimos.emprestar(isbns[3], matricula)


def test_r4_aluno_com_emprestimo_atrasado_nao_pega_outro(servicos, novo_livro, novo_aluno):
    matricula = novo_aluno()
    atrasado, outro = novo_livro(), novo_livro()
    # emprestado há 10 dias: o prazo de 7 dias venceu há 3
    servicos.emprestimos.emprestar(
        atrasado, matricula, data_emprestimo=tempo.agora() - timedelta(days=10))
    with pytest.raises(RegraNegocio, match="atrasado"):
        servicos.emprestimos.emprestar(outro, matricula)


def test_r4_aluno_ou_livro_inexistente(servicos, novo_livro, novo_aluno):
    with pytest.raises(RegraNegocio, match="Aluno"):
        servicos.emprestimos.emprestar(novo_livro(), "nao-existe")
    with pytest.raises(RegraNegocio, match="Livro"):
        servicos.emprestimos.emprestar("nao-existe", novo_aluno())


def test_r4_emprestimos_simultaneos_nao_deixam_estoque_negativo(
        servicos, novo_livro, novo_aluno):
    isbn = novo_livro(exemplares=1)
    matriculas = [novo_aluno() for _ in range(8)]

    def tentar(matricula):
        try:
            servicos.emprestimos.emprestar(isbn, matricula)
            return True
        except RegraNegocio:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        resultados = list(pool.map(tentar, matriculas))

    assert resultados.count(True) == 1               # só um aluno leva o único exemplar
    assert servicos.livros.buscar(isbn)["exemplares_disponiveis"] == 0
