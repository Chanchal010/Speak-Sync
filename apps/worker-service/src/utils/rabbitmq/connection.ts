import * as amqp from 'amqplib';

/**
 * RabbitMQ Connection Manager - Singleton Pattern
 * Handles connection lifecycle with auto-reconnect and connection pooling
 */
class RabbitMQConnection {
  private static instance: RabbitMQConnection;
  private connection: any = null;
  private channel: any = null;
  private isConnecting: boolean = false;
  private reconnectAttempts: number = 0;
  private readonly MAX_RECONNECT_ATTEMPTS: number = 10;
  private readonly RECONNECT_DELAY: number = 5000; // 5 seconds

  private constructor() {}

  /**
   * Get singleton instance
   */
  public static getInstance(): RabbitMQConnection {
    if (!RabbitMQConnection.instance) {
      RabbitMQConnection.instance = new RabbitMQConnection();
    }
    return RabbitMQConnection.instance;
  }

  /**
   * Connect to RabbitMQ
   */
  public async connect(): Promise<void> {
    if (this.connection && this.channel) {
      console.log('✅ RabbitMQ already connected');
      return;
    }

    if (this.isConnecting) {
      console.log('⏳ RabbitMQ connection in progress...');
      return;
    }

    this.isConnecting = true;

    try {
      const rabbitUrl = process.env.RABBITMQ_URL;
      if (!rabbitUrl) {
        throw new Error('RABBITMQ_URL environment variable is not set');
      }

      console.log('🔌 Connecting to RabbitMQ...');
      const connection = await amqp.connect(rabbitUrl);
      this.connection = connection;
      
      // Handle connection errors
      connection.on('error', (err) => {
        console.error('❌ RabbitMQ connection error:', err.message);
        this.handleDisconnect();
      });

      // Handle connection close
      connection.on('close', () => {
        console.warn('⚠️  RabbitMQ connection closed');
        this.handleDisconnect();
      });

      // Create channel
      const channel = await connection.createChannel();
      this.channel = channel;
      
      // Handle channel errors
      this.channel.on('error', (err) => {
        console.error('❌ RabbitMQ channel error:', err.message);
      });

      // Handle channel close
      this.channel.on('close', () => {
        console.warn('⚠️  RabbitMQ channel closed');
      });

      // Enable publisher confirms for reliable messaging
      await this.channel.assertQueue('', { durable: true });

      this.reconnectAttempts = 0;
      this.isConnecting = false;
      console.log('✅ RabbitMQ connected successfully');
    } catch (error) {
      this.isConnecting = false;
      console.error('❌ Failed to connect to RabbitMQ:', error);
      await this.reconnect();
    }
  }

  /**
   * Handle disconnection and trigger reconnect
   */
  private async handleDisconnect(): Promise<void> {
    this.connection = null;
    this.channel = null;
    await this.reconnect();
  }

  /**
   * Reconnect with exponential backoff
   */
  private async reconnect(): Promise<void> {
    if (this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
      console.error(
        `❌ Max reconnection attempts (${this.MAX_RECONNECT_ATTEMPTS}) reached. Giving up.`
      );
      process.exit(1); // Exit process to let orchestrator restart
    }

    this.reconnectAttempts++;
    const delay = this.RECONNECT_DELAY * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(
      `🔄 Reconnecting to RabbitMQ (attempt ${this.reconnectAttempts}/${this.MAX_RECONNECT_ATTEMPTS}) in ${delay}ms...`
    );

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Get active channel
   */
  public getChannel(): any {
    if (!this.channel) {
      console.warn('⚠️ RabbitMQ channel is not available');
      return null;
    }
    return this.channel;
  }

  /**
   * Get active connection
   */
  public getConnection(): any {
    if (!this.connection) {
      console.warn('⚠️ RabbitMQ connection is not available');
      return null;
    }
    return this.connection;
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.connection !== null && this.channel !== null;
  }

  /**
   * Close connection gracefully
   */
  public async close(): Promise<void> {
    try {
      const channel = this.channel;
      if (channel) {
        await channel.close();
        this.channel = null;
      }
      const connection = this.connection;
      if (connection) {
        await connection.close();
        this.connection = null;
      }
      console.log('✅ RabbitMQ connection closed gracefully');
    } catch (error) {
      console.error('❌ Error closing RabbitMQ connection:', error);
    }
  }
}

export default RabbitMQConnection;
