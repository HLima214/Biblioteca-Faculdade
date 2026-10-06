"""R7 - Menu de terminal (teste de fumaça)."""
from biblioteca import cli


def test_r7_menu_cadastra_e_busca_aluno(servicos, monkeypatch, capsys):
    respostas = iter(["2026777", "Maria Silva", "Engenharia de Software", "maria@x.com"])
    monkeypatch.setattr("builtins.input", lambda *_: next(respostas))
    cli.executar("6", servicos)

    monkeypatch.setattr("builtins.input", lambda *_: "2026777")
    cli.executar("7", servicos)

    saida = capsys.readouterr().out
    assert "Aluno cadastrado." in saida
    assert "Maria Silva" in saida


def test_r7_opcao_invalida(servicos, capsys):
    cli.executar("99", servicos)
    assert "Opção inválida" in capsys.readouterr().out
