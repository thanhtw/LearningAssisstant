# Nova Backend - Quick Start Guide

## 📦 Project Created Successfully

The nova-backend FastAPI + LangGraph project has been created at:
```
/home/selab/Desktop/Thomas/Learning-Assisstant/nova-backend/
```

## ✅ What Was Created

### Core Structure
```
nova-backend/
├── app/
│   ├── main.py              # FastAPI app with CORS configuration
│   ├── graph/
│   │   ├── state.py         # LearnerState TypedDict with 10 fields
│   │   ├── nodes.py         # 6 workflow node functions
│   │   └── graph.py         # Compiled StateGraph
│   ├── models/
│   │   └── student.py       # 6 Pydantic models
│   └── routers/
│       ├── chat.py          # POST /api/chat endpoint
│       └── session.py       # GET /api/session/{id} + more
├── pyproject.toml           # Dependencies configured
├── .env.example             # Configuration template
├── .gitignore              # Python project ignores
└── README.md               # Full documentation
```

### 📋 LearnerState TypedDict Fields
```python
messages: Annotated[List[dict], operator.add]  # Accumulated conversation
topic: str                                      # Learning subject
level: str                                      # beginner|intermediate|advanced
correct_answers: int                            # Count of correct responses
total_attempts: int                             # Total quiz attempts
misconceptions: List[str]                       # Identified learning gaps
mode: str                                       # explain|quiz|hint|celebrate
mood: str                                       # happy|excited|thinking|...
character_name: str                             # Tutor character name
session_id: str                                 # Session identifier
```

### 🔧 Graph Nodes (6 total)
1. **process_user_message** - Parse and analyze user input
2. **generate_response** - Create appropriate tutor response
3. **evaluate_answer** - Check answer correctness
4. **check_misconceptions** - Detect learning errors
5. **determine_difficulty** - Adjust level based on performance
6. **select_mode** - Choose next interaction mode

### 🎯 Pydantic Models (6 total)
- MessageModel
- ChatRequest
- ChatResponse
- SessionRequest
- SessionResponse
- StudentProfile

### 🛣️ API Endpoints
- `POST /api/chat` - Send message & get response
- `POST /api/session` - Create learning session
- `GET /api/session/{id}` - Get session details
- `DELETE /api/session/{id}` - Delete session
- `GET /api/sessions` - List all sessions
- `GET /` - Health check & API info
- `GET /health` - Service health endpoint

## 🚀 Installation

### 1. Create Virtual Environment
```bash
cd nova-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -e .
```

Or with uv (faster):
```bash
uv pip install -e .
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required in `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
API_PORT=8000
DEBUG=true
```

## 🏃 Running the Server

### Development Mode
```bash
python -m app.main
```

Server will start at: **http://localhost:8000**

### With Uvicorn Directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### View Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 Testing Endpoints

### Create Session
```bash
curl -X POST http://localhost:8000/api/session \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Basics",
    "level": "beginner",
    "character_name": "Nova"
  }'
```

### Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "What is a variable?",
    "topic": "Python Basics",
    "level": "beginner"
  }'
```

### Get Session Details
```bash
curl http://localhost:8000/api/session/550e8400-e29b-41d4-a716-446655440000
```

## 📦 Dependencies Installed

- **fastapi** - Modern async Python web framework
- **uvicorn** - ASGI server with reload support
- **langgraph** - Graph-based workflow orchestration
- **langchain-core** - Core LLM utilities
- **langchain-anthropic** - Anthropic Claude integration
- **pydantic** - Data validation with type hints
- **python-dotenv** - Environment configuration
- **pydantic-settings** - Settings management

## 🔗 Connecting to Frontend

Update frontend API calls to point to backend:

```javascript
const API_BASE_URL = 'http://localhost:8000';

// Create session
const sessionRes = await fetch(`${API_BASE_URL}/api/session`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'Python',
    level: 'beginner',
    character_name: 'Nova'
  })
});

// Send chat message
const chatRes = await fetch(`${API_BASE_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    message: 'What is a variable?',
    topic: 'Python',
    level: 'beginner'
  })
});
```

## 📚 Project Features

✅ **Async/await** - All endpoints are fully async  
✅ **CORS enabled** - Cross-origin requests from frontend  
✅ **Type-safe** - Full type hints with Pydantic  
✅ **Error handling** - Global exception handler  
✅ **Session management** - Per-student learning sessions  
✅ **Workflow orchestration** - LangGraph state management  
✅ **Scalable** - Ready for database integration  
✅ **Documentation** - Auto-generated API docs  

## 🔐 Production Deployment

### Environment Setup
```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export DEBUG=false
export ANTHROPIC_API_KEY=sk-ant-...
export LOG_LEVEL=info
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "app.main"]
```

### Build Docker Image
```bash
docker build -t nova-backend:latest .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... nova-backend:latest
```

## 🐛 Troubleshooting

### ModuleNotFoundError
```bash
# Reinstall package
pip install -e .

# Or use pip with no cache
pip install --no-cache-dir -e .
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

### CORS Errors
- Check frontend origin in `.env` ALLOWED_ORIGINS
- Ensure frontend is in the list

### Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📖 Next Steps

1. **Install dependencies**: `pip install -e .`
2. **Set API keys**: Edit `.env`
3. **Start server**: `python -m app.main`
4. **Test endpoints**: Visit `/docs` for interactive testing
5. **Connect frontend**: Point nova-tutor frontend to `http://localhost:8000`

## 📞 Support

Full documentation available in `README.md` in the nova-backend directory.

---

**Nova Backend is ready to power your AI learning assistant! 🚀**
