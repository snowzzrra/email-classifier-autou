document.addEventListener('DOMContentLoaded', function() {
    // Inicializa todas as funcionalidades do frontend
    initTheme();
    initTutorial();
    initExampleButtons();
    initCopyButton();
    loadHistory();

    const form = document.getElementById('email-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

// --- LÓGICA DO TEMA (MODO ESCURO) ---
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = '<i class="bi bi-sun-fill"></i>';
    const moonIcon = '<i class="bi bi-moon-fill"></i>';

    // Aplica o tema salvo no localStorage ao carregar a página
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = sunIcon;
    } else {
        themeToggle.innerHTML = moonIcon;
    }

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        // Salva a preferência do usuário
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = sunIcon;
        } else {
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = moonIcon;
        }
    });
}

// --- LÓGICA DO TUTORIAL DE PRIMEIRA VISITA ---
function initTutorial() {
    if (!localStorage.getItem('hasSeenTutorial')) {
        const tutorialModal = new bootstrap.Modal(document.getElementById('tutorial-modal'));
        tutorialModal.show();
        // Marca que o tutorial foi visto para não mostrar novamente
        localStorage.setItem('hasSeenTutorial', 'true');
    }
}

// --- LÓGICA DOS BOTÕES DE EXEMPLO ---
function initExampleButtons() {
    const emailText = document.getElementById('email-text');
    document.getElementById('load-example-prod').addEventListener('click', () => {
        emailText.value = "Prezados, poderiam por gentileza verificar o status do ticket #8451? Precisamos de uma atualização para alinhar com o cliente final o mais rápido possível. Obrigado.";
    });
    document.getElementById('load-example-improd').addEventListener('click', () => {
        emailText.value = "Só passando para desejar a todos um excelente final de semana! Se cuidem!";
    });
}

// --- LÓGICA DO BOTÃO DE COPIAR ---
function initCopyButton() {
    const copyBtn = document.getElementById('copy-reply-btn');
    copyBtn.addEventListener('click', () => {
        const replyText = document.getElementById('suggested-reply').textContent;
        navigator.clipboard.writeText(replyText).then(() => {
            // Feedback visual para o usuário
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';
            copyBtn.classList.add('btn-success');
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('btn-success');
            }, 2000);
        });
    });
}

// --- FUNÇÃO PRINCIPAL DO FORMULÁRIO ---
async function handleFormSubmit(event) {
    event.preventDefault();
    hideError();

    const activeTab = document.querySelector('#input-type-tabs .nav-link.active').getAttribute('data-bs-target');
    let fetchOptions;
    let textForHistory = "";

    if (activeTab === '#text-input-pane') {
        const emailText = document.getElementById('email-text').value;
        if (!emailText.trim()) {
            displayError('Por favor, insira o texto do email.');
            return;
        }
        textForHistory = emailText;
        fetchOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email_text: emailText })
        };
    } else {
        const fileInput = document.getElementById('email-file');
        const file = fileInput.files[0];
        if (!file) {
            displayError('Por favor, selecione um arquivo.');
            return;
        }
        textForHistory = `Arquivo: ${file.name}`; // Fallback inicial
        const formData = new FormData();
        formData.append('file', file);
        fetchOptions = { method: 'POST', body: formData };
    }

    setLoadingState(true);
    document.getElementById('results-card').style.display = 'none';

    try {
        const response = await fetch('/classify', fetchOptions);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `Erro ${response.status}: Ocorreu um problema no servidor.`);
        }
        
        displayResults(result);
        const textToSave = result.processed_text || textForHistory;
        saveToHistory(result, textToSave);

    } catch (error) {
        displayError('Erro: ' + error.message);
    } finally {
        setLoadingState(false);
    }
}

function displayResults(result) {
    const resultsCard = document.getElementById('results-card');
    const classificationResult = document.getElementById('classification-result');
    const suggestedReply = document.getElementById('suggested-reply');

    classificationResult.textContent = result.classification;
    classificationResult.className = result.classification === 'Produtivo' ? 'badge bg-success' : 'badge bg-warning text-dark';
    suggestedReply.textContent = result.suggested_reply;

    resultsCard.style.display = 'block';
}

// --- Funções de Estado, Erro e Histórico ---
function setLoadingState(isLoading) {
    const submitButton = document.querySelector('#email-form button[type="submit"]');
    const spinner = submitButton.querySelector('.spinner-border');
    const buttonText = submitButton.querySelector('.button-text');
    if(submitButton) {
        spinner.style.display = isLoading ? 'inline-block' : 'none';
        buttonText.textContent = isLoading ? 'Processando...' : 'Classificar';
        submitButton.disabled = isLoading;
    }
}

function displayError(message) {
    const errorAlert = document.getElementById('error-alert');
    errorAlert.textContent = message;
    errorAlert.style.display = 'block';
}

function hideError() {
    const errorAlert = document.getElementById('error-alert');
    errorAlert.style.display = 'none';
}

const HISTORY_KEY = 'emailClassificationHistory';

function saveToHistory(result, originalText) {
    let history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
    let textSnippet = originalText.substring(0, 100);
    if (originalText.length > 100) textSnippet += '...';
    
    const newEntry = {
        classification: result.classification,
        snippet: textSnippet,
        timestamp: new Date().toLocaleString('pt-BR')
    };

    history.unshift(newEntry);
    history = history.slice(0, 10);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    loadHistory();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
    const historyList = document.getElementById('history-list');
    const historyCard = document.getElementById('history-card');
    
    historyList.innerHTML = '';
    if (history.length === 0) {
        historyCard.style.display = 'none';
        return;
    }

    history.forEach(item => {
        const badgeClass = item.classification === 'Produtivo' ? 'bg-success' : 'bg-warning text-dark';
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <p class="mb-1 fst-italic">"${item.snippet}"</p>
                <small class="text-muted text-nowrap ms-3">${item.timestamp}</small>
            </div>
            <span class="badge ${badgeClass}">${item.classification}</span>
        `;
        historyList.appendChild(li);
    });
    historyCard.style.display = 'block';
}

function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    loadHistory();
}