# 🚀 Speak-Sync API Testing Guide

Complete guide for testing the Speak-Sync API using Postman with automatic token management and pre-configured requests.

## 📦 Quick Setup (2 Minutes)

### Step 1: Import Collection & Environment

1. Open **Postman**
2. Click **Import** (top left)
3. Drag and drop or select these files:
   - `Speak-Sync-Complete-API.postman_collection.json`
   - `Speak-Sync-Development.postman_environment.json`
4. Select **"Speak-Sync Development"** environment (top right dropdown)

### Step 2: Start Services

```powershell
# Start Scheduler Service
cd D:\Projects\Speak-Sync
pnpm dev:scheduler
```

### Step 3: Run First Request

Open **"🔍 Health Checks"** → **"Scheduler Health"** → Click **Send**

✅ You should see: `{ "status": "healthy", "service": "scheduler" }`

---

## 🎯 Complete Testing Workflow

### 1️⃣ Health Checks (Verify Services)

| Request | Expected Result |
|---------|----------------|
| **Scheduler Health** | `status: "healthy"` |
| **Gateway Health** | `status: "healthy"` (when Gateway runs) |

---

### 2️⃣ Authentication (Get Tokens)

#### Option A: Register New User

```
POST {{GATEWAY_URL}}/api/auth/register

Body:
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "SecurePass123!@#"
}
```

**What Happens Automatically:**
- ✅ `ACCESS_TOKEN` saved to environment
- ✅ `REFRESH_TOKEN` saved to environment
- ✅ `USER_ID` saved to environment
- ✅ `USER_EMAIL` saved to environment

#### Option B: Login Existing User

```
POST {{GATEWAY_URL}}/api/auth/login

Body:
{
    "email": "john.doe@example.com",
    "password": "SecurePass123!@#"
}
```

Same automatic token saving! 🎉

---

### 3️⃣ Categories (Organize Your Tasks)

#### Create Your First Category

```
POST {{SCHEDULER_URL}}/api/categories

Body:
{
    "name": "Personal",
    "icon": "👤",
    "color": "#3B82F6",
    "order": 1
}
```

**Auto-saved:** `CATEGORY_ID` → Use in next requests

#### Create More Categories

Try these default categories:

```json
// Learning
{ "name": "Learning", "icon": "📚", "color": "#10B981", "order": 2 }

// Fitness
{ "name": "Fitness", "icon": "💪", "color": "#F59E0B", "order": 3 }

// Work
{ "name": "Work", "icon": "💼", "color": "#EF4444", "order": 4 }

// Shopping
{ "name": "Shopping", "icon": "🛒", "color": "#8B5CF6", "order": 5 }

// Wish List
{ "name": "Wish List", "icon": "⭐", "color": "#EC4899", "order": 6 }
```

#### View All Categories

```
GET {{SCHEDULER_URL}}/api/categories?includeTasks=true
```

---

### 4️⃣ Tasks (The Main Feature!)

#### Create a Simple Task

```
POST {{SCHEDULER_URL}}/api/tasks

Body:
{
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread, and vegetables",
    "categoryId": "{{CATEGORY_ID}}",
    "priority": "MI",
    "status": "pending",
    "dueDate": "2025-12-05T18:00:00.000Z",
    "tags": ["shopping", "urgent"],
    "timeEstimateMinutes": 30,
    "colorHex": "#F59E0B"
}
```

**Auto-saved:** `TASK_ID` → Use in next requests

#### Create Task with Voice & AI Context

```json
{
    "title": "Call dentist for appointment",
    "description": "Schedule teeth cleaning appointment",
    "priority": "VI",
    "dueDate": "2025-12-10T12:00:00.000Z",
    "voiceTranscript": "Remind me to call the dentist urgently for my teeth cleaning",
    "sentimentScore": -0.3,
    "contextMetadata": {
        "device": "mobile",
        "location": "home",
        "time_of_day": "morning",
        "weather": "rainy",
        "user_mood": "stressed"
    },
    "tags": ["health", "urgent"],
    "timeEstimateMinutes": 15
}
```

#### Get All Tasks (with Filters)

```
GET {{SCHEDULER_URL}}/api/tasks?status=pending&priority=MI&page=1&limit=20&sortBy=dueDate&order=asc
```

**Available Filters:**
- `categoryId` - Filter by category UUID
- `priority` - VI, MI, or NI
- `status` - pending, in_progress, completed, cancelled
- `search` - Search in title/description
- `tags` - Filter by tags (comma-separated)
- `dueDateFrom` - Filter due date from
- `dueDateTo` - Filter due date to
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)
- `sortBy` - Field to sort by
- `order` - asc or desc

#### Get Tasks Grouped by Category

