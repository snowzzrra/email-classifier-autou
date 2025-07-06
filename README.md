# Classificador de Emails com IA - Desafio AutoU

## Visão Geral do Projeto

Esta é uma aplicação web desenvolvida como solução para o **Case Prático do processo seletivo da AutoU**. O objetivo é resolver um problema real enfrentado por empresas do setor financeiro: o alto volume de emails diários. A ferramenta utiliza Inteligência Artificial para automatizar a classificação de emails em **"Produtivo"** ou **"Improdutivo"** e, mais importante, gerar respostas personalizadas e adequadas para cada caso, otimizando o fluxo de trabalho e liberando tempo da equipe.

O projeto foi construído com foco na precisão da IA, na qualidade técnica do código e, principalmente, em uma experiência de usuário fluida e intuitiva.

---

## Links

* **Acesse a Aplicação Online:** **[LINK AQUI](https://email-classifier-autou.vercel.app/)**
* **Assista ao Vídeo Demonstrativo:** **[LINK AQUI](https://youtu.be/4n-UFggU300)**

---

## Funcionalidades Principais

* **Classificação Inteligente:** Distingue emails que exigem ação (Produtivos) daqueles que não (Improdutivos) usando um modelo de linguagem avançado.
* **Geração de Respostas Personalizadas:** A IA cria uma sugestão de resposta breve e profissional, adaptada ao contexto do email recebido.
* **Múltiplas Formas de Entrada:** Suporte para colar texto diretamente na interface ou fazer upload de arquivos `.txt` e `.pdf`.
* **Interface Rica e Intuitiva:**
    * **Modo Escuro:** Para maior conforto visual do usuário.
    * **Tutorial de Primeira Visita:** Um popup explica o funcionamento da ferramenta para novos usuários.
    * **Botões de Exemplo:** Permitem testar a aplicação rapidamente com exemplos pré-definidos.
    * **Botão "Copiar":** Facilita o uso da resposta sugerida com um único clique.
* **Histórico de Análises:** As últimas classificações ficam salvas localmente no navegador para referência futura.

---

## Tecnologias Utilizadas

* **Backend:**
    * **Python 3.10+**
    * **Flask:** Micro-framework web para servir a aplicação e a API.
    * **Google Generative AI (Gemini 1.5 Flash):** API do modelo de linguagem grande para a lógica de classificação e geração de resposta.
    * **PyPDF2:** Biblioteca para extração de texto de arquivos PDF.
    * **python-dotenv:** Para gerenciamento de variáveis de ambiente.
* **Frontend:**
    * **HTML5, CSS3, JavaScript (ES6+)**
    * **Bootstrap 5:** Para a criação de uma interface responsiva e moderna.
    * **Bootstrap Icons:** Para os ícones da interface.
* **Hospedagem:**
    * A aplicação está hospedada na plataforma Vercel.

---

## Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar a aplicação em seu ambiente local.

### Pré-requisitos

* Python 3.10 ou superior
* `pip` (gerenciador de pacotes do Python)
* Git

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/snowzzrra/email-classifier-autou
    cd email-classifier
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure as Variáveis de Ambiente:**
    * Crie um arquivo chamado `.env` na raiz do projeto.
    * Dentro deste arquivo, adicione sua chave da API do Google AI Studio:
        ```
        GOOGLE_API_KEY="AIzaSy...[SUA_CHAVE_AQUI]"
        ```
    * *Nota: A chave da API pode ser obtida gratuitamente no [Google AI Studio](https://aistudio.google.com/).*

4.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
    * A aplicação estará disponível em `http://127.0.0.1:5000` no seu navegador.

---

## Decisões Técnicas e Evolução do Projeto

1.  **Abordagem Inicial e Limitações:**
    * O desenvolvimento começou utilizando modelos de classificação Zero-Shot da Hugging Face.
    * No entanto, ao testar com exemplos mais complexos, o modelo se tornou inconsistente, errando em aproximadamente 20% dos testes.

2.  **Mudança para um Modelo de Linguagem Grande (LLM):**
    * Percebendo os limites da abordagem inicial, tomei a decisão estratégica de pivotar para uma tecnologia mais avançada: um LLM (Large Language Model), especificamente o **Gemini 1.5 Flash** do Google.
    * A vantagem fundamental desta abordagem é a capacidade do modelo de raciocinar e seguir instruções complexas.

3.  **Técnica de "Few-Shot Prompting":**
    * O uso de few-shot prompting foi a chave para o sucesso. Em vez de apenas enviar o email para a IA, eu construí um *prompt* detalhado que inclui:
        * A definição clara das categorias "Produtivo" e "Improdutivo".
        * Instruções para gerar uma resposta personalizada em formato JSON.

4.  **Decisão sobre o Pré-processamento NLP Clássico:**
    * O desafio mencionava o uso de técnicas como *stemming* e remoção de *stopwords*. Embora eu tenha o conhecimento para implementá-las, tomei a decisão técnica de **não aplicá-las** no texto final enviado ao Gemini.
    * **Motivo:** LLMs modernos como o Gemini extraem um contexto muito mais rico e preciso de frases completas. A remoção de palavras ou a alteração de seus radicais poderia degradar a performance da análise de intenção. Esta escolha demonstra a compreensão de quando aplicar técnicas tradicionais versus quando confiar na capacidade de modelos de ponta.