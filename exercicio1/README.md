# Exercício 1 — Cliente-Servidor TCP

Servidor TCP multithread (uma thread por conexão) e cliente que envia várias mensagens até o usuário digitar `sair`.

## Dependências

Apenas Python 3.10+ (só bibliotecas padrão: `socket`, `threading`, `argparse`, `datetime`). Nada para instalar.

## Como executar

Terminal 1 — servidor:

```bash
python3 servidor_tcp.py --porta 5000
```

Terminais 2, 3, ... — um cliente em cada (podem rodar vários ao mesmo tempo):

```bash
python3 cliente_tcp.py --host 127.0.0.1 --porta 5000
```

| Parâmetro | Programa | Padrão | Descrição |
|---|---|---|---|
| `--host` | servidor | `0.0.0.0` | interface onde o servidor escuta |
| `--porta` | servidor | `5000` | porta TCP |
| `--host` | cliente | `127.0.0.1` | IP do servidor |
| `--porta` | cliente | `5000` | porta do servidor |

Para encerrar: digite `sair` no cliente; `Ctrl+C` no servidor.

## Exemplo

Cliente:
```
Conectado ao servidor 127.0.0.1:5000
> ola servidor
Servidor: Mensagem recebida
>
Mensagem vazia não é permitida. Digite algo.
> sair
Encerrando a conexão...
```

Servidor:
```
[11/11/2026 11:55:27] Servidor TCP ouvindo em 0.0.0.0:5000
[11/11/2026 11:55:27] Cliente conectado: 127.0.0.1:42186
[11/11/2026 11:55:27] 127.0.0.1:42186 -> ola servidor
[11/11/2026 11:55:27] Cliente desconectado: 127.0.0.1:42186
```

## Requisitos atendidos

- **Múltiplos clientes simultâneos:** cada `accept()` cria uma `threading.Thread` que executa `atender_cliente()`.
- **Log com data/hora e IP:porta** de cada mensagem recebida, e resposta `"Mensagem recebida"`.
- **Mensagens vazias:** bloqueadas no cliente e também verificadas no servidor (que responde `Erro: mensagem vazia`).
- **Encerramento seguro:** sockets usados com `with` (context manager), que fecha a conexão mesmo em caso de erro.
- **Servidor indisponível:** o cliente trata `ConnectionRefusedError` e mostra uma mensagem clara em vez de travar.
