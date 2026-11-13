#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 3 - Chat em Rede TCP (SERVIDOR)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
# =============================================================================
"""
Servidor central de chat. Aceita qualquer número de clientes (uma thread por
cliente) e retransmite (broadcast) cada mensagem para todos os outros,
com o nome do remetente na frente. Avisa quando alguém entra ou sai.

Protocolo (texto, uma mensagem por linha terminada em "\\n"):
  1) a primeira linha que o cliente envia é o seu nickname;
  2) as linhas seguintes são mensagens do chat;
  3) a linha "sair" (ou fechar a conexão) tira o cliente da sala.
"""

import argparse
import socket
import threading
from datetime import datetime

# Dicionário {socket_do_cliente: nickname} compartilhado entre as threads
clientes = {}
# Lock para que duas threads não alterem/leiam o dicionário ao mesmo tempo
trava_clientes = threading.Lock()


def agora():
    """Hora atual para os logs do servidor."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def enviar_linha(conexao, texto):
    """Envia um texto terminado em quebra de linha (fim de mensagem)."""
    conexao.sendall((texto + "\n").encode("utf-8"))


def broadcast(texto, remetente=None):
    """
    Envia o texto para todos os clientes conectados, exceto o remetente.
    Se o envio para algum cliente falhar, ele é removido da lista.
    """
    with trava_clientes:
        destinos = list(clientes.keys())  # cópia para iterar com segurança

    for conexao in destinos:
        if conexao is remetente:
            continue
        try:
            enviar_linha(conexao, texto)
        except OSError:
            # Cliente com problema: remove para não tentar de novo
            with trava_clientes:
                clientes.pop(conexao, None)


def nick_em_uso(nick):
    """Verifica se já existe alguém na sala com esse nickname."""
    with trava_clientes:
        return nick.lower() in [n.lower() for n in clientes.values()]


def atender_cliente(conexao, endereco):
    """Thread de um cliente: recebe o nick e depois as mensagens."""
    ip, porta = endereco
    nick = None

    try:
        # makefile permite ler o socket linha por linha, como um arquivo
        leitor = conexao.makefile("r", encoding="utf-8", errors="replace")

        # ---- 1) Recebe e valida o nickname ----
        primeira_linha = leitor.readline()
        if not primeira_linha:
            return  # cliente desconectou antes de mandar o nick
        nick = primeira_linha.strip()

        if nick == "" or nick_em_uso(nick):
            enviar_linha(conexao, f"[Servidor] Nickname inválido ou já em uso: '{nick}'. "
                                  "Conecte novamente com outro nome.")
            nick = None
            return

        with trava_clientes:
            clientes[conexao] = nick

        print(f"[{agora()}] {nick} entrou ({ip}:{porta}). "
              f"Usuários online: {len(clientes)}")
        enviar_linha(conexao, f"[Servidor] Bem-vindo(a), {nick}! "
                              f"Há {len(clientes)} usuário(s) na sala.")
        broadcast(f"[Servidor] {nick} entrou na sala.", remetente=conexao)

        # ---- 2) Recebe mensagens até o cliente sair ----
        for linha in leitor:
            mensagem = linha.strip()
            if mensagem == "":
                continue  # ignora linhas vazias
            if mensagem.lower() == "sair":
                break
            print(f"[{agora()}] {nick}: {mensagem}")
            broadcast(f"[{nick}] {mensagem}", remetente=conexao)

    except (ConnectionResetError, BrokenPipeError):
        print(f"[{agora()}] Conexão perdida com {ip}:{porta}")
    except OSError as erro:
        print(f"[{agora()}] Erro com {ip}:{porta}: {erro}")
    finally:
        # ---- 3) Remove o cliente e avisa os outros ----
        with trava_clientes:
            clientes.pop(conexao, None)
        conexao.close()
        if nick is not None:
            print(f"[{agora()}] {nick} saiu. Usuários online: {len(clientes)}")
            broadcast(f"[Servidor] {nick} saiu da sala.")


def main():
    parser = argparse.ArgumentParser(description="Servidor de chat TCP")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço onde o servidor escuta (padrão: 0.0.0.0)")
    parser.add_argument("--porta", type=int, default=5001,
                        help="porta TCP do servidor (padrão: 5001)")
    args = parser.parse_args()

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor.bind((args.host, args.porta))
        servidor.listen()
        print(f"[{agora()}] Servidor de chat ouvindo em {args.host}:{args.porta}")
        print("Pressione Ctrl+C para encerrar.")

        while True:
            conexao, endereco = servidor.accept()
            threading.Thread(target=atender_cliente,
                             args=(conexao, endereco), daemon=True).start()

    except KeyboardInterrupt:
        print(f"\n[{agora()}] Servidor encerrado pelo usuário.")
    except OSError as erro:
        print(f"Erro ao iniciar o servidor: {erro}")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
