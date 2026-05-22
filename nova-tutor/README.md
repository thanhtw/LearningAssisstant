# Nova Tutor 🤖

An interactive AI learning assistant built with React, Vite, and TypeScript. Features a dynamic avatar, real-time chat, and voice interaction capabilities.

## Features

- **Interactive Avatar** - SVG-based character with emotion states
- **Chat Interface** - Real-time messaging with the AI tutor
- **Voice Controls** - Speech-to-Text (STT) and Text-to-Speech (TTS)
- **Responsive Design** - Built with Tailwind CSS
- **Type-Safe** - Full TypeScript support
- **Hot Module Replacement** - Fast development experience with Vite

## Project Structure

```
nova-tutor/
├── src/
│   ├── components/
│   │   ├── Avatar/           # Character avatar component
│   │   ├── Chat/             # Chat interface components
│   │   └── Voice/            # Voice control components
│   ├── hooks/
│   │   ├── useCharacter.ts   # Character state management
│   │   ├── useVoice.ts       # Voice interaction hook
│   │   └── useChat.ts        # Chat state management
│   ├── types/
│   │   └── index.ts          # Shared TypeScript types
│   ├── api/
│   │   └── client.ts         # API client utilities
│   ├── App.tsx               # Main app component
│   ├── main.tsx              # React entry point
│   └── index.css             # Global styles
├── public/                   # Static assets
├── index.html                # HTML entry point
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── vite.config.ts            # Vite config
├── tailwind.config.js        # Tailwind CSS config
└── postcss.config.js         # PostCSS config
```

## Installation

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Setup

1. Navigate to the project directory:

```bash
cd nova-tutor
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file from the example:

```bash
cp .env.example .env
```

4. Update `.env` with your configuration:

```
VITE_API_BASE_URL=http://localhost:3000
VITE_VOICE_LANG=en-US
VITE_VOICE_RATE=1.0
VITE_VOICE_PITCH=1.0
```

## Development

Start the development server:

```bash
npm run dev
```

The app will open automatically at `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Note:** Speech Recognition and Text-to-Speech APIs require modern browsers. Not all features may work in older browsers.

## API Integration

The chat component communicates with a backend API. Configure the endpoint in `.env`:

```
VITE_API_BASE_URL=http://localhost:3000
```

### Expected API Endpoint

**POST** `/api/chat`

Request:
```json
{
  "message": "user input"
}
```

Response:
```json
{
  "reply": "assistant response"
}
```

## Voice Features

### Text-to-Speech (TTS)
Controlled via the speaker button in VoiceControls. Configure voice settings in `.env`:
- `VITE_VOICE_LANG` - Language code (e.g., 'en-US', 'fr-FR')
- `VITE_VOICE_RATE` - Speech rate (0.1 to 10)
- `VITE_VOICE_PITCH` - Pitch level (0 to 2)

### Speech-to-Text (STT)
Controlled via the microphone button. Uses the Web Speech API for real-time transcription.

## Styling

The project uses Tailwind CSS for styling. Customize the design in `tailwind.config.js`.

## Emotion System

The character supports multiple emotions, each with unique visual representations:
- 😊 **Happy** - Smiling, yellow color
- 😢 **Sad** - Frowning, purple color
- 🎉 **Excited** - Wide mouth, red color
- 😕 **Confused** - Straight mouth, orange color
- 😐 **Neutral** - Neutral expression, blue color
- 🤔 **Thinking** - Contemplative, lavender color

## TypeScript Types

Core types are defined in `src/types/index.ts`:

```typescript
type Emotion = 'happy' | 'sad' | 'excited' | 'confused' | 'neutral' | 'thinking';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}
```

## Performance

- Vite provides extremely fast build times and HMR
- React code splitting for optimized bundle sizes
- Lazy loading for components (can be added)

## Troubleshooting

### Speech API Not Working
- Ensure you're using a secure context (HTTPS) or localhost
- Check browser permissions for microphone and speaker access
- Some browsers require user interaction to enable speech APIs

### Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install

# Clear Vite cache
rm -rf .vite
npm run build
```

## Future Enhancements

- [ ] Multi-language support
- [ ] User authentication
- [ ] Chat history persistence
- [ ] Custom avatar creation
- [ ] Advanced NLP features
- [ ] Mobile app version

## License

MIT

## Support

For issues or questions, please open an issue in the repository.

---

**Happy Learning with Nova Tutor! 🚀**
