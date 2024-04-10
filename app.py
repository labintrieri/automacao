from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import requests
from datetime import datetime


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



# conexão com o MongoDB
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
    eventos = list(db.eventos.find().sort("_id", -1).limit(5))
    if eventos:
        mensagem = "Oi! Esses são os últimos eventos anunciados no Sesc:\n\n"
        for evento in eventos:
            # formatar datas
            data_evento = datetime.strptime(evento['dataProxSessao'], "%Y-%m-%dT%H:%M")
            dia = data_evento.day
            mes = meses[data_evento.month]
            ano = data_evento.year
            hora = data_evento.strftime("%Hh%M")
            data_formatada = f"{dia} de {mes} de {ano}, às {hora}"
            
            mensagem += f"📅 <b>{evento['titulo']}</b>\n"
            mensagem += f"{evento['complemento']}\n"
            mensagem += f"Data da próxima sessão: {data_formatada}\n"
            if 'categorias' in evento:
                mensagem += "Categorias: " + ", ".join(categoria['titulo'] for categoria in evento['categorias']) + "\n"
            mensagem += f"<a href='https://www.sescsp.org.br{evento['link']}'>Mais informações</a>\n\n"
    else:
        mensagem = "Desculpe, não encontramos eventos recentes no Sesc."

    url_envio_mensagem = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    dados_mensagem = {"chat_id": chat_id, "text": mensagem, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url_envio_mensagem, data=dados_mensagem)
    return "ok"

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


def verificar_novos_eventos(token, chat_id, categorias_secundarias):
    mongodb_uri = 'mongodb://laura:dXrdqG6zRg3tv4nC@SG-insperdata-44537.servers.mongodirector.com:27017/mjd_laura?ssl=true'
    db = MongoClient(mongodb_uri, ssl=True, tlsAllowInvalidCertificates=True)['mjd_laura']
    eventos = buscar_eventos_sesc()
    for evento in eventos:
        if db.eventos.find_one({'id': evento['id']}) is None:
            db.eventos.insert_one(evento)


@app.route('/atualizar_eventos_sesc')
def atualizar_eventos_sesc():
    token = BOT_TOKEN  # Use o token conforme necessário
    chat_id = "SEU_CHAT_ID"  # Defina o chat_id conforme necessário
    verificar_novos_eventos(token, chat_id, categorias_secundarias)
    return jsonify({"status": "Eventos atualizados com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)