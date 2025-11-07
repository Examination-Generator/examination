# Pre-Deployment Test Script
# Run this script before deploying to catch common issues

Write-Host "🧪 Pre-Deployment Testing Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# Test 1: Check if Git repository is clean
Write-Host "1️⃣  Checking Git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "   ⚠️  You have uncommitted changes" -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "   ✅ Git repository is clean" -ForegroundColor Green
}
Write-Host ""

# Test 2: Check Python dependencies
Write-Host "2️⃣  Checking Python dependencies..." -ForegroundColor Yellow
cd django_backend
try {
    pip install -q -r requirements.txt
    Write-Host "   ✅ Python dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to install Python dependencies" -ForegroundColor Red
    $ErrorCount++
}
cd ..
Write-Host ""

# Test 3: Check Django migrations
Write-Host "3️⃣  Checking Django migrations..." -ForegroundColor Yellow
cd django_backend
$migrations = python manage.py showmigrations --plan 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Migrations are valid" -ForegroundColor Green
} else {
    Write-Host "   ❌ Migration check failed" -ForegroundColor Red
    $ErrorCount++
}
cd ..
Write-Host ""

# Test 4: Check for settings_production.py
Write-Host "4️⃣  Checking production settings..." -ForegroundColor Yellow
if (Test-Path "django_backend\examination_system\settings_production.py") {
    Write-Host "   ✅ Production settings file exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ Production settings file missing" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# Test 5: Check Node dependencies
Write-Host "5️⃣  Checking Node dependencies..." -ForegroundColor Yellow
cd frontend\exam
try {
    npm install --silent
    Write-Host "   ✅ Node dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to install Node dependencies" -ForegroundColor Red
    $ErrorCount++
}
cd ..\..
Write-Host ""

# Test 6: Check React build
Write-Host "6️⃣  Testing React build..." -ForegroundColor Yellow
cd frontend\exam
$env:CI = "false"
$buildResult = npm run build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ React build successful" -ForegroundColor Green
    Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
} else {
    Write-Host "   ❌ React build failed" -ForegroundColor Red
    $ErrorCount++
}
cd ..\..
Write-Host ""

# Test 7: Check environment variable templates
Write-Host "7️⃣  Checking environment files..." -ForegroundColor Yellow
$envFiles = @(
    "frontend\exam\.env.production",
    ".env.production"
)
$allExist = $true
foreach ($file in $envFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $allExist = $false
        $ErrorCount++
    }
}
Write-Host ""

# Test 8: Check Vercel configuration files
Write-Host "8️⃣  Checking Vercel config files..." -ForegroundColor Yellow
$vercelFiles = @(
    "vercel.json",
    "django_backend\vercel.json",
    "frontend\exam\vercel.json"
)
foreach ($file in $vercelFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $ErrorCount++
    }
}
Write-Host ""

# Test 9: Check .gitignore
Write-Host "9️⃣  Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -match "\.env" -and $gitignoreContent -match "venv" -and $gitignoreContent -match "node_modules") {
        Write-Host "   ✅ .gitignore properly configured" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  .gitignore might be missing important entries" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ .gitignore missing" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# Test 10: Check documentation
Write-Host "🔟 Checking deployment documentation..." -ForegroundColor Yellow
$docs = @(
    "VERCEL_DEPLOYMENT_GUIDE.md",
    "DEPLOYMENT_QUICK_REFERENCE.md",
    "PRE_DEPLOYMENT_CHECKLIST.md"
)
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "   ✅ $doc exists" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $doc missing" -ForegroundColor Yellow
    }
}
Write-Host ""

# Summary
Write-Host "=================================" -ForegroundColor Cyan
if ($ErrorCount -eq 0) {
    Write-Host "✅ All checks passed! You're ready to deploy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Read PRE_DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
    Write-Host "2. Follow VERCEL_DEPLOYMENT_GUIDE.md" -ForegroundColor White
    Write-Host "3. Push to GitHub: git push origin main" -ForegroundColor White
} else {
    Write-Host "❌ Found $ErrorCount error(s). Please fix before deploying." -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the errors above and:" -ForegroundColor Cyan
    Write-Host "1. Fix the issues" -ForegroundColor White
    Write-Host "2. Run this script again" -ForegroundColor White
    Write-Host "3. Once all checks pass, proceed with deployment" -ForegroundColor White
}
Write-Host "=================================" -ForegroundColor Cyan