```
GET {{SCHEDULER_URL}}/api/tasks/by-category
```

**Perfect for UI!** Returns structure like:
```json
[
  {
    "categoryId": "uuid",
    "categoryName": "Personal",
    "categoryIcon": "👤",
    "categoryColor": "#3B82F6",
    "tasks": [...]
  }
]
```

#### Update a Task

```
PUT {{SCHEDULER_URL}}/api/tasks/{{TASK_ID}}

Body:
{
    "title": "Buy groceries (Updated)",
    "priority": "VI",
    "status": "in_progress",
    "dueDate": "2025-12-06T18:00:00.000Z"
}
```

**AI Tracking:** Priority changes and rescheduling are automatically tracked!

#### Complete a Task

```
PATCH {{SCHEDULER_URL}}/api/tasks/{{TASK_ID}}/complete
```

**What Happens:**
- Status toggles between `completed` ↔ `pending`
- Actual time calculated
- Completion patterns recorded for AI

#### Delete a Task

```
DELETE {{SCHEDULER_URL}}/api/tasks/{{TASK_ID}}
```

**Note:** This is a SOFT DELETE - data is preserved for AI training!

#### Bulk Update Tasks

```
POST {{SCHEDULER_URL}}/api/tasks/bulk-update

Body:
{
    "taskIds": ["task-uuid-1", "task-uuid-2"],
    "updates": {
        "priority": "VI",
        "status": "in_progress",
        "categoryId": "{{CATEGORY_ID}}"
    }
}
```

#### Get Task Statistics

```
GET {{SCHEDULER_URL}}/api/tasks/stats
```

**Returns:**
```json
{
    "success": true,
    "data": {
        "totalTasks": 10,
        "completedTasks": 7,
        "completionRate": 70,
        "priorityDistribution": {
            "VI": 2,
            "MI": 5,
            "NI": 3
        },
        "statusDistribution": {
            "pending": 2,
            "in_progress": 1,
            "completed": 7
        }
    }
}
```

---

## 🎨 Understanding Task Fields

### Required Fields
- `title` (string, 1-200 chars)

