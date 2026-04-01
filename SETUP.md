# Web Automation Backend - Setup Guide

Complete setup instructions for the web automation backend with audio and speech integration.

## Quick Start

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/jokicdanijel/web-automation2-backend.git
cd web-automation2-backend

# Install dependencies
npm install
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# Node.js Environment
NODE_ENV=development
PORT=3000

# Speech-to-Text Providers (choose at least one)
GROQ_API_KEY=your_groq_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Text-to-Speech Providers (choose at least one)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus

# API Configuration
API_BASE_URL=http://localhost:3000
```

### 3. Get API Keys

#### For Speech-to-Text:

**Option A: Groq Whisper** (Recommended)
1. Go to https://console.groq.com
2. Sign up for free account
3. Create an API key
4. Add to `.env` as `GROQ_API_KEY`

**Option B: Deepgram**
1. Go to https://console.deepgram.com
2. Sign up (600 minutes/month free)
3. Create an API key
4. Add to `.env` as `DEEPGRAM_API_KEY`

#### For Text-to-Speech:

**Option A: ElevenLabs** (Recommended)
1. Go to https://elevenlabs.io
2. Sign up for free account
3. Go to API section
4. Copy API key
5. Add to `.env` as `ELEVENLABS_API_KEY`

**Option B: Google Cloud Text-to-Speech**
1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable Text-to-Speech API
4. Create API key
5. Add to `.env` as `GOOGLE_API_KEY`

**Option C: Azure Speech Services**
1. Go to https://azure.microsoft.com
2. Create Speech resource
3. Get API key and region
4. Add to `.env`:
   - `AZURE_SPEECH_KEY=your_key`
   - `AZURE_SPEECH_REGION=your_region`

**Option D: System espeak** (Fallback - Free)
```bash
# Linux
sudo apt install espeak

# macOS
brew install espeak
```

### 4. Start the Server

```bash
# Development mode
npm start

# Or with nodemon for auto-reload
npm install -g nodemon
nodemon server.js
```

The server will start on `http://localhost:3000`

## API Endpoints

Once running, you have access to:

### Automation
- `POST /api/automation` - Orchestrate multi-step workflows

### Form Handling
- `POST /api/form-automate` - Automated form filling and submission

### Speech Processing
- `POST /api/speech-to-text` - Convert audio to text
- `POST /api/text-to-speech` - Convert text to audio
- `POST /api/audio-pipeline` - Integrated audio workflows

### Basic Navigation
- `POST /api/navigate` - Navigate to URL
- `POST /api/click` - Click elements
- `POST /api/type` - Type text
- `POST /api/wait` - Wait for duration
- `POST /api/extract` - Extract data

## Testing the Audio APIs

### Test Speech-to-Text

```bash
# Create a simple audio test (you'll need actual audio file)
curl -X POST http://localhost:3000/api/speech-to-text \
  -H "Content-Type: application/json" \
  -d '{
    "audio": "your-base64-audio-here",
    "language": "en-US"
  }'
```

### Test Text-to-Speech

```bash
curl -X POST http://localhost:3000/api/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world, this is a test",
    "voice": "default",
    "language": "en-US",
    "returnBase64": true
  }'
```

### Test Audio Pipeline (Interactive)

```bash
curl -X POST http://localhost:3000/api/audio-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "action": "synthesize",
    "text": "Welcome to the automation system",
    "language": "en-US"
  }'
```

## Using in Your Application

### JavaScript/Node.js Example

```javascript
// Import or fetch the API
const API_URL = 'http://localhost:3000/api';

// Text-to-Speech
async function speak(text, voice = 'default') {
  const response = await fetch(`${API_URL}/text-to-speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text,
      voice,
      returnBase64: true
    })
  });

  const result = await response.json();
  
  // Play audio
  const audio = new Audio(result.dataUrl);
  audio.play();
  
  return result;
}

