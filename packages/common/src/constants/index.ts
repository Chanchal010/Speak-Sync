export const PRIORITY_LEVELS = {
  VI: 'Very Important',
  MI: 'Moderately Important',
  NI: 'Not Important',
} as const;

export const SERVICE_PORTS = {
  GATEWAY: 3000,
  SCHEDULER: 3001,
  WORKER: 3002,
  AI_BRAIN: 8000,
  LIFESTYLE: 8001,
} as const;