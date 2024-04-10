from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import requests

mongodb_uri = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_ID')
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

categorias_secundarias = ['ateliê aberto',
 'ateliê para família',
 'aula aberta',
 'bate-papo',
 'bibliotecas',
 'bicicleta',
 'cinema e video',
 'concerto',
 'contação de histórias',
 'corrida',
 'curso',
 'cursos',
 'dança',
 'demonstração',
 'encontro',
 'espetáculo',
 'esporte adulto (16+)',
 'esporte criança (3 a 6)',
 'esporte jovem (10 a 13)',
 'esporte jovem (13 a 16)',
 'excursão',
 'exibição',
 'exposição',
 'filmes',
 'ginástica multifuncional',
 'instalação',
 'intervenção',
 'lançamento',
 'leitura literária',
 'musical',
 'natação e hidroginástica',
 'ocupação',
 'oficina',
 'palestra',
 'para crianças',
 'para todos os públicos',
 'passeio',
 'performance',
 'recreação',
 'recreação aquática',
 'recreação campo',
 'recreação quadra',
 'sarau',
 'show',
 'tai chi chuan',
 'torneios e campeonatos',
 'vivência',
 'workshop',
 'yoga']

def buscar_eventos_sesc():
    cookies = {
        'PHPSESSID': 'j6b4gtqbl4jgvh3cigauba0g5h',
        'LGPD': 'here',
        'AWSALB': 'Ch2Vs/bxjN9zUuWn0joGjz4FkMsRJqkIirooIN/ULaKiLcx3olCaD4mPPaocMeMJOuxp1+oMeccJl6HZq/6qyh2X18FaLrKocPEDosDBP9I/bjCUiL5BxhLNWGB1',
        'AWSALBCORS': 'Ch2Vs/bxjN9zUuWn0joGjz4FkMsRJqkIirooIN/ULaKiLcx3olCaD4mPPaocMeMJOuxp1+oMeccJl6HZq/6qyh2X18FaLrKocPEDosDBP9I/bjCUiL5BxhLNWGB1',
    }
    headers = {
        'authority': 'www.sescsp.org.br',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'dnt': '1',
        'referer': 'https://www.sescsp.org.br/programacao/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    params = {
        'data_inicial': '',
        'data_final': '',
        'local': '',
        'categoria': '',
        'source': 'null',
        'ppp': '1000',
        'page': '1',
        'tipo': 'atividade',
    }
    response = requests.get('https://www.sescsp.org.br/wp-json/wp/v1/atividades/filter', params=params, cookies=cookies, headers=headers)
    return response.json()['atividade']
    pass

def verificar_novos_eventos():
    db = MongoClient(mongodb_uri, ssl=True, tlsAllowInvalidCertificates=True).get_default_database()
    eventos = buscar_eventos_sesc()
    for evento in eventos:
        if db.eventos.find_one({'id': evento['id']}) is None:
            db.eventos.insert_one(evento)

def gerar_texto_bot(eventos):
    texto_bot = "🌟 Últimos eventos do Sesc: 🌟\n\n"
    for evento in eventos[:5]:  # Limita a resposta aos primeiros 5 eventos
        texto_bot += f"{evento['titulo']}\n"
    return texto_bot

def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    mensagem = {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
    requests.post(url, data=mensagem)

