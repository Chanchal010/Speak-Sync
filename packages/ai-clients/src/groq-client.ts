import axios from 'axios';

export class GroqClient {
  constructor(private apiKey: string) { }

  async chat(prompt: string): Promise<string> {
    // Implementation here
    return 'Response from Groq';
  }
}
