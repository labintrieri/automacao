from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import requests
from app_telegram import verificar_novos_eventos, gerar_texto_bot, enviar_mensagem_telegram

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = Flask(__name__) # Cria uma instância do Flask.

# Busca os valores das variáveis de ambiente
mongodb_uri = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_ID')

# Inicia a conexão com o MongoDB
client = MongoClient(mongodb_uri, ssl=True, tlsAllowInvalidCertificates=True)
db = client[db_name]  # Usa o nome do banco de dados correto

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/infos")
def infos():
    return render_template('infos.html')

@app.route("/sesc")
def sesc():
    # Garanta que "eventos" é o nome correto da coleção
    documentos = list(db.eventos.find().sort("dataProxSessao", -1).limit(10))
    if documentos:
        return render_template('sesc.html', documentos=documentos)
    else:
        return "Informações do Sesc não encontradas", 404

@app.route("/projetos")
def projetos():
    return render_template('projetos.html')

@app.route("/publicacoes")
def publicacoes():
    return render_template('publicacoes.html')

@app.route("/telegram", methods=["POST"])
def telegram_update():
    update = request.json
    chat_id = update["message"]["chat"]["id"]
    verificar_novos_eventos()  # Verifica e armazena novos eventos no MongoDB
    eventos = list(db.eventos.find().sort([('_id', -1)]).limit(5))  # Busca os últimos 5 eventos armazenados
    texto_resposta = gerar_texto_bot(eventos)
    enviar_mensagem_telegram(chat_id, texto_resposta)
    
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)