### Core Fields
- `description` (string, max 2000 chars)
- `categoryId` (UUID)
- `priority` (VI/MI/NI) - Default: MI
- `status` (pending/in_progress/completed/cancelled) - Default: pending
- `scheduledDate` (datetime) - When planned
- `dueDate` (datetime) - Deadline
- `tags` (array of strings)
- `colorHex` (#RRGGBB)

### AI Training Fields 🤖
- `voiceTranscript` (max 1000 chars) - Voice command
- `sentimentScore` (-1.0 to 1.0) - User's mood
- `contextMetadata` (object) - Environment data
- `timeEstimateMinutes` (number) - Estimated duration
- Auto-tracked: `rescheduleCount`, `priorityChanges`, `completionPattern`

---

## 🔐 Authentication Details

### How It Works

1. **Login/Register** → Tokens saved automatically to environment
2. **Collection-level Auth** → Bearer token auto-injected
3. **Pre-request Script** → Adds `X-User-Id` header for direct Scheduler calls

### Token Variables

| Variable | Type | Auto-Populated | Usage |
|----------|------|----------------|-------|
| `ACCESS_TOKEN` | secret | ✅ Yes | Bearer token for auth |
| `REFRESH_TOKEN` | secret | ✅ Yes | Refresh expired tokens |
| `USER_ID` | string | ✅ Yes | User context |
| `USER_EMAIL` | string | ✅ Yes | Reference |

### Manual Token Management

If needed, you can manually set tokens:

1. Get token from login response
2. Click **Environment Quick Look** (eye icon)
3. Edit `ACCESS_TOKEN` value
4. Click **Save**

---

## 🧪 Test Scenarios

### Scenario 1: Daily Task Management

```javascript
// 1. Morning: Create tasks for the day
POST /api/tasks
{ "title": "Morning workout", "priority": "VI", "dueDate": "2025-12-03T07:00:00Z" }

// 2. Check what's pending
GET /api/tasks?status=pending&sortBy=priority&order=desc

// 3. Start working on a task
PUT /api/tasks/{{TASK_ID}}
{ "status": "in_progress" }

// 4. Complete the task
PATCH /api/tasks/{{TASK_ID}}/complete

// 5. Evening: Check progress
GET /api/tasks/stats
```

### Scenario 2: Category-Based Organization

```javascript
// 1. Create categories for different life areas
POST /api/categories → Personal, Work, Health, Learning

// 2. Assign tasks to categories
POST /api/tasks → categoryId = Personal category
POST /api/tasks → categoryId = Work category

// 3. View tasks grouped by category (for UI)
GET /api/tasks/by-category

// 4. Filter tasks by category
GET /api/tasks?categoryId={{CATEGORY_ID}}
```

### Scenario 3: Voice-to-Task AI Training

```javascript
// 1. Create task from voice input
POST /api/tasks
{
  "title": "Call mom",
  "voiceTranscript": "Remind me to call mom this evening",
  "sentimentScore": 0.5,
  "contextMetadata": {
    "device": "mobile",
    "location": "office",
    "time_of_day": "afternoon"
  }
}

// 2. Reschedule (tracks behavior)
PUT /api/tasks/{{TASK_ID}}
{ "dueDate": "2025-12-04T19:00:00Z" }

// 3. Change priority (tracks decision patterns)
PUT /api/tasks/{{TASK_ID}}
{ "priority": "VI" }

// 4. Complete (records completion patterns)
PATCH /api/tasks/{{TASK_ID}}/complete
```

---

## 🔧 Troubleshooting

### Error: "Unauthorized - No user context"

**Solution:**
1. Make sure you've logged in: **Authentication** → **Login User**
2. Check `ACCESS_TOKEN` is set: Click eye icon (top right)
3. Token expired? Use **Refresh Token** endpoint

### Error: "Invalid service credentials"

**Solution:**
1. Check `INTERNAL_API_KEY` in environment
2. Verify Scheduler `.env` has matching key: `96TDvSHYJATQsyzGdK2kY1WR8wp04hvrEzMoRD5uKCkTlSvIofe7uofakGdcujT9`

### Error: "Validation error"

**Common Issues:**
- Missing required field: Check `title` is present
- Invalid priority: Must be VI, MI, or NI
- Invalid status: Must be pending, in_progress, completed, or cancelled
- Invalid color: Must be hex format #RRGGBB
- Password requirements: Min 8 chars, must have uppercase, lowercase, number, special char

### Error: "Cannot connect to service"

**Solution:**
1. Check service is running in terminal
2. Verify URL in environment: `SCHEDULER_URL = http://localhost:3001`
3. Try health check first

### Response is slow

**Tips:**
- Check database connection (Neon)
- Look for N+1 queries in terminal logs
- Reduce `limit` parameter for large datasets
- Use specific filters instead of fetching all

---

## 📊 Response Format Reference

### Success Response
```json
{
  "success": true,
  "data": { /* resource data */ },
  "pagination": {  // For list endpoints
    "page": 1,
    "limit": 20,
    "totalPages": 5,
    "totalItems": 95
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": [  // For validation errors
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

---

## 🎓 Advanced Tips

### 1. Use Pre-request Scripts

Add dynamic data to requests:
```javascript
// In Pre-request Script tab
pm.environment.set("TIMESTAMP", new Date().toISOString());
pm.environment.set("RANDOM_EMAIL", `user${Date.now()}@example.com`);
```

### 2. Chain Requests with Tests

Auto-save IDs from responses:
```javascript
// In Tests tab
if (pm.response.code === 201) {
    const data = pm.response.json();
    pm.environment.set("TASK_ID", data.data.id);
}
```

### 3. Run Collection Tests

1. Click **Collections** → **"Speak-Sync Complete API"** → **...** → **Run collection**
2. Select requests to run
3. Click **Run Speak-Sync Complete API**
4. Watch tests pass! ✅

### 4. Export Environment

After setting up, export your environment:
1. Environments → **...** next to "Speak-Sync Development"
2. **Export**
3. Share with team!

---

## 📝 Checklist for First-Time Setup

- [ ] Import collection and environment into Postman
- [ ] Select "Speak-Sync Development" environment
- [ ] Start Scheduler Service (`pnpm dev:scheduler`)
- [ ] Test health check endpoint
- [ ] Register or login to get tokens
- [ ] Create at least one category
- [ ] Create your first task
- [ ] View tasks by category
- [ ] Update and complete a task
- [ ] Check task statistics

---

## 🚀 Next Steps

### When Gateway is Ready

Replace direct Scheduler URLs with Gateway proxy:
```
Before:  POST {{SCHEDULER_URL}}/api/tasks
After:   POST {{GATEWAY_URL}}/api/tasks
```

Gateway will handle JWT verification and forward requests!

### Phase 3: Calendar Events

New endpoints will be added for:
- Event CRUD
- Recurring events
- Calendar view integration

### Phase 6: AI Brain Service

Voice input endpoints will use the AI training data:
- Voice-to-task conversion
- Smart rescheduling
- Priority recommendations

---

## 📞 Support

**Issue:** Something not working?

1. Check terminal logs for errors
2. Verify all environment variables are set
3. Review request/response in Postman Console (View → Show Postman Console)
4. Check `/docs/PHASE2_COMPLETION_REPORT.md` for technical details

**Success!** 🎉 You're now ready to test the complete Speak-Sync API!
