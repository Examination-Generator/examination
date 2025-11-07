#!/bin/bash
# Pre-Deployment Test Script for Linux/Mac
# Run this script before deploying to catch common issues

echo "🧪 Pre-Deployment Testing Script"
echo "================================="
echo ""

ERROR_COUNT=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test 1: Check if Git repository is clean
echo -e "${YELLOW}1️⃣  Checking Git status...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "   ${RED}⚠️  You have uncommitted changes${NC}"
    ((ERROR_COUNT++))
else
    echo -e "   ${GREEN}✅ Git repository is clean${NC}"
fi
echo ""

# Test 2: Check Python dependencies
echo -e "${YELLOW}2️⃣  Checking Python dependencies...${NC}"
cd django_backend
if pip install -q -r requirements.txt; then
    echo -e "   ${GREEN}✅ Python dependencies OK${NC}"
else
    echo -e "   ${RED}❌ Failed to install Python dependencies${NC}"
    ((ERROR_COUNT++))
fi
cd ..
echo ""

# Test 3: Check Django migrations
echo -e "${YELLOW}3️⃣  Checking Django migrations...${NC}"
cd django_backend
if python manage.py showmigrations --plan > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Migrations are valid${NC}"
else
    echo -e "   ${RED}❌ Migration check failed${NC}"
    ((ERROR_COUNT++))
fi
cd ..
echo ""

# Test 4: Check for settings_production.py
echo -e "${YELLOW}4️⃣  Checking production settings...${NC}"
if [ -f "django_backend/examination_system/settings_production.py" ]; then
    echo -e "   ${GREEN}✅ Production settings file exists${NC}"
else
    echo -e "   ${RED}❌ Production settings file missing${NC}"
    ((ERROR_COUNT++))
fi
echo ""

# Test 5: Check Node dependencies
echo -e "${YELLOW}5️⃣  Checking Node dependencies...${NC}"
cd frontend/exam
if npm install --silent > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Node dependencies OK${NC}"
else
    echo -e "   ${RED}❌ Failed to install Node dependencies${NC}"
    ((ERROR_COUNT++))
fi
cd ../..
echo ""

# Test 6: Check React build
echo -e "${YELLOW}6️⃣  Testing React build...${NC}"
cd frontend/exam
export CI=false
if npm run build > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ React build successful${NC}"
    rm -rf build
else
    echo -e "   ${RED}❌ React build failed${NC}"
    ((ERROR_COUNT++))
fi
cd ../..
echo ""

# Test 7: Check environment variable templates
echo -e "${YELLOW}7️⃣  Checking environment files...${NC}"
ENV_FILES=("frontend/exam/.env.production" ".env.production")
for file in "${ENV_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅ $file exists${NC}"
    else
        echo -e "   ${RED}❌ $file missing${NC}"
        ((ERROR_COUNT++))
    fi
done
echo ""

# Test 8: Check Vercel configuration files
echo -e "${YELLOW}8️⃣  Checking Vercel config files...${NC}"
VERCEL_FILES=("vercel.json" "django_backend/vercel.json" "frontend/exam/vercel.json")
for file in "${VERCEL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅ $file exists${NC}"
    else
        echo -e "   ${RED}❌ $file missing${NC}"
        ((ERROR_COUNT++))
    fi
done
echo ""

# Test 9: Check .gitignore
echo -e "${YELLOW}9️⃣  Checking .gitignore...${NC}"
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore && grep -q "venv" .gitignore && grep -q "node_modules" .gitignore; then
        echo -e "   ${GREEN}✅ .gitignore properly configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️  .gitignore might be missing important entries${NC}"
    fi
else
    echo -e "   ${RED}❌ .gitignore missing${NC}"
    ((ERROR_COUNT++))
fi
echo ""

# Test 10: Check documentation
echo -e "${YELLOW}🔟 Checking deployment documentation...${NC}"
DOCS=("VERCEL_DEPLOYMENT_GUIDE.md" "DEPLOYMENT_QUICK_REFERENCE.md" "PRE_DEPLOYMENT_CHECKLIST.md")
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "   ${GREEN}✅ $doc exists${NC}"
    else
        echo -e "   ${YELLOW}⚠️  $doc missing${NC}"
    fi
done
echo ""

# Summary
echo "================================="
if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! You're ready to deploy!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "${NC}1. Read PRE_DEPLOYMENT_CHECKLIST.md${NC}"
    echo -e "${NC}2. Follow VERCEL_DEPLOYMENT_GUIDE.md${NC}"
    echo -e "${NC}3. Push to GitHub: git push origin main${NC}"
else
    echo -e "${RED}❌ Found $ERROR_COUNT error(s). Please fix before deploying.${NC}"
    echo ""
    echo -e "${CYAN}Check the errors above and:${NC}"
    echo -e "${NC}1. Fix the issues${NC}"
    echo -e "${NC}2. Run this script again${NC}"
    echo -e "${NC}3. Once all checks pass, proceed with deployment${NC}"
fi
echo "================================="
