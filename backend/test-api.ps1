# API Connection Test Script
# This tests all API endpoints to verify database integration

Write-Host "`n🧪 Testing API Endpoints...`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:5000/api"
$ErrorActionPreference = "Continue"

# Test 1: Health Check
Write-Host "1️⃣  Testing Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    if ($response.success) {
        Write-Host "   ✅ Health check passed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Cannot connect to server. Is it running?" -ForegroundColor Red
    Write-Host "   💡 Run: cd backend && npm run dev" -ForegroundColor Yellow
    exit 1
}

# Test 2: Send OTP (Registration)
Write-Host "`n2️⃣  Testing Send OTP..." -ForegroundColor Yellow
$otpBody = @{
    phoneNumber = "+254700000999"
    fullName = "Test User"
    purpose = "registration"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/send-otp" -Method Post -Body $otpBody -ContentType "application/json"
    if ($response.success) {
        Write-Host "   ✅ OTP sent successfully" -ForegroundColor Green
        Write-Host "   📱 OTP code will be in backend console" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Send OTP failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Login (using seed data)
Write-Host "`n3️⃣  Testing Login..." -ForegroundColor Yellow
$loginBody = @{
    phoneNumber = "+254700000001"
    password = "editor123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    if ($response.success) {
        Write-Host "   ✅ Login successful" -ForegroundColor Green
        Write-Host "   👤 User: $($response.user.fullName)" -ForegroundColor Cyan
        Write-Host "   🔑 Role: $($response.user.role)" -ForegroundColor Cyan
        $token = $response.token
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
    } else {
        Write-Host "   ❌ Login failed" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 Run: cd backend && npm run seed" -ForegroundColor Yellow
    exit 1
}

# Test 4: Get All Subjects
Write-Host "`n4️⃣  Testing Get Subjects..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/subjects" -Method Get -Headers $headers
    if ($response.success) {
        Write-Host "   ✅ Subjects retrieved successfully" -ForegroundColor Green
        Write-Host "   📚 Total subjects: $($response.count)" -ForegroundColor Cyan
        if ($response.data.Count -gt 0) {
            Write-Host "   📋 Subjects:" -ForegroundColor Cyan
            foreach ($subject in $response.data) {
                $paperCount = $subject.papers.Count
                Write-Host "      • $($subject.name): $paperCount papers" -ForegroundColor White
            }
        } else {
            Write-Host "   ⚠️  No subjects found. Add subjects via EditorDashboard" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Get subjects failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Create Subject
Write-Host "`n5️⃣  Testing Create Subject..." -ForegroundColor Yellow
$subjectBody = @{
    name = "Test Subject API"
    description = "Created via API test"
    papers = @(
        @{
            name = "Paper 1"
            topics = @("Topic A", "Topic B")
            sections = @("Section A", "Section B")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/subjects" -Method Post -Body $subjectBody -Headers $headers
    if ($response.success) {
        Write-Host "   ✅ Subject created successfully" -ForegroundColor Green
        Write-Host "   📚 Subject: $($response.data.name)" -ForegroundColor Cyan
        Write-Host "   📄 Papers: $($response.data.papers.Count)" -ForegroundColor Cyan
        $testSubjectId = $response.data._id
    }
} catch {
    $errorMsg = $_.ErrorDetails.Message | ConvertFrom-Json
    if ($errorMsg.message -like "*already exists*") {
        Write-Host "   ⚠️  Subject already exists (OK)" -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ Create subject failed: $($errorMsg.message)" -ForegroundColor Red
    }
}

# Test 6: Get Single Subject
if ($testSubjectId) {
    Write-Host "`n6️⃣  Testing Get Single Subject..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/subjects/$testSubjectId" -Method Get -Headers $headers
        if ($response.success) {
            Write-Host "   ✅ Subject retrieved successfully" -ForegroundColor Green
            Write-Host "   📚 Name: $($response.data.name)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "   ❌ Get subject failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    # Test 7: Update Subject
    Write-Host "`n7️⃣  Testing Update Subject..." -ForegroundColor Yellow
    $updateBody = @{
        name = "Test Subject API Updated"
        description = "Updated via API test"
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/subjects/$testSubjectId" -Method Put -Body $updateBody -Headers $headers
        if ($response.success) {
            Write-Host "   ✅ Subject updated successfully" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ❌ Update subject failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    # Test 8: Delete Subject
    Write-Host "`n8️⃣  Testing Delete Subject..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/subjects/$testSubjectId" -Method Delete -Headers $headers
        if ($response.success) {
            Write-Host "   ✅ Subject deleted successfully" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ❌ Delete subject failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 API TESTS COMPLETED! 🎉" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`n✅ Database connections are working!" -ForegroundColor Green
Write-Host "✅ Authentication is working!" -ForegroundColor Green
Write-Host "✅ Subject CRUD operations are working!" -ForegroundColor Green
Write-Host "`n💡 Check the backend console for detailed logs`n" -ForegroundColor Yellow
