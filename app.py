import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PyPDF2 import PdfReader

import nltk
try:
    nltk.data.find('corpus/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer

load_dotenv()

app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
API_KEY = os.getenv("HUGGINGFACE_API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}

def query_huggingface(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def classify_and_suggest(email_text):
    payload = {
        "inputs": email_text,
        "parameters": {
            "candidate_labels": ["Produtivo", "Improdutivo"]
        },
    }
    
    api_response = query_huggingface(payload)

    if 'labels' not in api_response or 'scores' not in api_response:
        if 'error' in api_response and 'estimated_time' in api_response:
            return {'error': 'Modelo de IA está sendo carregado. Tente novamente em alguns segundos.'}, 503
        return {'error': 'Resposta inesperada da API de IA.', 'details': api_response}, 500

    labels = api_response['labels']
    scores = api_response['scores']
    classification = labels[scores.index(max(scores))]

    suggested_reply = ""
    if classification == "Produtivo":
        suggested_reply = "Olá! Recebemos sua solicitação e nossa equipe já está analisando. Retornaremos o mais breve possível com uma atualização. Atenciosamente."
    else:
        suggested_reply = "Agradecemos o seu contato. Esta mensagem foi processada automaticamente."

    return {
        'classification': classification,
        'suggested_reply': suggested_reply
    }, 200


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/classify', methods=['POST'])
def classify_email():
    email_text = ""

    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400

            if file.filename.endswith('.txt'):
                email_text = file.read().decode('utf-8')
            elif file.filename.endswith('.pdf'):
                pdf_reader = PdfReader(file)
                text_parts = [page.extract_text() for page in pdf_reader.pages]
                email_text = "\n".join(text_parts)
            else:
                return jsonify({'error': 'Formato de arquivo inválido. Use .txt ou .pdf'}), 400
        
        else:
            data = request.get_json()
            email_text = data.get('email_text')

        if not email_text or not email_text.strip():
            return jsonify({'error': 'O conteúdo do email está vazio.'}), 400
        
        result, status_code = classify_and_suggest(email_text)
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro ao processar sua solicitação: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)