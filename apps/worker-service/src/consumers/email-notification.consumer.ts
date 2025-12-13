/**
 * Email Notification Consumer
 * Processes email notification events and sends emails
 */
import { BaseConsumer } from './base.consumer.js';
import { RABBITMQ_CONFIG } from '../config/rabbitmq';
import nodemailer from 'nodemailer';

interface EmailNotificationEvent {
  eventId: string;
  eventType: string;
  timestamp: string;
  userId: string;
  email: string;
  subject: string;
  body: string;
  template?: string;
  metadata?: {
    priority?: 'low' | 'medium' | 'high';
    category?: string;
    tags?: string[];
  };
}

export class EmailNotificationConsumer extends BaseConsumer {
  private transporter: nodemailer.Transporter | null = null;

  constructor() {
    super({
      queueName: RABBITMQ_CONFIG.QUEUES.EMAIL_NOTIFICATIONS,
      prefetchCount: 5, // Lower prefetch for email sending
      retryAttempts: 3,
      retryDelay: 10000, // 10 seconds between retries for emails
    });

    this.initializeTransporter();
  }

  /**
   * Initialize email transporter
   */
  private initializeTransporter(): void {
    const emailConfig = {
      host: process.env.EMAIL_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '587'),
      secure: process.env.EMAIL_SECURE === 'true',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASSWORD,
      },
    };

    if (!emailConfig.auth.user || !emailConfig.auth.pass) {
      console.warn('[WARNING] Email credentials not configured. Emails will be logged only.');
      return;
    }

    try {
      this.transporter = nodemailer.createTransport(emailConfig);
      console.log('[SUCCESS] Email transporter initialized');
    } catch (error) {
      console.error('[ERROR] Failed to initialize email transporter:', error);
    }
  }

  /**
   * Process email notification messages
   */
  protected async processMessage(message: EmailNotificationEvent): Promise<void> {
    const { userId, email, subject, body, template, metadata } = message;

    console.log(`[INFO] Processing email notification for user: ${userId}, email: ${email}`);

    try {
      // Validate email address
      if (!this.isValidEmail(email)) {
        throw new Error(`Invalid email address: ${email}`);
      }

      // Determine if we should use a template
      const emailContent = template
        ? await this.renderTemplate(template, message)
        : body;

      // Send email
      if (this.transporter) {
        await this.sendEmail({
          to: email,
          subject,
          html: emailContent,
          priority: metadata?.priority || 'medium',
        });

        console.log(`[SUCCESS] Email sent to ${email}: ${subject}`);
      } else {
        // Transporter not available, log the email
        console.log('[INFO] Email transporter not configured. Logging email:', {
          to: email,
          subject,
          preview: emailContent.substring(0, 100) + '...',
        });
      }

      // Track email sent (for analytics)
      await this.trackEmailSent(userId, email, subject, metadata);
    } catch (error) {
      console.error(`[ERROR] Failed to send email to ${email}:`, error);
      throw error; // Rethrow to trigger retry logic
    }
  }

  /**
   * Send email using nodemailer
   */
  private async sendEmail(options: {
    to: string;
    subject: string;
    html: string;
    priority: string;
  }): Promise<void> {
    if (!this.transporter) {
      throw new Error('Email transporter not initialized');
    }

    const mailOptions = {
      from: `"Speak-Sync" <${process.env.EMAIL_FROM || 'noreply@speak-sync.com'}>`,
      to: options.to,
      subject: options.subject,
      html: options.html,
      priority: options.priority as 'high' | 'normal' | 'low',
    };

    await this.transporter.sendMail(mailOptions);
  }

  /**
   * Validate email address format
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Render email template
   */
  private async renderTemplate(
    templateName: string,
    data: EmailNotificationEvent
  ): Promise<string> {
    // TODO: Integrate with email template engine (Handlebars, EJS, etc.)
    console.log(`[INFO] Rendering email template: ${templateName}`);

    // For now, return basic template
    switch (templateName) {
      case 'task_reminder':
        return this.getTaskReminderTemplate(data);
      case 'habit_streak':
        return this.getHabitStreakTemplate(data);
      case 'welcome':
        return this.getWelcomeTemplate(data);
      default:
        return data.body;
    }
  }

  /**
   * Task reminder email template
   */
  private getTaskReminderTemplate(data: EmailNotificationEvent): string {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
            .button { display: inline-block; background: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📋 Task Reminder</h1>
            </div>
            <div class="content">
              <h2>${data.subject}</h2>
              <p>${data.body}</p>
              <a href="${process.env.APP_URL || 'https://speak-sync.com'}/tasks" class="button">
                View Task
              </a>
            </div>
            <div class="footer">
              <p>You're receiving this because you have notifications enabled in Speak-Sync.</p>
              <p>&copy; 2025 Speak-Sync. All rights reserved.</p>
            </div>
          </div>
        </body>
      </html>
    `;
  }

  /**
   * Habit streak email template
   */
  private getHabitStreakTemplate(data: EmailNotificationEvent): string {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
            .streak-badge { background: #FFA500; color: white; font-size: 48px; font-weight: bold; width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 20px auto; }
            .button { display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🔥 Habit Streak Achievement!</h1>
            </div>
            <div class="content">
              <h2>${data.subject}</h2>
              <div class="streak-badge">🔥</div>
              <p style="text-align: center; font-size: 18px;">${data.body}</p>
              <center>
                <a href="${process.env.APP_URL || 'https://speak-sync.com'}/habits" class="button">
                  View Your Progress
                </a>
              </center>
            </div>
            <div class="footer">
              <p>Keep up the amazing work! You're building great habits.</p>
              <p>&copy; 2025 Speak-Sync. All rights reserved.</p>
            </div>
          </div>
        </body>
      </html>
    `;
  }

  /**
   * Welcome email template
   */
  private getWelcomeTemplate(data: EmailNotificationEvent): string {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #10B981; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
            .button { display: inline-block; background: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>👋 Welcome to Speak-Sync!</h1>
            </div>
            <div class="content">
              <h2>${data.subject}</h2>
              <p>${data.body}</p>
              <center>
                <a href="${process.env.APP_URL || 'https://speak-sync.com'}/dashboard" class="button">
                  Get Started
                </a>
              </center>
            </div>
            <div class="footer">
              <p>Thanks for joining us! We're excited to help you achieve your goals.</p>
              <p>&copy; 2025 Speak-Sync. All rights reserved.</p>
            </div>
          </div>
        </body>
      </html>
    `;
  }

  /**
   * Track email sent for analytics
   */
  private async trackEmailSent(
    userId: string,
    email: string,
    subject: string,
    metadata?: any
  ): Promise<void> {
    // TODO: Store email tracking in database for analytics
    console.log('[INFO] Tracking email sent:', {
      userId,
      email,
      subject,
      timestamp: new Date().toISOString(),
      category: metadata?.category,
    });

    // Simulate async operation
    await new Promise((resolve) => setTimeout(resolve, 50));
  }

  /**
   * Verify email transporter connection
   */
  async verifyConnection(): Promise<boolean> {
    if (!this.transporter) {
      return false;
    }

    try {
      await this.transporter.verify();
      console.log('[SUCCESS] Email transporter connection verified');
      return true;
    } catch (error) {
      console.error('[ERROR] Email transporter verification failed:', error);
      return false;
    }
  }
}

// Factory function
export function createEmailNotificationConsumer(): EmailNotificationConsumer {
  return new EmailNotificationConsumer();
}
