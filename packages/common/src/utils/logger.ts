export class Logger {
  static info(message: string, meta?: any) {
    console.log(`[INFO] ${message}`, meta || '');
  }
  
  static error(message: string, error?: any) {
    console.error(`[ERROR] ${message}`, error || '');
  }
}