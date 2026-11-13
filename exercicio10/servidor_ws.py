#!/usr/bin/env python3
# =============================================================================
# Trabalho 2 - Redes de Computadores 2 - Prof. Alessandro Vivas Andrade
# Exercício 10 - Chat em Rede com WebSockets (SERVIDOR)
#
# Integrantes do grupo:
#   - Aaron Araújo Agapito Guedes
#   - Kayky Francisco Rodrigues da Rocha
# =============================================================================
"""
Servidor de chat com WebSockets (biblioteca "websockets", versão 13 ou mais
nova). Usa asyncio: em vez de uma thread por cliente, cada conexão é uma
corrotina, e o servidor atende várias ao mesmo tempo.

Protocolo (mensagens em JSON):
  cliente -> servidor
    {"tipo": "entrar",   "nome": "Ana"}        (primeira mensagem)
    {"tipo": "mensagem", "texto": "Olá!"}
  servidor -> clientes
    {"tipo": "sistema",  "texto": "Ana entrou na sala."}
    {"tipo": "mensagem", "nome": "Ana", "texto": "Olá!", "hora": "14:03:10"}
    {"tipo": "erro",     "texto": "..."}
"""

import argparse
import asyncio
import json
from datetime import datetime

from websockets.asyncio.server import broadcast, serve
from websockets.exceptions import ConnectionClosed

# Dicionário {conexão: nome do usuário} com todos os clientes da sala.
# Com asyncio tudo roda em uma única thread, então não é preciso Lock.
clientes = {}


def agora():
    """Hora atual (para logs e para as mensagens)."""
    return datetime.now().strftime("%H:%M:%S")


def log(texto):
    """Imprime uma linha de log com data e hora."""
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {texto}", flush=True)


def para_json(**campos):
    """Monta uma mensagem JSON (ensure_ascii=False mantém os acentos)."""
    return json.dumps(campos, ensure_ascii=False)


def enviar_para_os_outros(mensagem, remetente=None):
    """Broadcast para todos os clientes, menos o remetente."""
    destinos = [c for c in clientes if c is not remetente]
    # broadcast() da biblioteca envia sem bloquear e ignora conexões que caíram
    broadcast(destinos, mensagem)


async def atender(conexao):
    """Corrotina executada para cada cliente que se conecta."""
    endereco = conexao.remote_address
    nome = None

    try:
        # ---- 1) A primeira mensagem deve ser a de entrada, com o nome ----
        primeira = json.loads(await conexao.recv())
        nome = str(primeira.get("nome", "")).strip()

        if primeira.get("tipo") != "entrar" or nome == "":
            await conexao.send(para_json(tipo="erro", texto="Envie primeiro o seu nome."))
            nome = None
            return
        if nome.lower() in [n.lower() for n in clientes.values()]:
            await conexao.send(para_json(tipo="erro",
                                         texto=f"O nome '{nome}' já está em uso."))
            nome = None
            return

        clientes[conexao] = nome
        log(f"{nome} entrou ({endereco[0]}:{endereco[1]}). Online: {len(clientes)}")
        await conexao.send(para_json(tipo="sistema",
                                     texto=f"Bem-vindo(a), {nome}! "
                                           f"Online: {', '.join(clientes.values())}"))
        enviar_para_os_outros(para_json(tipo="sistema", texto=f"{nome} entrou na sala."),
                              remetente=conexao)

        # ---- 2) Laço de mensagens: termina quando a conexão fecha ----
        async for bruto in conexao:
            try:
                dados = json.loads(bruto)
            except json.JSONDecodeError:
                await conexao.send(para_json(tipo="erro", texto="Mensagem não é JSON válido."))
                continue

            texto = str(dados.get("texto", "")).strip()
            if dados.get("tipo") != "mensagem" or texto == "":
                continue  # ignora mensagens vazias ou de tipo desconhecido

            log(f"{nome}: {texto}")
            enviar_para_os_outros(para_json(tipo="mensagem", nome=nome,
                                            texto=texto, hora=agora()),
                                  remetente=conexao)

    except ConnectionClosed:
        # Desconexão inesperada (aba fechada, rede caiu...). Não derruba o servidor.
        pass
    except (json.JSONDecodeError, AttributeError):
        # Primeira mensagem em formato errado
        try:
            await conexao.send(para_json(tipo="erro", texto="Formato de entrada inválido."))
        except ConnectionClosed:
            pass
    finally:
        # ---- 3) Remove o cliente e avisa os demais ----
        if conexao in clientes:
            del clientes[conexao]
        if nome is not None:
            log(f"{nome} saiu. Online: {len(clientes)}")
            enviar_para_os_outros(para_json(tipo="sistema", texto=f"{nome} saiu da sala."))


async def principal(host, porta):
    """Inicia o servidor e fica rodando para sempre."""
    async with serve(atender, host, porta) as servidor:
        log(f"Servidor WebSocket ouvindo em ws://{host}:{porta}")
        print("Pressione Ctrl+C para encerrar.", flush=True)
        await servidor.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Servidor de chat WebSocket")
    parser.add_argument("--host", default="0.0.0.0",
                        help="endereço onde o servidor escuta (padrão: 0.0.0.0)")
    parser.add_argument("--porta", type=int, default=8765,
                        help="porta do servidor (padrão: 8765)")
    args = parser.parse_args()

    try:
        asyncio.run(principal(args.host, args.porta))
    except KeyboardInterrupt:
        log("Servidor encerrado pelo usuário.")
    except OSError as erro:
        print(f"Erro ao iniciar o servidor: {erro}")


if __name__ == "__main__":
    main()
