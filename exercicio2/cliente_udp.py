#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 2 - Servidor Echo UDP (CLIENTE)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
#   - Gabriel Luiz Fonseca Brandão
# =============================================================================
"""
Cliente UDP: envia mensagens ao servidor de eco e mostra a resposta.
Valida o tamanho máximo do datagrama e usa timeout para não ficar travado
esperando uma resposta que nunca chega. Digite "sair" para encerrar.
"""

import argparse
import socket

# Payload máximo teórico de um datagrama UDP sobre IPv4 (65535 - 20 - 8)
TAMANHO_MAXIMO_UDP = 65507


def main():
    parser = argparse.ArgumentParser(description="Cliente echo UDP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--porta", type=int, default=6000,
                        help="porta do servidor (padrão: 6000)")
    parser.add_argument("--timeout", type=float, default=3.0,
                        help="segundos de espera pela resposta (padrão: 3)")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente:
        # Se nenhuma resposta chegar nesse tempo, recvfrom lança socket.timeout
        cliente.settimeout(args.timeout)
        destino = (args.host, args.porta)

        print(f"Enviando para {args.host}:{args.porta} (UDP)")
        print('Digite suas mensagens ("sair" para encerrar).')

        while True:
            try:
                mensagem = input("> ")
            except (KeyboardInterrupt, EOFError):
                print("\nCliente encerrado.")
                break

            if mensagem.strip().lower() == "sair":
                print("Encerrando...")
                break

            if mensagem.strip() == "":
                print("Mensagem vazia não é permitida. Digite algo.")
                continue

            dados = mensagem.encode("utf-8")

            # Validação do tamanho máximo permitido pelo UDP
            if len(dados) > TAMANHO_MAXIMO_UDP:
                print(f"Mensagem muito grande: {len(dados)} bytes. "
                      f"O máximo para UDP é {TAMANHO_MAXIMO_UDP} bytes.")
                continue

            try:
                cliente.sendto(dados, destino)
                resposta, _ = cliente.recvfrom(TAMANHO_MAXIMO_UDP)
                print("Eco:", resposta.decode("utf-8", errors="replace"))
            except socket.timeout:
                print(f"Sem resposta em {args.timeout}s. "
                      "O servidor pode estar desligado ou o pacote se perdeu.")
            except ConnectionRefusedError:
                # No Linux, um ICMP "porta inalcançável" pode chegar como este erro
                print("Erro: o servidor recusou a mensagem (porta fechada?).")
            except OSError as erro:
                print(f"Erro de comunicação: {erro}")


if __name__ == "__main__":
    main()
