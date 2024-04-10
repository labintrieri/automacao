from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import requests
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%dT%H:%M")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = Flask(__name__) 


mongodb_uri = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_ID')

meses = {
    1: "janeiro", 2: "fevereiro", 3: "março",
    4: "abril", 5: "maio", 6: "junho",
    7: "julho", 8: "agosto", 9: "setembro",
    10: "outubro", 11: "novembro", 12: "dezembro"
}



client = MongoClient(mongodb_uri, ssl=True, tlsAllowInvalidCertificates=True)
db = client[db_name]  

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/infos")
def infos():
    return render_template('infos.html')

@app.route("/sesc")
def sesc():
    documentos = list(db.eventos.find().sort("dataPrimeiraSessao", -1).limit(10))
    
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
    data_atual_iso = datetime.now().isoformat()

    eventos = list(db.eventos.find({"dataPrimeiraSessao": {"$gte": data_atual_iso}}).sort("dataPrimeiraSessao", 1).limit(10))

    if eventos:
        mensagem = "Oi! Esses são os próximos eventos anunciados no Sesc:\n\n"
        for evento in eventos:
            data_primeira_sessao = datetime.fromisoformat(evento['dataPrimeiraSessao'])
            data_formatada = data_primeira_sessao.strftime('%d/%m/%Y às %H:%M')
            mensagem += f"📅 <b>{evento['titulo']}</b>\n"
            mensagem += f"{evento['complemento']}\n"
            mensagem += f"Data da primeira sessão: {data_formatada}\n"
            if 'categorias' in evento:
                mensagem += "Categorias: " + ", ".join(categoria['titulo'] for categoria in evento['categorias']) + "\n"
            if evento['unidade']:
                mensagem += "Unidade: " + ", ".join(unidade['name'] for unidade in evento['unidade']) + "\n"
            mensagem += f"<a href='https://www.sescsp.org.br{evento['link']}'>Mais informações</a>\n\n"
    else:
        mensagem = "Desculpe, não encontramos eventos recentes no Sesc."

    url_envio_mensagem = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    dados_mensagem = {"chat_id": chat_id, "text": mensagem, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url_envio_mensagem, data=dados_mensagem)
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)