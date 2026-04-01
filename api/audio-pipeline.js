/**
 * Audio Pipeline Handler
 * Integrated audio processing: capture → transcribe → process → synthesize → play
 * Supports real-time speech interaction workflows
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      action, // 'transcribe', 'synthesize', 'interactive'
      audio, // base64 audio (for transcribe/interactive)
      text, // text to synthesize
      audioFormat = 'wav',
      language = 'en-US',
      voice = 'default',
      speechRate = 1.0,
      pitch = 1.0
    } = req.body;

    if (!action) {
      return res.status(400).json({ error: 'Action is required (transcribe, synthesize, or interactive)' });
    }

    switch (action) {
      case 'transcribe':
        if (!audio) {
          return res.status(400).json({ error: 'Audio data is required for transcribe action' });
        }
        return await handleTranscribe(res, audio, audioFormat, language);

      case 'synthesize':
        if (!text) {
          return res.status(400).json({ error: 'Text is required for synthesize action' });
        }
        return await handleSynthesize(res, text, voice, language, speechRate, pitch, audioFormat);

      case 'interactive':
        // Interactive: transcribe audio, then synthesize response
        if (!audio || !text) {
          return res.status(400).json({ error: 'Both audio and response text are required for interactive action' });
        }
        return await handleInteractive(res, audio, text, audioFormat, language, voice, speechRate, pitch);

      default:
        return res.status(400).json({ error: 'Invalid action. Use: transcribe, synthesize, or interactive' });
    }

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * Handle transcription action
 */
async function handleTranscribe(res, audio, audioFormat, language) {
  const transcriptionResponse = await fetch(
    `${process.env.API_BASE_URL || 'http://localhost:3000'}/api/speech-to-text`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ audio, audioFormat, language })
    }
  );

  const result = await transcriptionResponse.json();
  return res.status(transcriptionResponse.status).json({
    action: 'transcribe',
    ...result,
    timestamp: new Date().toISOString()
  });
}

/**
 * Handle synthesis action
 */
async function handleSynthesize(res, text, voice, language, speechRate, pitch, audioFormat) {
  const synthesisResponse = await fetch(
    `${process.env.API_BASE_URL || 'http://localhost:3000'}/api/text-to-speech`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        voice,
        language,
        speechRate,
        pitch,
        format: audioFormat,
        returnBase64: true
      })
    }
  );

  const result = await synthesisResponse.json();
  return res.status(synthesisResponse.status).json({
    action: 'synthesize',
    ...result,
    timestamp: new Date().toISOString()
  });
}

/**
 * Handle interactive action (transcribe input → synthesize output)
 * Simulates a conversational audio loop
 */
async function handleInteractive(res, audio, responseText, audioFormat, language, voice, speechRate, pitch) {
  try {
    // Step 1: Transcribe user input
    const transcriptionResponse = await fetch(
      `${process.env.API_BASE_URL || 'http://localhost:3000'}/api/speech-to-text`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio, audioFormat, language })
      }
    );

    const transcription = await transcriptionResponse.json();

    if (!transcription.success && !transcription.transcription) {
      return res.status(400).json({
        error: 'Failed to transcribe audio',
        details: transcription
      });
    }

    // Step 2: Synthesize response
    const synthesisResponse = await fetch(
      `${process.env.API_BASE_URL || 'http://localhost:3000'}/api/text-to-speech`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: responseText,
          voice,
          language,
          speechRate,
          pitch,
          format: audioFormat,
          returnBase64: true
        })
      }
    );

    const synthesis = await synthesisResponse.json();

    return res.status(200).json({
      action: 'interactive',
      input: {
        audio: !!audio,
        transcription: transcription.transcription || transcription.text,
        confidence: transcription.confidence,
        language
      },
      output: {
        text: responseText,
        audioUrl: synthesis.audioUrl || synthesis.dataUrl,
        voice,
        speechRate,
        estimatedDuration: synthesis.estimatedDuration
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    return res.status(500).json({
      action: 'interactive',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
