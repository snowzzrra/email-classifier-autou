document.addEventListener('DOMContentLoaded', function() {
    loadHistory();

    const form = document.getElementById('email-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

async function handleFormSubmit(event) {
    event.preventDefault();
    hideError(); // Esconde erros antigos

    const submitButton = this.querySelector('button[type="submit"]');
    const activeTab = document.querySelector('#input-type-tabs .nav-link.active').getAttribute('data-bs-target');
    let fetchOptions;
    let textForHistory = "";

    if (activeTab === '#text-input-pane') {
        const emailText = document.getElementById('email-text').value;
        textForHistory = emailText;
        if (!emailText.trim()) {
            displayError('Por favor, insira o texto do email.');
            return;
        }
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
        textForHistory = `Arquivo: ${file.name}`;
        const formData = new FormData();
        formData.append('file', file);
        fetchOptions = {
            method: 'POST',
            body: formData
        };
    }

    setLoadingState(true);
    document.getElementById('results-card').style.display = 'none';

    try {
        const response = await fetch('/classify', fetchOptions);
        const result = await response.json();

        if (!response.ok) {
            // Lança um erro para ser pego pelo bloco catch
            throw new Error(result.error || `Erro ${response.status}: Ocorreu um problema no servidor.`);
        }
        
        displayResults(result);
        saveToHistory(result, textForHistory);

    } catch (error) {
        displayError('Erro: ' + error.message);
    } finally {
        setLoadingState(false);
    }
}

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

function displayResults(result) {
    const resultsCard = document.getElementById('results-card');
    const classificationResult = document.getElementById('classification-result');
    const suggestedReply = document.getElementById('suggested-reply');
    const debugLabel = document.getElementById('debug-label');
    const confidenceBar = document.getElementById('confidence-bar');

    // Preenche os resultados principais
    classificationResult.textContent = result.classification;
    classificationResult.className = result.classification === 'Produtivo' ? 'badge bg-success' : 'badge bg-warning text-dark';
    suggestedReply.textContent = result.suggested_reply;

    // Preenche os detalhes da análise (confiança, etc.)
    if (result.debug_info) {
        const scorePercent = (result.debug_info.score * 100).toFixed(0);
        debugLabel.textContent = `"${result.debug_info.best_label_found}"`;
        
        confidenceBar.style.width = `${scorePercent}%`;
        confidenceBar.textContent = `${scorePercent}%`;
        confidenceBar.setAttribute('aria-valuenow', scorePercent);

        // Muda a cor da barra de progresso com base na confiança
        let barClass = 'progress-bar ';
        if (scorePercent > 75) barClass += 'bg-success';
        else if (scorePercent > 40) barClass += 'bg-warning text-dark';
        else barClass += 'bg-danger';
        confidenceBar.className = barClass;
    }

    resultsCard.style.display = 'block';
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
        timestamp: new Date().toLocaleString('pt-BR'),
        debug_info: result.debug_info // Salva as informações de debug
    };

    history.unshift(newEntry);
    history = history.slice(0, 10); // Aumentei para 10 itens no histórico

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
        let debugInfoHtml = '';
        if (item.debug_info) {
            const scorePercent = (item.debug_info.score * 100).toFixed(0);
            debugInfoHtml = `
                <small class="text-muted d-block mt-1">
                    Confiança: <strong>${scorePercent}%</strong> | Motivo: <em>"${item.debug_info.best_label_found}"</em>
                </small>
            `;
        }

        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <p class="mb-1 fst-italic">"${item.snippet}"</p>
                <small class="text-muted text-nowrap ms-3">${item.timestamp}</small>
            </div>
            <div>
                <span class="badge ${badgeClass}">${item.classification}</span>
                ${debugInfoHtml}
            </div>
        `;
        historyList.appendChild(li);
    });

    historyCard.style.display = 'block';
}

function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    loadHistory();
}