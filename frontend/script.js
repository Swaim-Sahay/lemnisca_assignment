let conversationId = null;

const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const sendBtn = document.getElementById('send-btn');
const convIdDisplay = document.getElementById('conv-id-display');

// Debug Panel Elements
const statModel = document.getElementById('debug-model');
const statClassification = document.getElementById('debug-classification');
const statLatency = document.getElementById('debug-latency');
const statInTokens = document.getElementById('debug-in-tokens');
const statOutTokens = document.getElementById('debug-out-tokens');
const statChunks = document.getElementById('debug-chunks');
const statFlags = document.getElementById('debug-flags');
const statusIndicator = document.querySelector('.status-indicator');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    appendMessage(text, 'user');
    userInput.value = '';

    // Add loading indicator
    const loadingId = appendLoading();

    try {
        statusIndicator.classList.remove('active');
        statusIndicator.style.backgroundColor = 'var(--accent-yellow)';
        sendBtn.disabled = true;

        const body = { question: text };
        if (conversationId) {
            body.conversation_id = conversationId;
        }

        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        // Remove loading
        document.getElementById(loadingId).remove();

        if (!response.ok) {
            appendMessage(`Error: ${data.detail || 'Something went wrong.'}`, 'assistant');
            return;
        }

        conversationId = data.conversation_id;
        convIdDisplay.textContent = `Conversation: ...${conversationId.slice(-6)}`;

        // Update Debug Panel
        updateDebugPanel(data.metadata);

        // Add assistant message
        appendMessage(data.answer, 'assistant', data);

    } catch (err) {
        document.getElementById(loadingId).remove();
        appendMessage(`Connection error: ${err.message}`, 'assistant');
    } finally {
        statusIndicator.classList.add('active');
        statusIndicator.style.backgroundColor = '';
        sendBtn.disabled = false;
        userInput.focus();
    }
});

function appendMessage(text, sender, fullData = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;

    const avatar = sender === 'user' ? '👤' : '🤖';

    let contentHtml = `<div class="text">${escapeHTML(text).replace(/\n/g, '<br>')}</div>`;

    // Handle Warning Banner based on evaluator flags
    if (sender === 'assistant' && fullData?.metadata?.evaluator_flags?.length > 0) {
        contentHtml += `
            <div class="warning-banner">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <span>Low confidence — please verify with support.</span>
            </div>
        `;
    }

    // Handle Sources
    if (sender === 'assistant' && fullData && fullData.sources.length > 0) {
        const uniqueDocs = [...new Set(fullData.sources.map(s => s.document))];
        const sourceTags = uniqueDocs.map(d => `<span class="source-tag">${d}</span>`).join('');
        contentHtml += `<div class="sources-container">Sources: ${sourceTags}</div>`;
    }

    msgDiv.innerHTML = `
        <div class="avatar">${avatar}</div>
        <div class="message-content">${contentHtml}</div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendLoading() {
    const id = 'loading-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = `message assistant-message`;
    msgDiv.id = id;

    msgDiv.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function updateDebugPanel(meta) {
    statModel.textContent = meta.model_used.includes('70b') ? '70B Versatile' : '8B Instant';
    statClassification.textContent = meta.classification.toUpperCase();

    // Color code classification
    statClassification.style.color = meta.classification === 'complex' ? 'var(--primary)' : 'var(--accent-green)';

    statLatency.textContent = `${meta.latency_ms} ms`;
    statInTokens.textContent = meta.tokens.input;
    statOutTokens.textContent = meta.tokens.output;
    statChunks.textContent = meta.chunks_retrieved;

    // Update Flags
    statFlags.innerHTML = '';
    if (meta.evaluator_flags.length === 0) {
        statFlags.innerHTML = '<span class="flag none">None</span>';
    } else {
        meta.evaluator_flags.forEach(flag => {
            const span = document.createElement('span');
            span.className = 'flag evaluator-flag';
            span.textContent = flag;
            statFlags.appendChild(span);
        });
    }
}

function escapeHTML(str) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(str));
    return p.innerHTML;
}
