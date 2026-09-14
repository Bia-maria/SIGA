import socket
import os
import struct


# ============================================================
# CONFIGURAÇÕES
# ============================================================

HOST = "127.0.0.1"
PORTA = 5000

# Pasta onde os arquivos enviados ao servidor serão armazenados.
PASTA_ARQUIVOS = "arquivos_servidor"

# Tamanho fixo utilizado para mensagens de status.
TAMANHO_STATUS = 32


# ============================================================
# PREPARAÇÃO DA PASTA
# ============================================================

def preparar_pasta():
    """
    Verifica se a pasta de armazenamento dos arquivos existe.

    Caso não exista, ela será criada automaticamente.
    """

    if not os.path.exists(PASTA_ARQUIVOS):
        os.makedirs(PASTA_ARQUIVOS)


# ============================================================
# RECEBER EXATAMENTE UMA QUANTIDADE DE BYTES
# ============================================================

def receber_exatamente(conexao, tamanho):
    """
    Recebe exatamente a quantidade de bytes informada.

    O TCP funciona como um fluxo de dados. Por isso, não devemos
    assumir que uma chamada recv() receberá todos os bytes
    solicitados.

    A função continua recebendo até atingir o tamanho esperado.
    """

    dados = b""

    while len(dados) < tamanho:

        parte = conexao.recv(
            tamanho - len(dados)
        )

        if not parte:
            raise ConnectionError(
                "A conexão foi encerrada antes do recebimento completo."
            )

        dados += parte

    return dados


# ============================================================
# RECEBER COMANDO
# ============================================================

def receber_comando(conexao):
    """
    Recebe o comando enviado pelo cliente até encontrar '\\n'.

    Os comandos utilizados são:

        LISTAR
        ENVIAR
        BAIXAR

    A função também retorna os dados que eventualmente tenham
    chegado junto com o comando.
    """

    dados = b""

    while b"\n" not in dados:

        parte = conexao.recv(1024)

        if not parte:
            raise ConnectionError(
                "A conexão foi encerrada antes do recebimento do comando."
            )

        dados += parte

    comando, restante = dados.split(
        b"\n",
        1
    )

    return comando.decode("utf-8"), restante


# ============================================================
# ENVIAR STATUS
# ============================================================

def enviar_status(conexao, mensagem):
    """
    Envia uma mensagem de status com tamanho fixo.

    O tamanho fixo evita que a resposta seja misturada com
    os próximos dados da comunicação TCP.
    """

    dados = mensagem.encode("utf-8")

    if len(dados) > TAMANHO_STATUS:
        raise ValueError(
            "Mensagem de status muito grande."
        )

    dados = dados.ljust(
        TAMANHO_STATUS,
        b" "
    )

    conexao.sendall(
        dados
    )


# ============================================================
# ETAPA 2 - LISTAR ARQUIVOS
# ============================================================

def listar_arquivos():
    """
    Retorna a lista de arquivos existentes no servidor.
    """

    arquivos = os.listdir(
        PASTA_ARQUIVOS
    )

    arquivos.sort()

    return arquivos


def processar_listagem(conexao):
    """
    Envia ao cliente os arquivos disponíveis no servidor.

    Primeiro é enviado um número de 4 bytes informando o tamanho
    da lista. Depois são enviados os nomes dos arquivos.
    """

    arquivos = listar_arquivos()

    if arquivos:
        resposta = "\n".join(arquivos)
    else:
        resposta = "Nenhum arquivo disponível no servidor."

    resposta_bytes = resposta.encode("utf-8")

    # Envia o tamanho da resposta.
    conexao.sendall(
        struct.pack(
            "!I",
            len(resposta_bytes)
        )
    )

    # Envia a lista.
    conexao.sendall(
        resposta_bytes
    )


# ============================================================
# ETAPA 3 - RECEBER ARQUIVO
# ============================================================

