# Exercício 3 — Chat em Rede TCP

Servidor central que aceita vários clientes (uma thread por cliente) e retransmite cada mensagem para todos os outros, com o nome do remetente. Avisa a sala quando alguém entra ou sai.

## Dependências

Apenas Python 3.10+ (bibliotecas padrão). Nada para instalar.

## Como executar

Terminal 1 — servidor:

```bash
python3 servidor_chat.py --porta 5001
```

Terminais 2, 3, 4, ... — um cliente por usuário:

```bash
python3 cliente_chat.py --host 127.0.0.1 --porta 5001
```

O cliente pede o nickname ao iniciar (ou passe `--nick Ana`).

| Parâmetro | Programa | Padrão | Descrição |
|---|---|---|---|
| `--host` | servidor | `0.0.0.0` | interface onde o servidor escuta |
| `--porta` | servidor | `5001` | porta TCP (5001 para não conflitar com o exercício 1) |
| `--host` | cliente | `127.0.0.1` | IP do servidor |
| `--porta` | cliente | `5001` | porta do servidor |
| `--nick` | cliente | (pergunta) | nome de usuário |

Para sair da sala: digite `sair`. O servidor e os outros clientes continuam funcionando.

## Exemplo

Tela da Ana:
```
Digite seu nickname: Ana
Você entrou no chat. Digite "sair" para sair.
[Servidor] Bem-vindo(a), Ana! Há 1 usuário(s) na sala.
[Servidor] Bia entrou na sala.
> oi pessoal
[Bia] ola Ana
[Servidor] Bia saiu da sala.
```

Servidor:
```
[11/11/2026 11:55:39] Ana entrou (127.0.0.1:43024). Usuários online: 1
[11/11/2026 11:55:39] Bia entrou (127.0.0.1:43032). Usuários online: 2
[11/11/2026 11:55:40] Ana: oi pessoal
[11/11/2026 11:55:40] Bia saiu. Usuários online: 1
```

## Protocolo

Texto UTF-8, uma mensagem por linha (terminada em `\n`), para que mensagens seguidas não se misturem no fluxo TCP:

1. a primeira linha enviada pelo cliente é o nickname;
2. as demais são mensagens do chat;
3. a linha `sair` (ou fechar o socket) remove o cliente da sala.

## Requisitos atendidos

- **Vários clientes (sem limite de dois):** dicionário `clientes` `{socket: nick}` compartilhado, protegido por `threading.Lock`.
- **Broadcast com o nome do remetente** para todos os demais conectados.
- **Avisos de entrada e saída** (inclusive quando o cliente cai sem digitar `sair`).
- **Envio e recebimento em paralelo no cliente:** a thread principal lê o teclado e uma thread separada (`receber_mensagens`) fica lendo o socket continuamente.
- **Comando `sair`** encerra só aquele cliente.
- **Validação:** nickname vazio ou repetido é recusado; mensagens vazias não são enviadas; clientes que falham no envio são removidos sem derrubar o servidor.
