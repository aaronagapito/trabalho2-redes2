# Exercício 10 — Chat em Rede com WebSockets

Servidor de chat em Python com a biblioteca `websockets` e dois clientes: um em Python (terminal) e um em HTML/JavaScript (navegador, WebSocket API nativa). Os dois podem conversar na mesma sala.

## Dependências

- Python 3.10+
- Biblioteca `websockets` **versão 13 ou mais nova** (o código usa a API `websockets.asyncio`):

```bash
pip install -r ../requirements.txt
# ou
pip install "websockets>=13"
```

## Como executar

Terminal 1 — servidor:

```bash
python3 servidor_ws.py --porta 8765
```

Cliente em Python (um terminal por usuário):

```bash
python3 cliente_ws.py --host 127.0.0.1 --porta 8765 --nome Ana
```

Cliente no navegador: abra o arquivo `cliente.html` (duplo clique ou `xdg-open cliente.html`), confira o endereço `ws://localhost:8765`, digite o nome e clique em **Conectar**. Abra em várias abas para simular vários usuários.

| Parâmetro | Programa | Padrão | Descrição |
|---|---|---|---|
| `--host` | servidor | `0.0.0.0` | interface onde o servidor escuta |
| `--porta` | servidor | `8765` | porta do servidor |
| `--host` | cliente | `127.0.0.1` | IP do servidor |
| `--porta` | cliente | `8765` | porta do servidor |
| `--nome` | cliente | (pergunta) | nome de usuário |

Para sair: `sair` no cliente Python, botão **Sair** (ou fechar a aba) no HTML, `Ctrl+C` no servidor.

## Protocolo (JSON)

| Direção | Mensagem |
|---|---|
| cliente → servidor | `{"tipo": "entrar", "nome": "Ana"}` (primeira mensagem) |
| cliente → servidor | `{"tipo": "mensagem", "texto": "Olá!"}` |
| servidor → clientes | `{"tipo": "mensagem", "nome": "Ana", "texto": "Olá!", "hora": "14:03:10"}` |
| servidor → clientes | `{"tipo": "sistema", "texto": "Ana entrou na sala."}` |
| servidor → cliente | `{"tipo": "erro", "texto": "O nome 'ana' já está em uso."}` |

## Exemplo

Servidor:
```
[11/11/2026 11:57:01] Servidor WebSocket ouvindo em ws://0.0.0.0:8765
[11/11/2026 11:57:02] Ana entrou (127.0.0.1:44158). Online: 1
[11/11/2026 11:57:03] Bia entrou (127.0.0.1:44168). Online: 2
[11/11/2026 11:57:04] Ana: oi Bia, tudo bem?
[11/11/2026 11:57:05] Bia saiu. Online: 1
```

Cliente da Bia:
```
*** Bem-vindo(a), Bia! Online: Ana, Bia
[11:57:04] Ana: oi Bia, tudo bem?
```

## Requisitos atendidos

- **Biblioteca `websockets`**, porta configurável (padrão 8765).
- **Múltiplas conexões simultâneas:** cada conexão é uma corrotina `asyncio` (`atender`); o laço de eventos atende todas ao mesmo tempo.
- **Broadcast** para todos os demais com `websockets.asyncio.server.broadcast`.
- **Identificação por nome de usuário** em todas as mensagens; nomes vazios ou repetidos são recusados.
- **Desconexões inesperadas** (aba fechada, rede caiu) geram `ConnectionClosed`, tratada no `try/finally`: o cliente é removido, os outros são avisados e o servidor continua no ar. JSON inválido recebe uma mensagem de erro e não derruba nada.
