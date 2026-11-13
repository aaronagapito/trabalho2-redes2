# Exercício 2 — Servidor Echo UDP

O servidor devolve (eco) cada datagrama recebido e imprime a mensagem com o endereço do remetente. O cliente envia mensagens até o usuário digitar `sair`.

## Dependências

Apenas Python 3.10+ (bibliotecas padrão). Nada para instalar.

## Como executar

Terminal 1 — servidor:

```bash
python3 servidor_udp.py --porta 6000
```

Terminal 2 — cliente:

```bash
python3 cliente_udp.py --host 127.0.0.1 --porta 6000 --timeout 3
```

| Parâmetro | Programa | Padrão | Descrição |
|---|---|---|---|
| `--host` | servidor | `0.0.0.0` | interface onde o servidor escuta |
| `--porta` | servidor | `6000` | porta UDP |
| `--host` | cliente | `127.0.0.1` | IP do servidor |
| `--porta` | cliente | `6000` | porta do servidor |
| `--timeout` | cliente | `3` | segundos esperando o eco antes de desistir |

## Exemplo

```
> eco teste
Eco: eco teste
> (mensagem com 70000 caracteres)
Mensagem muito grande: 70000 bytes. O máximo para UDP é 65507 bytes.
> sair
Encerrando...
```

Com o servidor desligado:
```
> oi
Sem resposta em 3.0s. O servidor pode estar desligado ou o pacote se perdeu.
```

Servidor:
```
[11/11/2026 11:55:28] 127.0.0.1:40244 (9 bytes) -> eco teste
```

## Requisitos atendidos

- **Tamanho máximo:** o cliente mede a mensagem em bytes (UTF-8) e recusa acima de **65.507 bytes** (65.535 do pacote IP − 20 do cabeçalho IP − 8 do cabeçalho UDP).
- **Timeout:** `socket.settimeout()` no cliente; `socket.timeout` é tratado e o programa continua.
- **Erros de comunicação:** `ConnectionRefusedError` e `OSError` tratados no cliente; no servidor, uma falha ao responder um cliente não derruba o serviço.
- Como o UDP não tem conexão, não há `connect`/`accept`: cada mensagem é independente (`sendto` / `recvfrom`).
