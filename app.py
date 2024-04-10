from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import requests
from datetime import datetime


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
    
    # Busca os últimos 5 eventos armazenados com base no _id (assumindo que o _id reflete a ordem de inserção)
    eventos = list(db.eventos.find().sort("_id", -1).limit(5))
    
    # Formata a mensagem com os dados dos eventos
    if eventos:
        mensagem = "Oi! Esses são os últimos eventos anunciados no Sesc:\n\n"
        for evento in eventos:
            # Formata a data do evento
            data_formatada = datetime.strptime(evento['dataProxSessao'], "%Y-%m-%dT%H:%M").strftime("%d de %B de %Y, às %Hh%M")
            
            mensagem += f"📅 <b>{evento['titulo']}</b>\n"
            mensagem += f"{evento['complemento']}\n"
            mensagem += f"Data da próxima sessão: {data_formatada}\n"
            mensagem += "Categorias: " + ", ".join([categoria['titulo'] for categoria in evento.get('categorias', [])]) + "\n"
            mensagem += f"<a href='https://www.sescsp.org.br{evento['link']}'>Mais informações</a>\n\n"
    else:
        mensagem = "Desculpe, não encontramos eventos recentes no Sesc."

    # Envia a mensagem formatada
    url_envio_mensagem = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    dados_mensagem = {"chat_id": chat_id, "text": mensagem, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url_envio_mensagem, data=dados_mensagem)
    
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)