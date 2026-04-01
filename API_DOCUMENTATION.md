# Web Automation Backend - API Documentation

## Overview

This backend provides comprehensive automation capabilities for web tasks including workflow orchestration, form handling, speech recognition/synthesis, and real-time audio processing.

---

## 1. Automation Script (`/api/automation.js`)

### Purpose
Orchestrates multiple automation actions in sequence with error handling, state tracking, and conditional logic.

### Endpoint
```
POST /api/automation
```

### Request Body
```json
{
  "workflow": {
    "actions": [
      {
        "type": "navigate",
        "url": "https://example.com"
      },
      {
        "type": "click",
        "selector": "button.submit",
        "waitAfter": 2000
      },
      {
        "type": "type",
        "selector": "input[name='email']",
        "text": "user@example.com"
      },
      {
        "type": "wait",
        "duration": 1000
      }
    ],
    "stopOnError": true
  }
}
```

### Supported Actions

| Type | Parameters | Description |
|------|------------|-------------|
| **navigate** | `url` | Navigate to a URL |
| **click** | `selector`, `waitAfter?` | Click on element |
| **type** | `selector`, `text` | Type text into field |
| **extract** | `selector` | Extract data from element |
| **wait** | `duration?` | Wait (default 1000ms) |
| **scroll** | `direction?`, `distance?` | Scroll page |
| **screenshot** | `name` | Take screenshot |
| **condition** | `checks[]` | Conditional execution |

### Response
```json
{
  "success": true,
  "summary": {
    "totalActions": 4,
    "executedActions": 4,
    "failedActions": 0,
    "duration": "2150ms"
  },
  "results": [
    {
      "actionIndex": 0,
      "action": "navigate",
      "status": "success",
      "result": {
        "url": "https://example.com",
        "message": "Navigated to https://example.com"
      },
      "timestamp": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

### Example: Complex Workflow
```bash
curl -X POST http://localhost:3000/api/automation \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "actions": [
        {"type": "navigate", "url": "https://example.com/login"},
        {"type": "type", "selector": "input[name=\"username\"]", "text": "testuser"},
        {"type": "type", "selector": "input[name=\"password\"]", "text": "testpass"},
        {"type": "click", "selector": "button[type=\"submit\"]", "waitAfter": 3000},
        {"type": "screenshot", "name": "after_login"}
      ],
      "stopOnError": false
    }
  }'
```

---

## 2. Form Automation (`/api/form-automate.js`)

### Purpose
Specialized form handling with detection, field validation, filling, and submission capabilities.

### Endpoint
```
POST /api/form-automate
```

### Actions

#### 2.1 Detect Form Structure
```json
{
  "action": "detect",
  "formSelector": "form#contact-form"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "formFound": true,
    "detectedFields": [
      {
        "type": "text",
        "name": "email",
        "selector": "input[name=\"email\"]",
        "required": true
      }
    ],
    "hasSubmitButton": true,
    "submitButtonSelector": "button[type=\"submit\"]"
  }
}
```

#### 2.2 Fill Form Fields
```json
{
  "action": "fill",
  "formSelector": "form#contact-form",
  "fields": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello, this is a test"
  },
  "options": {
    "validateBeforeFill": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "totalFields": 3,
    "filledFields": 3,
    "failedFields": 0,
    "message": "All fields filled successfully"
  }
}
```

#### 2.3 Validate Form
```json
{
  "action": "validate",
  "formSelector": "form#contact-form"
}
```

#### 2.4 Submit Form
```json
{
  "action": "submit",
  "formSelector": "form#contact-form"
}
```

#### 2.5 Clear Form
```json
{
  "action": "clear",
  "formSelector": "form#contact-form"
}
```

#### 2.6 Fill and Submit (Combined)
```json
{
  "action": "fill-and-submit",
  "formSelector": "form#contact-form",
  "fields": {
    "name": "Jane Doe",
    "email": "jane@example.com"
  }
}
```

---

## 3. Speech-to-Text (`/api/speech-to-text.js`)

### Purpose
Convert audio input to text transcription with support for multiple languages and formats.

### Endpoint
```
POST /api/speech-to-text
```

### Request Body
```json
{
  "audio": "SUQzBAAAI1RTU0UAAAAPAAADTGF2ZjU5LjI3LjEwMAAAAAAAAAAAAAAA//...",
  "audioFormat": "mp3",
  "language": "en-US",
  "includeConfidence": true
}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **audio** | string | required | Base64 encoded audio data |
| **audioFormat** | string | "wav" | Audio format: wav, mp3, ogg, webm |
| **language** | string | "en-US" | BCP-47 language code |
| **includeConfidence** | boolean | false | Include confidence score |

