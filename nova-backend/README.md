# Nova Backend 🚀

FastAPI + LangGraph backend for the Nova Tutor AI Learning Assistant.

## Features

- **FastAPI** - Modern async Python web framework
- **LangGraph** - Agent workflow orchestration for educational interactions
- **TypedDict State Management** - Type-safe state handling across workflow nodes
- **CORS Enabled** - Cross-origin requests from frontend
- **Session Management** - Per-student learning session tracking
- **Adaptive Learning** - Difficulty adjustment based on performance

## Project Structure

```
nova-backend/
├── app/
│   ├── main.py              # FastAPI app & CORS setup
│   ├── graph/
│   │   ├── state.py         # LearnerState TypedDict
│   │   ├── nodes.py         # Workflow node functions
│   │   └── graph.py         # Compiled StateGraph
│   ├── models/
│   │   └── student.py       # Pydantic models
│   └── routers/
│       ├── chat.py          # POST /api/chat
│       └── session.py       # GET /api/session/{id}
├── pyproject.toml           # Dependencies
└── .env.example             # Configuration template
```

## Installation

### Prerequisites

- Python 3.10+
- pip or uv

### Setup

1. **Clone and navigate to backend:**

```bash
cd nova-backend
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

4. **Configure environment:**

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
API_PORT=8000
DEBUG=true
```

## Running the Server

### Development Mode

```bash
python -m app.main
```

Server runs at `http://localhost:8000`

### With Uvicorn Directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Create Session

```bash
POST /api/session
Content-Type: application/json

{
  "topic": "Python Basics",
  "level": "beginner",
  "character_name": "Nova"
}
```

Response:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Python Basics",
  "level": "beginner",
  "created_at": "2024-05-21T10:30:00"
}
```

### Send Chat Message

```bash
POST /api/chat
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "What is a variable?",
  "topic": "Python Basics",
  "level": "beginner"
}
```

Response:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "A variable is a named container for storing values...",
  "mood": "happy",
  "mode": "explain",
  "correct_answers": 3,
  "total_attempts": 5,
  "misconceptions": []
}
```

### Get Session Details

```bash
GET /api/session/550e8400-e29b-41d4-a716-446655440000
```

Response:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Python Basics",
  "level": "intermediate",
  "character_name": "Nova",
  "correct_answers": 7,
  "total_attempts": 10,
  "misconceptions": ["variables are immutable"],
  "messages": [
    {
      "role": "user",
      "content": "What is a variable?"
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ],
  "created_at": "2024-05-21T10:30:00",
  "last_activity": "2024-05-21T10:45:30"
}
```

### List All Sessions

```bash
GET /api/sessions
```

### Delete Session

```bash
DELETE /api/session/550e8400-e29b-41d4-a716-446655440000
```

## LearnerState

The workflow state includes:

```python
class LearnerState(TypedDict):
    messages: Annotated[List[dict], operator.add]  # Accumulated messages
    topic: str                                      # Learning topic
    level: str                                      # beginner|intermediate|advanced
    correct_answers: int                            # Correct answer count
    total_attempts: int                             # Quiz attempts
    misconceptions: List[str]                       # Identified misconceptions
    mode: str                                       # explain|quiz|hint|celebrate
    mood: str                                       # happy|excited|thinking|sad|confused|proud
    character_name: str                             # Tutor name
    session_id: str                                 # Session ID
```

## Workflow Nodes

1. **process_message** - Parse and analyze user input
2. **generate_response** - Create appropriate tutor response
3. **evaluate_answer** - Check correctness in quiz mode
4. **check_misconceptions** - Detect learning errors
5. **determine_difficulty** - Adjust level based on performance
6. **select_mode** - Choose next interaction mode

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **langgraph** - Graph-based workflows
- **langchain-core** - LLM integration
- **langchain-anthropic** - Claude API integration
- **pydantic** - Data validation
- **python-dotenv** - Environment variables

## Development

### Adding New Nodes

1. Create function in `app/graph/nodes.py`
2. Add to graph in `app/graph/graph.py`
3. Connect edges to workflow

### Extending State

Modify `app/graph/state.py` to add new fields to `LearnerState`.

### Adding Routes

Create new routers in `app/routers/` and include in `app.main`.

## Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## Deployment

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "app.main"]
```

### Environment Variables

Configure in production:

```
API_HOST=0.0.0.0
API_PORT=8000
ANTHROPIC_API_KEY=sk-ant-...
DEBUG=false
LOG_LEVEL=info
```

## Performance Considerations

- **Session Storage**: Currently in-memory; use database for production
- **Graph Caching**: StateGraph is compiled once at startup
- **Async Operations**: All routes are async-ready
- **Streaming**: Ready for token streaming with LLM responses

## Troubleshooting

### Module Not Found

```bash
# Reinstall in development mode
pip install -e .
```

### Import Errors

```bash
# Ensure package is in PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### API Not Responding

- Check if server is running on correct port
- Verify CORS origins in `.env`
- Check logs for errors

## License

MIT

## Support

For issues or feature requests, contact the development team.

---

**Ready to empower learning! 🎓**