// Speech-to-Text
async function transcribe(audioBase64, language = 'en-US') {
  const response = await fetch(`${API_URL}/speech-to-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio: audioBase64,
      language
    })
  });

  return response.json();
}

// Example: Capture mic and transcribe
async function recordAndTranscribe() {
  const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(mediaStream);
  const chunks = [];

  mediaRecorder.ondataavailable = e => chunks.push(e.data);
  mediaRecorder.start();

  // Record for 5 seconds
  setTimeout(() => {
    mediaRecorder.stop();
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(chunks, { type: 'audio/wav' });
      const reader = new FileReader();
      
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        const result = await transcribe(base64Audio);
        console.log('Transcribed:', result.transcription);
      };
      
      reader.readAsDataURL(audioBlob);
    };
  }, 5000);
}
```

### Python Example

```python
import requests
import base64

API_URL = 'http://localhost:3000/api'

def text_to_speech(text, voice='default', language='en-US'):
    """Convert text to speech"""
    response = requests.post(
        f'{API_URL}/text-to-speech',
        json={
            'text': text,
            'voice': voice,
            'language': language,
            'returnBase64': True
        }
    )
    return response.json()

def speech_to_text(audio_base64, language='en-US'):
    """Convert speech to text"""
    response = requests.post(
        f'{API_URL}/speech-to-text',
        json={
            'audio': audio_base64,
            'language': language
        }
    )
    return response.json()

def interactive_conversation(audio_base64, response_text, language='en-US'):
    """Full conversation loop"""
    response = requests.post(
        f'{API_URL}/audio-pipeline',
        json={
            'action': 'interactive',
            'audio': audio_base64,
            'text': response_text,
            'language': language
        }
    )
    return response.json()

# Example usage
if __name__ == '__main__':
    # Test TTS
    result = text_to_speech('Hello from Python')
    print('Audio URL:', result.get('dataUrl'))
    
    # Test audio pipeline
    result = interactive_conversation(
        'base64_audio_here',
        'This is the AI response',
        'en-US'
    )
    print('Conversation:', result)
```

## Automation Workflow Examples

### Simple Form Automation

```bash
curl -X POST http://localhost:3000/api/automation \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "actions": [
        { "type": "navigate", "url": "https://example.com/form" },
        { "type": "click", "selector": "#email" },
        { "type": "type", "selector": "#email", "text": "user@example.com" },
        { "type": "click", "selector": "#password" },
        { "type": "type", "selector": "#password", "text": "password123" },
        { "type": "click", "selector": "#submit" },
        { "type": "wait", "duration": 2000 }
      ],
      "stopOnError": true
    }
  }'
```

### Form Automation with Audio Feedback

```javascript
// Orchestrate: navigate → fill form → speak confirmation
async function automateWithAudio() {
  // Step 1: Automate form
  await fetch('http://localhost:3000/api/automation', {
    method: 'POST',
    body: JSON.stringify({
      workflow: {
        actions: [
          { type: 'navigate', url: 'https://example.com/form' },
          { type: 'type', selector: '#name', text: 'John Doe' },
          { type: 'click', selector: '#submit' }
        ]
      }
    })
  });

  // Step 2: Speak success message
  await speak('Form submitted successfully');
}
```

## Troubleshooting

### "Module not found"
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### "API key not found"
- Check `.env` file exists in root directory
- Verify API keys are correctly set
- Restart the server after changing `.env`

### "Audio synthesis failed"
- Ensure at least one TTS provider API key is set
- Check API key is valid
- Verify text is not empty and under 5000 characters

### "Transcription failed"
- Ensure audio is valid base64
- Check Groq or Deepgram API key is valid
- Verify language code is supported

### "espeak not found"
- Linux: `sudo apt install espeak`
- macOS: `brew install espeak`

## Production Deployment

### Using PM2

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start server.js --name "web-automation"

# Enable auto-restart on reboot
pm2 startup
pm2 save
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
```

Build and run:
```bash
docker build -t web-automation-backend .
docker run -p 3000:3000 --env-file .env web-automation-backend
```

### Using Vercel

1. Push to GitHub
2. Import repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

## Next Steps

1. Read [AUDIO_INTEGRATION.md](./AUDIO_INTEGRATION.md) for advanced audio setup
2. Read [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference
3. Explore [api/](./api/) directory for endpoint implementations
4. Check [examples/](./examples/) for integration samples

## Support

- Check logs: `tail -f server.log`
- Test endpoints with Postman or curl
- Review environment variables: `cat .env`
- Check API provider status pages for outages

## License

See LICENSE file in repository
