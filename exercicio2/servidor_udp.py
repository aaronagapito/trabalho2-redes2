#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 2 - Servidor Echo UDP (SERVIDOR)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
# =============================================================================
"""
Servidor de eco UDP: tudo que chega é impresso no console junto com o
endereço do remetente e devolvido exatamente igual para quem enviou.
"""

import argparse
import socket
from datetime import datetime

# Maior payload possível de um datagrama UDP sobre IPv4:
# 65535 (máx. IP) - 20 (cabeçalho IP) - 8 (cabeçalho UDP) = 65507 bytes
TAMANHO_MAXIMO_UDP = 65507


def agora():
    """Retorna a data/hora atual formatada para os logs."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(description="Servidor echo UDP")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço onde o servidor escuta (padrão: 0.0.0.0)")
    parser.add_argument("--porta", type=int, default=6000,
                        help="porta UDP do servidor (padrão: 6000)")
    args = parser.parse_args()

    # SOCK_DGRAM = UDP (sem conexão, cada mensagem é um datagrama)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor:
        try:
            servidor.bind((args.host, args.porta))
        except OSError as erro:
            print(f"Erro ao iniciar o servidor: {erro}")
            return

        print(f"[{agora()}] Servidor echo UDP ouvindo em {args.host}:{args.porta}")
        print("Pressione Ctrl+C para encerrar.")

        try:
            while True:
                # recvfrom devolve os dados e o endereço (ip, porta) de quem enviou
                dados, endereco = servidor.recvfrom(TAMANHO_MAXIMO_UDP)
                ip, porta = endereco
                texto = dados.decode("utf-8", errors="replace")
                print(f"[{agora()}] {ip}:{porta} ({len(dados)} bytes) -> {texto}")

                try:
                    # Eco: envia de volta os mesmos bytes para o remetente
                    servidor.sendto(dados, endereco)
                except OSError as erro:
                    # Uma falha ao responder um cliente não derruba o servidor
                    print(f"[{agora()}] Erro ao responder {ip}:{porta}: {erro}")

        except KeyboardInterrupt:
            print(f"\n[{agora()}] Servidor encerrado pelo usuário.")


if __name__ == "__main__":
    main()
