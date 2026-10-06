"""Camada de acesso a dados (só aqui se fala com o MongoDB)."""
from biblioteca.repositories.alunos import AlunoRepository
from biblioteca.repositories.emprestimos import EmprestimoRepository
from biblioteca.repositories.livros import LivroRepository
from biblioteca.repositories.relatorios import RelatorioRepository

__all__ = ["AlunoRepository", "EmprestimoRepository", "LivroRepository", "RelatorioRepository"]
