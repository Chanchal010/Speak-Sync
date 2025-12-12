import { serviceRegistry } from './service-registry.service.js';
import { AxiosInstance } from 'axios';

/**
 * AI Brain Service Client
 * Proxies requests to AI Brain Service (STT, TTS, NLU, Conversations, Scheduling, Habits, Memory)
 */
export class AIBrainService {
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
     * Forward request to AI Brain service
     */
    async forwardRequest(
        method: string,
        path: string,
        data?: any,
        headers?: Record<string, string>
    ): Promise<any> {
        const client = this.ensureClient();

        const config: any = {
            method,
            url: path,
            headers: headers || {}
        };

        if (data) {
            if (data instanceof FormData || Buffer.isBuffer(data)) {
                config.data = data;
            } else {
                config.data = data;
            }
        }

        const response = await client.request(config);
        return response.data;
    }

    // === Voice Endpoints ===

    /**
     * POST /api/ai/voice/transcribe
     * Speech-to-Text
     */
    async transcribe(audioFile: Buffer, language?: string): Promise<any> {
        const FormData = (await import('form-data')).default;
        const form = new FormData();
        form.append('file', audioFile, { filename: 'audio.wav' });
        if (language) form.append('language', language);

        return this.forwardRequest('POST', '/api/ai/voice/transcribe', form, {
            ...form.getHeaders()
        });
    }

    /**
     * POST /api/ai/voice/synthesize
     * Text-to-Speech
     */
    async synthesize(text: string, voice?: string): Promise<Buffer> {
        const response = await this.ensureClient().post(
            '/api/ai/voice/synthesize',
            { text, voice },
            { responseType: 'arraybuffer' }
        );
        return Buffer.from(response.data);
    }

    /**
     * GET /api/ai/voice/voices
     * List available voices
     */
    async getVoices(): Promise<any> {
        return this.forwardRequest('GET', '/api/ai/voice/voices');
    }

    // === Chat Endpoints ===

    /**
     * POST /api/ai/chat
     * Generate chat response
     */
    async chat(message: string, context?: any): Promise<any> {
        return this.forwardRequest('POST', '/api/ai/chat', { message, context });
    }

    // === Conversation Endpoints ===

    /**
     * POST /api/ai/conversation/voice
     * Full voice conversation (STT -> NLU -> TTS)
     */
    async voiceConversation(audioFile: Buffer, sessionId?: string, voiceProfile?: string): Promise<any> {
        const FormData = (await import('form-data')).default;
        const form = new FormData();
        form.append('audio', audioFile, { filename: 'voice.wav' });
        if (sessionId) form.append('session_id', sessionId);
        if (voiceProfile) form.append('voice_profile', voiceProfile);

        return this.forwardRequest('POST', '/api/ai/conversation/voice', form, {
            ...form.getHeaders()
        });
    }

    /**
     * POST /api/ai/conversation/text
     * Text conversation with voice response
     */
    async textConversation(text: string, sessionId?: string, voiceProfile?: string): Promise<any> {
        return this.forwardRequest('POST', '/api/ai/conversation/text', {
            text,
            session_id: sessionId,
            voice_profile: voiceProfile
        });
    }

    // === Scheduling Endpoints ===

    /**
     * POST /api/scheduling/*
     * Forward scheduling requests
     */
    async scheduleAnalyzeConflicts(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/scheduling/analyze-conflicts', data);
    }

    async scheduleSuggestTimeSlot(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/scheduling/suggest-time-slot', data);
    }

    async scheduleOptimize(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/scheduling/optimize-schedule', data);
    }

    async scheduleSmartSuggestions(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/scheduling/smart-suggestions', data);
    }

    async scheduleGetPatterns(userId: string): Promise<any> {
        return this.forwardRequest('GET', `/api/scheduling/patterns/${userId}`);
    }

    // === Habits Endpoints ===

    /**
     * POST /api/habits/*
     * Forward habit prediction requests
     */
    async habitsAnalyzePatterns(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/analyze-patterns', data);
    }

    async habitsPredictStreak(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/predict-streak', data);
    }

    async habitsPredictCompletion(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/predict-next-completion', data);
    }

    async habitsGetInsights(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/personalized-insights', data);
    }

    async habitsOptimalSchedule(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/optimal-schedule', data);
    }

    async habitsFormationPrediction(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/formation-prediction', data);
    }

    async habitsGetStrength(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/habits/habit-strength', data);
    }

    async habitsGetMomentum(userId: string, habitType: string): Promise<any> {
        return this.forwardRequest('GET', `/api/habits/momentum/${userId}/${habitType}`);
    }

    // === Memory Endpoints ===

    /**
     * POST /api/memory/*
     * Forward vector memory requests
     */
    async memoryStoreConversation(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/memory/store-conversation', data);
    }

    async memoryRecallConversations(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/memory/recall-conversations', data);
    }

    async memoryStoreContext(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/memory/store-context', data);
    }

    async memoryRetrieveContext(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/memory/retrieve-context', data);
    }

    async memoryGetSummary(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/memory/contextual-summary', data);
    }

    async memoryGetStats(userId: string): Promise<any> {
        return this.forwardRequest('GET', `/api/memory/stats/${userId}`);
    }

    async memoryExtractContexts(data: any): Promise<any> {
        return this.forwardRequest('POST', '/api/memory/extract-contexts', data);
    }

    /**
     * Generic proxy for any AI Brain endpoint
     */
    async proxy(method: string, path: string, data?: any, headers?: Record<string, string>): Promise<any> {
        return this.forwardRequest(method, path, data, headers);
    }
}

export const aiBrainService = new AIBrainService();
