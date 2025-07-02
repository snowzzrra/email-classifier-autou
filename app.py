import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PyPDF2 import PdfReader

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
    Sua tarefa é classificar um email como 'Produtivo' ou 'Improdutivo'.

    Definições:
    - Produtivo: Requer uma ação de trabalho específica, é uma solicitação de negócio ou uma atualização crítica de projeto.
    - Improdutivo: É uma conversa pessoal, ofensa, spam, marketing, cortesia, ou um assunto não relacionado ao trabalho direto.

    Analise os seguintes exemplos para entender o contexto:

    ---
    Exemplo 1:
    Email: "E aí, mano, beleza? Manda aquele relatório de vendas pra mim assim que der, valeu! Abraço."
    Classificação: Produtivo

    Exemplo 2:
    Email: "filho da puta, eu te odeio"
    Classificação: Improdutivo

    Exemplo 3:
    Email: "O ar condicionado do nosso andar está quebrado de novo, está impossível se concentrar com este calor."
    Classificação: Improdutivo

    Exemplo 4:
    Email: "Pessoal, estou vendendo meu monitor antigo, se alguém tiver interesse me avisa."
    Classificação: Improdutivo

    Exemplo 5:
    Email: "Francamente, não gostei nada da primeira versão do texto. Por favor, refaçam do zero seguindo o briefing."
    Classificação: Produtivo
    ---

    Agora, classifique o seguinte email. Responda APENAS com a palavra 'Produtivo' ou 'Improdutivo'.

    Email: "{processed_text}"
    Classificação:
    """

    try:
        response = model.generate_content(prompt)
        classification = response.text.strip()

        if classification not in ['Produtivo', 'Improdutivo']:
             classification = "Improdutivo"

        suggested_reply = ""
        if classification == "Produtivo":
            suggested_reply = "Olá! Recebemos sua solicitação e nossa equipe já está analisando. Retornaremos o mais breve possível."
        else:
            suggested_reply = "Agradecemos o seu contato. Esta mensagem foi processada automaticamente."
        
        return {
            'classification': classification,
            'suggested_reply': suggested_reply,
            'debug_info': {
                'best_label_found': f"Análise por Gemini",
                'score': 1.0 # A confiança é alta com este método
            }
        }, 200

    except Exception as e:
        return {'error': f'Ocorreu um erro na API do Gemini: {str(e)}'}, 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_email():
    email_text = ""
    try:
        if 'file' in request.files:
            file = request.files['file']
            # ... (seu código de leitura de arquivo .txt e .pdf continua o mesmo)
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
        
        # A chamada para a função de classificação foi renomeada
        result, status_code = classify_email_with_gemini(email_text)
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro ao processar sua solicitação: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)