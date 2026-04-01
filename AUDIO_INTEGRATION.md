# Audio & Speech Integration Guide

Complete guide for setting up and using speech-to-text and text-to-speech in your web automation backend.

## Overview

The audio/speech system provides three integrated APIs:

1. **Speech-to-Text** (`/api/speech-to-text`) - Convert audio to text transcription
2. **Text-to-Speech** (`/api/text-to-speech`) - Convert text to audio output
3. **Audio Pipeline** (`/api/audio-pipeline`) - Integrated audio workflows

## Setup Instructions

### Free Providers

#### 1. Groq Whisper (Recommended for Speech-to-Text)
- **Cost**: Free tier available
- **Model**: Whisper Large V3 Turbo
- **Setup**:
  ```bash
  # Get API key from: https://console.groq.com
  export GROQ_API_KEY="your-groq-api-key"
  ```

#### 2. Deepgram (Alternative for Speech-to-Text)
- **Cost**: 600 min/month free
- **Setup**:
  ```bash
  # Get API key from: https://console.deepgram.com
  export DEEPGRAM_API_KEY="your-deepgram-api-key"
  ```

#### 3. ElevenLabs (Recommended for Text-to-Speech)
- **Cost**: 10,000 characters/month free
- **Setup**:
  ```bash
  # Get API key from: https://elevenlabs.io
  export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
  ```

#### 4. Google Cloud Text-to-Speech
- **Cost**: 1 million characters/month free (with free trial credit)
- **Setup**:
  ```bash
  # Get API key from: https://console.cloud.google.com
  export GOOGLE_API_KEY="your-google-api-key"
  ```

#### 5. Azure Speech Services
- **Cost**: 5 audio hours/month free
- **Setup**:
  ```bash
  export AZURE_SPEECH_KEY="your-azure-speech-key"
  export AZURE_SPEECH_REGION="eastus"  # or your region
  ```

#### 6. Fallback: System espeak
- **Cost**: Free (system-level)
- **Setup**:
  ```bash
  # Linux
  sudo apt install espeak

  # macOS
  brew install espeak
  ```

## API Endpoints

### Speech-to-Text: `/api/speech-to-text`

Convert audio to text transcription.

**Request**:
```json
{
  "audio": "base64-encoded-audio-data",
  "audioFormat": "wav",  // wav, mp3, ogg, webm
  "language": "en-US",   // en-US, en-GB, de-DE, fr-FR, etc.
  "includeConfidence": false
}
```

**Response**:
```json
{
  "success": true,
  "transcription": "Hello, this is a test message",
  "language": "en-US",
  "confidence": 0.95,
  "duration": 2.5,
  "wordCount": 6,
  "provider": "groq-whisper",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example Usage**:
```javascript
// Capture audio from microphone
const audioBlob = await captureAudio();
const base64Audio = await blobToBase64(audioBlob);

// Send to transcription API
const response = await fetch('/api/speech-to-text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    audio: base64Audio,
    audioFormat: 'wav',
    language: 'en-US'
  })
});

const result = await response.json();
console.log('Transcribed:', result.transcription);
```

### Text-to-Speech: `/api/text-to-speech`

Convert text to audio output.

**Request**:
```json
{
  "text": "Hello, this is a test message",
  "voice": "default",      // default, male, female, neural
  "language": "en-US",     // en-US, de-DE, fr-FR, etc.
  "speechRate": 1.0,       // 0.5 to 2.0
  "pitch": 1.0,            // 0.5 to 2.0
  "format": "mp3",         // mp3, wav, ogg, webm
  "returnBase64": true     // true for base64, false for URL
}
```

**Response** (returnBase64: true):
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
  "audioData": "SUQzBAAAAAAAI1...",
  "dataUrl": "data:audio/mp3;base64,SUQzBAAAAAAAI1...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response** (returnBase64: false):
```json
{
  "success": true,
  "audioUrl": "/audio/1705318200000-speech.mp3",
  ...
}
```

**Example Usage**:
```javascript
// Synthesize speech
const response = await fetch('/api/text-to-speech', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Welcome to our automation system',
    voice: 'female',
    language: 'en-US',
    returnBase64: true
  })
});

const result = await response.json();

