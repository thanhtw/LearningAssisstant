#!/bin/bash

# Run script for Nova Learning Assistant
# Starts both backend (FastAPI) and frontend (Vite) servers

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKEND_ENV="nova-backend"
FRONTEND_ENV="LearningAssistant"

echo -e "${BLUE}🚀 Starting Nova Learning Assistant...${NC}"
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda is not installed. Please run setup.sh first.${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping Nova Learning Assistant...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Check if environments exist
if ! conda env list | grep -q "^${BACKEND_ENV}"; then
    echo -e "${RED}❌ Backend environment '${BACKEND_ENV}' not found.${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

if ! conda env list | grep -q "^${FRONTEND_ENV}"; then
    echo -e "${RED}❌ Frontend environment '${FRONTEND_ENV}' not found.${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f nova-backend/.env ]; then
    echo -e "${RED}❌ .env file not found in nova-backend/${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and update it with your API keys${NC}"
    exit 1
fi

echo -e "${BLUE}📝 Starting Backend (FastAPI)...${NC}"
echo "   Environment: ${BACKEND_ENV}"
echo "   Directory: ./nova-backend"
echo ""

# Start backend server
(
    eval "$(conda shell.bash hook)"
    conda activate ${BACKEND_ENV}
    cd nova-backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo -e "${BLUE}📝 Starting Frontend (Vite Dev Server)...${NC}"
echo "   Environment: ${FRONTEND_ENV}"
echo "   Directory: ./nova-tutor"
echo ""

# Start frontend server
(
    eval "$(conda shell.bash hook)"
    conda activate ${FRONTEND_ENV}
    cd nova-tutor
    npm run dev
) &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Nova Learning Assistant is running!${NC}"
echo ""
echo -e "${BLUE}📍 Access points:${NC}"
echo -e "   Frontend: ${YELLOW}http://localhost:5173${NC}"
echo -e "   Backend:  ${YELLOW}http://localhost:8000${NC}"
echo -e "   API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for both processes
wait
