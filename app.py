import os
import requests
import re
import string
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer

def initialize_nltk():
    resources = {
        'stopwords': 'portuguese',
        'punkt': 'portuguese'
    }
    
    print("Verificando recursos do NLTK...")
    try:
        stopwords.words(resources['stopwords'])
        print(f"[NLTK] Recurso 'stopwords' ({resources['stopwords']}) OK.")
    except LookupError:
        print(f"[NLTK] Baixando recurso 'stopwords'...")
        nltk.download('stopwords')

    try:
        word_tokenize('teste', language=resources['punkt'])
        print(f"[NLTK] Recurso 'punkt' ({resources['punkt']}) OK.")
    except LookupError:
        print(f"[NLTK] Baixando recurso 'punkt'...")
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
    
    try:
        st = RSLPStemmer()
        print(f"[NLTK] Recurso 'RSLP' ({resources['rslp']}) OK.")
    except LookupError:
        print(f"[NLTK] Baixando recurso 'RSLP'...")
        nltk.download('rslp')

    print("Verificação do NLTK concluída.")

load_dotenv()

app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
API_KEY = os.getenv("HUGGINGFACE_API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}

def preprocess_text(text):
    return text.lower().strip()

def query_huggingface(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def classify_and_suggest(email_text):
    processed_text = preprocess_text(email_text)

    productive_labels = [
        "solicitação de suporte técnico",
        "pedido de atualização de status de projeto",
        "dúvida sobre procedimento de trabalho",
        "marcação de reunião de negócios",
        "envio de documento importante para análise"
    ]
    unproductive_labels = [
        "mensagem de agradecimento ou cortesia",
        "email de felicitações ou comemoração",
        "assunto pessoal ou conversa informal", 
        "spam, propaganda ou marketing",
        "email ofensivo, impróprio ou reclamação",
        "email de teste sem propósito definido"   
    ]
    
    all_labels = productive_labels + unproductive_labels
    
    payload = {
        "inputs": processed_text,
        "parameters": { "candidate_labels": all_labels },
    }
    api_response = query_huggingface(payload)

    if 'labels' not in api_response or 'scores' not in api_response:
        if 'error' in api_response and 'estimated_time' in api_response:
            return {'error': 'Modelo de IA está sendo carregado. Tente novamente em alguns segundos.'}, 503
        return {'error': 'Resposta inesperada da API de IA.', 'details': api_response}, 500

    best_label = api_response['labels'][0]

    classification = ""
    if best_label in productive_labels:
        classification = "Produtivo"
    else:
        classification = "Improdutivo"

    suggested_reply = ""
    if classification == "Produtivo":
        suggested_reply = "Olá! Recebemos sua solicitação e nossa equipe já está analisando. Retornaremos o mais breve possível com uma atualização. Atenciosamente."
    else:
        if best_label == "email ofensivo, impróprio ou reclamação":
             suggested_reply = "Sua mensagem foi recebida e será encaminhada ao departamento responsável para análise."
        else:
             suggested_reply = "Agradecemos o seu contato. Esta mensagem foi processada automaticamente."
        
    return {
        'classification': classification,
        'suggested_reply': suggested_reply,
        'debug_info': {
             'best_label_found': best_label,
             'score': api_response['scores'][0]
        }
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

initialize_nltk()

if __name__ == '__main__':
    app.run(debug=True)