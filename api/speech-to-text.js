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
 * In production, this would use a real speech-to-text API
 * (Google Cloud Speech-to-Text, Azure Speech, AssemblyAI, etc.)
 */
async function transcribeAudio(audioBase64, audioFormat, language) {
  try {
    // Validate audio data
    const audioBuffer = Buffer.from(audioBase64, 'base64');
    
    if (audioBuffer.length === 0) {
      throw new Error('Audio buffer is empty');
    }

    // Calculate approximate duration (rough estimate based on file size)
    // Typically: 128kbps = 16KB/second
    const estimatedDuration = Math.round((audioBuffer.length / 16000) * 10) / 10;

    // Mock transcription response
    // In production, send to actual speech-to-text API
    const mockText = "Sample transcription from audio input";
    const mockConfidence = 0.95;

    return {
      text: mockText,
      confidence: mockConfidence,
      duration: estimatedDuration,
      format: audioFormat,
      language,
      words: mockText.split(/\s+/).length
    };

    /* Production example using Google Cloud Speech-to-Text:
    
    const speech = require('@google-cloud/speech');
    const client = new speech.SpeechClient();

    const request = {
      audio: { content: audioBase64 },
      config: {
        encoding: 'LINEAR16',
        sampleRateHertz: 16000,
        languageCode: language,
        enableAutomaticPunctuation: true,
      },
    };

    const [operation] = await client.longRunningRecognize(request);
    const [response] = await operation.promise();
    
    return {
      text: response.results.map(r => r.alternatives[0].transcript).join(' '),
      confidence: response.results[0]?.alternatives[0]?.confidence || 0.95,
      ...
    };
    */

  } catch (error) {
    throw new Error(`Audio transcription failed: ${error.message}`);
  }
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
