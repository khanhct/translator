const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Translation endpoint
app.post('/api/translate', async (req, res) => {
    try {
        const { text, targetLanguage = 'vietnamese' } = req.body;
        
        if (!text) {
            return res.status(400).json({ error: 'Text is required' });
        }

        const response = await axios.post('https://gpt-api.niteco.se/api/chat-completion', {
            model: "gpt-4.1",
            messages: [
                { 
                    role: "system", 
                    content: "You are a professional translator. Translate the text to Vietnamese with proper formatting suitable for document use. Rules: 1) Return ONLY the translated text without explanations or prefixes 2) Maintain proper paragraph breaks and sentence structure 3) Use appropriate punctuation and spacing 4) Format the output to be clean and professional for copying to document files 5) Preserve any original text structure (bullets, lists, etc.) in Vietnamese format 6) If there are keywords in parentheses ( ), keep the keywords in parentheses in the translation to help understand more."
                },
                { 
                    role: "user", 
                    content: `Translate this text to Vietnamese: ${text}` 
                }
            ],
            stream: false
        }, {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': '0abccf10-6e8f-11f0-85e5-330c35ef9772'
            }
        });

        const translatedText = response.data.content;
        
        res.json({ 
            success: true, 
            originalText: text,
            translatedText: translatedText,
            targetLanguage: targetLanguage
        });

    } catch (error) {
        console.error('Translation error:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Translation failed', 
            message: error.response?.data?.error || error.message 
        });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Translation app is running on http://localhost:${PORT}`);
}); 