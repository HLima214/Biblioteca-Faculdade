"""R4 (emprestar) e R5 (devolver)."""
from datetime import timedelta

from biblioteca import config, tempo
from biblioteca.errors import RegraNegocio


class EmprestimoService:
    def __init__(self, livros, alunos, emprestimos):
        self.livros = livros
        self.alunos = alunos
        self.emprestimos = emprestimos

    def emprestar(self, isbn, matricula, data_emprestimo=None):
        """Empresta um livro. `data_emprestimo` (opcional) permite registrar um empréstimo
        retroativo, usado nos dados de exemplo e nos testes de atraso."""
        if not self.alunos.obter(matricula):
            raise RegraNegocio("Aluno não encontrado.")
        if not self.livros.obter(isbn):
            raise RegraNegocio("Livro não encontrado.")

        if self.emprestimos.contar_abertos_do_aluno(matricula) >= config.LIMITE_EMPRESTIMOS:
            raise RegraNegocio(
                f"O aluno já tem {config.LIMITE_EMPRESTIMOS} empréstimos em aberto.")
        if self.emprestimos.existe_atrasado(matricula, tempo.agora()):
            raise RegraNegocio("O aluno tem empréstimo atrasado e não pode pegar outro livro.")

        # update_one com filtro exemplares_disponiveis > 0 e $inc: operação atômica,
        # então dois empréstimos simultâneos nunca deixam o estoque negativo.
        if not self.livros.baixar_estoque(isbn):
            raise RegraNegocio("Não há exemplares disponíveis desse livro.")

        inicio = data_emprestimo or tempo.agora()
        emprestimo = {
            "isbn": isbn,
            "matricula": matricula,
            "data_emprestimo": inicio,
            "data_prevista": inicio + timedelta(days=config.PRAZO_DIAS),
            "data_devolucao": None,
            "multa": 0,
        }
        try:
            self.emprestimos.inserir(emprestimo)
        except Exception:
            self.livros.repor_estoque(isbn)  # desfaz a baixa se o registro falhar
            raise
        return emprestimo

    def devolver(self, isbn, matricula):
        aberto = self.emprestimos.obter_aberto(isbn, matricula)
        if not aberto:
            if self.emprestimos.existe_historico(isbn, matricula):
                raise RegraNegocio("Esse empréstimo já foi devolvido.")
            raise RegraNegocio("Empréstimo não encontrado.")

        agora = tempo.agora()
        # dias de calendário (UTC), a mesma contagem do relatório de atrasados ($dateDiff)
        prevista = tempo.como_utc(aberto["data_prevista"])
        dias_atraso = max((agora.date() - prevista.date()).days, 0)
        multa = round(dias_atraso * config.MULTA_POR_DIA, 2)

        if not self.emprestimos.registrar_devolucao(aberto["_id"], agora, multa):
            raise RegraNegocio("Esse empréstimo já foi devolvido.")
        self.livros.repor_estoque(isbn)
        return {"dias_atraso": dias_atraso, "multa": multa}

    def listar_abertos(self):
        return self.emprestimos.listar_abertos()

    def listar_devolucoes(self):
        return self.emprestimos.listar_devolucoes()
