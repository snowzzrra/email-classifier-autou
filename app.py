import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import json

load_dotenv()

app = Flask(__name__)

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Modelo Gemini configurado com sucesso.")
except Exception as e:
    print(f"Erro ao configurar o modelo Gemini: {e}")
    model = None

def preprocess_text(text):
    return " ".join(text.strip().split())[:4000]

def classify_email_with_gemini(email_text):
    if not model:
        return {'error': 'O modelo de IA não foi inicializado corretamente.'}, 500

    processed_text = preprocess_text(email_text)

    prompt = f"""
    Sua tarefa é analisar um email e retornar um objeto JSON com duas chaves: "classification" e "reply".

    Definições de Classificação:
    - Produtivo: Requer uma ação de trabalho específica, é uma solicitação de negócio ou uma atualização crítica de projeto.
    - Improdutivo: É uma conversa pessoal, ofensa, spam, marketing, cortesia, ou um assunto não relacionado ao trabalho direto.

    Diretrizes para a Resposta ('reply'):
    - A resposta deve ser em português, breve, profissional e adequada ao conteúdo do email.
    - Para emails produtivos, confirme o recebimento e informe que a equipe está analisando.
    - Para emails improdutivos, use uma resposta genérica de agradecimento ou, se for ofensivo, uma resposta neutra.

    Analise os exemplos a seguir para entender o formato de saída JSON:
    ---
    Exemplo 1:
    Email: "Olá, poderiam me dar uma atualização sobre o status do projeto Alpha? Precisamos apresentar os resultados amanhã."
    Resposta JSON: {{"classification": "Produtivo", "reply": "Olá! Recebemos sua solicitação de status sobre o projeto Alpha e retornaremos em breve com as informações."}}

    Exemplo 2:
    Email: "babaca, seu serviço é um lixo"
    Resposta JSON: {{"classification": "Improdutivo", "reply": "Agradecemos o seu feedback. Sua mensagem foi registrada."}}

    Exemplo 3:
    Email: "Muito obrigado pela ajuda de ontem, foi excelente!"
    Resposta JSON: {{"classification": "Improdutivo", "reply": "Agradecemos o seu contato e ficamos felizes em ajudar!"}}
    ---

    Agora, analise o seguinte email e forneça sua resposta APENAS no formato de um objeto JSON válido.

    Email: "{processed_text}"
    Resposta JSON:
    """

    try:
        response = model.generate_content(prompt)
        
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        
        result_json = json.loads(cleaned_response_text)
        
        classification = result_json.get('classification', 'Improdutivo')
        suggested_reply = result_json.get('reply', 'Agradecemos o contato.')

        return {
            'classification': classification,
            'suggested_reply': suggested_reply,
            'debug_info': { 'best_label_found': 'Análise por Gemini' }
        }, 200

    except (json.JSONDecodeError, AttributeError, Exception) as e:
        # Fallback para o método antigo se a IA não retornar um JSON válido
        return {
            'classification': 'Improdutivo',
            'suggested_reply': 'Agradecemos o seu contato. Esta mensagem foi processada automaticamente.',
            'debug_info': {'best_label_found': f'Fallback de Emergência: {e}'}
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
        
        result, status_code = classify_email_with_gemini(email_text)
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro ao processar sua solicitação: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)