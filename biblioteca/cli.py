"""R7 - Interface de terminal. Só conversa com os services."""
from pymongo.errors import PyMongoError

from biblioteca import exemplos, tempo
from biblioteca.errors import RegraNegocio

MENU = """
============== BIBLIOTECA DA FACULDADE ==============
 LIVROS
   1  Cadastrar livro
   2  Buscar livro por ISBN
   3  Listar livros
   4  Atualizar livro
   5  Remover livro
 ALUNOS
   6  Cadastrar aluno
   7  Buscar aluno por matrícula
   8  Listar alunos
   9  Remover aluno
 BUSCA
  10  Buscar livros (título/autor e categoria)
 EMPRÉSTIMOS
  11  Emprestar livro
  12  Devolver livro
  13  Listar empréstimos em aberto
  14  Listar devoluções
 RELATÓRIOS
  15  Top 5 livros mais emprestados
  16  Empréstimos por curso
  17  Alunos com empréstimo atrasado
  18  Total arrecadado em multas
 OUTROS
  19  Carregar dados de exemplo
   0  Sair
====================================================="""


def ler_int(msg):
    while True:
        try:
            return int(input(msg).strip())
        except ValueError:
            print("Digite um número inteiro.")


def mostrar_livros(lista):
    if not lista:
        print("Nenhum livro encontrado.")
        return
    for l in lista:
        print(f"- {l['titulo']} | {l['autor']} | {l['ano']} | {l['categoria']} | "
              f"ISBN {l['isbn']} | disponíveis: {l['exemplares_disponiveis']}/{l['exemplares_total']}")


def mostrar_alunos(lista):
    if not lista:
        print("Nenhum aluno cadastrado.")
        return
    for a in lista:
        print(f"- {a['nome']} | matrícula {a['matricula']} | {a['curso']} | {a['email']}")
    print(f"Total: {len(lista)} aluno(s).")


def mostrar_emprestimos_abertos(lista):
    if not lista:
        print("Nenhum empréstimo em aberto.")
        return
    for e in lista:
        atrasado = tempo.como_utc(e["data_prevista"]) < tempo.agora()
        status = "ATRASADO" if atrasado else "no prazo"
        print(f"- {e['livro']} | {e['aluno']} (mat. {e['matricula']}) | "
              f"emprestado em {e['data_emprestimo']:%d/%m/%Y} | "
              f"devolver até {e['data_prevista']:%d/%m/%Y} | {status}")
    print(f"Total: {len(lista)} empréstimo(s) em aberto.")


def mostrar_devolucoes(lista):
    if not lista:
        print("Nenhuma devolução registrada.")
        return
    for e in lista:
        print(f"- {e['livro']} | {e['aluno']} (mat. {e['matricula']}) | "
              f"devolvido em {e['data_devolucao']:%d/%m/%Y} | multa: R$ {e['multa']:.2f}")
    print(f"Total: {len(lista)} devolução(ões).")


def executar(opcao, s):
    """Executa uma opção do menu. `s` é o conjunto de services (fabrica.Servicos)."""
    if opcao == "1":
        s.livros.cadastrar(input("ISBN: ").strip(), input("Título: ").strip(),
                           input("Autor: ").strip(), ler_int("Ano: "),
                           input("Categoria: ").strip(), ler_int("Exemplares: "))
        print("Livro cadastrado.")
    elif opcao == "2":
        livro = s.livros.buscar(input("ISBN: ").strip())
        mostrar_livros([livro] if livro else [])
    elif opcao == "3":
        mostrar_livros(s.livros.listar())
    elif opcao == "4":
        isbn = input("ISBN do livro: ").strip()
        print("Deixe em branco o que não quiser alterar.")
        campos = {}
        for nome in ("titulo", "autor", "categoria"):
            valor = input(f"Novo {nome}: ").strip()
            if valor:
                campos[nome] = valor
        ano = input("Novo ano: ").strip()
        if ano:
            campos["ano"] = int(ano)
        total = input("Novo total de exemplares: ").strip()
        if total:
            campos["exemplares_total"] = int(total)
        s.livros.atualizar(isbn, campos)
        print("Livro atualizado.")
    elif opcao == "5":
        s.livros.remover(input("ISBN: ").strip())
        print("Livro removido.")
    elif opcao == "6":
        s.alunos.cadastrar(input("Matrícula: ").strip(), input("Nome: ").strip(),
                           input("Curso: ").strip(), input("E-mail: ").strip())
        print("Aluno cadastrado.")
    elif opcao == "7":
        aluno = s.alunos.buscar(input("Matrícula: ").strip())
        print(aluno if aluno else "Aluno não encontrado.")
    elif opcao == "8":
        mostrar_alunos(s.alunos.listar())
    elif opcao == "9":
        s.alunos.remover(input("Matrícula: ").strip())
        print("Aluno removido.")
    elif opcao == "10":
        termo = input("Parte do título ou autor (enter para ignorar): ").strip()
        categoria = input("Categoria (enter para ignorar): ").strip()
        mostrar_livros(s.livros.pesquisar(termo, categoria))
    elif opcao == "11":
        e = s.emprestimos.emprestar(input("ISBN: ").strip(), input("Matrícula: ").strip())
        print(f"Empréstimo realizado. Devolver até {e['data_prevista']:%d/%m/%Y}.")
    elif opcao == "12":
        r = s.emprestimos.devolver(input("ISBN: ").strip(), input("Matrícula: ").strip())
        print(f"Devolução registrada. Dias de atraso: {r['dias_atraso']} | "
              f"Multa: R$ {r['multa']:.2f}")
    elif opcao == "13":
        mostrar_emprestimos_abertos(s.emprestimos.listar_abertos())
    elif opcao == "14":
        mostrar_devolucoes(s.emprestimos.listar_devolucoes())
    elif opcao == "15":
        for i, r in enumerate(s.relatorios.top_livros(), 1):
            print(f"{i}. {r['titulo']} ({r['isbn']}) - {r['total_emprestimos']} empréstimos")
    elif opcao == "16":
        for r in s.relatorios.emprestimos_por_curso():
            print(f"- {r['curso']}: {r['total_emprestimos']} empréstimos")
    elif opcao == "17":
        lista = s.relatorios.alunos_atrasados()
        if not lista:
            print("Nenhum empréstimo atrasado.")
        for r in lista:
            print(f"- {r['aluno']} | {r['livro']} | {r['dias_atraso']} dia(s) de atraso")
    elif opcao == "18":
        print(f"Total arrecadado em multas: R$ {s.relatorios.total_multas():.2f}")
    elif opcao == "19":
        exemplos.carregar(s)
        print("Dados de exemplo carregados.")
    else:
        print("Opção inválida.")


def executar_menu(s):
    while True:
        print(MENU)
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            print("Até logo!")
            break
        try:
            executar(opcao, s)
        except RegraNegocio as e:
            print(f"Erro: {e}")
        except ValueError:
            print("Erro: valor numérico inválido.")
        except PyMongoError as e:
            print(f"Erro no banco de dados: {str(e)[:200]}")