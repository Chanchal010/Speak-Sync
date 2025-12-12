# Phase 4: Lifestyle Service - Comprehensive Habit Tracking System
## Architecture & Implementation Plan

**Date**: December 4, 2025  
**Complexity**: HIGH - Multi-habit system with specialized AI features  
**Estimated Duration**: 10-14 days (broken into sub-phases)

---

## 🔍 System Analysis from Wireframes

### Identified Habit Types (6 Categories)

1. **Food** - Meal tracking and nutrition patterns
2. **Exercise** - Physical activity with RPE and recovery tracking
3. **Financial** - Expense/income/savings with behavioral analysis
4. **Sleep** - Chronotype determination and sleep debt tracking
5. **Study** - Focus tracking with "stickiness factor" calculation
6. **Water** - Hydration with cognitive correlation tracking

### Key UI Elements Observed
- Navigation: Task, Calendar, Report (central), Habit Tracker, More
- Each habit has: Name label + "explanation" button
- Report button (central) - generates AI insights
- Export to Sheets functionality
- Infinity symbol (∞) - possibly streak indicator
- Wave/notification icons in header

---

## 📊 Detailed Data Models by Habit Type

### 1. FOOD HABIT

**Objective**: Track eating patterns and nutritional habits

```typescript
// FoodLog Schema
{
  _id: ObjectId,
  userId: String,
  habitId: ObjectId, // Reference to parent Habit
  
  // UI Fields
  mealType: String, // "breakfast" | "lunch" | "dinner" | "snack"
  timestamp: Date,
  description: String,
  portion: String, // "small" | "medium" | "large"
  
  // AI Training Fields
  hungerLevel: Number, // 1-10 before eating
  satisfactionLevel: Number, // 1-10 after eating
  eatingSpeed: String, // "slow" | "moderate" | "fast"
  emotionalState: String, // "stressed" | "happy" | "neutral" | "sad"
  location: String, // "home" | "restaurant" | "work" | "car"
  socialContext: String, // "alone" | "family" | "friends" | "business"
  distractionLevel: Number, // 1-5 (phone/TV while eating)
  
  // Nutrition (Optional - future ML model)
  estimatedCalories: Number,
  macros: {
    protein: Number,
    carbs: Number,
    fats: Number
  },
  
  // Voice & Context
  voiceTranscript: String,
  sentimentScore: Number, // -1.0 to 1.0
  
  createdAt: Date
}
```

**AI Insights**:
- Pattern: "You eat faster when stressed"
- Trigger: "Late night snacking correlates with work deadlines"
- Recommendation: "Schedule dinner at 7 PM - your highest satisfaction time"

---

### 2. EXERCISE HABIT

**Objective**: Track workouts with recovery patterns

```typescript
// ExerciseLog Schema
{
  _id: ObjectId,
  userId: String,
  habitId: ObjectId,
  
  // UI Fields
  activityType: String, // "Yoga" | "HIIT" | "Cardio" | "Lifting" | "Walking"
  duration: Number, // Minutes
  timestamp: Date,
  
  // Critical AI Fields (from wireframe)
  rpe: Number, // Rate of Perceived Exertion (1-10) ⚠️ CRUCIAL for AI
  postActivityEnergy: Number, // 1-5 (energized vs drained)
  focusAreas: Array<String>, // ["Legs", "Mobility", "Mindfulness"]
  
  // Recovery & Context
  sleepQualityBefore: Number, // 1-10
  muscularSoreness: Number, // 1-10
  injuryRisk: Boolean,
  weatherCondition: String, // "hot" | "cold" | "ideal"
  
  // Voice & Sentiment
  voiceTranscript: String,
  voiceSentiment: Number, // -1.0 to 1.0 (out of breath vs relaxed)
  
  // Session Details
  completed: Boolean,
  skippedReason: String, // If not completed
  
  createdAt: Date
}
```

**AI Insight Example** (from wireframe):
> "If the user reports high RPE but low Post-Activity Energy, the AI learns to schedule a 'Recovery Block' immediately after this specific activity type in the future."

**Implementation Priority**: HIGH - RPE tracking is critical

---

### 3. FINANCIAL HABIT

**Objective**: Financial behavioral analyst identifying spending triggers

