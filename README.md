# Translator App

A web application for translating text using OpenAI GPT-4 API with multiple translation modes.

## Features

- **Multiple Translation Modes:**
  - **Formal**: Professional and formal Vietnamese suitable for business documents
  - **Casual**: Everyday conversational Vietnamese for informal communication
  - **Technical**: Technical Vietnamese with specialized terminology for technical documents
  - **Creative**: Creative and expressive Vietnamese for artistic and creative content
- **OpenAI GPT-4 Integration**: High-quality translations using OpenAI's latest model
- **Fallback Support**: Legacy GPT API endpoint for backup
- **RESTful API**: Clean API endpoints for integration
- **Modern Web Interface**: Responsive frontend with real-time translation

## Prerequisites

- Node.js (v14 or higher)
- OpenAI API key

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/khanhct/translator.git
   cd translator
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure OpenAI API:**
   
   Create a `.env` file in the root directory:
   ```bash
   # OpenAI API Configuration
   OPENAI_API_KEY=your-actual-openai-api-key-here
   
   # Server Configuration (optional)
   PORT=3000
   ```
   
   **Get your OpenAI API key:**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key and paste it in your `.env` file

4. **Start the application:**
   ```bash
   # Development mode with auto-reload
   npm run dev
   
   # Production mode
   npm start
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

## API Endpoints

### Get Available Translation Modes
```
GET /api/modes
```
Returns all available translation modes with descriptions.

### Translate Text (OpenAI)
```
POST /api/translate
```
**Body:**
```json
{
  "text": "Text to translate",
  "targetLanguage": "vietnamese",
  "mode": "formal"
}
```

**Available modes:** `formal`, `casual`, `technical`, `creative`

### Translate Text (Legacy GPT API)
```
POST /api/translate/legacy
```
**Body:**
```json
{
  "text": "Text to translate",
  "targetLanguage": "vietnamese"
}
```

## Translation Modes

### Formal Mode
- **Use case**: Business documents, legal documents, professional communications
- **Style**: Professional and formal Vietnamese vocabulary and grammar
- **Output**: Clean, professional formatting suitable for document use

### Casual Mode
- **Use case**: Informal communication, social media, casual conversations
- **Style**: Natural, conversational Vietnamese vocabulary and grammar
- **Output**: Easy-to-read, natural language

### Technical Mode
- **Use case**: Technical documents, manuals, professional technical communications
- **Style**: Technical Vietnamese vocabulary and terminology
- **Output**: Technically accurate with specialized terminology

### Creative Mode
- **Use case**: Artistic content, creative writing, expressive communications
- **Style**: Creative and expressive Vietnamese vocabulary and grammar
- **Output**: Engaging and artistic tone preservation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `PORT` | Server port number | 3000 |

## Error Handling

The API includes comprehensive error handling for:
- Invalid API keys
- Rate limiting
- Network errors
- Invalid translation modes
- Missing text input

## Development

- **Auto-reload**: Uses nodemon for development
- **CORS enabled**: For frontend integration
- **Static file serving**: Frontend files served from `public/` directory

## Security Notes

- Never commit your `.env` file (already in .gitignore)
- Keep your OpenAI API key secure
- Consider implementing rate limiting for production use

## License

ISC 