#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 4 - Servidor de Hora com Threads TCP (CLIENTE)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
#   - Gabriel Luiz Fonseca Brandão
# =============================================================================
"""
Cliente que pede a hora ao servidor e mostra no console.
Com --clientes N, abre N conexões ao mesmo tempo (uma thread cada) para
testar se o servidor realmente atende vários clientes em paralelo.
"""

import argparse
import socket
import threading


def pedir_hora(host, porta, numero):
    """Abre uma conexão, envia "HORA" e imprime a resposta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.settimeout(15)
            cliente.connect((host, porta))
            cliente.sendall("HORA\n".encode("utf-8"))
            resposta = cliente.recv(1024).decode("utf-8").strip()
            if resposta == "":
                print(f"[cliente {numero}] O servidor não respondeu.")
            else:
                print(f"[cliente {numero}] Hora no servidor: {resposta}")
    except ConnectionRefusedError:
        print(f"[cliente {numero}] Erro: servidor {host}:{porta} indisponível.")
    except socket.timeout:
        print(f"[cliente {numero}] Erro: tempo de resposta esgotado.")
    except OSError as erro:
        print(f"[cliente {numero}] Erro de rede: {erro}")


def main():
    parser = argparse.ArgumentParser(description="Cliente do servidor de hora")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--porta", type=int, default=7000,
                        help="porta do servidor (padrão: 7000)")
    parser.add_argument("--clientes", type=int, default=1,
                        help="quantos pedidos simultâneos fazer (padrão: 1)")
    args = parser.parse_args()

    if args.clientes < 1:
        print("--clientes deve ser pelo menos 1.")
        return

    if args.clientes == 1:
        pedir_hora(args.host, args.porta, 1)
        return

    # Várias threads, cada uma fazendo um pedido ao mesmo tempo
    threads = []
    for i in range(1, args.clientes + 1):
        t = threading.Thread(target=pedir_hora, args=(args.host, args.porta, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()  # espera todas terminarem


if __name__ == "__main__":
    main()
