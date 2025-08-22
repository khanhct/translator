// Load environment variables
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// OpenAI API configuration
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'your-openai-api-key-here';
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

// Translation modes configuration
const TRANSLATION_MODES = {
    formal: {
        name: 'Formal',
        description: 'Professional and formal Vietnamese suitable for business documents',
        systemPrompt: 'You are a professional translator specializing in formal Vietnamese translations. Translate the text to Vietnamese with proper formal language suitable for business documents, legal documents, and professional communications. Rules: 1) Return ONLY the translated text without explanations or prefixes 2) Use formal Vietnamese vocabulary and grammar 3) Maintain proper paragraph breaks and sentence structure 4) Use appropriate punctuation and spacing 5) Format the output to be clean and professional for copying to document files 6) Preserve any original text structure (bullets, lists, etc.) in Vietnamese format 7) If there are keywords in parentheses ( ), keep the keywords in parentheses in the translation to help understand more.'
    },
    casual: {
        name: 'Casual',
        description: 'Everyday conversational Vietnamese for informal communication',
        systemPrompt: 'You are a professional translator specializing in casual Vietnamese translations. Translate the text to Vietnamese using everyday conversational language suitable for informal communication, social media, and casual conversations. Rules: 1) Return ONLY the translated text without explanations or prefixes 2) Use natural, conversational Vietnamese vocabulary and grammar 3) Maintain proper paragraph breaks and sentence structure 4) Use appropriate punctuation and spacing 5) Format the output to be clean and easy to read 6) Preserve any original text structure (bullets, lists, etc.) in Vietnamese format 7) If there are keywords in parentheses ( ), keep the keywords in parentheses in the translation to help understand more.'
    },
    technical: {
        name: 'Technical',
        description: 'Technical Vietnamese with specialized terminology for technical documents',
        systemPrompt: 'You are a professional translator specializing in technical Vietnamese translations. Translate the text to Vietnamese using appropriate technical terminology and language suitable for technical documents, manuals, and professional technical communications. Rules: 1) Return ONLY the translated text without explanations or prefixes 2) Use appropriate technical Vietnamese vocabulary and terminology 3) Maintain proper paragraph breaks and sentence structure 4) Use appropriate punctuation and spacing 5) Format the output to be clean and professional for technical documentation 6) Preserve any original text structure (bullets, lists, etc.) in Vietnamese format 7) If there are keywords in parentheses ( ), keep the keywords in parentheses in the translation to help understand more 8) Maintain technical accuracy and precision.'
    },
    creative: {
        name: 'Creative',
        description: 'Creative and expressive Vietnamese for artistic and creative content',
        systemPrompt: 'You are a professional translator specializing in creative Vietnamese translations. Translate the text to Vietnamese using creative and expressive language suitable for artistic content, creative writing, and expressive communications. Rules: 1) Return ONLY the translated text without explanations or prefixes 2) Use creative and expressive Vietnamese vocabulary and grammar 3) Maintain proper paragraph breaks and sentence structure 4) Use appropriate punctuation and spacing 5) Format the output to be clean and engaging 6) Preserve any original text structure (bullets, lists, etc.) in Vietnamese format 7) If there are keywords in parentheses ( ), keep the keywords in parentheses in the translation to help understand more 8) Maintain the creative and artistic tone of the original text.'
    }
};

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Get available translation modes
app.get('/api/modes', (req, res) => {
    res.json({
        success: true,
        modes: Object.keys(TRANSLATION_MODES).map(key => ({
            id: key,
            ...TRANSLATION_MODES[key]
        }))
    });
});

// Translation endpoint with mode support
app.post('/api/translate', async (req, res) => {
    try {
        const { text, targetLanguage = 'vietnamese', mode = 'formal' } = req.body;
        
        if (!text) {
            return res.status(400).json({ error: 'Text is required' });
        }

        // Validate mode
        if (!TRANSLATION_MODES[mode]) {
            return res.status(400).json({ 
                error: 'Invalid mode', 
                availableModes: Object.keys(TRANSLATION_MODES) 
            });
        }

        const selectedMode = TRANSLATION_MODES[mode];

        // Use OpenAI API for translation
        const response = await axios.post(OPENAI_API_URL, {
            model: "gpt-4",
            messages: [
                { 
                    role: "system", 
                    content: selectedMode.systemPrompt
                },
                { 
                    role: "user", 
                    content: `Translate this text to Vietnamese: ${text}` 
                }
            ],
            temperature: 0.3,
            max_tokens: 2000
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            }
        });

        const translatedText = response.data.choices[0].message.content;
        
        res.json({ 
            success: true, 
            originalText: text,
            translatedText: translatedText,
            targetLanguage: targetLanguage,
            mode: mode,
            modeName: selectedMode.name,
            modeDescription: selectedMode.description
        });

    } catch (error) {
        console.error('Translation error:', error.response?.data || error.message);
        
        // Handle OpenAI API errors specifically
        if (error.response?.status === 401) {
            return res.status(401).json({ 
                error: 'OpenAI API key is invalid or missing',
                message: 'Please check your OpenAI API key configuration'
            });
        }
        
        if (error.response?.status === 429) {
            return res.status(429).json({ 
                error: 'OpenAI API rate limit exceeded',
                message: 'Please try again later or upgrade your OpenAI plan'
            });
        }

        res.status(500).json({ 
            error: 'Translation failed', 
            message: error.response?.data?.error?.message || error.message 
        });
    }
});

// Fallback to original GPT API endpoint
app.post('/api/translate/legacy', async (req, res) => {
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
            targetLanguage: targetLanguage,
            mode: 'legacy'
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
    console.log(`Available translation modes: ${Object.keys(TRANSLATION_MODES).join(', ')}`);
    console.log(`OpenAI API configured: ${OPENAI_API_KEY !== 'your-openai-api-key-here' ? 'Yes' : 'No (using placeholder)'}`);
}); 