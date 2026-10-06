# Sistema de Empréstimo de Livros — MongoDB

**Grupo:** SFI – Search For Innovation

| Integrante | RM |
|---|---|
| Anny Carolina | RM98295 |
| Eric Carvalho | RM550249 |
| Henrique Lima | RM551528 |
| Pedro Menezes | RM97432 |
| Renato Izumi | RM99242 |
| Bernardo Rocha | RM99209 |

Backend do novo sistema da biblioteca da faculdade, substituindo a planilha que permitia
emprestar livros sem exemplar na estante. Livros, alunos e empréstimos ficam no **MongoDB**
(local via Docker ou **MongoDB Atlas**) e o uso é feito por um **menu no terminal**.

---

## Arquitetura em camadas

```
sfi-biblioteca/
├── biblioteca/
│   ├── cli.py                 # Interface: menu de terminal (R7)
│   ├── services/              # Regras de negócio (R1–R6)
│   │   ├── livros.py          #   R1 CRUD de livros, R3 busca
│   │   ├── alunos.py          #   R2 alunos
│   │   ├── emprestimos.py     #   R4 emprestar, R5 devolver
│   │   └── relatorios.py      #   R6 relatórios
│   ├── repositories/          # Acesso a dados: só aqui se fala com o MongoDB
│   │   ├── livros.py, alunos.py, emprestimos.py
│   │   └── relatorios.py      #   pipelines de agregação
│   ├── database.py            # Conexão, validações e índices (idempotente)
│   ├── fabrica.py             # Monta repositories -> services
│   ├── config.py              # Variáveis de ambiente e constantes (7 dias, R$ 2,00, 3)
│   ├── errors.py, tempo.py, exemplos.py
├── tests/                     # pytest (MongoDB real via Docker)
├── main.py                    # Ponto de entrada
├── docker-compose.yml         # MongoDB local
├── requirements.txt
└── .env.example
```

**Regra de dependência:** `cli → services → repositories → MongoDB`. O menu nunca acessa o
banco, e as regras de negócio não sabem nada de terminal, o que as torna testáveis.

## Requisitos × implementação × testes

| Req. | O que faz | Código | Testes |
|---|---|---|---|
| R1 | CRUD de livros; ISBN único; não remove livro com empréstimo em aberto | `services/livros.py`, `repositories/livros.py` | `tests/test_r1_livros.py` |
| R2 | Cadastro/busca de alunos; matrícula única; e-mail com `@` | `services/alunos.py` | `tests/test_r2_alunos.py` |
| R3 | Busca por título/autor sem diferenciar maiúsculas + categoria, ordenada por título | `repositories/livros.py` (`pesquisar`) | `tests/test_r3_busca.py` |
| R4 | Emprestar: estoque, máx. 3 em aberto, bloqueio por atraso, prazo de 7 dias, baixa atômica | `services/emprestimos.py` | `tests/test_r4_emprestar.py` |
| R5 | Devolver: reposição de estoque, multa R$ 2,00/dia, erro na devolução duplicada | `services/emprestimos.py` | `tests/test_r5_devolver.py` |
| R6 | 4 relatórios com Aggregation Pipeline | `repositories/relatorios.py` | `tests/test_r6_relatorios.py` |
| R7 | Menu de terminal com todas as funções | `cli.py` | `tests/test_r7_menu.py` |
| Extras | Listar alunos, remover aluno, listar empréstimos em aberto e devoluções | `services/alunos.py`, `services/emprestimos.py` | `tests/test_extras.py` |

---

## Como rodar

### Pré-requisitos
- Python 3.10+
- Docker (para o MongoDB local e para os testes) **ou** uma conta no MongoDB Atlas (para rodar o menu)

### 1. Instalar as dependências
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate        Linux/Mac:  source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Escolher o banco

**Opção A — MongoDB local com Docker (padrão)**
```bash
docker compose up -d --wait
```
Nada mais a configurar: a aplicação usa `mongodb://localhost:27017` por padrão.
Para parar: `docker compose down` (os dados ficam no volume; `down -v` apaga tudo).

**Opção B — MongoDB Atlas**
1. No Atlas, em **Network Access**, libere o seu IP.
2. Copie a string de conexão do cluster (*Connect → Drivers*).
3. Copie `.env.example` para `.env` e preencha (o `.env` está no `.gitignore`):
   ```
   MONGO_URI=mongodb+srv://USUARIO:SENHA@dbcluster.gd1gop6.mongodb.net/?appName=DBCluster
   DB_NAME=Biblioteca_Faculdade
   ```
   Ou, sem arquivo: `export MONGO_URI="..."` (Linux/Mac) / `set MONGO_URI=...` (Windows).

> Nunca coloque usuário e senha no código nem suba o `.env` para o repositório.

