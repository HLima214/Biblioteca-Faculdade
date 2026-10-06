"""R1 - Cadastro de livros (CRUD)."""
import pytest
from pymongo.errors import DuplicateKeyError

from biblioteca.errors import RegraNegocio


def test_r1_crud_completo(servicos, novo_livro):
    isbn = novo_livro(titulo="Dom Casmurro", autor="Machado de Assis",
                      categoria="Romance", exemplares=3)

    livro = servicos.livros.buscar(isbn)                       # buscar por ISBN
    assert livro["titulo"] == "Dom Casmurro"
    assert livro["exemplares_disponiveis"] == 3
    assert [l["isbn"] for l in servicos.livros.listar()] == [isbn]   # listar

    servicos.livros.atualizar(isbn, {"categoria": "Clássico", "exemplares_total": 5})
    atualizado = servicos.livros.buscar(isbn)                  # atualizar
    assert atualizado["categoria"] == "Clássico"
    assert atualizado["exemplares_total"] == 5
    assert atualizado["exemplares_disponiveis"] == 5

    servicos.livros.remover(isbn)                              # remover
    assert servicos.livros.buscar(isbn) is None


def test_r1_isbn_duplicado_e_recusado(servicos, novo_livro):
    isbn = novo_livro()
    with pytest.raises(RegraNegocio, match="ISBN"):
        servicos.livros.cadastrar(isbn, "Outro", "Outro", 2000, "Geral", 1)


def test_r1_indice_unico_existe_no_banco(db):
    livro = {"isbn": "123", "titulo": "A", "autor": "B", "ano": 2000, "categoria": "C",
             "exemplares_total": 1, "exemplares_disponiveis": 1}
    db.livros.insert_one(dict(livro))
    with pytest.raises(DuplicateKeyError):
        db.livros.insert_one(dict(livro))
    assert any(i.get("unique") for i in db.livros.index_information().values()
               if i["key"] == [("isbn", 1)])


def test_r1_livro_com_emprestimo_em_aberto_nao_pode_ser_removido(
        servicos, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(), novo_aluno()
    servicos.emprestimos.emprestar(isbn, matricula)

    with pytest.raises(RegraNegocio, match="em aberto"):
        servicos.livros.remover(isbn)

    servicos.emprestimos.devolver(isbn, matricula)   # depois de devolver, pode remover
    servicos.livros.remover(isbn)
    assert servicos.livros.buscar(isbn) is None


def test_r1_nao_reduz_total_abaixo_dos_exemplares_emprestados(
        servicos, novo_livro, novo_aluno):
    isbn, matricula = novo_livro(exemplares=2), novo_aluno()
    servicos.emprestimos.emprestar(isbn, matricula)
    servicos.emprestimos.emprestar(isbn, novo_aluno())
    with pytest.raises(RegraNegocio, match="emprestados"):
        servicos.livros.atualizar(isbn, {"exemplares_total": 1})
