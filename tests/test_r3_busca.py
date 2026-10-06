"""R3 - Busca de livros."""


def _popular(novo_livro):
    novo_livro(titulo="banana split", autor="Maria Machado", categoria="Culinária")
    novo_livro(titulo="Ágil na Prática", autor="Fulano de Tal", categoria="Tecnologia")
    novo_livro(titulo="Casa Grande", autor="Gilberto Freyre", categoria="Sociologia")
    novo_livro(titulo="Dado e Bola", autor="Beltrano", categoria="tecnologia")


def titulos(lista):
    return [l["titulo"] for l in lista]


def test_r3_busca_por_parte_do_titulo_sem_diferenciar_maiusculas(servicos, novo_livro):
    _popular(novo_livro)
    assert titulos(servicos.livros.pesquisar("GRANDE")) == ["Casa Grande"]
    assert titulos(servicos.livros.pesquisar("split")) == ["banana split"]


def test_r3_busca_por_parte_do_autor_sem_diferenciar_maiusculas(servicos, novo_livro):
    _popular(novo_livro)
    assert titulos(servicos.livros.pesquisar("MACHADO")) == ["banana split"]


def test_r3_filtro_por_categoria_sem_diferenciar_maiusculas(servicos, novo_livro):
    _popular(novo_livro)
    resultado = titulos(servicos.livros.pesquisar(categoria="TECNOLOGIA"))
    assert resultado == ["Ágil na Prática", "Dado e Bola"]


def test_r3_combina_termo_e_categoria(servicos, novo_livro):
    _popular(novo_livro)
    assert titulos(servicos.livros.pesquisar("dado", "tecnologia")) == ["Dado e Bola"]
    assert servicos.livros.pesquisar("dado", "culinária") == []


def test_r3_resultados_ordenados_por_titulo(servicos, novo_livro):
    _popular(novo_livro)
    # ordem alfabética real (ignora caixa e acento), não a ordem binária
    assert titulos(servicos.livros.pesquisar()) == [
        "Ágil na Prática", "banana split", "Casa Grande", "Dado e Bola"]