### 3. Rodar o menu
```bash
python main.py
```
Ao iniciar, a aplicação garante os índices únicos e as validações das collections.
A opção **15** do menu carrega dados de exemplo (inclui um empréstimo já atrasado, bom para
testar R4, R5 e R6).

### 4. Rodar os testes
Os testes usam um **MongoDB real**, o do `docker-compose.yml`:
```bash
docker compose up -d --wait
pytest
```
- Rodam num banco separado (`biblioteca_teste`), apagado a cada teste. Não tocam no banco da
  aplicação.
- Recusam rodar contra o Atlas (`mongodb+srv`).
- Se o Mongo não estiver no ar, o pytest para com uma mensagem explicando como subir.
- Para apontar para outro Mongo local: `MONGO_URI_TESTE=mongodb://host:porta`.

---

## Modelo de dados

Um banco (`Biblioteca_Faculdade`) com três collections:

| Collection | Campos | Índices |
|---|---|---|
| `livros` | isbn, titulo, autor, ano, categoria, exemplares_total, exemplares_disponiveis | **único** em `isbn` |
| `alunos` | matricula, nome, curso, email | **único** em `matricula` |
| `emprestimos` | isbn, matricula, data_emprestimo, data_prevista, data_devolucao (`null` enquanto aberto), multa | comuns em `(isbn, data_devolucao)` e `(matricula, data_devolucao)` |

`isbn` e `matricula` são **texto** (string), assim como nos empréstimos.

---

## Principais decisões da equipe

1. **Um banco, três collections.** Facilita consultas que cruzam dados (`$lookup`) e reflete um
   único sistema.
2. **Índices únicos só onde faz sentido.** `isbn` (livros) e `matricula` (alunos) são únicos.
   Em `emprestimos` os índices são comuns, porque o mesmo aluno faz vários empréstimos e o
   mesmo livro é emprestado várias vezes; um índice único ali bloquearia o segundo empréstimo.
3. **Estoque protegido contra concorrência (R4).** A baixa usa
   `update_one({isbn, exemplares_disponiveis: {$gt: 0}}, {$inc: {exemplares_disponiveis: -1}})`:
   checagem e decremento acontecem numa operação atômica, então dois empréstimos simultâneos
   do último exemplar nunca deixam o estoque negativo (há teste com 8 threads).
4. **Devolução idempotente (R5).** O registro só atualiza empréstimos com `data_devolucao: null`;
   devolver duas vezes gera erro e não repõe o estoque duas vezes.
5. **Contagem de dias de atraso.** Usamos diferença em **dias de calendário (UTC)**, a mesma
   contagem do `$dateDiff` do relatório de atrasados, para que a multa e o relatório sempre
   concordem. Multa = dias × R$ 2,00.
6. **Remoção protegida.** Livro com empréstimo em aberto não pode ser removido (R1). Aplicamos a
   mesma regra a alunos, para não deixar empréstimos órfãos. O histórico de devoluções continua
   legível mesmo se o aluno/livro for removido depois (aparece `(aluno removido)`).
7. **Validação em duas camadas.** O serviço valida (e-mail com `@`, exemplares ≥ 1) e a própria
   collection também (`$jsonSchema`), então dados inválidos são barrados mesmo fora da aplicação.
8. **Arquitetura em camadas com injeção de dependência.** Os services recebem os repositories,
   e os repositories recebem o banco; assim os testes apontam para um banco de teste sem mudar código.
9. **Segurança de credenciais.** A conexão vem de variável de ambiente/`.env`; nenhum segredo no
   código. Os testes recusam rodar no Atlas.
10. **Datas em UTC** (`tz_aware`), evitando erros de fuso na comparação de prazos.
11. **Empréstimo retroativo opcional** (`data_emprestimo`) no serviço, usado apenas pelos dados de
    exemplo e pelos testes de atraso, sem mexer diretamente no banco.

### Sobre o banco criado no Atlas/Compass
O banco e as collections foram criados manualmente pelo MongoDB Compass no Atlas, e isso não
atrapalha: a aplicação usa os mesmos nomes (`livros`, `alunos`, `emprestimos`) e o
`preparar_banco` é **idempotente**. Ele cria o que faltar, mantém índices únicos já existentes
e recria como único um índice comum de `isbn`/`matricula`, se houver. Pontos de atenção:
`isbn` e `matricula` devem ser cadastrados como texto, e datas inseridas pelo Compass devem usar
o tipo *Date*.

---

## Solução de problemas
- **`TLSV1_ALERT_INTERNAL_ERROR` / não conecta no Atlas:** quase sempre é o IP não liberado em
  *Network Access* ou o cluster pausado (botão *Resume*). Teste também sem VPN/proxy.
- **Testes dizem "MongoDB indisponível":** rode `docker compose up -d --wait` e confira com
  `docker compose ps`.
- **`$dateDiff` não reconhecido:** o MongoDB precisa ser 5.0 ou superior (o compose usa a 7).
