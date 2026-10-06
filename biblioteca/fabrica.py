"""Monta as camadas (repositories -> services) a partir de um banco."""
from dataclasses import dataclass

from biblioteca.repositories import (AlunoRepository, EmprestimoRepository,
                                     LivroRepository, RelatorioRepository)
from biblioteca.services import (AlunoService, EmprestimoService, LivroService,
                                 RelatorioService)


@dataclass
class Servicos:
    livros: LivroService
    alunos: AlunoService
    emprestimos: EmprestimoService
    relatorios: RelatorioService


def criar_servicos(db):
    livros = LivroRepository(db)
    alunos = AlunoRepository(db)
    emprestimos = EmprestimoRepository(db)
    relatorios = RelatorioRepository(db)
    return Servicos(
        livros=LivroService(livros, emprestimos),
        alunos=AlunoService(alunos, emprestimos),
        emprestimos=EmprestimoService(livros, alunos, emprestimos),
        relatorios=RelatorioService(relatorios),
    )
