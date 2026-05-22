# 🎓 Nova Learning Assistant - Setup & Running Guide

## Project Overview

Nova Learning Assistant is a full-stack learning platform combining:
- **Backend**: FastAPI + LangGraph with Groq AI (llama-3.3-70b-versatile)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS

---

## 📋 Prerequisites

Before starting, ensure you have installed:
- **Anaconda** or **Miniconda** ([Download](https://www.anaconda.com/download))
- **Git** (for version control)

---

## 🚀 Quick Start

### Step 1: Initial Setup (One-time)

Run the setup script to create conda environments and install all dependencies:

```bash
./setup.sh
```

This script will:
- ✅ Create conda environment `nova-backend` with Python 3.10
- ✅ Create conda environment `LearningAssistant` with Node.js 20
- ✅ Install all Python dependencies (FastAPI, LangGraph, etc.)
- ✅ Install all Node.js dependencies (React, Vite, etc.)
- ✅ Create `.env` file from `.env.example` (if not exists)

### Step 2: Configure API Keys

1. Navigate to `nova-backend/.env`
2. Replace the placeholder with your Groq API key:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
MODEL=llama-3.3-70b-versatile
```

Get your Groq API key from: [https://console.groq.com](https://console.groq.com)

### Step 3: Run the Project

#### Option A: Run Both Backend & Frontend Together (Recommended)

```bash
./run.sh
```

This will start:
- 🔵 **Backend API**: http://localhost:8000
- 🔵 **API Documentation**: http://localhost:8000/docs
- 🟡 **Frontend**: http://localhost:5173

#### Option B: Run Backend Only

```bash
./run-backend-only.sh
```

Starts only the FastAPI server at `http://localhost:8000`

#### Option C: Run Frontend Only

```bash
./run-frontend-only.sh
```

Starts only the Vite dev server at `http://localhost:5173`

---

## 🛠️ Manual Environment Management

If you prefer manual control, you can manage the conda environments directly:

### Activate Backend Environment
```bash
conda activate nova-backend
cd nova-backend
pip install -e .
uvicorn app.main:app --reload
```

### Activate Frontend Environment
```bash
conda activate LearningAssistant
cd nova-tutor
npm run dev
```

---

## 📁 Project Structure

```
Learning-Assistant/
├── setup.sh                          # Initial setup script
├── run.sh                           # Run both backend & frontend
├── run-backend-only.sh              # Run backend only
├── run-frontend-only.sh             # Run frontend only
│
├── nova-backend/                    # FastAPI + LangGraph backend
│   ├── .env                         # Configuration (create from .env.example)
│   ├── .env.example                 # Configuration template with Groq API
│   ├── pyproject.toml               # Python dependencies
│   ├── app/
│   │   ├── main.py                  # FastAPI application
│   │   ├── graph/                   # LangGraph state machine
│   │   ├── models/                  # Pydantic models
│   │   ├── routers/                 # API routes
│   │   └── services/                # Business logic
│   └── data/
│       └── curriculum.json          # Learning curriculum
│
└── nova-tutor/                      # React + Vite frontend
    ├── package.json                 # Node.js dependencies
    ├── tsconfig.json                # TypeScript configuration
    ├── vite.config.ts               # Vite configuration
    ├── tailwind.config.js           # Tailwind CSS configuration
    ├── src/
    │   ├── main.tsx                 # React entry point
    │   ├── App.tsx                  # Main component
    │   ├── components/              # React components
    │   ├── hooks/                   # Custom React hooks
    │   ├── api/                     # API client
    │   └── types/                   # TypeScript types
    └── public/                      # Static assets
```

---

## 🔑 Environment Variables

### Backend (.env.example)
```ini
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# LLM Configuration - Groq API
GROQ_API_KEY=your_groq_api_key_here
MODEL=llama-3.3-70b-versatile

# Alternative LLM Providers (Optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
LOG_LEVEL=INFO
MAX_TOKENS=2048
```

---

## 📦 Dependencies

### Backend
- **FastAPI** >= 0.104.1 - Web framework
- **Uvicorn** >= 0.24.0 - ASGI server
- **LangGraph** >= 0.0.38 - Graph-based workflows
- **LangChain** - LLM integration framework
- **Pydantic** >= 2.5.0 - Data validation
- **python-dotenv** - Environment configuration

### Frontend
- **React** ^18.2.0 - UI library
- **TypeScript** ^5.3.3 - Type safety
- **Vite** ^5.0.8 - Build tool
- **Tailwind CSS** ^3.4.1 - Styling
- **Axios** - HTTP client (implicit in api/client.ts)

---

## 🐍 Conda Environments

### nova-backend
- **Python**: 3.10
- **Location**: Created by setup.sh
- **Activate**: `conda activate nova-backend`

### LearningAssistant (Frontend)
- **Node.js**: 20
- **Location**: Created by setup.sh
- **Activate**: `conda activate LearningAssistant`

---

## 🔍 API Endpoints

Once the backend is running, explore the API:

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### Common Endpoints
- `POST /api/chat` - Send a message to the tutor
- `GET /api/session/{id}` - Get session information
- `GET /health` - Health check

---

## 📝 Common Tasks

### Install a New Backend Package
```bash
conda activate nova-backend
cd nova-backend
pip install package-name
```

### Install a New Frontend Package
```bash
conda activate LearningAssistant
cd nova-tutor
npm install package-name
```

### Update Frontend Build
```bash
conda activate LearningAssistant
cd nova-tutor
npm run build
```

### View Backend Logs
The backend runs with `--reload` flag, so logs appear in the terminal.

---

## 🐛 Troubleshooting

### "Conda is not installed"
**Solution**: Install Anaconda from https://www.anaconda.com/download

### "Environment not found"
**Solution**: Run `./setup.sh` again to create the environments

### ".env file not found"
**Solution**: Copy `.env.example` to `.env` and update your API keys
```bash
cp nova-backend/.env.example nova-backend/.env
```

### "Port 8000 already in use"
**Solution**: Change the port in `nova-backend/.env`:
```ini
API_PORT=8001
```

### "Port 5173 already in use"
**Solution**: Vite will automatically use the next available port

### Frontend can't reach backend
**Solution**: Ensure both servers are running:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Check CORS configuration in `nova-backend/app/main.py`

---

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review backend logs in the terminal
3. Check browser console for frontend errors (F12)
4. Ensure API keys are correctly configured in `.env`

---

## 🎯 Next Steps

1. ✅ Run `./setup.sh`
2. ✅ Configure `nova-backend/.env` with your Groq API key
3. ✅ Run `./run.sh` to start both servers
4. 🌐 Open http://localhost:5173 in your browser
5. 📚 Begin learning!

---

**Happy Learning! 🚀**
