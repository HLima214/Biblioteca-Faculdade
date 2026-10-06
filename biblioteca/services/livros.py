"""R1 (CRUD de livros) e R3 (busca)."""
from pymongo.errors import DuplicateKeyError

from biblioteca.errors import RegraNegocio

CAMPOS_EDITAVEIS = {"titulo", "autor", "ano", "categoria", "exemplares_total"}


class LivroService:
    def __init__(self, livros, emprestimos):
        self.livros = livros
        self.emprestimos = emprestimos

    def cadastrar(self, isbn, titulo, autor, ano, categoria, exemplares):
        if not isbn or not titulo or not autor or not categoria:
            raise RegraNegocio("ISBN, título, autor e categoria são obrigatórios.")
        if exemplares < 1:
            raise RegraNegocio("A quantidade de exemplares deve ser pelo menos 1.")
        livro = {
            "isbn": isbn, "titulo": titulo, "autor": autor, "ano": ano,
            "categoria": categoria,
            "exemplares_total": exemplares,
            "exemplares_disponiveis": exemplares,
        }
        try:
            self.livros.inserir(livro)  # o índice único em isbn barra duplicados
        except DuplicateKeyError:
            raise RegraNegocio("Já existe um livro com esse ISBN.")

    def buscar(self, isbn):
        return self.livros.obter(isbn)

    def listar(self):
        return self.livros.listar()

    def atualizar(self, isbn, campos):
        livro = self.livros.obter(isbn)
        if not livro:
            raise RegraNegocio("Livro não encontrado.")
        if not campos:
            raise RegraNegocio("Nenhum campo informado para atualizar.")
        invalidos = set(campos) - CAMPOS_EDITAVEIS
        if invalidos:
            raise RegraNegocio(f"Campos não editáveis: {', '.join(sorted(invalidos))}.")

        delta = None
        if "exemplares_total" in campos:
            delta = campos["exemplares_total"] - livro["exemplares_total"]
            if campos["exemplares_total"] < 0 or livro["exemplares_disponiveis"] + delta < 0:
                raise RegraNegocio("Há mais exemplares emprestados do que o novo total.")
        if not self.livros.atualizar(isbn, campos, delta):
            raise RegraNegocio("Não foi possível atualizar (o estoque mudou, tente de novo).")

    def remover(self, isbn):
        if self.emprestimos.contar_abertos_do_livro(isbn) > 0:
            raise RegraNegocio("Livro com empréstimo em aberto não pode ser removido.")
        if not self.livros.remover(isbn):
            raise RegraNegocio("Livro não encontrado.")

    def pesquisar(self, termo="", categoria=""):
        """R3: parte do título/autor (sem diferenciar maiúsculas) + categoria, ordenado por título."""
        return self.livros.pesquisar(termo.strip(), categoria.strip())