### Supported Languages
- `en-US` - English (US)
- `en-GB` - English (UK)
- `de-DE` - German
- `fr-FR` - French
- `es-ES` - Spanish
- `it-IT` - Italian
- `pt-BR` - Portuguese (Brazil)

### Response
```json
{
  "success": true,
  "transcription": "Hello, this is a test message",
  "language": "en-US",
  "confidence": 0.95,
  "duration": 2.5,
  "wordCount": 6,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Example: Convert Audio File to Text
```bash
# Convert audio file to base64
base64 -w 0 audio.mp3 > audio.b64

# Send to API
curl -X POST http://localhost:3000/api/speech-to-text \
  -H "Content-Type: application/json" \
  -d "{
    \"audio\": \"$(cat audio.b64)\",
    \"audioFormat\": \"mp3\",
    \"language\": \"en-US\",
    \"includeConfidence\": true
  }"
```

### JavaScript Example
```javascript
// Read audio file and convert to base64
const fs = require('fs');
const audioBuffer = fs.readFileSync('audio.mp3');
const base64Audio = audioBuffer.toString('base64');

// Send to API
fetch('/api/speech-to-text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    audio: base64Audio,
    audioFormat: 'mp3',
    language: 'en-US',
    includeConfidence: true
  })
})
.then(res => res.json())
.then(data => console.log('Transcription:', data.transcription));
```

---

## 4. Text-to-Speech (`/api/text-to-speech.js`)

### Purpose
Convert text to audio output with customizable voice, language, and speech parameters.

### Endpoint
```
POST /api/text-to-speech
```

### Request Body
```json
{
  "text": "Hello, this is a test message",
  "voice": "default",
  "language": "en-US",
  "speechRate": 1.0,
  "pitch": 1.0,
  "format": "mp3",
  "returnBase64": false
}
```

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| **text** | string | - | required | Text to synthesize |
| **voice** | string | - | "default" | Voice name/ID |
| **language** | string | - | "en-US" | BCP-47 language code |
| **speechRate** | number | 0.5-2.0 | 1.0 | Speech speed multiplier |
| **pitch** | number | 0.5-2.0 | 1.0 | Pitch adjustment |
| **format** | string | - | "mp3" | Audio format: mp3, wav, ogg, webm |
| **returnBase64** | boolean | - | false | Return base64 data URL |

### Available Voices
- `default` - Default voice
- `male` - Male voice
- `female` - Female voice
- `neural` - Neural voice (higher quality)

### Response (URL Mode)
```json
{
  "success": true,
  "text": "Hello, this is a test message",
  "language": "en-US",
  "voice": "default",
  "speechRate": 1.0,
  "pitch": 1.0,
  "format": "mp3",
  "estimatedDuration": {
    "seconds": 3,
    "formatted": "0:03"
  },
  "audioUrl": "/audio/1705316400000-speech.mp3",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Response (Base64 Mode)
```json
{
  "success": true,
  "text": "Hello, this is a test message",
  "audioData": "//NExAAU...",
  "dataUrl": "data:audio/mp3;base64,//NExAAU...",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Example: Generate Speech
```bash
curl -X POST http://localhost:3000/api/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to our automation service",
    "language": "en-US",
    "voice": "default",
    "speechRate": 1.0,
    "pitch": 1.0,
    "format": "mp3",
    "returnBase64": false
  }'
