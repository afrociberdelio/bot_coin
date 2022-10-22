# -*- coding: utf-8 -*-
import requests
import json
from flask import Flask
from flask import request
from flask import Response
import re
import os


app = Flask(__name__)

def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_cmc_data(crypto):
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    params = {'symbol': crypto, 'convert': 'USD'}
    headers = {'X-CMC_PRO_API_KEY': f'{os.getenv("cmc_token")}'}

    r = requests.get(url, headers=headers, params=params).json()

    price = r['data'][crypto][0]['quote']['USD']['price']

    return price


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']

    pattern = r'/[a-zA-Z]{2,4}'

    ticket = re.findall(pattern, txt)

    if ticket:
        symbol = ticket[0][1:].upper()
    else:
        symbol = ''

    return chat_id, symbol


def send_message(chat_id, text='bla-bla-bla'):
    url = f'https://api.telegram.org/bot{os.getenv("token_tg")}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}

    r = requests.post(url, json=payload)
    return r


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message(msg)

        if not symbol:
            send_message(chat_id, 'Wrog data')
            return Response('ok', status=200)

        price = get_cmc_data(symbol)
        send_message(chat_id, price)
        write_json(msg, 'telegram_request.json')

        return Response('ok', status=200)
    else:
        return '<h1>Hello World</h1>'



def main():
    print(get_cmc_data('BTC'))

if __name__ == '__main__':
    app.run(port=8080)
