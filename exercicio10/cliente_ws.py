#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 10 - Chat em Rede com WebSockets (CLIENTE EM PYTHON)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
#   - Gabriel Luiz Fonseca Brandão
# =============================================================================
"""
Cliente de terminal para o chat WebSocket. Duas tarefas rodam juntas:
  - uma recebe e imprime as mensagens da sala;
  - outra envia o que é digitado (input() roda numa thread auxiliar
    para não travar o recebimento).
Digite "sair" para sair.
"""

import argparse
import asyncio
import json
import threading

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed


def mostrar(dados):
    """Formata uma mensagem recebida do servidor para exibir no terminal."""
    tipo = dados.get("tipo")
    if tipo == "mensagem":
        texto = f"[{dados.get('hora', '')}] {dados.get('nome')}: {dados.get('texto')}"
    elif tipo == "erro":
        texto = f"*** ERRO: {dados.get('texto')}"
    else:
        texto = f"*** {dados.get('texto')}"
    print("\r" + texto)
    print("> ", end="", flush=True)


async def receber(conexao):
    """Recebe mensagens até a conexão fechar."""
    try:
        async for bruto in conexao:
            try:
                mostrar(json.loads(bruto))
            except json.JSONDecodeError:
                print("\r(mensagem inválida recebida)")
    except ConnectionClosed:
        pass
    print("\rConexão com o servidor encerrada.")


def ler_teclado(loop, fila):
    """
    Roda numa thread separada (daemon), pois input() bloqueia.
    Cada linha digitada é colocada na fila do asyncio; None indica fim.
    """
    while True:
        try:
            linha = input("> ")
        except (EOFError, KeyboardInterrupt):
            linha = None
        # call_soon_threadsafe: forma segura de falar com o loop a partir de outra thread
        loop.call_soon_threadsafe(fila.put_nowait, linha)
        if linha is None:
            break


async def enviar(conexao):
    """Pega as linhas digitadas (da fila) e envia para o servidor."""
    fila = asyncio.Queue()
    threading.Thread(target=ler_teclado, args=(asyncio.get_running_loop(), fila),
                     daemon=True).start()
    while True:
        texto = await fila.get()
        if texto is None:
            break
        texto = texto.strip()
        if texto == "":
            continue
        if texto.lower() == "sair":
            break
        await conexao.send(json.dumps({"tipo": "mensagem", "texto": texto},
                                      ensure_ascii=False))


async def principal(url, nome):
    try:
        async with connect(url) as conexao:
            # Primeira mensagem: identifica o usuário
            await conexao.send(json.dumps({"tipo": "entrar", "nome": nome},
                                          ensure_ascii=False))
            print(f'Conectado a {url} como "{nome}". Digite "sair" para sair.')

            tarefa_receber = asyncio.create_task(receber(conexao))
            tarefa_enviar = asyncio.create_task(enviar(conexao))

            # Termina quando qualquer uma das duas acabar (sair ou servidor caiu)
            await asyncio.wait([tarefa_receber, tarefa_enviar],
                               return_when=asyncio.FIRST_COMPLETED)
            tarefa_receber.cancel()
    except (ConnectionRefusedError, OSError):
        print(f"Erro: não foi possível conectar em {url}. O servidor está ligado?")
    except ConnectionClosed:
        print("A conexão foi encerrada.")


def main():
    parser = argparse.ArgumentParser(description="Cliente de chat WebSocket")
    parser.add_argument("--host", default="127.0.0.1",
                        help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--porta", type=int, default=8765,
                        help="porta do servidor (padrão: 8765)")
    parser.add_argument("--nome", default=None,
                        help="nome de usuário (se não informar, será perguntado)")
    args = parser.parse_args()

    nome = args.nome
    while not nome or not nome.strip():
        try:
            nome = input("Digite seu nome de usuário: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

    url = f"ws://{args.host}:{args.porta}"
    try:
        asyncio.run(principal(url, nome.strip()))
    except KeyboardInterrupt:
        pass
    print("Você saiu do chat.")


if __name__ == "__main__":
    main()
