# SIGA — Sistema de Compartilhamento de Arquivos

##  Sobre o projeto

O **SIGA (Sistema de Compartilhamento de Arquivos)** é uma aplicação desenvolvida em **Python** para realizar o compartilhamento de arquivos utilizando comunicação de rede através do protocolo **TCP (Transmission Control Protocol)**.

O sistema é composto por duas partes:

* **Servidor:** responsável por armazenar, listar e enviar arquivos.
* **Cliente:** responsável por enviar arquivos ao servidor, consultar os arquivos disponíveis e realizar downloads.

A comunicação entre cliente e servidor é realizada por meio de **sockets TCP**.

---

##  Objetivo

O objetivo do projeto é aplicar na prática conceitos de:

* Comunicação em rede;
* Protocolo TCP;
* Sockets em Python;
* Arquitetura cliente-servidor;
* Transferência de arquivos;
* Envio e recebimento de dados pela rede;
* Manipulação de arquivos em Python.

---

## 🛠️ Tecnologias utilizadas

* **Python 3**
* **Socket TCP**
* **Git**
* **GitHub**

O projeto utiliza apenas bibliotecas padrão do Python, não sendo necessário instalar bibliotecas externas.

---

##  Estrutura do projeto

```text
SIGA/
│
├── arquivos_servidor/
│   └── teste.txt
│
├── downloads/
│
├── cliente.py
├── servidor.py
├── arquivo_teste.txt
└── README.md
```

### Descrição dos arquivos

| Arquivo/Pasta        | Descrição                                                      |
| -------------------- | -------------------------------------------------------------- |
| `servidor.py`        | Código responsável pelo funcionamento do servidor              |
| `cliente.py`         | Código responsável pelo funcionamento do cliente               |
| `arquivos_servidor/` | Pasta onde os arquivos recebidos pelo servidor são armazenados |
| `downloads/`         | Pasta onde os arquivos baixados pelo cliente são salvos        |
| `arquivo_teste.txt`  | Arquivo utilizado para testar o envio para o servidor          |
| `teste.txt`          | Arquivo utilizado para testar a listagem e o download          |
| `README.md`          | Documentação do projeto                                        |

---

##  Como executar o projeto

### 1. Pré-requisito

É necessário ter o **Python 3** instalado no computador.

Para verificar a instalação:

```bash
python --version
```

---

### 2. Abrir a pasta do projeto

No Git Bash:

```bash
cd ~/SIGA
```

---

### 3. Verificar a sintaxe dos arquivos

Antes de executar o sistema, pode ser realizada uma verificação dos arquivos Python:

```bash
python -m py_compile servidor.py cliente.py
```

Se nenhum erro for apresentado, os arquivos estão com a sintaxe correta.

---

##  Executando o servidor

Abra uma janela do terminal dentro da pasta do projeto e execute:

```bash
python servidor.py
```

O servidor será iniciado utilizando:

```text
Host: 127.0.0.1
Porta: 5000
```

A mensagem apresentada será semelhante a:

```text
==================================================
SICA - SERVIDOR
==================================================
Servidor iniciado em 127.0.0.1:5000
Aguardando conexão de um cliente...
```

O servidor deve permanecer aberto enquanto o cliente estiver sendo utilizado.

---

##  Executando o cliente

Abra uma **segunda janela do terminal** e execute:

```bash
cd ~/SIGA
python cliente.py
```

Será apresentado o menu:

```text
1 - Enviar arquivo
2 - Listar arquivos
3 - Baixar arquivo
4 - Sair
```

---

#  1. Enviar arquivo

Escolha a opção:

```text
1
```

Em seguida, informe o caminho do arquivo que deseja enviar.

Exemplo:

```text
arquivo_teste.txt
```

O cliente envia o arquivo através da conexão TCP.

Após o recebimento, o servidor armazena o arquivo na pasta:

```text
arquivos_servidor/
```

Exemplo de confirmação:

```text
Arquivo enviado: arquivo_teste.txt
Tamanho: 55 bytes
Servidor confirmou o recebimento do arquivo.
```

---

#  2. Listar arquivos

Escolha:

```text
2
```

O cliente solicita ao servidor a lista de arquivos disponíveis.

Exemplo:

```text
===== ARQUIVOS DISPONÍVEIS =====
arquivo_teste.txt
teste.txt
===============================
```

Os arquivos são aqueles armazenados na pasta:

```text
arquivos_servidor/
```

---

#  3. Baixar arquivo

Escolha:

```text
3
```

Depois informe o nome do arquivo disponível no servidor.

Exemplo:

```text
Digite o nome do arquivo que deseja baixar: teste.txt
```

O servidor envia o arquivo através da conexão TCP.

O cliente salva o arquivo automaticamente na pasta:

```text
downloads/
```

Exemplo de resultado:

```text
Arquivo baixado: teste.txt
Tamanho: 44 bytes
Salvo em: downloads\teste.txt
```

---

#  4. Encerrar o cliente

Para finalizar o programa cliente, escolha:

```text
4
```

Será exibido:

```text
Encerrando o cliente...
Cliente encerrado.
```

Para encerrar o servidor, utilize:

```text
Ctrl + C
```

---

##  Funcionamento da comunicação

O funcionamento básico do sistema ocorre da seguinte forma:

```text
                 TCP / SOCKET
                     │
                     │
          ┌──────────▼──────────┐
          │       SERVIDOR      │
          │    127.0.0.1:5000   │
          └──────────▲──────────┘
                     │
                     │
          ┌──────────▼──────────┐
          │       CLIENTE       │
          └─────────────────────┘
```

O cliente estabelece uma conexão TCP com o servidor e pode realizar três operações principais:

```text
CLIENTE
   │
   ├── ENVIAR ────────► SERVIDOR
   │                      │
   │                      └── Salva arquivo
   │
   ├── LISTAR ────────► SERVIDOR
   │                      │
   │                      └── Retorna arquivos
   │
   └── BAIXAR ◄──────── SERVIDOR
                          │
                          └── Envia arquivo
```

---

##  Testes realizados

Durante os testes do sistema foram verificadas as seguintes funcionalidades:

### Envio

O arquivo:

```text
arquivo_teste.txt
```

foi enviado com sucesso para o servidor.

Tamanho testado:

```text
55 bytes
```

### Listagem

Os arquivos armazenados no servidor foram listados corretamente.

Exemplo:

```text
arquivo_teste.txt
teste.txt
```

### Download

O arquivo:

```text
teste.txt
```

foi baixado com sucesso pelo cliente.

Tamanho confirmado:

```text
44 bytes
```

O arquivo foi salvo em:

```text
downloads\teste.txt
```

---

##  Comunicação e organização dos dados

O projeto utiliza **sockets TCP** para estabelecer a comunicação entre cliente e servidor.

O protocolo TCP foi utilizado porque fornece uma comunicação orientada à conexão, permitindo que os dados sejam transmitidos de maneira confiável entre as duas aplicações.

Para evitar problemas na interpretação dos dados recebidos, o sistema utiliza estruturas de controle para identificar:

* Comandos enviados pelo cliente;
* Tamanho dos nomes dos arquivos;
* Tamanho dos arquivos;
* Dados dos arquivos;
* Mensagens de status.

---

##  Autoria

Projeto desenvolvido como atividade prática acadêmica, com o objetivo de aplicar conceitos de **redes de computadores, programação em Python e comunicação cliente-servidor**.

**Projeto:** SIGA — Sistema de Compartilhamento de Arquivos
