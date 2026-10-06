"""R2 - Cadastro de alunos."""
import pytest
from pymongo.errors import WriteError

from biblioteca.errors import RegraNegocio


def test_r2_cadastrar_e_buscar_por_matricula(servicos, novo_aluno):
    matricula = novo_aluno(nome="Maria Silva", curso="Engenharia de Software")
    aluno = servicos.alunos.buscar(matricula)
    assert aluno["nome"] == "Maria Silva"
    assert aluno["curso"] == "Engenharia de Software"
    assert servicos.alunos.buscar("inexistente") is None


def test_r2_matricula_duplicada_e_recusada(servicos, novo_aluno):
    matricula = novo_aluno()
    with pytest.raises(RegraNegocio, match="matrícula"):
        servicos.alunos.cadastrar(matricula, "Outro", "Curso", "outro@x.com")


def test_r2_email_sem_arroba_e_recusado(servicos):
    with pytest.raises(RegraNegocio, match="@"):
        servicos.alunos.cadastrar("2026999", "Fulano", "Curso", "semarroba")
    assert servicos.alunos.buscar("2026999") is None


def test_r2_validacao_de_email_tambem_existe_no_banco(db):
    with pytest.raises(WriteError):  # regra da collection (Validation) barra e-mail sem @
        db.alunos.insert_one({"matricula": "1", "nome": "A", "curso": "B", "email": "semarroba"})


def test_r2_indice_unico_da_matricula_existe_no_banco(db):
    assert any(i.get("unique") for i in db.alunos.index_information().values()
               if i["key"] == [("matricula", 1)])
