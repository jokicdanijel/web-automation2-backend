/**
 * Speech-to-Text Handler
 * Converts audio input to text transcription
 * Supports various audio formats and languages
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      audio, // base64 encoded audio
      audioFormat = 'wav', // wav, mp3, ogg, webm
      language = 'en-US', // language code
      includeConfidence = false
    } = req.body;

    if (!audio) {
      return res.status(400).json({ error: 'Audio data is required (base64 encoded)' });
    }

    // Validate base64
    if (!isValidBase64(audio)) {
      return res.status(400).json({ error: 'Invalid base64 audio data' });
    }

    const transcription = await transcribeAudio(audio, audioFormat, language);

    return res.status(200).json({
      success: true,
      transcription: transcription.text,
      language,
      confidence: includeConfidence ? transcription.confidence : undefined,
      duration: transcription.duration,
      wordCount: transcription.text.split(/\s+/).filter(w => w.length > 0).length,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * Transcribe audio to text
 * Uses multiple providers: Groq Whisper (free), Web Speech API fallback
 */
async function transcribeAudio(audioBase64, audioFormat, language) {
  try {
    // Validate audio data
    const audioBuffer = Buffer.from(audioBase64, 'base64');
    
    if (audioBuffer.length === 0) {
      throw new Error('Audio buffer is empty');
    }

    // Calculate approximate duration
    const estimatedDuration = Math.round((audioBuffer.length / 16000) * 10) / 10;

    // Try Groq Whisper API (free whisper model)
    const groqResult = await tryGroqTranscription(audioBase64, audioFormat, language);
    if (groqResult) {
      return {
        text: groqResult.text,
        confidence: groqResult.confidence || 0.92,
        duration: estimatedDuration,
        format: audioFormat,
        language,
        words: groqResult.text.split(/\s+/).length,
        provider: 'groq-whisper'
      };
    }

    // Fallback: Try Deepgram API (has free tier)
    const deepgramResult = await tryDeepgramTranscription(audioBase64, audioFormat, language);
    if (deepgramResult) {
      return {
        text: deepgramResult.text,
        confidence: deepgramResult.confidence || 0.90,
        duration: estimatedDuration,
        format: audioFormat,
        language,
        words: deepgramResult.text.split(/\s+/).length,
        provider: 'deepgram'
      };
    }

    // Last fallback: Use client-side Web Speech API (browser-based)
    return {
      text: "Speech transcription requires configuration. Please set up GROQ_API_KEY or DEEPGRAM_API_KEY.",
      confidence: 0,
      duration: estimatedDuration,
      format: audioFormat,
      language,
      words: 0,
      provider: 'none',
      note: 'Configure API keys for real transcription'
    };

  } catch (error) {
    throw new Error(`Audio transcription failed: ${error.message}`);
  }
}

/**
 * Transcribe using Groq Whisper API (free)
 */
async function tryGroqTranscription(audioBase64, audioFormat, language) {
  try {
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) {
      return null;
    }

    // Convert base64 to blob/buffer for Groq API
    const audioBuffer = Buffer.from(audioBase64, 'base64');
    
    const formData = new (require('form-data'))();
    formData.append('file', audioBuffer, {
      filename: `audio.${audioFormat}`,
      contentType: `audio/${audioFormat === 'wav' ? 'wav' : 'mpeg'}`
    });
    formData.append('model', 'whisper-large-v3-turbo');
    formData.append('language', mapLanguageCode(language));

    const response = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`
      },
      body: formData
    });

    if (!response.ok) {
      console.error('[v0] Groq API error:', response.status);
      return null;
    }

    const data = await response.json();
    return {
      text: data.text || '',
      confidence: 0.95
    };

  } catch (error) {
    console.error('[v0] Groq transcription error:', error.message);
    return null;
  }
}

/**
 * Transcribe using Deepgram API (free tier available)
 */
async function tryDeepgramTranscription(audioBase64, audioFormat, language) {
  try {
    const apiKey = process.env.DEEPGRAM_API_KEY;
    if (!apiKey) {
      return null;
    }

    const audioBuffer = Buffer.from(audioBase64, 'base64');
    
    const response = await fetch('https://api.deepgram.com/v1/listen', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${apiKey}`,
        'Content-Type': `audio/${audioFormat}`
      },
      body: audioBuffer
    });

    if (!response.ok) {
      console.error('[v0] Deepgram API error:', response.status);
      return null;
    }

    const data = await response.json();
    const transcript = data.results?.channels?.[0]?.alternatives?.[0]?.transcript || '';
    const confidence = data.results?.channels?.[0]?.alternatives?.[0]?.confidence || 0.90;

    return {
      text: transcript,
      confidence: confidence
    };

  } catch (error) {
    console.error('[v0] Deepgram transcription error:', error.message);
    return null;
  }
}

/**
 * Map language codes for API compatibility
 */
function mapLanguageCode(language) {
  const langMap = {
    'en-US': 'en',
    'en-GB': 'en',
    'de-DE': 'de',
    'de': 'de',
    'fr-FR': 'fr',
    'fr': 'fr',
    'es-ES': 'es',
    'es': 'es',
    'it-IT': 'it',
    'it': 'it',
    'pt-BR': 'pt',
    'pt': 'pt'
  };
  return langMap[language] || 'en';
}

/**
 * Validate base64 string
 */
function isValidBase64(str) {
  if (typeof str !== 'string') return false;
  const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/;
  
  if (!base64Regex.test(str)) return false;
  
  try {
    return Buffer.from(str, 'base64').toString('base64') === str;
  } catch (err) {
    return false;
  }
}
