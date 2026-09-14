import socket
import os
import struct


# ============================================================
# CONFIGURAÇÕES
# ============================================================

HOST = "127.0.0.1"
PORTA = 5000

# Pasta onde os arquivos baixados serão salvos.
PASTA_DOWNLOADS = "downloads"

# Tamanho fixo das mensagens de status.
TAMANHO_STATUS = 32


# ============================================================
# PREPARAR PASTA DE DOWNLOADS
# ============================================================

def preparar_pasta_downloads():
    """
    Cria a pasta de downloads caso ela ainda não exista.
    """

    if not os.path.exists(
        PASTA_DOWNLOADS
    ):

        os.makedirs(
            PASTA_DOWNLOADS
        )


# ============================================================
# RECEBER EXATAMENTE
# ============================================================

def receber_exatamente(cliente, tamanho):
    """
    Recebe exatamente a quantidade de bytes informada.

    Essa função é importante porque o TCP pode entregar os dados
    em várias partes.
    """

    dados = b""

    while len(dados) < tamanho:

        parte = cliente.recv(
            tamanho - len(dados)
        )

        if not parte:

            raise ConnectionError(
                "A conexão foi encerrada antes do recebimento completo."
            )

        dados += parte

    return dados


# ============================================================
# RECEBER STATUS
# ============================================================

def receber_status(cliente):
    """
    Recebe uma mensagem de status com tamanho fixo.
    """

    dados = receber_exatamente(
        cliente,
        TAMANHO_STATUS
    )

    return dados.decode(
        "utf-8"
    ).strip()


# ============================================================
# ETAPA 2 - LISTAR
# ============================================================

def listar_arquivos():
    """
    Solicita ao servidor a lista dos arquivos disponíveis.
    """

    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        cliente.connect(
            (HOST, PORTA)
        )

        # Envia o comando.
        cliente.sendall(
            b"LISTAR\n"
        )

        # Recebe o tamanho da resposta.
        dados_tamanho = receber_exatamente(
            cliente,
            4
        )

        tamanho_resposta = struct.unpack(
            "!I",
            dados_tamanho
        )[0]

        # Recebe a lista.
        dados_resposta = receber_exatamente(
            cliente,
            tamanho_resposta
        )

        resposta = dados_resposta.decode(
            "utf-8"
        )

        print()
        print(
            "===== ARQUIVOS DISPONÍVEIS ====="
        )

        print(
            resposta
        )

        print(
            "==============================="
        )

    except Exception as erro:

        print(
            f"Erro ao listar arquivos: {erro}"
        )

    finally:

        cliente.close()


# ============================================================
# ETAPA 3 - ENVIAR ARQUIVO
# ============================================================

def enviar_arquivo():
    """
    Envia um arquivo do computador do cliente para o servidor.
    """

    caminho_arquivo = input(
        "Digite o caminho do arquivo: "
    ).strip()

    if not os.path.isfile(
        caminho_arquivo
    ):

        print(
            "Arquivo não encontrado."
        )

        return

    nome_arquivo = os.path.basename(
        caminho_arquivo
    )

    nome_bytes = nome_arquivo.encode(
        "utf-8"
    )

    tamanho_arquivo = os.path.getsize(
        caminho_arquivo
    )

    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        cliente.connect(
            (HOST, PORTA)
        )

        # ----------------------------------------------------
        # COMANDO
        # ----------------------------------------------------

        cliente.sendall(
            b"ENVIAR\n"
        )

        # ----------------------------------------------------
        # TAMANHO DO NOME
        # ----------------------------------------------------

        cliente.sendall(
            struct.pack(
                "!I",
                len(nome_bytes)
            )
        )

        # ----------------------------------------------------
        # NOME
        # ----------------------------------------------------

        cliente.sendall(
            nome_bytes
        )

        # ----------------------------------------------------
        # TAMANHO DO ARQUIVO
        # ----------------------------------------------------

        cliente.sendall(
            struct.pack(
                "!Q",
                tamanho_arquivo
            )
        )

        # ----------------------------------------------------
        # CONTEÚDO
        # ----------------------------------------------------

        total_enviado = 0

        with open(
            caminho_arquivo,
            "rb"
        ) as arquivo:

            while True:

                parte = arquivo.read(
                    4096
                )

                if not parte:
                    break

                cliente.sendall(
                    parte
                )

                total_enviado += len(
                    parte
                )

        print()
        print(
            f"Arquivo enviado: {nome_arquivo}"
        )

        print(
            f"Tamanho: {total_enviado} bytes"
        )

        # ----------------------------------------------------
        # CONFIRMAÇÃO
        # ----------------------------------------------------

        resposta = receber_status(
            cliente
        )

        if resposta == "ARQUIVO_RECEBIDO":

            print(
                "Servidor confirmou o recebimento do arquivo."
            )

        else:

            print(
                f"Resposta do servidor: {resposta}"
            )

    except Exception as erro:

        print(
            f"Erro ao enviar arquivo: {erro}"
        )

    finally:

        cliente.close()


