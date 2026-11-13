#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 3 - Chat em Rede TCP (CLIENTE)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
# =============================================================================
"""
Cliente de chat. Pede um nickname, conecta ao servidor e usa duas linhas de
execução em paralelo:
  - a thread principal lê o teclado e envia as mensagens;
  - uma thread separada fica recebendo e imprimindo as mensagens da sala.
Digite "sair" para deixar a sala (o servidor e os outros continuam).
"""

import argparse
import os
import socket
import threading

# Fica "ligado" quando o próprio usuário pediu para sair, para a thread de
# recebimento saber que o fechamento do socket foi intencional
saindo = threading.Event()


def receber_mensagens(conexao):
    """Thread que lê continuamente as mensagens enviadas pelo servidor."""
    try:
        leitor = conexao.makefile("r", encoding="utf-8", errors="replace")
        for linha in leitor:
            # \r apaga o "> " da linha atual antes de mostrar a mensagem
            print("\r" + linha.rstrip("\n"))
            print("> ", end="", flush=True)
    except OSError:
        pass  # o socket foi fechado

    if not saindo.is_set():
        # Foi o servidor que encerrou: avisa e termina o programa inteiro
        print("\nConexão encerrada pelo servidor.")
        os._exit(0)


def main():
    parser = argparse.ArgumentParser(description="Cliente de chat TCP")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--porta", type=int, default=5001,
                        help="porta do servidor (padrão: 5001)")
    parser.add_argument("--nick", default=None,
                        help="nickname (se não informar, será perguntado)")
    args = parser.parse_args()

    # Solicita o nickname até o usuário digitar algo válido
    nick = args.nick
    while not nick or not nick.strip():
        try:
            nick = input("Digite seu nickname: ")
        except (KeyboardInterrupt, EOFError):
            print()
            return
    nick = nick.strip().replace("\n", " ")

    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conexao.connect((args.host, args.porta))
    except ConnectionRefusedError:
        print(f"Erro: servidor {args.host}:{args.porta} indisponível.")
        conexao.close()
        return
    except OSError as erro:
        print(f"Erro ao conectar: {erro}")
        conexao.close()
        return

    try:
        # Primeira linha enviada = nickname (regra do protocolo)
        conexao.sendall((nick + "\n").encode("utf-8"))

        # Thread separada para receber mensagens enquanto o usuário digita
        threading.Thread(target=receber_mensagens, args=(conexao,),
                         daemon=True).start()

        print('Você entrou no chat. Digite "sair" para sair.')
        while True:
            texto = input("> ").strip()
            if texto == "":
                continue  # não envia mensagens vazias
            if texto.lower() == "sair":
                break
            conexao.sendall((texto + "\n").encode("utf-8"))

    except (KeyboardInterrupt, EOFError):
        pass
    except OSError as erro:
        print(f"Erro de comunicação: {erro}")
    finally:
        # Saída limpa: avisa o servidor e fecha o socket
        saindo.set()
        try:
            conexao.sendall("sair\n".encode("utf-8"))
            conexao.shutdown(socket.SHUT_RDWR)  # acorda a thread de leitura
        except OSError:
            pass
        conexao.close()
        print("\nVocê saiu do chat.")


if __name__ == "__main__":
    main()