def receber_arquivo(conexao, dados_iniciais):
    """
    Recebe um arquivo enviado pelo cliente.

    Ordem dos dados:

    1. 4 bytes com o tamanho do nome.
    2. Nome do arquivo.
    3. 8 bytes com o tamanho do arquivo.
    4. Conteúdo do arquivo.
    """

    dados = dados_iniciais

    # --------------------------------------------------------
    # TAMANHO DO NOME
    # --------------------------------------------------------

    while len(dados) < 4:

        dados += conexao.recv(
            4 - len(dados)
        )

        if not dados:
            raise ConnectionError(
                "Conexão encerrada ao receber o tamanho do nome."
            )

    tamanho_nome = struct.unpack(
        "!I",
        dados[:4]
    )[0]

    dados = dados[4:]

    # --------------------------------------------------------
    # NOME DO ARQUIVO
    # --------------------------------------------------------

    while len(dados) < tamanho_nome:

        parte = conexao.recv(
            tamanho_nome - len(dados)
        )

        if not parte:
            raise ConnectionError(
                "Conexão encerrada ao receber o nome do arquivo."
            )

        dados += parte

    nome_arquivo = dados[:tamanho_nome].decode(
        "utf-8"
    )

    dados = dados[tamanho_nome:]

    # Segurança contra caminhos externos.
    nome_arquivo = os.path.basename(
        nome_arquivo
    )

    if not nome_arquivo:
        raise ValueError(
            "Nome de arquivo inválido."
        )

    # --------------------------------------------------------
    # TAMANHO DO ARQUIVO
    # --------------------------------------------------------

    while len(dados) < 8:

        parte = conexao.recv(
            8 - len(dados)
        )

        if not parte:
            raise ConnectionError(
                "Conexão encerrada ao receber o tamanho do arquivo."
            )

        dados += parte

    tamanho_arquivo = struct.unpack(
        "!Q",
        dados[:8]
    )[0]

    dados = dados[8:]

    # --------------------------------------------------------
    # SALVAR ARQUIVO
    # --------------------------------------------------------

    caminho = os.path.join(
        PASTA_ARQUIVOS,
        nome_arquivo
    )

    total_recebido = 0

    with open(
        caminho,
        "wb"
    ) as arquivo:

        # Aproveita dados que já chegaram junto.
        if dados:

            quantidade = min(
                len(dados),
                tamanho_arquivo
            )

            arquivo.write(
                dados[:quantidade]
            )

            total_recebido += quantidade

        # Recebe o restante do arquivo.
        while total_recebido < tamanho_arquivo:

            restante = (
                tamanho_arquivo
                - total_recebido
            )

            quantidade = min(
                4096,
                restante
            )

            parte = conexao.recv(
                quantidade
            )

            if not parte:
                raise ConnectionError(
                    "Conexão encerrada durante o recebimento do arquivo."
                )

            arquivo.write(
                parte
            )

            total_recebido += len(
                parte
            )

    print()
    print(
        f"Arquivo recebido: {nome_arquivo}"
    )
    print(
        f"Tamanho: {total_recebido} bytes"
    )

    enviar_status(
        conexao,
        "ARQUIVO_RECEBIDO"
    )


# ============================================================
# ETAPA 4 - ENVIAR ARQUIVO
# ============================================================

