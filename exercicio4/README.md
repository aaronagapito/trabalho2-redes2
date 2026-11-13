# Exercício 4 — Servidor de Hora com Threads (TCP)

Servidor multithread que responde a hora atual no formato `HH:MM:SS`. Mantém um contador de clientes atendidos protegido por `threading.Lock`, que aparece em todas as linhas de log.

## Dependências

Apenas Python 3.10+ (bibliotecas padrão: `socket`, `threading`, `logging`, `argparse`). Nada para instalar.

## Como executar

Terminal 1 — servidor:

```bash
python3 servidor_hora.py --porta 7000
```

Terminal 2 — cliente (um pedido):

```bash
python3 cliente_hora.py --host 127.0.0.1 --porta 7000
```

Teste de concorrência (10 clientes ao mesmo tempo):

```bash
# servidor demorando 1 s para responder cada pedido
python3 servidor_hora.py --porta 7000 --atraso 1
# em outro terminal
python3 cliente_hora.py --clientes 10
```

Os 10 clientes recebem resposta em ~1 segundo no total (e não 10 s), o que mostra que as threads atendem em paralelo.

| Parâmetro | Programa | Padrão | Descrição |
|---|---|---|---|
| `--host` | servidor | `0.0.0.0` | interface onde o servidor escuta |
| `--porta` | servidor | `7000` | porta TCP |
| `--log` | servidor | `servidor_hora.log` | arquivo onde o log também é gravado |
| `--atraso` | servidor | `0` | segundos de espera antes de responder (só para testes) |
| `--host` | cliente | `127.0.0.1` | IP do servidor |
| `--porta` | cliente | `7000` | porta do servidor |
| `--clientes` | cliente | `1` | quantos pedidos simultâneos (uma thread cada) |

## Protocolo

O cliente envia `HORA`; o servidor responde `HH:MM:SS`. Qualquer outro comando recebe `ERRO: comando desconhecido (use HORA)`.

## Exemplo de log (console e `servidor_hora.log`)

```
11/11/2026 11:55:48 [MainThread] Servidor de hora ouvindo em 0.0.0.0:7000 | atendidos=0
11/11/2026 11:55:48 [Thread-1 (atender_cliente)] Solicitação recebida | cliente=127.0.0.1:52390 | pedido='HORA' | atendidos=0
11/11/2026 11:55:48 [Thread-2 (atender_cliente)] Solicitação recebida | cliente=127.0.0.1:52392 | pedido='HORA' | atendidos=0
11/11/2026 11:55:49 [Thread-1 (atender_cliente)] Solicitação atendida | cliente=127.0.0.1:52390 | hora=11:55:49 | atendidos=1
11/11/2026 11:55:49 [Thread-2 (atender_cliente)] Solicitação atendida | cliente=127.0.0.1:52392 | hora=11:55:49 | atendidos=2
11/11/2026 11:55:49 [Thread-6 (atender_cliente)] Pedido inválido | cliente=127.0.0.1:52436 | atendidos=5
```

## Requisitos atendidos

- **Threads:** uma `threading.Thread` por conexão.
- **Contador thread-safe:** `total_atendidos` só é lido/alterado dentro de `with trava_contador:` (`threading.Lock`), evitando condição de corrida quando várias threads terminam juntas.
- **Logs:** cada solicitação recebida e atendida é registrada com data/hora, cliente (IP:porta) e contador, no console e em arquivo.
- **Tolerância a falhas:** erros de um cliente (desconexão no meio, timeout de 10 s, comando inválido) ficam restritos à thread dele; o servidor continua aceitando conexões.
