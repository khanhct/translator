// DOM Elements
const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const translateBtn = document.getElementById('translateBtn');
const copyBtn = document.getElementById('copyBtn');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const notification = document.getElementById('notification');

// Event Listeners
translateBtn.addEventListener('click', translateText);
copyBtn.addEventListener('click', copyToClipboard);
clearBtn.addEventListener('click', clearText);
inputText.addEventListener('input', handleInputChange);

// Handle Enter key for translation (Ctrl+Enter)
inputText.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        translateText();
    }
});

// Functions
function handleInputChange() {
    const hasText = inputText.value.trim().length > 0;
    translateBtn.disabled = !hasText;
}

async function translateText() {
    const text = inputText.value.trim();
    
    if (!text) {
        showNotification('Please enter some text to translate', 'error');
        return;
    }

    // Show loading state
    showLoading(true);
    translateBtn.disabled = true;
    outputText.value = '';
    copyBtn.disabled = true;

    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (data.success) {
            outputText.value = data.translatedText;
            copyBtn.disabled = false;
            showNotification('Translation completed successfully!', 'success');
        } else {
            throw new Error(data.message || 'Translation failed');
        }

    } catch (error) {
        console.error('Translation error:', error);
        showNotification(`Translation failed: ${error.message}`, 'error');
        outputText.value = 'Translation failed. Please try again.';
    } finally {
        showLoading(false);
        translateBtn.disabled = false;
    }
}

async function copyToClipboard() {
    const text = outputText.value;
    
    if (!text) {
        showNotification('No text to copy', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showNotification('Text copied to clipboard!', 'success');
        
        // Visual feedback
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
        }, 2000);

    } catch (error) {
        console.error('Copy failed:', error);
        
        // Fallback for older browsers
        try {
            outputText.select();
            document.execCommand('copy');
            showNotification('Text copied to clipboard!', 'success');
        } catch (fallbackError) {
            showNotification('Failed to copy text', 'error');
        }
    }
}

function clearText() {
    inputText.value = '';
    outputText.value = '';
    copyBtn.disabled = true;
    translateBtn.disabled = true;
    inputText.focus();
    showNotification('Text cleared', 'success');
}

function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');

    // Auto hide after 3 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    inputText.focus();
    translateBtn.disabled = true;
    copyBtn.disabled = true;
    
    // Add keyboard shortcut info
    const shortcuts = document.createElement('div');
    shortcuts.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: rgba(255,255,255,0.9);
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 12px;
        color: #666;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    `;
    shortcuts.innerHTML = '<strong>Tip:</strong> Press Ctrl+Enter to translate';
    document.body.appendChild(shortcuts);
}); 