# ============================================================
# ETAPA 4 - BAIXAR ARQUIVO
# ============================================================

def baixar_arquivo():
    """
    Solicita ao servidor o download de um arquivo.

    O arquivo recebido será salvo na pasta downloads.
    """

    nome_arquivo = input(
        "Digite o nome do arquivo que deseja baixar: "
    ).strip()

    if not nome_arquivo:

        print(
            "Nome de arquivo inválido."
        )

        return

    nome_arquivo = os.path.basename(
        nome_arquivo
    )

    nome_bytes = nome_arquivo.encode(
        "utf-8"
    )

    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        cliente.connect(
            (HOST, PORTA)
        )

        # ----------------------------------------------------
        # COMANDO
        # ----------------------------------------------------

        cliente.sendall(
            b"BAIXAR\n"
        )

        # ----------------------------------------------------
        # TAMANHO DO NOME
        # ----------------------------------------------------

        cliente.sendall(
            struct.pack(
                "!I",
                len(nome_bytes)
            )
        )

        # ----------------------------------------------------
        # NOME
        # ----------------------------------------------------

        cliente.sendall(
            nome_bytes
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        resposta = receber_status(
            cliente
        )

        if resposta == "ARQUIVO_NAO_ENCONTRADO":

            print(
                "Arquivo não encontrado no servidor."
            )

            return

        if resposta != "ARQUIVO_ENCONTRADO":

            print(
                f"Resposta inesperada do servidor: {resposta}"
            )

            return

        # ----------------------------------------------------
        # TAMANHO DO ARQUIVO
        # ----------------------------------------------------

        dados_tamanho = receber_exatamente(
            cliente,
            8
        )

        tamanho_arquivo = struct.unpack(
            "!Q",
            dados_tamanho
        )[0]

        # ----------------------------------------------------
        # PREPARAR DOWNLOAD
        # ----------------------------------------------------

        preparar_pasta_downloads()

        caminho_download = os.path.join(
            PASTA_DOWNLOADS,
            nome_arquivo
        )

        total_recebido = 0

        # ----------------------------------------------------
        # RECEBER ARQUIVO
        # ----------------------------------------------------

        with open(
            caminho_download,
            "wb"
        ) as arquivo:

            while total_recebido < tamanho_arquivo:

                restante = (
                    tamanho_arquivo
                    - total_recebido
                )

                quantidade = min(
                    4096,
                    restante
                )

                parte = cliente.recv(
                    quantidade
                )

                if not parte:

                    raise ConnectionError(
                        "A conexão foi encerrada durante o download."
                    )

                arquivo.write(
                    parte
                )

                total_recebido += len(
                    parte
                )

        print()
        print(
            f"Arquivo baixado: {nome_arquivo}"
        )

        print(
            f"Tamanho: {total_recebido} bytes"
        )

        print(
            f"Salvo em: {caminho_download}"
        )

    except Exception as erro:

        print(
            f"Erro ao baixar arquivo: {erro}"
        )

    finally:

        cliente.close()


# ============================================================
# MENU PRINCIPAL
# ============================================================

def executar_cliente():
    """
    Exibe o menu principal do SICA.

    Opções:

    1 - Enviar arquivo.
    2 - Listar arquivos.
    3 - Baixar arquivo.
    4 - Sair.
    """

    print("=" * 50)

    print(
        "SICA - SISTEMA DE COMPARTILHAMENTO DE ARQUIVOS"
    )

    print("=" * 50)

    while True:

        print()

        print(
            "1 - Enviar arquivo"
        )

        print(
            "2 - Listar arquivos"
        )

        print(
            "3 - Baixar arquivo"
        )

        print(
            "4 - Sair"
        )

        opcao = input(
            "Escolha uma opção: "
        ).strip()

        if opcao == "1":

            enviar_arquivo()

        elif opcao == "2":

            listar_arquivos()

        elif opcao == "3":

            baixar_arquivo()

        elif opcao == "4":

            print(
                "Encerrando o cliente..."
            )

            break

        else:

            print(
                "Opção inválida."
            )

    print(
        "Cliente encerrado."
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    executar_cliente()
