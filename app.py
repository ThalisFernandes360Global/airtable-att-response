from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from pyairtable import Table
import json
import logging

load_dotenv()

logging.basicConfig(
    filename='alteracoesAirtable.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')


app = Flask(__name__)

# 🔐 Airtable config
AIRTABLE_API_KEY = os.getenv('AIR_TABLE_KEY')
BASE_ID = "app33F8uf0F6dQkPH"
TABLE_NAME = "tbl38ywsZPimg8U1E"

# 🧠 URL base da API do Airtable
AIRTABLE_URL = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'

headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

def procurar_linha_por_coluna( valor_desejado, nome_coluna='usernames'):
    # Conecta à tabela
    table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
    
    # Define a fórmula para filtrar os registros
    formula = f"{{{nome_coluna}}} = '{valor_desejado}'"
    
    # Obtém os registros que atendem ao filtro
    registros = table.all(formula=formula)

    if registros:
        return registros[0]['id']
    else:
        print(f"Nenhum registro encontrado para '{nome_coluna}' = '{valor_desejado}'.")
        return False

def setar_respondido(id):
    AIRTABLE_API_KEY = "pat39oW2cnvz87JRR.5a7c60aebce90b864b229996578e9a8bd3f0423a55a0f0ddc55567e44900e74a"
    BASE_ID = "app33F8uf0F6dQkPH"
    TABLE_ID = "tbl38ywsZPimg8U1E"
    URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}/{id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-type": "application/json"
    }

    data = {
        "fields":{
            "retornouContato": "Respondeu"
        }
    }

    response = requests.patch(URL, headers=headers, data = json.dumps(data))
    
    logging.info(f'id:{id} status:{response.status_code} response:{response.json()} \n')
   

    return response.status_code


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    record_id = data.get('usernameIG')
    origem = data.get('origem')

    if not record_id or not origem:
        return jsonify({'error': 'recordId e origem são obrigatórios'}), 400

    if origem == 'mannychat':
        
        id = procurar_linha_por_coluna(record_id)
        if id:
            resultado = setar_respondido(id)
            if resultado == 200:
                return jsonify({'status': 'Respondido com sucesso'}), 200
            else:
                return jsonify({'error': 'Erro ao responder'}), 500
        else:
            return jsonify({'error': 'Registro não encontrado'}), 404
            
if __name__ == '__main__':
    app.run(host='0.0.0.0',port= 5003, debug=True)