def enviar_arquivo(conexao, dados_iniciais):
    """
    Envia um arquivo armazenado no servidor para o cliente.

    Ordem:

    1. Recebe o tamanho do nome.
    2. Recebe o nome.
    3. Verifica se existe.
    4. Envia status.
    5. Envia tamanho do arquivo.
    6. Envia conteúdo.
    """

    dados = dados_iniciais

    # --------------------------------------------------------
    # TAMANHO DO NOME
    # --------------------------------------------------------

    while len(dados) < 4:

        parte = conexao.recv(
            4 - len(dados)
        )

        if not parte:
            raise ConnectionError(
                "Conexão encerrada ao receber o tamanho do nome."
            )

        dados += parte

    tamanho_nome = struct.unpack(
        "!I",
        dados[:4]
    )[0]

    dados = dados[4:]

    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    while len(dados) < tamanho_nome:

        parte = conexao.recv(
            tamanho_nome - len(dados)
        )

        if not parte:
            raise ConnectionError(
                "Conexão encerrada ao receber o nome."
            )

        dados += parte

    nome_arquivo = dados[:tamanho_nome].decode(
        "utf-8"
    )

    nome_arquivo = os.path.basename(
        nome_arquivo
    )

    # --------------------------------------------------------
    # LOCALIZAR ARQUIVO
    # --------------------------------------------------------

    caminho = os.path.join(
        PASTA_ARQUIVOS,
        nome_arquivo
    )

    if not os.path.isfile(caminho):

        enviar_status(
            conexao,
            "ARQUIVO_NAO_ENCONTRADO"
        )

        print()
        print(
            f"Arquivo não encontrado: {nome_arquivo}"
        )

        return

    # --------------------------------------------------------
    # INFORMAR QUE O ARQUIVO EXISTE
    # --------------------------------------------------------

    enviar_status(
        conexao,
        "ARQUIVO_ENCONTRADO"
    )

    # --------------------------------------------------------
    # ENVIAR TAMANHO
    # --------------------------------------------------------

    tamanho_arquivo = os.path.getsize(
        caminho
    )

    conexao.sendall(
        struct.pack(
            "!Q",
            tamanho_arquivo
        )
    )

    # --------------------------------------------------------
    # ENVIAR CONTEÚDO
    # --------------------------------------------------------

    total_enviado = 0

    with open(
        caminho,
        "rb"
    ) as arquivo:

        while True:

            parte = arquivo.read(
                4096
            )

            if not parte:
                break

            conexao.sendall(
                parte
            )

            total_enviado += len(
                parte
            )

    print()
    print(
        f"Arquivo enviado para o cliente: {nome_arquivo}"
    )
    print(
        f"Tamanho: {total_enviado} bytes"
    )


# ============================================================
# PROCESSAR CLIENTE
# ============================================================

def processar_cliente(conexao, endereco):
    """
    Processa uma solicitação do cliente.

    Comandos:

        LISTAR
        ENVIAR
        BAIXAR
    """

    print(
        f"Cliente conectado: {endereco}"
    )

    try:

        solicitacao, dados_restantes = receber_comando(
            conexao
        )

        print(
            f"Solicitação recebida: {solicitacao}"
        )

        if solicitacao == "LISTAR":

            processar_listagem(
                conexao
            )

        elif solicitacao == "ENVIAR":

            receber_arquivo(
                conexao,
                dados_restantes
            )

        elif solicitacao == "BAIXAR":

            enviar_arquivo(
                conexao,
                dados_restantes
            )

        else:

            enviar_status(
                conexao,
                "OPERACAO_INVALIDA"
            )

    except Exception as erro:

        print()
        print(
            f"Erro ao processar solicitação: {erro}"
        )

    finally:

        conexao.close()

        print(
            "Cliente desconectado."
        )

        print(
            "Aguardando novo cliente..."
        )

        print()


# ============================================================
# INICIAR SERVIDOR
# ============================================================

def iniciar_servidor():
    """
    Cria o socket TCP do servidor, coloca-o em modo de escuta
    e aguarda conexões dos clientes.
    """

    preparar_pasta()

    servidor = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(
        (HOST, PORTA)
    )

    servidor.listen()

    print("=" * 50)
    print(
        "SICA - SERVIDOR"
    )
    print("=" * 50)

    print(
        f"Servidor iniciado em {HOST}:{PORTA}"
    )

    print(
        "Aguardando conexão de um cliente..."
    )

    print()

    while True:

        conexao, endereco = servidor.accept()

        processar_cliente(
            conexao,
            endereco
        )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    iniciar_servidor()
