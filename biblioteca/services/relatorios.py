"""R6 - Relatórios."""


class RelatorioService:
    def __init__(self, relatorios):
        self.relatorios = relatorios

    def top_livros(self):
        return self.relatorios.top_livros(5)

    def emprestimos_por_curso(self):
        return self.relatorios.emprestimos_por_curso()

    def alunos_atrasados(self):
        return self.relatorios.alunos_atrasados()

    def total_multas(self):
        return self.relatorios.total_multas()
