# Simple Postman Test - Verify Backend Routes

Write-Host "`n🧪 TESTING BACKEND ROUTES`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:5000"

# Test 1: Health Check (No Auth)
Write-Host "1️⃣  Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/health" -Method Get
    Write-Host "   ✅ Health check passed" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend is NOT running!" -ForegroundColor Red
    Write-Host "   💡 Start backend: cd backend; npm run dev" -ForegroundColor Yellow
    exit 1
}

# Test 2: Login to get token
Write-Host "`n2️⃣  Login..." -ForegroundColor Yellow
$loginBody = @{
    phoneNumber = "+254700000001"
    password = "editor123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $login.token
    Write-Host "   ✅ Login successful" -ForegroundColor Green
    Write-Host "   🔑 Token: $($token.Substring(0,30))..." -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Test 3: GET /api/subjects (should work)
Write-Host "`n3️⃣  GET /api/subjects..." -ForegroundColor Yellow
try {
    $subjects = Invoke-RestMethod -Uri "$baseUrl/api/subjects" -Method Get -Headers $headers
    Write-Host "   ✅ GET request works" -ForegroundColor Green
    Write-Host "   📚 Found $($subjects.data.Count) subjects" -ForegroundColor Gray
    
    if ($subjects.data.Count -gt 0) {
        $subjectId = $subjects.data[0]._id
        Write-Host "   🆔 Sample Subject ID: $subjectId" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  No subjects found" -ForegroundColor Yellow
        $subjectId = $null
    }
} catch {
    Write-Host "   ❌ GET failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# Test 4: POST /api/subjects (Create Subject)
Write-Host "`n4️⃣  POST /api/subjects (Create Subject)..." -ForegroundColor Yellow
$timestamp = Get-Date -Format 'HHmmss'
$createBody = @{
    name = "Test Subject - $timestamp"
    description = "Test subject created via PowerShell"
    papers = @(
        @{
            name = "Test Paper 1"
            description = "Test paper"
            sections = @("Section A")
            topics = @("Topic 1", "Topic 2")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $created = Invoke-RestMethod -Uri "$baseUrl/api/subjects" -Method Post -Body $createBody -Headers $headers
    Write-Host "   ✅ POST request works" -ForegroundColor Green
    Write-Host "   🆔 Created ID: $($created.data._id)" -ForegroundColor Gray
    $newSubjectId = $created.data._id
} catch {
    Write-Host "   ❌ POST failed" -ForegroundColor Red
    Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "   Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    $newSubjectId = $null
}

# Test 5: PUT /api/subjects/:id (Update Subject)
if ($newSubjectId) {
    Write-Host "`n5️⃣  PUT /api/subjects/$newSubjectId (Update Subject)..." -ForegroundColor Yellow
    $updateBody = @{
        name = "Updated Test Subject"
        description = "Updated description"
    } | ConvertTo-Json

    try {
        $updated = Invoke-RestMethod -Uri "$baseUrl/api/subjects/$newSubjectId" -Method Put -Body $updateBody -Headers $headers
        Write-Host "   ✅ PUT request works" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ PUT failed" -ForegroundColor Red
        Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        Write-Host "   Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }

    # Test 6: DELETE /api/subjects/:id
    Write-Host "`n6️⃣  DELETE /api/subjects/$newSubjectId..." -ForegroundColor Yellow
    try {
        $deleted = Invoke-RestMethod -Uri "$baseUrl/api/subjects/$newSubjectId" -Method Delete -Headers $headers
        Write-Host "   ✅ DELETE request works" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ DELETE failed" -ForegroundColor Red
        Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        Write-Host "   Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "`n⏭️  Skipping UPDATE and DELETE tests (no subject created)" -ForegroundColor Yellow
}

# Test 7: POST /api/questions (Create Question)
if ($subjectId -and $subjects.data[0].papers -and $subjects.data[0].papers.Count -gt 0) {
    $paperId = $subjects.data[0].papers[0]._id
    $topicId = if ($subjects.data[0].papers[0].topics -and $subjects.data[0].papers[0].topics.Count -gt 0) {
        $subjects.data[0].papers[0].topics[0]._id
    } else {
        $null
    }

    if ($topicId) {
        Write-Host "`n7️⃣  POST /api/questions (Create Question)..." -ForegroundColor Yellow
        $questionBody = @{
            subject = $subjectId
            paper = $paperId
            topic = $topicId
            questionText = "Test question created via PowerShell?"
            answerText = "This is a test answer."
            marks = 5
        } | ConvertTo-Json

        try {
            $question = Invoke-RestMethod -Uri "$baseUrl/api/questions" -Method Post -Body $questionBody -Headers $headers
            Write-Host "   ✅ POST /api/questions works" -ForegroundColor Green
            Write-Host "   🆔 Question ID: $($question.data._id)" -ForegroundColor Gray
        } catch {
            Write-Host "   ❌ POST /api/questions failed" -ForegroundColor Red
            Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
            Write-Host "   Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "`n⏭️  Skipping question test (no topics found)" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n⏭️  Skipping question test (no subjects found)" -ForegroundColor Yellow
}

Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ ROUTE TESTING COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════`n" -ForegroundColor Cyan
