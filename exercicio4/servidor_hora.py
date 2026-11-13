#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 4 - Servidor de Hora com Threads TCP (SERVIDOR)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
# =============================================================================
"""
Servidor TCP multithread que devolve a hora atual ("HH:MM:SS").
Mantém um contador de clientes atendidos protegido por threading.Lock,
para que várias threads não o alterem ao mesmo tempo (condição de corrida).
Todas as solicitações são registradas em log (console e arquivo).

Protocolo: o cliente envia a linha "HORA" e recebe a hora como resposta.
"""

import argparse
import logging
import socket
import threading
import time

# ---- Contador thread-safe ----
total_atendidos = 0
trava_contador = threading.Lock()


def incrementar_contador():
    """Soma 1 ao contador de forma segura e devolve o novo valor."""
    global total_atendidos
    with trava_contador:  # só uma thread por vez entra neste bloco
        total_atendidos += 1
        return total_atendidos


def ler_contador():
    """Lê o contador com a trava (leitura consistente)."""
    with trava_contador:
        return total_atendidos


def configurar_log(arquivo):
    """Log com data/hora no console e em arquivo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)s] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(arquivo, encoding="utf-8")],
    )


def atender_cliente(conexao, endereco, atraso):
    """Atende um cliente. Qualquer erro fica restrito a esta thread."""
    ip, porta = endereco
    cliente = f"{ip}:{porta}"
    try:
        with conexao:
            conexao.settimeout(10)  # não espera para sempre por um cliente travado
            pedido = conexao.recv(1024).decode("utf-8", errors="replace").strip()
            logging.info("Solicitação recebida | cliente=%s | pedido='%s' | atendidos=%d",
                         cliente, pedido, ler_contador())

            if pedido.upper() != "HORA":
                conexao.sendall("ERRO: comando desconhecido (use HORA)\n".encode("utf-8"))
                logging.info("Pedido inválido | cliente=%s | atendidos=%d",
                             cliente, ler_contador())
                return

            # Atraso opcional para simular processamento e evidenciar a concorrência
            if atraso > 0:
                time.sleep(atraso)

            hora = time.strftime("%H:%M:%S")
            conexao.sendall((hora + "\n").encode("utf-8"))
            numero = incrementar_contador()
            logging.info("Solicitação atendida | cliente=%s | hora=%s | atendidos=%d",
                         cliente, hora, numero)

    except socket.timeout:
        logging.warning("Tempo esgotado esperando %s | atendidos=%d",
                        cliente, ler_contador())
    except OSError as erro:
        # Ex.: cliente caiu no meio. O servidor continua funcionando.
        logging.warning("Falha com cliente %s: %s | atendidos=%d",
                        cliente, erro, ler_contador())


def main():
    parser = argparse.ArgumentParser(description="Servidor de hora multithread")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço onde o servidor escuta (padrão: 0.0.0.0)")
    parser.add_argument("--porta", type=int, default=7000,
                        help="porta TCP do servidor (padrão: 7000)")
    parser.add_argument("--log", default="servidor_hora.log",
                        help="arquivo de log (padrão: servidor_hora.log)")
    parser.add_argument("--atraso", type=float, default=0.0,
                        help="segundos de espera antes de responder, para testes "
                             "de concorrência (padrão: 0)")
    args = parser.parse_args()

    configurar_log(args.log)

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        servidor.bind((args.host, args.porta))
        servidor.listen()
        logging.info("Servidor de hora ouvindo em %s:%d | atendidos=%d",
                     args.host, args.porta, ler_contador())

        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=atender_cliente,
                             args=(conexao, endereco, args.atraso),
                             daemon=True).start()

    except KeyboardInterrupt:
        logging.info("Servidor encerrado | total de atendidos=%d", ler_contador())
    except OSError as erro:
        logging.error("Erro ao iniciar o servidor: %s", erro)
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
