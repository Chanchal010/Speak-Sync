/**
 * Base Consumer Class
 * Abstract class providing common functionality for all RabbitMQ consumers
 */
import { Channel, ConsumeMessage } from 'amqplib';
import { rabbitmqConnection } from '../config/connection';

export interface ConsumerOptions {
  queueName: string;
  prefetchCount?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

export abstract class BaseConsumer {
  protected channel: Channel;
  protected queueName: string;
  protected prefetchCount: number;
  protected retryAttempts: number;
  protected retryDelay: number;
  protected isConsuming = false;
  protected consumerTag: string | null = null;

  constructor(options: ConsumerOptions) {
    this.queueName = options.queueName;
    this.prefetchCount = options.prefetchCount || 10;
    this.retryAttempts = options.retryAttempts || 3;
    this.retryDelay = options.retryDelay || 5000;
    this.channel = rabbitmqConnection.getChannel();
  }

  /**
   * Abstract method to be implemented by child classes
   * Contains the business logic for processing messages
   */
  protected abstract processMessage(message: any): Promise<void>;

  /**
   * Start consuming messages from the queue
   */
  async startConsuming(): Promise<void> {
    if (this.isConsuming) {
      console.log(`[INFO] Consumer already consuming from queue: ${this.queueName}`);
      return;
    }

    try {
      // Set prefetch count for this consumer
      await this.channel.prefetch(this.prefetchCount);

      console.log(`[INFO] Starting consumer for queue: ${this.queueName}`);

      // Start consuming messages
      const consumeResult = await this.channel.consume(
        this.queueName,
        async (msg) => {
          if (msg) {
            await this.handleMessage(msg);
          }
        },
        {
          noAck: false, // Require manual acknowledgment
        }
      );

      this.consumerTag = consumeResult.consumerTag;
      this.isConsuming = true;

      console.log(
        `[SUCCESS] Consumer started for queue: ${this.queueName} (tag: ${this.consumerTag})`
      );
    } catch (error) {
      console.error(`[ERROR] Failed to start consumer for ${this.queueName}:`, error);
      throw error;
    }
  }

  /**
   * Handle incoming message with error handling and acknowledgment
   */
  private async handleMessage(msg: ConsumeMessage): Promise<void> {
    const startTime = Date.now();
    let messageContent: any;

    try {
      // Parse message content
      messageContent = JSON.parse(msg.content.toString());
      
      console.log(`[INFO] Processing message from ${this.queueName}:`, {
        eventId: messageContent.eventId,
        eventType: messageContent.eventType,
      });

      // Process the message (implemented by child class)
      await this.processMessage(messageContent);

      // Acknowledge successful processing
      this.channel.ack(msg);

      const duration = Date.now() - startTime;
      console.log(
        `[SUCCESS] Message processed successfully from ${this.queueName} in ${duration}ms`
      );
    } catch (error) {
      console.error(`[ERROR] Error processing message from ${this.queueName}:`, error);

      // Check retry attempts
      const retryCount = this.getRetryCount(msg);

      if (retryCount < this.retryAttempts) {
        // Retry the message
        console.log(
          `[INFO] Retrying message (attempt ${retryCount + 1}/${this.retryAttempts})`
        );
        await this.retryMessage(msg, retryCount);
      } else {
        // Max retries exceeded, send to DLQ
        console.error(
          `[ERROR] Max retry attempts (${this.retryAttempts}) exceeded. Sending to DLQ.`
        );
        await this.sendToDeadLetterQueue(msg, error);
      }

      // Reject the message (it's been requeued or sent to DLQ)
      this.channel.nack(msg, false, false);
    }
  }

  /**
   * Get the current retry count from message headers
   */
  private getRetryCount(msg: ConsumeMessage): number {
    return (msg.properties.headers?.['x-retry-count'] as number) || 0;
  }

  /**
   * Retry message by republishing with incremented retry count
   */
  private async retryMessage(msg: ConsumeMessage, currentRetryCount: number): Promise<void> {
    try {
      const newRetryCount = currentRetryCount + 1;
      const delay = this.retryDelay * Math.pow(2, currentRetryCount); // Exponential backoff

      console.log(`[INFO] Scheduling retry in ${delay}ms...`);

      // Wait before retrying
      await new Promise((resolve) => setTimeout(resolve, delay));

      // Republish message with updated retry count
      this.channel.sendToQueue(this.queueName, msg.content, {
        ...msg.properties,
        headers: {
          ...msg.properties.headers,
          'x-retry-count': newRetryCount,
          'x-first-death-reason': msg.properties.headers?.['x-first-death-reason'] || 'processing-error',
        },
        persistent: true,
      });

      console.log(`[INFO] Message requeued for retry (attempt ${newRetryCount})`);
    } catch (error) {
      console.error('[ERROR] Failed to retry message:', error);
    }
  }

  /**
   * Send failed message to Dead Letter Queue
   */
  private async sendToDeadLetterQueue(msg: ConsumeMessage, error: any): Promise<void> {
    try {
      const dlqName = 'dlq.retry';

      // Parse original message
      let messageContent: any;
      try {
        messageContent = JSON.parse(msg.content.toString());
      } catch {
        messageContent = msg.content.toString();
      }

      // Create DLQ message with error details
      const dlqMessage = {
        originalQueue: this.queueName,
        originalMessage: messageContent,
        error: {
          message: error.message,
          stack: error.stack,
          timestamp: new Date().toISOString(),
        },
        retryCount: this.getRetryCount(msg),
        headers: msg.properties.headers,
      };

      // Send to DLQ
      this.channel.sendToQueue(dlqName, Buffer.from(JSON.stringify(dlqMessage)), {
        persistent: true,
        headers: {
          'x-original-queue': this.queueName,
          'x-death-timestamp': Date.now(),
        },
      });

      console.log(`[INFO] Message sent to DLQ: ${dlqName}`);
    } catch (error) {
      console.error('[ERROR] Failed to send message to DLQ:', error);
    }
  }

  /**
   * Stop consuming messages
   */
  async stopConsuming(): Promise<void> {
    if (!this.isConsuming || !this.consumerTag) {
      console.log(`[INFO] Consumer not active for queue: ${this.queueName}`);
      return;
    }

    try {
      await this.channel.cancel(this.consumerTag);
      this.isConsuming = false;
      this.consumerTag = null;
      console.log(`[SUCCESS] Consumer stopped for queue: ${this.queueName}`);
    } catch (error) {
      console.error(`[ERROR] Failed to stop consumer for ${this.queueName}:`, error);
    }
  }

  /**
   * Check if consumer is active
   */
  isActive(): boolean {
    return this.isConsuming;
  }

  /**
   * Get queue name
   */
  getQueueName(): string {
    return this.queueName;
  }
}