```

### JavaScript Example
```javascript
// Generate speech and play audio
fetch('/api/text-to-speech', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Welcome to our automation service',
    language: 'en-US',
    voice: 'default',
    speechRate: 1.0,
    format: 'mp3',
    returnBase64: true
  })
})
.then(res => res.json())
.then(data => {
  // Play audio
  const audio = new Audio(data.dataUrl);
  audio.play();
});
```

---

## Integration Examples

### Complete Workflow: Form Filling with Voice Feedback

```javascript
// 1. Detect form structure
const detectResult = await fetch('/api/form-automate', {
  method: 'POST',
  body: JSON.stringify({
    action: 'detect',
    formSelector: 'form#feedback'
  })
});

// 2. Fill form with data
const fillResult = await fetch('/api/form-automate', {
  method: 'POST',
  body: JSON.stringify({
    action: 'fill',
    formSelector: 'form#feedback',
    fields: {
      name: 'John Doe',
      email: 'john@example.com',
      message: 'Great service!'
    }
  })
});

// 3. Provide audio confirmation
const voiceResult = await fetch('/api/text-to-speech', {
  method: 'POST',
  body: JSON.stringify({
    text: 'Form submitted successfully',
    voice: 'default',
    returnBase64: true
  })
});

// 4. Play confirmation audio
const audioData = await voiceResult.json();
const audio = new Audio(audioData.dataUrl);
audio.play();
```

### Workflow with Automation Script

```javascript
const workflow = {
  actions: [
    { type: 'navigate', url: 'https://example.com/form' },
    { type: 'type', selector: 'input[name="username"]', text: 'user123' },
    { type: 'type', selector: 'input[name="password"]', text: 'pass123' },
    { type: 'click', selector: 'button.login', waitAfter: 2000 },
    { type: 'screenshot', name: 'post-login' }
  ],
  stopOnError: false
};

const result = await fetch('/api/automation', {
  method: 'POST',
  body: JSON.stringify({ workflow })
});
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Description of what went wrong",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Common HTTP Status Codes
- `200 OK` - Request succeeded
- `400 Bad Request` - Invalid request parameters
- `405 Method Not Allowed` - Wrong HTTP method
- `500 Internal Server Error` - Server-side error

---

## Best Practices

1. **Workflow Design**
   - Keep workflows focused and modular
   - Use meaningful action names
   - Add wait times between critical actions

2. **Form Automation**
   - Always detect form structure first
   - Validate fields before submission
   - Use appropriate selectors (id > name > class)

3. **Speech Processing**
   - Compress audio files before sending
   - Use language codes matching actual content
   - Handle network timeouts gracefully

4. **Error Handling**
   - Implement retry logic for failed actions
   - Log all automation attempts
   - Use stopOnError based on criticality

---

## 5. Speech-to-Text (`/api/speech-to-text`)

### Purpose
Converts audio input to text transcription with support for multiple languages and providers.

### Endpoint
```
POST /api/speech-to-text
```

### Request Body
```json
{
  "audio": "base64-encoded-audio-data",
  "audioFormat": "wav",
  "language": "en-US",
  "includeConfidence": false
}
```

### Response
```json
{
  "success": true,
  "transcription": "Hello, this is a test",
  "language": "en-US",
  "confidence": 0.95,
  "duration": 2.5,
  "wordCount": 5,
  "provider": "groq-whisper",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Supported Providers
- **Groq Whisper** (Recommended) - Free, fast, accurate
- **Deepgram** - Free tier: 600 min/month
- Fallback to Web Speech API

### Usage Example
```bash
curl -X POST http://localhost:3000/api/speech-to-text \
  -H "Content-Type: application/json" \
  -d '{
    "audio": "SUQzBAAAAAAAI1...",
    "language": "en-US"
  }'
