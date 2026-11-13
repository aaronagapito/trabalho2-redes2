#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 1 - Cliente-Servidor TCP (CLIENTE)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
#   - Gabriel Luiz Fonseca Brandão
# =============================================================================
"""
Cliente TCP: conecta ao servidor, envia várias mensagens digitadas pelo
usuário e mostra a resposta de cada uma. Digite "sair" para encerrar.
"""

import argparse
import socket

TAMANHO_BUFFER = 4096


def main():
    parser = argparse.ArgumentParser(description="Cliente TCP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--porta", type=int, default=5000,
                        help="porta do servidor (padrão: 5000)")
    args = parser.parse_args()

    try:
        # O "with" fecha o socket automaticamente ao sair do bloco
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((args.host, args.porta))
            print(f"Conectado ao servidor {args.host}:{args.porta}")
            print('Digite suas mensagens ("sair" para encerrar).')

            while True:
                mensagem = input("> ").strip()

                if mensagem.lower() == "sair":
                    print("Encerrando a conexão...")
                    break

                # Validação: não envia mensagem vazia
                if mensagem == "":
                    print("Mensagem vazia não é permitida. Digite algo.")
                    continue

                cliente.sendall(mensagem.encode("utf-8"))

                resposta = cliente.recv(TAMANHO_BUFFER)
                if not resposta:
                    print("O servidor fechou a conexão.")
                    break
                print("Servidor:", resposta.decode("utf-8"))

    except ConnectionRefusedError:
        print(f"Erro: não foi possível conectar em {args.host}:{args.porta}. "
              "O servidor está ligado?")
    except ConnectionResetError:
        print("Erro: a conexão foi encerrada pelo servidor.")
    except (KeyboardInterrupt, EOFError):
        print("\nCliente encerrado.")
    except OSError as erro:
        print(f"Erro de rede: {erro}")


if __name__ == "__main__":
    main()
