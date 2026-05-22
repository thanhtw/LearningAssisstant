#!/bin/bash

# Run backend only (FastAPI server)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BACKEND_ENV="nova-backend"

echo -e "${BLUE}🚀 Starting Nova Backend (FastAPI)...${NC}"
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda is not installed. Please run setup.sh first.${NC}"
    exit 1
fi

# Check if environment exists
if ! conda env list | grep -q "^${BACKEND_ENV}"; then
    echo -e "${RED}❌ Backend environment '${BACKEND_ENV}' not found.${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f nova-backend/.env ]; then
    echo -e "${RED}❌ .env file not found in nova-backend/${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and update it with your API keys${NC}"
    exit 1
fi

echo -e "${BLUE}📝 Configuration:${NC}"
echo "   Environment: ${BACKEND_ENV}"
echo "   Directory: ./nova-backend"
echo ""

# Start backend server
eval "$(conda shell.bash hook)"
conda activate ${BACKEND_ENV}
cd nova-backend

echo -e "${GREEN}✅ Backend starting...${NC}"
echo ""
echo -e "${BLUE}📍 Access points:${NC}"
echo -e "   API Server: ${YELLOW}http://localhost:8000${NC}"
echo -e "   API Docs:   ${YELLOW}http://localhost:8000/docs${NC}"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