```typescript
// FinancialLog Schema
{
  _id: ObjectId,
  userId: String,
  habitId: ObjectId,
  
  // UI Fields
  transactionType: String, // "expense" | "income" | "savings"
  amount: Number, // Decimal
  category: String, // "Groceries" | "Impulse Buy" | "Fixed Bill" | etc
  timestamp: Date,
  description: String,
  
  // Behavioral Analysis (from wireframe)
  necessityScore: Number, // 1-5 (need vs want) ⚠️ CRUCIAL
  associatedMood: String, // "Stressed" | "Happy" | "Neutral"
  timeOfPurchase: Date, // Pattern recognition
  
  // Context
  location: String,
  paymentMethod: String, // "card" | "cash" | "digital"
  plannedPurchase: Boolean,
  
  // Savings Tracking
  savingsAllocation: Number, // Percentage of income to savings
  budgetCategory: String,
  overBudget: Boolean,
  
  // Voice & Sentiment
  voiceTranscript: String,
  sentimentScore: Number,
  
  createdAt: Date
}
```

**AI Insight Example** (from wireframe):
> "By tracking Time of Purchase + Mood, the AI can predict 'Impulse Buys' and voice-prompt a warning: 'You usually spend over budget when you are stressed on Thursday nights. Do you want to lock your card?'"

**Implementation Priority**: MEDIUM-HIGH

---

### 4. SLEEP HABIT

**Objective**: Determine user's Chronotype (night owl or early bird) to optimize schedule

```typescript
// SleepLog Schema
{
  _id: ObjectId,
  userId: String,
  habitId: ObjectId,
  
  // Core Sleep Data (from wireframe)
  bedtime: Date,
  wakeTime: Date,
  sleepLatency: Number, // Minutes to fall asleep
  grogginessLevel: Number, // 1-10 (difficulty waking up) ⚠️ CRUCIAL
  sleepDebt: Number, // Hours - rolling average of missed sleep
  
  // Sleep Quality
  sleepQuality: Number, // 1-10
  interruptions: Number, // Wake-up count
  dreamActivity: String, // "vivid" | "none" | "nightmare"
  
  // Context (from wireframe)
  preSleepActivity: String, // "Coding" | "Reading" | "Phone" ⚠️ CRUCIAL
  roomTemperature: Number, // Celsius
  screenTimeBefore: Number, // Minutes before bed
  caffeineHoursBeforeBed: Number,
  exerciseHoursBeforeBed: Number,
  
  // Calculated Fields
  totalSleepHours: Number,
  sleepEfficiency: Number, // Percentage
  
  // Voice & Context
  voiceTranscript: String,
  morningMood: String,
  
  createdAt: Date
}
```

**AI Insight Example** (from wireframe):
> "If Grogginess Level is high when Wake Time is before 7:00 AM, the AI learns to stop scheduling 'Deep Work' tasks before 9:00 AM."

**Chronotype Detection Logic**:
```javascript
// Analyze 21+ days of data
if (avgBedtime > 23:00 && avgWakeTime > 8:00 && grogginessLevelMorning > 7) {
  chronotype = "night_owl";
  recommendedSchedule = "afternoon_heavy";
}
```

**Implementation Priority**: HIGH - Chronotype affects task scheduling in Phase 2

---

### 5. STUDY HABIT

**Objective**: Calculate "Stickiness Factor" - how likely user actually does what they plan

```typescript
// StudyLog Schema
{
  _id: ObjectId,
  userId: String,
  habitId: ObjectId,
  taskId: String, // Link to Task from Phase 2
  
  // Time Tracking (from wireframe)
  scheduledStartTime: Date,
  scheduledEndTime: Date,
  actualStartTime: Date,
  actualEndTime: Date,
  
  // Deviation Analysis ⚠️ CRITICAL FOR AI
  deviationDuration: Number, // Minutes (Actual - Scheduled)
  interruptionCount: Number, // How many times distracted
  
  // Focus & Productivity
  flowStateScore: Number, // 1-5 (in the zone?)
  productivityRating: Number, // 1-10 self-reported
  energyLevelStart: Number, // 1-10
  energyLevelEnd: Number, // 1-10
  
  // Context Tags (from wireframe)
  contextTags: Array<String>, // ["Deep Work", "Meeting", "Admin"]
  taskType: String, // "coding" | "writing" | "reading" | "meeting"
  
  // Environment
  location: String, // "office" | "home" | "cafe"
  distractionSources: Array<String>, // ["phone", "people", "noise"]
  
  // Voice & Sentiment
  voiceTranscript: String,
  sentimentScore: Number,
  
  completed: Boolean,
  abandonedReason: String,
  
  createdAt: Date
}
```