```

---

## 6. Text-to-Speech (`/api/text-to-speech`)

### Purpose
Converts text to natural-sounding audio output with customizable voice, language, and speech parameters.

### Endpoint
```
POST /api/text-to-speech
```

### Request Body
```json
{
  "text": "Hello, this is a test",
  "voice": "default",
  "language": "en-US",
  "speechRate": 1.0,
  "pitch": 1.0,
  "format": "mp3",
  "returnBase64": true
}
```

### Response
```json
{
  "success": true,
  "text": "Hello, this is a test",
  "audioData": "SUQzBAAAAAAAI1...",
  "dataUrl": "data:audio/mp3;base64,SUQzBAAAAAAAI1...",
  "estimatedDuration": {
    "seconds": 3,
    "formatted": "0:03"
  },
  "provider": "elevenlabs",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Supported Providers
- **ElevenLabs** (Recommended) - Free: 10K chars/month
- **Google Cloud TTS** - Free: 1M chars/month (trial)
- **Azure Speech** - Free: 5 audio hours/month
- **System espeak** - Unlimited, system-level

### Voice Options
- `default` - Natural, neutral voice
- `male` - Deep male voice
- `female` - High female voice
- `neural` - Advanced neural voice

### Usage Example
```bash
curl -X POST http://localhost:3000/api/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to the system",
    "voice": "female",
    "language": "en-US",
    "returnBase64": true
  }'
```

---

## 7. Audio Pipeline (`/api/audio-pipeline`)

### Purpose
Integrated audio processing supporting transcription, synthesis, and interactive conversation flows.

### Endpoint
```
POST /api/audio-pipeline
```

### Actions

#### Transcribe Action
```json
{
  "action": "transcribe",
  "audio": "base64-audio",
  "audioFormat": "wav",
  "language": "en-US"
}
```

#### Synthesize Action
```json
{
  "action": "synthesize",
  "text": "Hello world",
  "voice": "default",
  "language": "en-US"
}
```

#### Interactive Action (Full Conversation)
```json
{
  "action": "interactive",
  "audio": "base64-user-audio",
  "text": "AI response text",
  "language": "en-US"
}
```

### Interactive Response
```json
{
  "action": "interactive",
  "input": {
    "transcription": "What is the weather?",
    "confidence": 0.92,
    "language": "en-US"
  },
  "output": {
    "text": "The weather is sunny",
    "audioUrl": "/audio/speech.mp3",
    "estimatedDuration": {
      "seconds": 2,
      "formatted": "0:02"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Usage Example
```bash
# Interactive conversation
curl -X POST http://localhost:3000/api/audio-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "action": "interactive",
    "audio": "SUQzBAAAAAAAI1...",
    "text": "The forecast shows clear skies tomorrow",
    "language": "en-US"
  }'
```

---

## Supported Languages

All audio APIs support these language codes:

| Language | Code |
|----------|------|
| English (US) | en-US |
| English (UK) | en-GB |
| German | de-DE |
| French | fr-FR |
| Spanish | es-ES |
| Italian | it-IT |
| Portuguese (Brazil) | pt-BR |

---

## Deployment Notes

### Production Configuration
- Integrate with real speech-to-text services (Groq, Deepgram)
- Use premium TTS providers (ElevenLabs, Google Cloud, Azure)
- Implement rate limiting and authentication
- Add request/response logging
- Cache frequently used voice outputs
- Use CDN for audio file delivery
- Monitor API usage and costs

### Environment Variables
```env
# Speech-to-Text
GROQ_API_KEY=your_groq_key_here
DEEPGRAM_API_KEY=your_deepgram_key_here

# Text-to-Speech
ELEVENLABS_API_KEY=your_elevenlabs_key_here
GOOGLE_API_KEY=your_google_key_here
AZURE_SPEECH_KEY=your_azure_key_here
AZURE_SPEECH_REGION=eastus

# Base URL (for audio-pipeline)
API_BASE_URL=http://localhost:3000
```

### Audio File Limits
- **Maximum file size**: 25MB
- **Maximum text length**: 5000 characters
- **Audio formats**: WAV, MP3, OGG, WebM
- **Sample rates**: 8kHz, 16kHz, 44.1kHz, 48kHz

---

## Support & Contributing

For detailed audio integration guides, see [AUDIO_INTEGRATION.md](./AUDIO_INTEGRATION.md)

For issues or contributions, please refer to the main repository documentation.
