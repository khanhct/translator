# Text Translator Web App

A modern, responsive web application for translating text to Vietnamese using GPT-4.1 AI translation API.

## Features

- **Clean Interface**: Modern and intuitive user interface with responsive design
- **Real-time Translation**: Translate text to Vietnamese using GPT-4.1 API
- **Copy Functionality**: One-click copy of translated text to clipboard
- **Keyboard Shortcuts**: Use Ctrl+Enter to quickly translate text
- **Loading States**: Visual feedback during translation process
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

## Technology Stack

- **Backend**: Node.js with Express.js
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **API Integration**: Axios for HTTP requests
- **Styling**: Modern CSS with gradients and animations
- **Icons**: Font Awesome icons

## Prerequisites

- Node.js (version 14 or higher)
- npm (Node Package Manager)

## Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd translator-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the application**
   ```bash
   # For production
   npm start
   
   # For development (with auto-restart)
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## Usage

1. **Enter Text**: Type or paste the text you want to translate in the input box
2. **Translate**: Click the "Translate" button or press `Ctrl+Enter`
3. **Copy Result**: Click the "Copy Result" button to copy the translation to your clipboard
4. **Clear**: Use the "Clear" button to reset both input and output fields

## API Configuration

The application uses the GPT-4.1 translation API with the following configuration:

- **Endpoint**: `https://gpt-api.niteco.se/api/chat-completion`
- **API Key**: Pre-configured (replace in `server.js` if needed)
- **Model**: GPT-4.1
- **Target Language**: Vietnamese

To modify the API configuration, edit the `server.js` file:

```javascript
// Update API endpoint or headers
const response = await axios.post('YOUR_API_ENDPOINT', {
    model: "gpt-4.1",
    messages: [{ role: "user", content: prompt }],
    stream: false
}, {
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'YOUR_API_KEY'
    }
});
```

## Project Structure

```
translator-app/
├── package.json          # Dependencies and scripts
├── server.js            # Express.js server and API routes
├── README.md            # Project documentation
└── public/              # Static files
    ├── index.html       # Main HTML file
    ├── styles.css       # CSS styling
    └── script.js        # Frontend JavaScript
```

## Features in Detail

### User Interface
- Gradient background with modern design
- Card-based layout for input and output sections
- Hover effects and smooth animations
- Responsive grid layout that adapts to screen size

### Functionality
- Input validation to ensure text is provided
- Loading spinner during API calls
- Success/error notifications
- Disabled states for better UX
- Keyboard shortcut support

### Error Handling
- Network error handling
- API error responses
- User-friendly error messages
- Graceful fallbacks for clipboard functionality

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

## Development

To modify the application:

1. **Backend changes**: Edit `server.js` for API routes and server configuration
2. **Frontend styling**: Edit `public/styles.css` for visual changes
3. **Frontend functionality**: Edit `public/script.js` for interactive features
4. **UI structure**: Edit `public/index.html` for layout changes

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `server.js`: `const PORT = process.env.PORT || 3001;`

2. **API key errors**
   - Verify the API key in `server.js` is correct
   - Check if the API endpoint is accessible

3. **Copy function not working**
   - Ensure HTTPS is enabled for clipboard API (or use localhost)
   - The app includes fallback for older browsers

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository. 