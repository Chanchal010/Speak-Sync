# Test Scheduler Service API
$ErrorActionPreference = "Stop"

Write-Host "Testing Scheduler Service API" -ForegroundColor Cyan
Write-Host ""

# Configuration
$baseUrl = "http://localhost:3001"
$internalApiKey = "96TDvSHYJATQsyzGdK2kY1WR8wp04hvrEzMoRD5uKCkTlSvIofe7uofakGdcujT9"

# Test 1: Health Check
Write-Host "1. Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "[OK] Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "[ERROR] Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Create User
Write-Host "2. Creating test user..." -ForegroundColor Yellow
$headers = @{
    'Content-Type' = 'application/json'
    'X-Internal-API-Key' = $internalApiKey
}
$userBody = @{
    name = "Test User"
    email = "testuser_$(Get-Random)@example.com"
    password = "Test123456!@#"
} | ConvertTo-Json

try {
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/internal/users" -Method POST -Headers $headers -Body $userBody
    Write-Host "[OK] User created successfully" -ForegroundColor Green
    Write-Host "   User ID: $($userResponse.data.id)" -ForegroundColor Gray
    Write-Host "   Email: $($userResponse.data.email)" -ForegroundColor Gray
    Write-Host ""
    $userId = $userResponse.data.id
} catch {
    Write-Host "[ERROR] User creation failed: $_" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Red
    exit 1
}

# Test 3: Get Categories (should be empty initially)
Write-Host "3. Fetching categories..." -ForegroundColor Yellow
$authHeaders = @{
    'Content-Type' = 'application/json'
    'X-User-Id' = $userId
}
try {
    $categories = Invoke-RestMethod -Uri "$baseUrl/api/categories" -Method GET -Headers $authHeaders
    Write-Host "[OK] Categories fetched: $($categories.data.Count) categories" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Categories fetch failed: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 4: Create Category
Write-Host "4. Creating a category..." -ForegroundColor Yellow
$categoryBody = @{
    name = "Personal"
    icon = "person"
    color = "#3B82F6"
    order = 1
} | ConvertTo-Json

try {
    $category = Invoke-RestMethod -Uri "$baseUrl/api/categories" -Method POST -Headers $authHeaders -Body $categoryBody
    Write-Host "[OK] Category created successfully" -ForegroundColor Green
    Write-Host "   Category ID: $($category.data.id)" -ForegroundColor Gray
    Write-Host "   Name: $($category.data.name)" -ForegroundColor Gray
    Write-Host ""
    $categoryId = $category.data.id
} catch {
    Write-Host "[ERROR] Category creation failed: $_" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 5: Create Task
Write-Host "5. Creating a task..." -ForegroundColor Yellow
$taskBody = @{
    title = "Test Task - Buy groceries"
    description = "Get milk, eggs, bread"
    categoryId = $categoryId
    priority = "MI"
    status = "pending"
    dueDate = (Get-Date).AddDays(2).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    tags = @("shopping", "urgent")
} | ConvertTo-Json

try {
    $task = Invoke-RestMethod -Uri "$baseUrl/api/tasks" -Method POST -Headers $authHeaders -Body $taskBody
    Write-Host "[OK] Task created successfully" -ForegroundColor Green
    Write-Host "   Task ID: $($task.data.id)" -ForegroundColor Gray
    Write-Host "   Title: $($task.data.title)" -ForegroundColor Gray
    Write-Host "   Priority: $($task.data.priority)" -ForegroundColor Gray
    Write-Host ""
    $taskId = $task.data.id
} catch {
    Write-Host "[ERROR] Task creation failed: $_" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 6: Get Tasks
Write-Host "6. Fetching tasks..." -ForegroundColor Yellow
try {
    $tasks = Invoke-RestMethod -Uri "$baseUrl/api/tasks" -Method GET -Headers $authHeaders
    Write-Host "[OK] Tasks fetched: $($tasks.data.Count) tasks" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Tasks fetch failed: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 7: Get Tasks by Category
Write-Host "7. Fetching tasks by category..." -ForegroundColor Yellow
try {
    $tasksByCategory = Invoke-RestMethod -Uri "$baseUrl/api/tasks/by-category" -Method GET -Headers $authHeaders
    Write-Host "[OK] Tasks grouped by category: $($tasksByCategory.data.Count) categories" -ForegroundColor Green
    if ($tasksByCategory.data -and $tasksByCategory.data.Count -gt 0) {
        foreach ($cat in $tasksByCategory.data) {
            Write-Host "   Category $($cat.categoryName): $($cat.tasks.Count) tasks" -ForegroundColor Gray
        }
    }
    Write-Host ""
} catch {
    Write-Host "[ERROR] Tasks by category fetch failed: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 8: Update Task
Write-Host "8. Updating task..." -ForegroundColor Yellow
$updateBody = @{
    title = "Test Task - Buy groceries (Updated)"
    priority = "VI"
} | ConvertTo-Json

try {
    $updatedTask = Invoke-RestMethod -Uri "$baseUrl/api/tasks/$taskId" -Method PUT -Headers $authHeaders -Body $updateBody
    Write-Host "[OK] Task updated successfully" -ForegroundColor Green
    Write-Host "   New priority: $($updatedTask.data.priority)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "[ERROR] Task update failed: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 9: Toggle Task Completion
Write-Host "9. Toggling task completion..." -ForegroundColor Yellow
try {
    $completedTask = Invoke-RestMethod -Uri "$baseUrl/api/tasks/$taskId/complete" -Method PATCH -Headers $authHeaders
    Write-Host "[OK] Task completion toggled" -ForegroundColor Green
    Write-Host "   Status: $($completedTask.data.status)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "[ERROR] Task completion toggle failed: $_" -ForegroundColor Red
    Write-Host ""
}

# Test 10: Get Task Stats
Write-Host "10. Fetching task statistics..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/api/tasks/stats" -Method GET -Headers $authHeaders
    Write-Host "[OK] Task stats fetched" -ForegroundColor Green
    Write-Host "   Total tasks: $($stats.data.totalTasks)" -ForegroundColor Gray
    Write-Host "   Completed: $($stats.data.completedTasks)" -ForegroundColor Gray
    Write-Host "   Completion rate: $($stats.data.completionRate)%" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "[ERROR] Task stats fetch failed: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "API testing complete!" -ForegroundColor Green
