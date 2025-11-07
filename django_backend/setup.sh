#!/bin/bash

# Django Backend Setup Script for Linux/Mac
# Run this script to automatically setup the Django backend

echo "========================================"
echo "Django Backend Setup Script"
echo "Examination System"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${YELLOW}[1/8] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python not found. Please install Python 3.10 or higher.${NC}"
    echo -e "${YELLOW}  Install with: sudo apt install python3 python3-pip python3-venv${NC}"
    exit 1
fi

# Check if PostgreSQL is accessible
echo ""
echo -e "${YELLOW}[2/8] Checking PostgreSQL installation...${NC}"
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version)
    echo -e "${GREEN}✓ PostgreSQL found: $PG_VERSION${NC}"
else
    echo -e "${RED}✗ PostgreSQL not found. Please install PostgreSQL.${NC}"
    echo -e "${YELLOW}  Install with: sudo apt install postgresql postgresql-contrib${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo -e "${YELLOW}[3/8] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${YELLOW}[4/8] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo ""
echo -e "${YELLOW}[5/8] Installing Python dependencies...${NC}"
echo -e "${GRAY}  This may take a few minutes...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if .env exists
echo ""
echo -e "${YELLOW}[6/8] Checking environment configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file found${NC}"
else
    echo -e "${YELLOW}! .env not found, copying from .env.example${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Update .env with your PostgreSQL password!${NC}"
    echo -e "${GRAY}  Open .env and change DB_PASSWORD=postgres to your password${NC}"
    echo ""
    read -p "Press Enter to continue after updating .env, or type 'skip' to continue anyway: " continue
fi

# Create database
echo ""
echo -e "${YELLOW}[7/8] Setting up database...${NC}"
echo -e "${GRAY}  You may be prompted for PostgreSQL password${NC}"

DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -w examination_system | wc -l)

if [ $DB_EXISTS -eq 0 ]; then
    echo -e "${GRAY}  Creating database...${NC}"
    sudo -u postgres psql -c "CREATE DATABASE examination_system;" 2>/dev/null
    echo -e "${GREEN}✓ Database 'examination_system' created${NC}"
else
    echo -e "${GREEN}✓ Database 'examination_system' already exists${NC}"
fi

# Run migrations
echo ""
echo -e "${YELLOW}[8/8] Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}✓ Migrations completed${NC}"

# Success message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  ${NC}1. Create superuser (optional):${NC}"
echo -e "     ${GRAY}python manage.py createsuperuser${NC}"
echo ""
echo -e "  ${NC}2. Start development server:${NC}"
echo -e "     ${GRAY}python manage.py runserver${NC}"
echo ""
echo -e "  ${NC}3. Access the application:${NC}"
echo -e "     ${GRAY}API: http://127.0.0.1:8000/api/${NC}"
echo -e "     ${GRAY}Swagger: http://127.0.0.1:8000/swagger/${NC}"
echo -e "     ${GRAY}Admin: http://127.0.0.1:8000/admin/${NC}"
echo ""
echo -e "${YELLOW}For more information, see README.md${NC}"
echo ""