**"Stickiness Factor" Calculation**:
```javascript
stickinessRatio = actualDuration / scheduledDuration;

// If user consistently underestimates "Coding Tasks" by 30%
if (stickinessRatio < 0.7 && taskType === "coding") {
  // AI pads future coding blocks by 30% automatically
  adjustedDuration = scheduledDuration * 1.3;
}
```

**AI Insight Example** (from wireframe):
> "The AI calculates a Deviation Ratio. If the user underestimates 'Coding Tasks' by 30% consistently, the AI will automatically pad future coding blocks by 30% when generating the schedule."

**Implementation Priority**: VERY HIGH - Directly integrates with Phase 2 Tasks

---

### 6. WATER HABIT

**Objective**: Correlate water intake with cognitive sharpness and schedule "Hydration Checkpoints"

```typescript
// WaterLog Schema
{
  _id: ObjectId,
  userId: String,
  habitId: ObjectId,
  
  // Hydration Data (from wireframe)
  intakeVolume: Number, // ml ⚠️ CRUCIAL
  timestamp: Date,
  
  // Dehydration Indicators
  urineColor: Number, // 1-8 (Armstrong Scale) ⚠️ Gold Standard
  thirstIntensity: Number, // 1-5
  
  // Physiological Tracking
  caffeineIntake: Number, // mg (diuretic - must subtract)
  environmentTemp: Number, // °C (affects requirement)
  exerciseMinutes: Number, // Increases need
  
  // Cognitive Impact ⚠️ CRUCIAL FOR AI
  cognitiveFog: Boolean, // Struggling to find words? (voice fluency)
  energyLevel: Number, // 1-10
  headache: Boolean,
  
  // Context
  activityLevel: String, // "sedentary" | "active" | "intense"
  location: String,
  
  // Voice Analysis
  voiceTranscript: String,
  voiceFluency: Number, // Words per minute
  
  createdAt: Date
}
```

**AI Insight Example** (from wireframe):
> "The AI looks for the '2 PM Crash Pattern.' If Intake Volume < 1000ml by 1:00 PM, and Cognitive Fog is detected in voice notes, the AI learns to schedule a mandatory 'Water & Walk' break at 1:30 PM to save the afternoon work block."

**Hydration Calculation**:
```javascript
requiredIntake = (bodyWeight * 35) + exerciseMinutes * 15 - caffeineIntake * 0.5;

if (currentIntake < requiredIntake * 0.5 && time > "13:00" && cognitiveFog === true) {
  triggerAlert("Hydration Checkpoint - 500ml needed");
  scheduleBreak("14:00", "Water & Walk", 15);
}
```

**Implementation Priority**: MEDIUM - Affects afternoon productivity

---

## 🏗️ Implementation Architecture

### Technology Stack

```
┌─────────────────────────────────────┐
│   Lifestyle Service (Python/FastAPI) │
├─────────────────────────────────────┤
│  - Port: 8001                       │
│  - MongoDB Atlas Connection         │
│  - Mongoose ODM (via Pymongo)       │
│  - Pydantic validation              │
│  - Aggregation pipelines            │
└─────────────────────────────────────┘
         │
         ├──> MongoDB Collections:
         │    - habits (base collection)
         │    - food_logs
         │    - exercise_logs
         │    - financial_logs
         │    - sleep_logs
         │    - study_logs
         │    - water_logs
         │    - habit_insights (AI generated)
         │
         └──> Integrations:
              - Phase 2 Tasks (Study habit)
              - Phase 3 Events (Scheduling conflicts)
              - Phase 6 AI Brain (Pattern analysis)
```

### Database Design Strategy