// Play audio
const audio = new Audio(result.dataUrl);
audio.play();
```

### Audio Pipeline: `/api/audio-pipeline`

Integrated audio processing with multiple actions.

**Actions**:

#### 1. Transcribe Action
```json
{
  "action": "transcribe",
  "audio": "base64-audio",
  "audioFormat": "wav",
  "language": "en-US"
}
```

#### 2. Synthesize Action
```json
{
  "action": "synthesize",
  "text": "Hello world",
  "voice": "default",
  "language": "en-US",
  "speechRate": 1.0,
  "pitch": 1.0
}
```

#### 3. Interactive Action (Full Conversation Loop)
```json
{
  "action": "interactive",
  "audio": "base64-user-audio",
  "text": "Here is the AI response",
  "language": "en-US",
  "voice": "default",
  "audioFormat": "mp3"
}
```

**Interactive Response**:
```json
{
  "action": "interactive",
  "input": {
    "audio": true,
    "transcription": "What is the weather today?",
    "confidence": 0.92,
    "language": "en-US"
  },
  "output": {
    "text": "The weather is sunny and 72 degrees Fahrenheit",
    "audioUrl": "/audio/1705318200000-speech.mp3",
    "voice": "default",
    "speechRate": 1.0,
    "estimatedDuration": {
      "seconds": 5,
      "formatted": "0:05"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Client-Side Implementation

### Audio Capture

```javascript
// Capture audio from microphone
async function captureAudio(duration = 5000) {
  const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(mediaStream);
  const chunks = [];

  mediaRecorder.ondataavailable = e => chunks.push(e.data);
  mediaRecorder.start();

  // Stop after specified duration
  await new Promise(resolve => setTimeout(resolve, duration));
  mediaRecorder.stop();

  return new Promise(resolve => {
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(chunks, { type: 'audio/wav' });
      resolve(audioBlob);
    };
  });
}

// Convert blob to base64
async function blobToBase64(blob) {
  return new Promise(resolve => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.readAsDataURL(blob);
  });
}
```

### Audio Playback

```javascript
// Play audio from base64
function playAudioFromBase64(base64Data, mimeType = 'audio/mp3') {
  const dataUrl = `data:${mimeType};base64,${base64Data}`;
  const audio = new Audio(dataUrl);
  audio.play();
  return audio;
}

// Play audio from URL
function playAudioFromUrl(url) {
  const audio = new Audio(url);
  audio.play();
  return audio;
}
```

## Advanced Usage

### Multi-Language Support

The system automatically detects and supports multiple languages:

- **English**: en-US, en-GB
- **German**: de-DE
- **French**: fr-FR
- **Spanish**: es-ES
- **Italian**: it-IT
- **Portuguese**: pt-BR

```javascript
// German speech-to-text
await fetch('/api/speech-to-text', {
  method: 'POST',
  body: JSON.stringify({
    audio: base64Audio,
    language: 'de-DE'
  })
});

// German text-to-speech
await fetch('/api/text-to-speech', {
  method: 'POST',
  body: JSON.stringify({
    text: 'Hallo, dies ist ein Test',
    language: 'de-DE'
  })
});
```

### Voice Customization

```javascript
// Use different voices
const voices = ['default', 'male', 'female', 'neural'];

for (const voice of voices) {
  const response = await fetch('/api/text-to-speech', {
    method: 'POST',
    body: JSON.stringify({
      text: 'This is voice customization',
      voice,
      language: 'en-US'
    })
  });
}
```

### Real-Time Interactive Conversation

```javascript
async function conversationLoop() {
  while (true) {
    // Capture user speech
    const userAudio = await captureAudio(5000);
    const userAudioBase64 = await blobToBase64(userAudio);

    // Send to chatbot/AI for processing
    const aiResponse = await getAIResponse(userAudioBase64);

    // Convert response to speech and play
    const ttsResponse = await fetch('/api/text-to-speech', {
      method: 'POST',
      body: JSON.stringify({
        text: aiResponse,
        voice: 'female',
        returnBase64: true
      })
    });

    const result = await ttsResponse.json();
    playAudioFromBase64(result.audioData, 'audio/mp3');

    // Wait for audio to finish
    await new Promise(resolve => setTimeout(resolve, result.estimatedDuration.seconds * 1000));
  }
}
```

## Error Handling

All endpoints return standard error responses:

```json
{
  "error": "Audio data is required",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

```javascript
// Handle errors in client code
try {
  const response = await fetch('/api/speech-to-text', {
    method: 'POST',
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.error);
    return;
  }

  const result = await response.json();
  console.log('Success:', result);

} catch (error) {
  console.error('Network Error:', error);
}
```

## Performance & Limits

| Provider | Speed | Quality | Free Limit |
|----------|-------|---------|-----------|
| Groq Whisper | Fast | High | Generous |
| Deepgram | Very Fast | High | 600 min/month |
| ElevenLabs | Fast | Very High | 10K chars/month |
| Google TTS | Medium | Very High | 1M chars/month (trial) |
| Azure Speech | Medium | High | 5 audio hours/month |
| espeak (System) | Very Fast | Medium | Unlimited |

## Troubleshooting

### "No TTS provider available"
- Set up at least one API key: `ELEVENLABS_API_KEY`, `GOOGLE_API_KEY`, or `AZURE_SPEECH_KEY`
- Or ensure `espeak` is installed on the system

### "Audio transcription failed"
- Verify audio is valid base64
- Check API key is valid in environment variables
- Try different language code

### "Speech synthesis failed"
- Check text length (max 5000 characters)
- Verify API key is set
- Check speechRate and pitch values (0.5-2.0)

## Integration with Automation Scripts

Use audio in your automation workflows:

```javascript
const automationWorkflow = [
  { action: 'navigate', url: 'https://example.com' },
  { action: 'click', selector: '#start-button' },
  
  // Capture speech input
  { 
    action: 'speech-input',
    duration: 5000,
    transcribeApi: '/api/speech-to-text'
  },
  
  // Process the transcribed text
  { action: 'type', selector: '#input-field', text: '${transcribed_text}' },
  
  // Read response aloud
  {
    action: 'speech-output',
    text: 'Form submitted successfully',
    synthesizeApi: '/api/text-to-speech'
  },
  
  { action: 'submit', selector: '#submit-button' }
];
```

## Security Notes

- API keys are stored in environment variables, never hardcoded
- Use HTTPS in production
- Limit file sizes and implement rate limiting
- Validate base64 audio before processing
- Consider user privacy with audio data

## Support & Resources

- [Groq Console](https://console.groq.com)
- [Deepgram Dashboard](https://console.deepgram.com)
- [ElevenLabs API](https://elevenlabs.io)
- [Google Cloud Speech](https://cloud.google.com/speech-to-text)
- [Azure Speech Services](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/)
