#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 1 - Cliente-Servidor TCP (SERVIDOR)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
#   - Gabriel Luiz Fonseca Brandão
# =============================================================================
"""
Servidor TCP que aceita vários clientes ao mesmo tempo (uma thread por conexão).
Cada mensagem recebida é mostrada no console com data/hora e IP:porta do
cliente, e o servidor responde com uma confirmação.
"""

import argparse
import socket
import threading
from datetime import datetime

TAMANHO_BUFFER = 4096  # quantidade máxima de bytes lidos por vez


def agora():
    """Retorna a data/hora atual formatada para os logs."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def atender_cliente(conexao, endereco):
    """
    Função executada por uma thread para cada cliente conectado.
    Fica lendo mensagens até o cliente fechar a conexão.
    """
    ip, porta = endereco
    print(f"[{agora()}] Cliente conectado: {ip}:{porta}")

    try:
        # O "with" garante que o socket do cliente será fechado no final
        with conexao:
            while True:
                dados = conexao.recv(TAMANHO_BUFFER)

                # recv() retorna b"" quando o cliente fecha a conexão
                if not dados:
                    break

                mensagem = dados.decode("utf-8", errors="replace").strip()

                # Validação de mensagem vazia (o cliente já valida, mas o
                # servidor também verifica para não confiar só no cliente)
                if mensagem == "":
                    conexao.sendall("Erro: mensagem vazia".encode("utf-8"))
                    continue

                print(f"[{agora()}] {ip}:{porta} -> {mensagem}")
                conexao.sendall("Mensagem recebida".encode("utf-8"))

    except ConnectionResetError:
        # O cliente caiu sem fechar a conexão corretamente
        print(f"[{agora()}] Conexão com {ip}:{porta} foi resetada pelo cliente")
    except OSError as erro:
        print(f"[{agora()}] Erro de comunicação com {ip}:{porta}: {erro}")
    finally:
        print(f"[{agora()}] Cliente desconectado: {ip}:{porta}")


def main():
    # Lê host e porta pela linha de comando (com valores padrão)
    parser = argparse.ArgumentParser(description="Servidor TCP multithread")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço onde o servidor escuta (padrão: 0.0.0.0)")
    parser.add_argument("--porta", type=int, default=5000,
                        help="porta TCP do servidor (padrão: 5000)")
    args = parser.parse_args()

    # Cria o socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reutilizar a porta logo após reiniciar o servidor
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor.bind((args.host, args.porta))
        servidor.listen()
        print(f"[{agora()}] Servidor TCP ouvindo em {args.host}:{args.porta}")
        print("Pressione Ctrl+C para encerrar.")

        while True:
            # accept() bloqueia até um cliente se conectar
            conexao, endereco = servidor.accept()
            # Uma thread nova para cada cliente (daemon = encerra junto com o programa)
            thread = threading.Thread(target=atender_cliente,
                                      args=(conexao, endereco), daemon=True)
            thread.start()

    except KeyboardInterrupt:
        print(f"\n[{agora()}] Servidor encerrado pelo usuário.")
    except OSError as erro:
        print(f"Erro ao iniciar o servidor: {erro}")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