**Option 1: Single Collection with Type Discriminator** (Recommended)
```javascript
// Base Habit Document
{
  _id: ObjectId,
  userId: String,
  habitType: String, // "food" | "exercise" | "financial" | "sleep" | "study" | "water"
  name: String,
  color: String,
  isActive: Boolean,
  
  // Common tracking
  currentStreak: Number,
  longestStreak: Number,
  totalLogs: Number,
  
  // Type-specific data in nested object
  config: {
    // Food-specific
    targetMeals?: Number,
    trackMacros?: Boolean,
    
    // Exercise-specific
    targetWorkouts?: Number,
    preferredTypes?: Array,
    
    // Financial-specific
    monthlyBudget?: Number,
    savingsGoal?: Number,
    
    // Sleep-specific
    targetSleepHours?: Number,
    idealBedtime?: String,
    
    // Study-specific
    targetHours?: Number,
    focusGoal?: Number,
    
    // Water-specific
    targetIntake?: Number,
    bodyWeight?: Number
  },
  
  // AI metadata
  aiInsights: Array,
  lastAnalyzed: Date,
  
  createdAt: Date,
  updatedAt: Date,
  deletedAt: Date
}

// Separate Log Collections (one per type)
food_logs: { ... }
exercise_logs: { ... }
financial_logs: { ... }
sleep_logs: { ... }
study_logs: { ... }
water_logs: { ... }
```

**Why Separate Log Collections?**
- Different indexes for different query patterns
- Schema flexibility per habit type
- Better aggregation performance
- Easier to add new habit types

---

## 📋 Implementation Phases (10 Sub-Phases)

### Phase 4.1: Infrastructure Setup (Days 1-2)
**Deliverables**:
- [ ] MongoDB Atlas setup and connection
- [ ] Lifestyle Service FastAPI scaffolding
- [ ] Base Habit model with CRUD
- [ ] Soft delete implementation
- [ ] Health check endpoint
- [ ] User context middleware

**Files**:
```
apps/lifestyle-service/
├── src/
│   ├── main.py
│   ├── config/
│   │   └── database.py (MongoDB connection)
│   ├── models/
│   │   └── habit.py (Base Habit model)
│   ├── schemas/
│   │   └── habit.py (Pydantic validation)
│   ├── services/
│   │   └── habit_service.py
│   ├── api/
│   │   └── routes/
│   │       └── habits.py
│   └── utils/
│       └── streak_calculator.py
```

---

### Phase 4.2: Food Habit System (Days 3-4)
**Deliverables**:
- [ ] FoodLog model with nutrition tracking
- [ ] Meal logging API endpoints
- [ ] Eating pattern analysis
- [ ] Voice transcript integration
- [ ] Basic insights generation

**API Endpoints**:
```
POST   /api/habits/food              - Create food habit
POST   /api/habits/:id/food-logs     - Log meal
GET    /api/habits/:id/food-logs     - Get meal history
GET    /api/habits/:id/food-stats    - Eating patterns
```

---

### Phase 4.3: Exercise Habit System (Days 5-6)
**Deliverables**:
- [ ] ExerciseLog model with RPE tracking
- [ ] Workout logging with recovery data
- [ ] Post-activity energy correlation
- [ ] Recovery block scheduling logic
- [ ] Voice sentiment analysis

**Key Feature**: **RPE vs Post-Activity Energy** correlation for recovery scheduling

---

### Phase 4.4: Financial Habit System (Days 7-8)
**Deliverables**:
- [ ] FinancialLog model with behavioral data
- [ ] Transaction categorization
- [ ] Necessity score tracking
- [ ] Mood-spending correlation
- [ ] Impulse buy detection algorithm

**Key Feature**: **Time + Mood** pattern detection for spending triggers

---

### Phase 4.5: Sleep Habit System (Days 9-10)
**Deliverables**:
- [ ] SleepLog model with chronotype tracking
- [ ] Sleep debt calculation
- [ ] Grogginess level tracking
- [ ] Pre-sleep activity correlation
- [ ] Chronotype determination algorithm

**Key Feature**: **Chronotype detection** affects task scheduling in Phase 2

---

### Phase 4.6: Study Habit System (Days 11-12)
**Deliverables**:
- [ ] StudyLog model with deviation tracking
- [ ] Scheduled vs actual time logging
- [ ] Flow state score tracking
- [ ] Stickiness factor calculation
- [ ] Integration with Phase 2 Tasks

**Key Feature**: **Deviation Ratio** for automatic time padding

---

