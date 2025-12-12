-- DropForeignKey
ALTER TABLE "Event" DROP CONSTRAINT "Event_userId_fkey";

-- AlterTable
ALTER TABLE "Event" ADD COLUMN     "attendancePattern" JSONB,
ADD COLUMN     "attendees" JSONB,
ADD COLUMN     "colorHex" TEXT,
ADD COLUMN     "conflictResolutions" JSONB,
ADD COLUMN     "contextMetadata" JSONB,
ADD COLUMN     "deletedAt" TIMESTAMP(3),
ADD COLUMN     "estimatedDuration" INTEGER,
ADD COLUMN     "eventType" TEXT,
ADD COLUMN     "exceptionDates" JSONB,
ADD COLUMN     "isAllDay" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "location" TEXT,
ADD COLUMN     "organizerId" TEXT,
ADD COLUMN     "parentEventId" TEXT,
ADD COLUMN     "preferredTimeSlots" JSONB,
ADD COLUMN     "recurrenceEnd" TIMESTAMP(3),
ADD COLUMN     "recurrenceRule" TEXT,
ADD COLUMN     "reminders" JSONB,
ADD COLUMN     "rescheduleCount" INTEGER NOT NULL DEFAULT 0,
ADD COLUMN     "sentimentScore" DOUBLE PRECISION,
ADD COLUMN     "voiceTranscript" TEXT;

-- CreateIndex
CREATE INDEX "Event_userId_idx" ON "Event"("userId");

-- CreateIndex
CREATE INDEX "Event_startTime_idx" ON "Event"("startTime");

-- CreateIndex
CREATE INDEX "Event_endTime_idx" ON "Event"("endTime");

-- CreateIndex
CREATE INDEX "Event_isRecurring_idx" ON "Event"("isRecurring");

-- CreateIndex
CREATE INDEX "Event_parentEventId_idx" ON "Event"("parentEventId");

-- CreateIndex
CREATE INDEX "Event_deletedAt_idx" ON "Event"("deletedAt");

-- CreateIndex
CREATE INDEX "Event_userId_startTime_deletedAt_idx" ON "Event"("userId", "startTime", "deletedAt");

-- CreateIndex
CREATE INDEX "Event_userId_isRecurring_idx" ON "Event"("userId", "isRecurring");

-- AddForeignKey
ALTER TABLE "Event" ADD CONSTRAINT "Event_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
