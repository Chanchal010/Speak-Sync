/**
 * RabbitMQ Connection Manager
 * Manages persistent connection to RabbitMQ with auto-reconnect
 */
import amqp from 'amqplib';
import type { Channel, ConsumeMessage } from 'amqplib';

class RabbitMQConnection {
  private static instance: RabbitMQConnection;
  private connection: any = null; // amqplib's Connection type has compatibility issues
  private channel: Channel | null = null;
  private isConnecting = false;
  private reconnectAttempts = 0;
  private readonly MAX_RECONNECT_ATTEMPTS = 10;
  private readonly RECONNECT_DELAY = 5000; // 5 seconds

  private constructor() {}

  static getInstance(): RabbitMQConnection {
    if (!RabbitMQConnection.instance) {
      RabbitMQConnection.instance = new RabbitMQConnection();
    }
    return RabbitMQConnection.instance;
  }

  async connect(): Promise<void> {
    if (this.connection && this.channel) {
      console.log('[SUCCESS] RabbitMQ already connected');
      return;
    }

    if (this.isConnecting) {
      console.log('[INFO] RabbitMQ connection in progress...');
      return;
    }

    this.isConnecting = true;

    try {
      const rabbitUrl = process.env.RABBITMQ_URL;
      if (!rabbitUrl) {
        throw new Error('RABBITMQ_URL environment variable is not set');
      }

      console.log('[INFO] Connecting to RabbitMQ...');

      this.connection = await amqp.connect(rabbitUrl, {
        heartbeat: 60,
      });

      this.channel = await this.connection.createChannel();
      
      // Set prefetch for consumer load balancing
      await this.channel.prefetch(10);

      this.reconnectAttempts = 0;
      this.isConnecting = false;

      console.log('[SUCCESS] RabbitMQ connected successfully');

      // Handle connection errors
      this.connection.on('error', (err) => {
        console.error('[ERROR] RabbitMQ connection error:', err);
        this.reconnect();
      });

      this.connection.on('close', () => {
        console.warn('[WARNING] RabbitMQ connection closed');
        this.reconnect();
      });

      this.channel.on('error', (err) => {
        console.error('[ERROR] RabbitMQ channel error:', err);
      });

      this.channel.on('close', () => {
        console.warn('[WARNING] RabbitMQ channel closed');
      });
    } catch (error) {
      this.isConnecting = false;
      console.error('[ERROR] Failed to connect to RabbitMQ:', error);
      throw error;
    }
  }

  private async reconnect(): Promise<void> {
    if (this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
      console.error(
        `[ERROR] Max reconnection attempts (${this.MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`
      );
      process.exit(1);
    }

    this.connection = null;
    this.channel = null;
    this.reconnectAttempts++;

    const delay = this.RECONNECT_DELAY * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `[INFO] Reconnecting to RabbitMQ (attempt ${this.reconnectAttempts}/${this.MAX_RECONNECT_ATTEMPTS}) in ${delay}ms...`
    );

    setTimeout(() => {
      this.connect().catch((err) => {
        console.error('[ERROR] Reconnection failed:', err);
      });
    }, delay);
  }

  getChannel(): Channel {
    if (!this.channel) {
      throw new Error('RabbitMQ channel is not available. Call connect() first.');
    }
    return this.channel;
  }

  getConnection(): any {
    if (!this.connection) {
      throw new Error('RabbitMQ connection is not available. Call connect() first.');
    }
    return this.connection;
  }

  isConnected(): boolean {
    return this.connection !== null && this.channel !== null;
  }

  async close(): Promise<void> {
    try {
      if (this.channel) {
        await this.channel.close();
        this.channel = null;
      }
      if (this.connection) {
        await this.connection.close();
        this.connection = null;
      }
      console.log('[SUCCESS] RabbitMQ connection closed gracefully');
    } catch (error) {
      console.error('[ERROR] Error closing RabbitMQ connection:', error);
    }
  }
}

export const rabbitmqConnection = RabbitMQConnection.getInstance();
export { Channel, ConsumeMessage };