### Phase 4.7: Water Habit System (Day 13)
**Deliverables**:
- [ ] WaterLog model with cognitive tracking
- [ ] Hydration requirement calculation
- [ ] Cognitive fog detection
- [ ] 2 PM crash pattern detection
- [ ] Hydration checkpoint scheduling

**Key Feature**: **Intake Volume + Cognitive Fog** triggers break scheduling

---

### Phase 4.8: Analytics & Statistics (Day 14)
**Deliverables**:
- [ ] Streak calculation service
- [ ] Completion rate analytics
- [ ] Trend analysis endpoints
- [ ] Correlation insights
- [ ] AI pattern recognition aggregations

**Aggregation Pipelines**:
```javascript
// Example: Food habit pattern
db.food_logs.aggregate([
  { $match: { userId: "..." } },
  { $group: { 
      _id: { $hour: "$timestamp" },
      avgSatisfaction: { $avg: "$satisfactionLevel" },
      count: { $sum: 1 }
  }},
  { $sort: { avgSatisfaction: -1 } }
]);
```

---

### Phase 4.9: Export & Reporting (Day 15)
**Deliverables**:
- [ ] Export to Google Sheets API
- [ ] Generate insight reports
- [ ] Visualization data endpoints
- [ ] PDF report generation (optional)

**API Endpoint**:
```
GET    /api/habits/:id/export        - Export habit data
POST   /api/reports/generate          - Generate AI insights report
```

---

### Phase 4.10: Testing & Integration (Day 16)
**Deliverables**:
- [ ] Unit tests for each habit type
- [ ] Integration tests with Tasks/Events
- [ ] Postman collection updates
- [ ] Documentation updates
- [ ] Performance testing

---

## 🎯 Critical AI Features Priority Matrix

| Feature | Habit Type | Priority | Complexity | Impact |
|---------|-----------|----------|------------|--------|
| RPE vs Energy Correlation | Exercise | 🔴 CRITICAL | HIGH | Recovery scheduling |
| Time + Mood Spending | Financial | 🟠 HIGH | MEDIUM | Impulse prevention |
| Chronotype Detection | Sleep | 🔴 CRITICAL | HIGH | Task scheduling |
| Stickiness Factor | Study | 🔴 CRITICAL | MEDIUM | Time padding |
| Cognitive Fog Detection | Water | 🟠 HIGH | HIGH | Break scheduling |
| Eating Speed + Emotion | Food | 🟡 MEDIUM | LOW | Pattern awareness |

---

## 🔗 Integration Points

### With Phase 2 (Tasks)
- Study habit logs link to Task IDs
- Chronotype affects task scheduling times
- Stickiness factor adjusts task duration estimates

### With Phase 3 (Events)
- Sleep schedule affects calendar availability
- Exercise recovery blocks auto-create calendar events
- Study sessions sync with calendar

### With Phase 6 (AI Brain)
- All habit logs feed into embeddings database
- Pattern recognition across all 6 habit types
- Cross-habit correlation analysis (e.g., sleep quality → exercise RPE)

---

## 📊 Success Metrics

- [ ] All 6 habit types fully functional
- [ ] Streak calculation accurate
- [ ] AI insights generating within 30 days of data
- [ ] Export to Sheets working
- [ ] Integration with Tasks/Events seamless
- [ ] MongoDB aggregations < 500ms
- [ ] 90%+ data collection completion rate

---

## ⚠️ Technical Challenges

1. **MongoDB Schema Design**: Balance flexibility vs performance
2. **Aggregation Complexity**: 6 different habit types with unique patterns
3. **Data Volume**: Logs can grow to 100K+ per user/year
4. **Chronotype Accuracy**: Needs 21+ days of data
5. **Real-time Insights**: Pattern detection without heavy computation
6. **Integration Complexity**: Links to 3 other services

---

## 🚀 Next Steps

1. Review and approve this architecture plan
2. Setup MongoDB Atlas account
3. Begin Phase 4.1: Infrastructure
4. Create detailed API specifications per habit type
5. Design MongoDB indexes for optimal queries

**Estimated Total Duration**: 16 days (vs original 5-7 estimate)  
**Reason**: 6 specialized habit types with unique AI features

---

**Ready to begin implementation?** Let me know which phase to start with, or if you want to modify the architecture plan first.
