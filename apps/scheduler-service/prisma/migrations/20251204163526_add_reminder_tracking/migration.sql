-- AlterTable
ALTER TABLE "Event" ADD COLUMN     "lastReminderSentAt" TIMESTAMP(3);

-- AlterTable
ALTER TABLE "Task" ADD COLUMN     "lastReminderSentAt" TIMESTAMP(3);
