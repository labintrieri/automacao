import os
from pymongo import MongoClient
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
mongodb_uri = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_ID')

# Inicia a conexão com o MongoDB
client = MongoClient(mongodb_uri, ssl=True, tlsAllowInvalidCertificates=True)
db = client[db_name]  # Usa o nome do banco de dados correto

def buscar_eventos_recentes():
    client = MongoClient(mongodb_uri)
    db = client['nome_do_seu_banco']
    eventos = list(db.eventos.find().sort([('_id', -1)]).limit(5))  # Busca os últimos 5 eventos armazenados
    return eventos

def gerar_texto_bot(eventos):
    texto_bot = "🌟 Últimos eventos do Sesc: 🌟\n\n"
    for evento in eventos:
        texto_bot += f"{evento['titulo']}\n"
    return texto_bot

def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    mensagem = {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
    requests.post(url, data=mensagem)
