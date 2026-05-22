#!/bin/bash

# Setup script for Nova Learning Assistant project
# Creates conda environments and installs dependencies

set -e  # Exit on error

echo "🚀 Setting up Nova Learning Assistant..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda or Miniconda first."
    exit 1
fi

echo -e "${BLUE}📦 Step 1: Setting up backend environment...${NC}"
echo ""

# Initialize conda
eval "$(conda shell.bash hook)"

# Create nova-backend conda environment
BACKEND_ENV="nova-backend"
if conda env list | grep -q "^${BACKEND_ENV}"; then
    echo -e "${YELLOW}Environment '${BACKEND_ENV}' already exists. Updating...${NC}"
    conda activate ${BACKEND_ENV}
else
    echo "Creating conda environment: ${BACKEND_ENV}"
    conda create -n ${BACKEND_ENV} python=3.10 -y
    conda activate ${BACKEND_ENV}
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd nova-backend

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update .env with your Groq API key${NC}"
fi

# Install dependencies from pyproject.toml
pip install -e .
echo -e "${GREEN}✅ Backend environment ready!${NC}"
echo ""

# Navigate back to project root
cd ..

echo -e "${BLUE}📦 Step 2: Setting up frontend environment...${NC}"
echo ""

# Initialize conda
eval "$(conda shell.bash hook)"

# Create nova-tutor conda environment
FRONTEND_ENV="LearningAssistant"
if conda env list | grep -q "^${FRONTEND_ENV}"; then
    echo -e "${YELLOW}Environment '${FRONTEND_ENV}' already exists. Updating...${NC}"
    conda activate ${FRONTEND_ENV}
else
    echo "Creating conda environment: ${FRONTEND_ENV}"
    conda create -n ${FRONTEND_ENV} nodejs=20 -y
    conda activate ${FRONTEND_ENV}
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd nova-tutor
npm install
echo -e "${GREEN}✅ Frontend environment ready!${NC}"
echo ""

cd ..

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Update ./nova-backend/.env with your Groq API key"
echo "2. To run the project, use: ${YELLOW}./run.sh${NC}"
echo ""
echo -e "${BLUE}📝 Quick reference:${NC}"
echo "   Backend environment:  ${YELLOW}conda activate ${BACKEND_ENV}${NC}"
echo "   Frontend environment: ${YELLOW}conda activate ${FRONTEND_ENV}${NC}"
