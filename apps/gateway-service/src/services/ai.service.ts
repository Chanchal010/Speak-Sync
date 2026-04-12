import { serviceRegistry } from './service-registry.service.js';
import { AxiosInstance } from 'axios';
import FormData from 'form-data';

/**
 * AI Service Client
 * Proxies requests to AI Brain Service (STT, TTS, LLM)
 */
export class AIService {
    private client: AxiosInstance | null;

    constructor() {
        this.client = serviceRegistry.createServiceClient('ai-brain');
    }

    private ensureClient() {
        if (!this.client) {
            throw new Error('AI Brain service client not initialized');
        }
        return this.client;
    }

    /**
     * Transcribe audio to text (STT)
     */
    async transcribeAudio(
        audioBuffer: Buffer,
        filename: string,
        language: string = 'auto'
    ): Promise<any> {
        const client = this.ensureClient();

        const formData = new FormData();
        formData.append('audio', audioBuffer, filename);
        formData.append('language', language);

        const response = await client.post('/api/ai/voice/transcribe', formData, {
            headers: formData.getHeaders()
        });

        return response.data;
    }

    /**
     * Convert text to speech (TTS)
     */
    async synthesizeSpeech(
        text: string,
        voice: string = 'nova',
        speed: number = 1.0
    ): Promise<Buffer> {
        const client = this.ensureClient();

        const formData = new FormData();
        formData.append('text', text);
        formData.append('voice', voice);
        formData.append('speed', speed.toString());

        const response = await client.post('/api/ai/voice/synthesize', formData, {
            headers: formData.getHeaders(),
            responseType: 'arraybuffer'
        });

        return Buffer.from(response.data);
    }

    /**
     * Complete conversation: STT → NLU → Action → TTS (via AI Brain Service)
     * Sends audio to AI Brain's full conversation pipeline which:
     * 1. Transcribes speech via Whisper
     * 2. Detects intent via LLM (NLU)
     * 3. Executes action (creates tasks, logs habits, etc.)
     * 4. Generates conversational response
     * 5. Synthesizes speech via TTS
     */
    async converse(
        audioBuffer: Buffer,
        filename: string,
        userId: string,
        language: string = 'auto',
        voice: string = 'nova'
    ): Promise<any> {
        const client = this.ensureClient();

        // Send to AI Brain's full conversation pipeline
        const formData = new FormData();
        formData.append('audio', audioBuffer, { filename: filename || 'recording.wav' });
        formData.append('user_id', userId);
        formData.append('voice_profile', 'friendly');
        if (language) formData.append('language', language);

        try {
            const response = await client.post('/api/ai/conversation/voice', formData, {
                headers: formData.getHeaders(),
                timeout: 60000, // 60s timeout for full pipeline
            });

            const result = response.data;

            // The AI Brain conversation endpoint returns:
            // - transcription: { text, confidence, language }
            // - understanding: { intent, domain, confidence, entities }
            // - action_result: { action_executed, action_type, service, confirmation_text, ... }
            // - response: { text, sentiment }
            // - audio_data: raw audio bytes (base64 encoded in the route)

            // Convert audio_data to base64 if it exists (AI Brain returns raw bytes)
            let audioBase64 = null;
            if (result.audio_data) {
                // audio_data comes as base64 from the conversation route
                audioBase64 = result.audio_data;
            } else if (result.audio_base64) {
                audioBase64 = result.audio_base64;
            }

            return {
                transcript: result.transcription?.text || '',
                response_text: result.response?.text || '',
                audio_base64: audioBase64,
                language: result.transcription?.language || 'en',
                confidence: result.transcription?.confidence || 0,
                // New fields from Jarvis pipeline
                intent: result.understanding?.intent || 'unknown',
                domain: result.understanding?.domain || 'general',
                intent_confidence: result.understanding?.confidence || 0,
                entities: result.understanding?.entities || {},
                action_result: result.action_result || null,
                session_id: result.session_id || null,
                turn: result.turn || 0,
                sentiment: result.response?.sentiment || null,
            };
        } catch (error: any) {
            // Fallback: if AI Brain conversation endpoint fails, try basic STT + echo
            console.error('AI Brain conversation failed, falling back to basic STT:', error.message);

            try {
                const transcript = await this.transcribeAudio(audioBuffer, filename, language);
                const responseText = `I heard you say: "${transcript.text}". The full AI pipeline is temporarily unavailable.`;
                const audioResponse = await this.synthesizeSpeech(responseText, voice);

                return {
                    transcript: transcript.text,
                    response_text: responseText,
                    audio_base64: audioResponse.toString('base64'),
                    language: transcript.language,
                    confidence: transcript.confidence,
                    intent: 'unknown',
                    domain: 'general',
                    action_result: null,
                    fallback: true,
                };
            } catch (fallbackError) {
                throw error; // Re-throw original error if fallback also fails
            }
        }
    }

    /**
     * List available TTS voices
     */
    async listVoices(): Promise<any> {
        const client = this.ensureClient();
        const response = await client.get('/api/ai/voice/voices');
        return response.data;
    }

    /**
     * Get supported audio formats
     */
    async getSupportedFormats(): Promise<any> {
        const client = this.ensureClient();
        const response = await client.get('/api/ai/voice/supported-formats');
        return response.data;
    }
}

export const aiService = new AIService();
