# Trabalho 2 — Redes de Computadores 2

**Disciplina:** Redes de Computadores 2 — UFVJM
**Professor:** Alessandro Vivas Andrade
**Entrega:** 13/11/2026

**Integrantes:**
- Aaron Araújo Agapito Guedes
- Kayky Francisco Rodrigues da Rocha

## Estrutura do repositório

| Diretório | Exercício | Arquivos principais |
|---|---|---|
| `exercicio1/` | Cliente-servidor TCP multithread | `servidor_tcp.py`, `cliente_tcp.py` |
| `exercicio2/` | Servidor echo UDP | `servidor_udp.py`, `cliente_udp.py` |
| `exercicio3/` | Chat em rede TCP (broadcast) | `servidor_chat.py`, `cliente_chat.py` |
| `exercicio4/` | Servidor de hora com threads e `Lock` | `servidor_hora.py`, `cliente_hora.py` |
| `exercicio5/` | Wireshark — HTTP | `captura_http.pcapng`, `print_wireshark.png` |
| `exercicio6/` | Wireshark — handshake e encerramento TCP | `captura_tcp.pcapng`, `print_wireshark.png` |
| `exercicio7/` | Wireshark — DNS | `captura_dns.pcapng`, `print_wireshark.png` |
| `exercicio8/` | Wireshark — ICMP (ping) | `captura_icmp.pcapng`, `print_wireshark.png` |
| `exercicio9/` | Wireshark — DHCP (DORA) | `captura_dhcp.pcapng`, `print_wireshark.png` |
| `exercicio10/` | Chat com WebSockets | `servidor_ws.py`, `cliente_ws.py`, `cliente.html` |
| `scripts/` | Automação das capturas 5–9 no Windows (instala Wireshark/Npcap e captura) | `CAPTURAR.bat`, `capturar_windows.ps1` |

Cada diretório tem um `README.md` com o comando exato para executar, os parâmetros e as dependências.

## Requisitos

- Linux
- Python 3.10 ou superior (`python3 --version`)
- Exercícios 1 a 4: apenas a biblioteca padrão do Python
- Exercício 10: biblioteca `websockets` (versão 13+)
- Exercícios 5 a 9: Wireshark (e as ferramentas citadas em cada README)

## Instalação

```bash
git clone <URL-DO-REPOSITORIO>
cd <NOME-DO-REPOSITORIO>

# (opcional, recomendado) ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Execução rápida

Todos os programas aceitam `--host` e `--porta` (veja `--help`). Rode o servidor em um terminal e os clientes em outros:

```bash
# Exercício 1 (porta 5000)
python3 exercicio1/servidor_tcp.py
python3 exercicio1/cliente_tcp.py

# Exercício 2 (porta 6000)
python3 exercicio2/servidor_udp.py
python3 exercicio2/cliente_udp.py

# Exercício 3 (porta 5001)
python3 exercicio3/servidor_chat.py
python3 exercicio3/cliente_chat.py --nick Ana

# Exercício 4 (porta 7000)
python3 exercicio4/servidor_hora.py
python3 exercicio4/cliente_hora.py --clientes 5

# Exercício 10 (porta 8765)
python3 exercicio10/servidor_ws.py
python3 exercicio10/cliente_ws.py --nome Ana     # ou abra exercicio10/cliente.html no navegador
```

## Decisões gerais

- **Parâmetros por linha de comando** com `argparse` em todos os scripts (nenhum host/porta fixo no código, só valores padrão).
- **Concorrência:** exercícios 1, 3 e 4 usam uma `threading.Thread` por cliente; dados compartilhados entre threads (lista de clientes do chat, contador do servidor de hora) são protegidos com `threading.Lock`. O exercício 10 usa `asyncio`, modelo exigido pela biblioteca `websockets`.
- **Tratamento de erros:** servidor indisponível (`ConnectionRefusedError`), conexão resetada, timeout e entradas inválidas são tratados; a falha de um cliente nunca derruba o servidor.
- **Encerramento seguro:** sockets abertos com `with` ou fechados em `finally`.
- **Mensagens delimitadas por linha** (`\n`) no chat TCP, para que mensagens enviadas em sequência não se misturem no fluxo de bytes do TCP.
