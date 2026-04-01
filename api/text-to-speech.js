/**
 * Text-to-Speech Handler
 * Converts text to audio output
 * Supports multiple voices, languages, and speech rates
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      text, // Text to convert to speech
      voice = 'default', // Voice name/ID
      language = 'en-US', // Language code
      speechRate = 1.0, // 0.5 to 2.0
      pitch = 1.0, // 0.5 to 2.0
      format = 'mp3', // mp3, wav, ogg, webm
      returnBase64 = false // Return audio as base64 or URL
    } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    if (text.trim().length === 0) {
      return res.status(400).json({ error: 'Text cannot be empty' });
    }

    // Validate parameters
    if (speechRate < 0.5 || speechRate > 2.0) {
      return res.status(400).json({ error: 'Speech rate must be between 0.5 and 2.0' });
    }

    if (pitch < 0.5 || pitch > 2.0) {
      return res.status(400).json({ error: 'Pitch must be between 0.5 and 2.0' });
    }

    const audioData = await synthesizeSpeech({
      text,
      voice,
      language,
      speechRate,
      pitch,
      format
    });

    const response = {
      success: true,
      text,
      language,
      voice,
      speechRate,
      pitch,
      format,
      estimatedDuration: calculateEstimatedDuration(text, speechRate),
      timestamp: new Date().toISOString()
    };

    if (returnBase64) {
      response.audioData = audioData.base64;
      response.dataUrl = `data:audio/${format};base64,${audioData.base64}`;
    } else {
      response.audioUrl = `/audio/${Date.now()}-speech.${format}`;
    }

    return res.status(200).json(response);

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * Synthesize speech from text
 * Uses multiple free TTS providers: Eleven Labs (free tier), Google TTS API, ElevenLabs
 */
async function synthesizeSpeech(params) {
  const { text, voice, language, speechRate, pitch, format } = params;

  try {
    // Validate text
    if (text.length > 5000) {
      throw new Error('Text exceeds maximum length of 5000 characters');
    }

    // Try ElevenLabs API (free tier available)
    const elevenLabsResult = await tryElevenLabsSynthesis(text, voice, language, speechRate, pitch, format);
    if (elevenLabsResult) {
      return elevenLabsResult;
    }

    // Try Google Cloud TTS API
    const googleResult = await tryGoogleTTSSynthesis(text, voice, language, speechRate, pitch, format);
    if (googleResult) {
      return googleResult;
    }

    // Try Azure TTS (free tier)
    const azureResult = await tryAzureTTSSynthesis(text, voice, language, speechRate, pitch, format);
    if (azureResult) {
      return azureResult;
    }

    // Fallback: Use espeak or system command
    const espeakResult = await tryEspeakSynthesis(text, language, speechRate, format);
    if (espeakResult) {
      return espeakResult;
    }

    throw new Error('No TTS provider available. Configure ELEVENLABS_API_KEY, GOOGLE_APPLICATION_CREDENTIALS, or AZURE_SPEECH_KEY');

  } catch (error) {
    throw new Error(`Speech synthesis failed: ${error.message}`);
  }
}

/**
 * Synthesize using ElevenLabs API (free tier: 10,000 chars/month)
 */
async function tryElevenLabsSynthesis(text, voice, language, speechRate, pitch, format) {
  try {
    const apiKey = process.env.ELEVENLABS_API_KEY;
    if (!apiKey) return null;

    // Map voice to ElevenLabs voice ID
    const voiceId = mapVoiceToElevenLabsId(voice);
    
    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75
        },
        model_id: 'eleven_monolingual_v1'
      })
    });

    if (!response.ok) {
      console.error('[v0] ElevenLabs API error:', response.status);
      return null;
    }

    const audioBuffer = await response.arrayBuffer();
    return {
      base64: Buffer.from(audioBuffer).toString('base64'),
      format: 'mp3',
      voice,
      language,
      speechRate,
      pitch,
      size: audioBuffer.byteLength,
      provider: 'elevenlabs'
    };

  } catch (error) {
    console.error('[v0] ElevenLabs synthesis error:', error.message);
    return null;
  }
}

/**
 * Synthesize using Google Cloud Text-to-Speech API
 */
async function tryGoogleTTSSynthesis(text, voice, language, speechRate, pitch, format) {
  try {
    const apiKey = process.env.GOOGLE_API_KEY;
    if (!apiKey) return null;

    const response = await fetch(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: { text },
        voice: {
          languageCode: language,
          name: `${language}-Neural2-${mapVoiceGender(voice)}`
        },
        audioConfig: {
          audioEncoding: format.toUpperCase(),
          pitch,
          speakingRate: speechRate
        }
      })
    });

    if (!response.ok) {
      console.error('[v0] Google TTS API error:', response.status);
      return null;
    }

    const data = await response.json();
    return {
      base64: data.audioContent,
      format,
      voice,
      language,
      speechRate,
      pitch,
      provider: 'google-cloud-tts'
    };

  } catch (error) {
    console.error('[v0] Google TTS synthesis error:', error.message);
    return null;
  }
}

/**
 * Synthesize using Azure Cognitive Services Speech API
 */
