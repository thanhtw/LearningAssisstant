#!/bin/bash

# Run frontend only (Vite dev server)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

FRONTEND_ENV="LearningAssistant"

echo -e "${BLUE}🚀 Starting Nova Frontend (Vite)...${NC}"
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda is not installed. Please run setup.sh first.${NC}"
    exit 1
fi

# Check if environment exists
if ! conda env list | grep -q "^${FRONTEND_ENV}"; then
    echo -e "${RED}❌ Frontend environment '${FRONTEND_ENV}' not found.${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

echo -e "${BLUE}📝 Configuration:${NC}"
echo "   Environment: ${FRONTEND_ENV}"
echo "   Directory: ./nova-tutor"
echo ""

# Start frontend server
eval "$(conda shell.bash hook)"
conda activate ${FRONTEND_ENV}
cd nova-tutor

echo -e "${GREEN}✅ Frontend starting...${NC}"
echo ""
echo -e "${BLUE}📍 Access point:${NC}"
echo -e "   Frontend: ${YELLOW}http://localhost:5173${NC}"
echo ""

npm run dev