async function tryAzureTTSSynthesis(text, voice, language, speechRate, pitch, format) {
  try {
    const apiKey = process.env.AZURE_SPEECH_KEY;
    const region = process.env.AZURE_SPEECH_REGION || 'eastus';
    if (!apiKey) return null;

    const ssml = `<speak version="1.0" xml:lang="${language}"><voice name="${mapVoiceToAzureId(voice, language)}"><prosody pitch="${pitch * 100}%" rate="${speechRate}">${escapeXml(text)}</prosody></voice></speak>`;

    const response = await fetch(`https://${region}.tts.speech.microsoft.com/cognitiveservices/v1`, {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': apiKey,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': mapFormatToAzure(format)
      },
      body: ssml
    });

    if (!response.ok) {
      console.error('[v0] Azure TTS API error:', response.status);
      return null;
    }

    const audioBuffer = await response.arrayBuffer();
    return {
      base64: Buffer.from(audioBuffer).toString('base64'),
      format,
      voice,
      language,
      speechRate,
      pitch,
      size: audioBuffer.byteLength,
      provider: 'azure-speech'
    };

  } catch (error) {
    console.error('[v0] Azure TTS synthesis error:', error.message);
    return null;
  }
}

/**
 * Fallback: Synthesize using system espeak command
 */
async function tryEspeakSynthesis(text, language, speechRate, format) {
  try {
    const { execSync } = require('child_process');
    const fs = require('fs');
    const path = require('path');
    const os = require('os');

    // Check if espeak is available
    try {
      execSync('which espeak', { stdio: 'ignore' });
    } catch {
      return null;
    }

    const tmpFile = path.join(os.tmpdir(), `tts-${Date.now()}.wav`);
    const langCode = mapLanguageCode(language);
    const speed = Math.round(150 * speechRate); // Default 150 wpm

    execSync(`espeak -v ${langCode} -s ${speed} -w ${tmpFile} "${text.replace(/"/g, '\\"')}"`, {
      stdio: 'pipe'
    });

    const audioBuffer = fs.readFileSync(tmpFile);
    fs.unlinkSync(tmpFile);

    return {
      base64: audioBuffer.toString('base64'),
      format: 'wav',
      language,
      speechRate,
      pitch: 1.0,
      size: audioBuffer.length,
      provider: 'espeak'
    };

  } catch (error) {
    console.error('[v0] Espeak synthesis error:', error.message);
    return null;
  }
}

/**
 * Helper functions for voice/language mapping
 */
function mapVoiceToElevenLabsId(voice) {
  const voiceMap = {
    'default': '21m00Tcm4TlvDq8ikWAM',
    'male': 'EXAVITQu4vr4xnSDxMaL',
    'female': 'XB0fDUnXU5powFXDhCwa',
    'neural': 'g5CIjZEefAuth4XA7teF'
  };
  return voiceMap[voice] || voiceMap['default'];
}

function mapVoiceToAzureId(voice, language) {
  const voiceMap = {
    'en-US': { default: 'en-US-AvaNeural', male: 'en-US-GuyNeural', female: 'en-US-AvaNeural', neural: 'en-US-AvaNeural' },
    'de-DE': { default: 'de-DE-KatjaNeural', male: 'de-DE-ConradNeural', female: 'de-DE-KatjaNeural', neural: 'de-DE-KatjaNeural' },
    'fr-FR': { default: 'fr-FR-DeniseNeural', male: 'fr-FR-HenriNeural', female: 'fr-FR-DeniseNeural', neural: 'fr-FR-DeniseNeural' }
  };
  const langVoices = voiceMap[language] || voiceMap['en-US'];
  return langVoices[voice] || langVoices['default'];
}

function mapVoiceGender(voice) {
  const genderMap = { 'male': 'A', 'female': 'C', 'default': 'B', 'neural': 'D' };
  return genderMap[voice] || 'B';
}

function mapFormatToAzure(format) {
  const formatMap = {
    'mp3': 'audio-16khz-32kbitrate-mono-mp3',
    'wav': 'riff-16khz-16bit-mono-pcm',
    'ogg': 'ogg-16khz-16bit-mono-opus'
  };
  return formatMap[format] || formatMap['mp3'];
}

function mapLanguageCode(language) {
  const langMap = {
    'en-US': 'en', 'en-GB': 'en', 'de-DE': 'de', 'de': 'de',
    'fr-FR': 'fr', 'fr': 'fr', 'es-ES': 'es', 'es': 'es',
    'it-IT': 'it', 'it': 'it', 'pt-BR': 'pt', 'pt': 'pt'
  };
  return langMap[language] || 'en';
}

function escapeXml(text) {
  return text.replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Calculate estimated audio duration in seconds
 */
function calculateEstimatedDuration(text, speechRate) {
  // Average speaking rate is ~150 words per minute
  // Adjust based on speechRate parameter
  const baseWordsPerMinute = 150;
  const adjustedWordsPerMinute = baseWordsPerMinute * speechRate;
  const words = text.split(/\s+/).length;
  const minutes = words / adjustedWordsPerMinute;
  const seconds = Math.round(minutes * 60);
  
  return {
    seconds,
    formatted: `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
  };
}

/**
 * Get available voices for a language
 */
export async function getAvailableVoices(language = 'en-US') {
  return {
    language,
    voices: [
      { id: 'default', name: 'Default Voice', gender: 'neutral' },
      { id: 'male', name: 'Male Voice', gender: 'male' },
      { id: 'female', name: 'Female Voice', gender: 'female' },
      { id: 'neural', name: 'Neural Voice', gender: 'neutral' }
    ],
    supportedLanguages: [
      'en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES', 'it-IT', 'pt-BR'
    ]
  };
}
