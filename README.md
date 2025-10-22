# 🏥 Medical Clinic Chatbot - Educational Project

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-green.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini%202.0-orange.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-149%20total-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-65%25-yellowgreen.svg)](pytest.ini)

An **AI-powered conversational assistant** for medical clinics demonstrating modern chatbot development with Google's Gemini 2.0 Flash, FastAPI, and SQLAlchemy. Features intelligent appointment scheduling, FAQ handling, task management, and conversation history persistence.

> 🎓 **Educational Project**: Built for learning chatbot development patterns, LLM integration, and production-ready architecture. Not intended for actual medical use without HIPAA compliance and proper security measures.

---

## 📑 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start-5-minutes)
- [Demo Scenarios](#-demo-scenarios)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Development Guide](#-development-guide)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Capabilities

- 🤖 **Natural Language Conversations**: Powered by Google Gemini 2.0 Flash with context retention
- 📅 **Smart Appointment Scheduling**: Multi-turn booking with date/time validation and conflict checking
- ❓ **FAQ Knowledge Base**: Answers common questions about clinic hours, services, insurance, and policies
- ✅ **Task Management**: Auto-creates follow-up tasks for staff (callbacks, prescriptions, medical records)
- 💾 **Conversation Persistence**: Database-backed history with session restoration after server restarts
- 🌐 **Web Chat Interface**: Simple, responsive chat widget for patient interactions

### Technical Highlights

- ⚡ **Function Calling**: LLM autonomously executes Python functions for appointments and todos
- 🔄 **Context Tracking**: Maintains conversation state across multiple turns and server restarts
- 🏗️ **REST API**: 20+ FastAPI endpoints with OpenAPI documentation
- 🗄️ **Database Integration**: SQLAlchemy ORM with SQLite (easily migrates to PostgreSQL)
- 🧪 **Comprehensive Testing**: 149 pytest tests with 65% code coverage
- 📊 **Production Ready**: Error handling, rate limiting awareness, graceful degradation

---

## 🚀 Quick Start (5 Minutes)

## 🏗️ Architecture

```
┌─────────────┐
│   Patient   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Chat Widget    │  (HTML/JS)
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   FastAPI       │  /chat, /appointments, /todos
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌──────────────┐
│ Gemini │  │   Database   │
│ 2.0    │  │   (SQLite)   │
└────────┘  └──────────────┘
    │
    ▼
┌─────────────────┐
│ Function Tools  │  schedule_appointment, create_todo, get_faq
└─────────────────┘
```

### Prerequisites

- **Python 3.11+** (get it at [python.org](https://www.python.org/downloads/))
- **Google API Key** ([free at Google AI Studio](https://aistudio.google.com/app/apikey)) - 50 requests/day free!

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Topic

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
echo "GOOGLE_API_KEY=your-actual-key-here" > .env

# 5. Initialize database
python src/init_db.py
```

### Start the Server

```bash
uvicorn src.main:app --reload

# ✅ Server running at http://localhost:8000
# 📚 API docs at http://localhost:8000/docs
# 🔧 Interactive docs at http://localhost:8000/redoc
```

### Test It Out

**Option 1: Web Interface** (Easiest)
```bash
# Open the chat widget in your browser
open frontend/index.html  # macOS
xdg-open frontend/index.html  # Linux
start frontend/index.html  # Windows
```

**Option 2: Command Line**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your hours?", "session_id": "test-123"}'
```

**Option 3: Interactive Demo**
```bash
# Run all demo scenarios
python demo_interactive.py

# Or try manual chat mode
python demo_interactive.py --manual
```

### 📖 Detailed Setup Guide

For comprehensive setup instructions, troubleshooting, and best practices, see:
- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step guide with common issues
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: Development guide

---

## 🎭 Demo Scenarios

## 📖 Example Conversations

### Scheduling an Appointment
```
User: I need to see a doctor next week
Bot:  I'd be happy to help you schedule an appointment! 
      What day next week works best for you?

User: Tuesday at 2pm
Bot:  Great! And what's the reason for your visit?

User: Annual checkup
Bot:  Perfect! I've scheduled your appointment for Tuesday, 
      October 28th at 2:00 PM for an annual checkup. 
      You'll receive a confirmation shortly.
```

### Asking About Clinic Hours
```
User: What are your hours?
Bot:  We're open Monday through Friday, 9 AM to 5 PM, 
      and Saturdays from 9 AM to 12 PM. Is there anything 
      else you'd like to know?
```

### Creating a Follow-up Task
```
User: I've been having headaches for 3 days
Bot:  I understand that must be concerning. I'm creating a 
      high-priority task for one of our nurses to call you 
      back within 4 hours to discuss your symptoms. 
      
      In the meantime, if this is an emergency, please call 
      911 or go to the nearest ER.
```

### 🎭 More Demo Scenarios

For comprehensive demonstrations of all chatbot capabilities, see:
- **[DEMO_SCENARIOS.md](DEMO_SCENARIOS.md)**: 8 detailed scenarios with full conversations
- **Interactive Demo Script**: Run `python demo_interactive.py` to see scenarios in action

```bash
# Run all scenarios (automated)
python demo_interactive.py

# Run specific scenario
python demo_interactive.py --scenario 3

# Manual chat mode (try it yourself!)
python demo_interactive.py --manual

# List all available scenarios
python demo_interactive.py --list
```

**Demo Scenarios Include**:
1. ✅ Simple appointment booking
2. ✅ FAQ → Appointment flow
3. ✅ Multi-turn conversation with context
4. ✅ Insurance verification + booking
5. ✅ Callback request (todo creation)
6. ✅ Multiple FAQ questions
7. ✅ Complex multi-function conversation
8. ✅ Session restoration after restart

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────┐
│   Patient   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Chat Widget    │  HTML/CSS/JavaScript
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────┐
│         FastAPI Server              │
│  • /chat - Main chat endpoint       │
│  • /appointments - Booking API      │
│  • /todos - Task management         │
│  • /knowledge-base - FAQ search     │
└────────┬────────────────────────────┘
         │
    ┌────┴─────────────┐
    ▼                  ▼
┌──────────┐    ┌────────────────┐
│  Gemini  │    │   SQLite DB    │
│  2.0 API │    │  • Appointments│
│          │    │  • Todos       │
│ Function │    │  • Conversations│
│ Calling  │    │  • Settings    │
└────┬─────┘    └────────────────┘
     │
     ▼
┌─────────────────────────┐
│   Function Tools        │
│  • schedule_appointment │
│  • create_todo          │
│  • search_knowledge_base│
└─────────────────────────┘
```

### Data Flow Example

```
User: "Schedule me Tuesday at 2pm"
  ↓
FastAPI /chat endpoint
  ↓
ChatBot.send_message()
  ├─► Save to conversations table (user message)
  ↓
Google Gemini API
  ├─► Analyzes: Appointment request detected
  ├─► Extracts: date="2025-10-29", time="14:00"
  ├─► Calls: schedule_appointment() function
  ↓
AppointmentHandler.schedule_appointment()
  ├─► Validates date/time
  ├─► Checks conflicts
  ├─► Saves to appointments table
  ├─► Auto-creates todo reminder
  ↓
Gemini formats confirmation message
  ↓
ChatBot saves bot response to conversations
  ↓
Returns JSON to frontend
  ↓
User sees: "✅ Appointment confirmed!"
```

**📐 For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)**

---

## 📡 API Documentation

### Chat Endpoint

**POST** `/chat`

Main conversational interface. Processes natural language and executes appropriate functions.

```bash
# Request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need an appointment Tuesday at 2pm for checkup",
    "session_id": "patient-123"  # Optional: maintains context
  }'

# Response
{
  "response": "I've scheduled your appointment for Tuesday, October 29th at 2:00 PM for an annual checkup. You'll receive a confirmation shortly.",
  "session_id": "patient-123"
}
```

### Appointment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/appointments` | List all appointments |
| `POST` | `/appointments` | Create appointment directly |
| `GET` | `/appointments/{id}` | Get appointment details |
| `PUT` | `/appointments/{id}` | Update appointment |
| `DELETE` | `/appointments/{id}` | Cancel appointment |

**Example: List Appointments**
```bash
curl http://localhost:8000/appointments

# Response
[
  {
    "id": 1,
    "patient_name": "Sarah Johnson",
    "date": "2025-10-29",
    "time": "14:00",
    "reason": "Annual checkup",
    "status": "scheduled",
    "created_at": "2025-10-20T10:30:00"
  }
]
```

### Todo Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/todos` | List all todos |
| `POST` | `/todos` | Create new todo |
| `GET` | `/todos/{id}` | Get todo details |
| `PUT` | `/todos/{id}` | Update todo |
| `PUT` | `/todos/{id}/complete` | Mark todo complete |
| `DELETE` | `/todos/{id}` | Delete todo |

**Example: Create Todo**
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Call patient about prescription",
    "description": "Blood pressure medication refill",
    "priority": "high",
    "assignee": "nurse",
    "category": "callback"
  }'
```

### Knowledge Base Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/knowledge-base/search?query=hours` | Search FAQs |
| `GET` | `/clinic-info` | Get clinic information |

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📁 Project Structure

```
Topic/
├── src/
│   ├── main.py                 # FastAPI app with all endpoints
│   ├── chatbot.py              # ChatBot class with Gemini integration
│   ├── todo_manager.py         # Todo CRUD operations
│   ├── database.py             # SQLAlchemy session management
│   ├── models.py               # Database models (ORM)
│   ├── init_db.py              # Database initialization script
│   ├── handlers/
│   │   ├── appointment.py      # Appointment scheduling logic
│   │   └── faq.py             # FAQ response handling
│   └── knowledge_base.py       # Clinic FAQs and information
│
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_chatbot.py         # ChatBot tests (28 tests)
│   ├── test_todo_manager.py    # TodoManager tests (26 tests)
│   ├── test_appointment_handler.py  # Appointment tests (24 tests)
│   ├── test_faq_knowledge_base.py   # FAQ tests (36 tests)
│   └── test_api_endpoints.py   # FastAPI tests (35 tests)
│
├── frontend/
│   ├── index.html              # Chat widget interface
│   ├── chat.js                 # Frontend JavaScript
│   └── styles.css              # Chat widget styling
│
├── .github/
│   └── copilot-instructions.md # AI development guide
│
├── demo_interactive.py         # Interactive demo script
├── test_comprehensive_demo.py  # Automated demo scenarios
├── test_context_tracking.py    # Context persistence tests
│
├── DEMO_SCENARIOS.md           # 8 detailed conversation examples
├── ARCHITECTURE.md             # System architecture documentation
├── QUICKSTART.md               # Quick setup guide
├── TASK9_COMPLETE.md           # Testing documentation
├── TASK10_COMPLETE.md          # Context tracking documentation
│
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

### Key Files Explained

| File | Purpose | Lines |
|------|---------|-------|
| `src/chatbot.py` | Core chatbot with Gemini integration | ~250 |
| `src/main.py` | FastAPI server with 20+ endpoints | ~400 |
| `src/models.py` | SQLAlchemy database models | ~150 |
| `src/handlers/appointment.py` | Appointment validation & scheduling | ~200 |
| `src/todo_manager.py` | Task CRUD operations | ~150 |
| `src/knowledge_base.py` | FAQ database and search | ~300 |
| `demo_interactive.py` | Interactive demo runner | ~350 |

---

## 💻 Development Guide

### Prerequisites

- Python 3.11+ installed
- Virtual environment activated
- Google API key configured
- SQLite (comes with Python)

### Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Run server with auto-reload
uvicorn src.main:app --reload

# 3. Make code changes
# Server auto-restarts on file changes

# 4. Test changes
pytest tests/test_your_module.py -v

# 5. Run all tests before committing
pytest --cov=src tests/
```

### Adding New Features

**Example: Add new function for the chatbot**

1. **Define function in `src/chatbot.py`:**
```python
def check_lab_results(patient_name: str):
    """Check if lab results are available"""
    # Implementation
    return {"status": "available", "results_url": "..."}
```

2. **Register function tool:**
```python
tools = [
    # ... existing tools ...
    {
        "type": "function",
        "function": {
            "name": "check_lab_results",
            "description": "Check laboratory test results",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"}
                },
                "required": ["patient_name"]
            }
        }
    }
]
```

3. **Add function call handler in `send_message()`:**
```python
if func_name == "check_lab_results":
    result = check_lab_results(**func_args)
```

4. **Write tests in `tests/test_chatbot.py`:**
```python
def test_check_lab_results(chatbot):
    response = chatbot.send_message(
        "Are my lab results ready?",
        session_id="test"
    )
    assert "results" in response.lower()
```

### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for function parameters
- Add docstrings to all classes and functions
- Keep functions under 50 lines when possible
- Use meaningful variable names

### Database Migrations

```bash
# View current schema
sqlite3 clinic.db ".schema"

# Add new column (example)
sqlite3 clinic.db "ALTER TABLE appointments ADD COLUMN provider VARCHAR;"

# Reset database (development only!)
rm clinic.db
python src/init_db.py
```

---

## 🧪 Testing

### Test Suite Overview

**149 tests** across 5 test files with **65% code coverage**

| Test File | Tests | Focus Area |
|-----------|-------|------------|
| `test_chatbot.py` | 28 | ChatBot class, Gemini integration |
| `test_todo_manager.py` | 26 | Todo CRUD operations |
| `test_appointment_handler.py` | 24 | Appointment scheduling |
| `test_faq_knowledge_base.py` | 36 | FAQ search and retrieval |
| `test_api_endpoints.py` | 35 | FastAPI endpoints |

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chatbot.py -v

# Run specific test function
pytest tests/test_chatbot.py::test_schedule_appointment -v

# Run with coverage report
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# Opens in htmlcov/index.html
```

### Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

### Writing Tests

**Example test structure:**

```python
import pytest
from src.chatbot import ChatBot

@pytest.fixture
def chatbot():
    """Create ChatBot instance for testing"""
    bot = ChatBot()
    yield bot
    # Cleanup if needed

def test_simple_faq(chatbot):
    """Test FAQ handling"""
    response = chatbot.send_message(
        "What are your hours?",
        session_id="test-faq"
    )
    assert "9" in response
    assert "5" in response
    
def test_appointment_booking(chatbot):
    """Test appointment scheduling"""
    response = chatbot.send_message(
        "Schedule me Tuesday at 2pm for checkup",
        session_id="test-appt"
    )
    assert "confirm" in response.lower() or "scheduled" in response.lower()
```

### Demo Tests

```bash
# Run comprehensive demo scenarios
python test_comprehensive_demo.py

# Run context tracking tests
python test_context_tracking.py

# Run interactive demo
python demo_interactive.py --manual
```

**📚 For detailed testing documentation, see [TASK9_COMPLETE.md](TASK9_COMPLETE.md)**

---

## 🚀 Deployment

### Development Deployment (Current)

```bash
# Single process server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Characteristics:**
- SQLite database (file-based)
- Single process (no horizontal scaling)
- Suitable for testing and demos
- No authentication required

### Production Deployment (Recommended)

#### Option 1: Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY frontend/ ./frontend/

ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t clinic-chatbot .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your-key clinic-chatbot
```

#### Option 2: Cloud Platform (Heroku, AWS, GCP)

**Heroku Example:**
```bash
# Procfile
web: uvicorn src.main:app --host=0.0.0.0 --port=${PORT:-8000}

# Deploy
git push heroku main
heroku config:set GOOGLE_API_KEY=your-key
```

**AWS EC2 Example:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx

# Clone and setup
git clone <repo>
cd Topic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo systemctl start clinic-chatbot.service
```

#### Option 3: Multiple Workers (Production Scale)

```bash
# Using Gunicorn with Uvicorn workers
pip install gunicorn

gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Production Checklist

#### Security
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Add user authentication (JWT tokens)
- [ ] Implement rate limiting
- [ ] Enable HTTPS/TLS
- [ ] Sanitize all user inputs
- [ ] Add HIPAA compliance measures
- [ ] Implement audit logging
- [ ] Use environment variables for secrets

#### Performance
- [ ] Add Redis for session caching
- [ ] Implement connection pooling
- [ ] Set up load balancer
- [ ] Configure CDN for static files
- [ ] Add database indexes
- [ ] Enable response compression

#### Monitoring
- [ ] Set up logging (e.g., Sentry)
- [ ] Add health check endpoints
- [ ] Monitor API quota usage
- [ ] Track response times
- [ ] Set up alerts for errors

#### Database Migration

```python
# Switch from SQLite to PostgreSQL
# In src/database.py

# Before (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./clinic.db"

# After (PostgreSQL)
SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/clinic_db"
```

---

## 🔧 Troubleshooting

## 📁 Project Structure

```
Topic/
├── src/
│   ├── main.py              # FastAPI app
│   ├── chatbot.py           # ChatBot class with OpenAI
│   ├── todo_manager.py      # Todo operations
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── init_db.py           # Database initialization
│   ├── handlers/
│   │   ├── appointment.py   # Appointment logic
│   │   └── faq.py          # FAQ responses
│   └── knowledge_base.py    # Clinic FAQs
├── tests/
│   ├── test_chatbot.py
│   ├── test_todo_manager.py
│   └── test_api.py
├── frontend/
│   ├── index.html          # Chat interface
│   └── chat.js             # Frontend logic
├── .github/
│   └── copilot-instructions.md  # AI coding guide
├── requirements.txt
├── .env.example
└── README.md
```

## 🎓 Key Learning Concepts

### 1. Gemini Function Calling
The chatbot uses function calling to let Gemini decide when to execute actions:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_appointment",
            "description": "Schedule a patient appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "reason": {"type": "string"}
                }
            }
        }
    }
]
```

### 2. Conversation Context
Messages are stored and passed to maintain context:

```python
messages = [
    {"role": "system", "content": "You are a helpful clinic assistant."},
    {"role": "user", "content": "I need an appointment"},
    {"role": "assistant", "content": "What date works for you?"},
    {"role": "user", "content": "Next Tuesday"}
]
```

### 3. Database Integration
SQLAlchemy models for structured data:

```python
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_name = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String, default="scheduled")
```

## 🛠️ Customization Ideas

- Add SMS notifications using Twilio
- Implement provider-specific scheduling
- Add symptom checker with medical knowledge base
- Build admin dashboard for viewing conversations
- Add voice interface with speech-to-text
- Implement multi-language support
- Add patient authentication
- Connect to real calendar systems

### Common Issues and Solutions

#### "Google API key not found"

**Problem:** Server won't start or chatbot returns errors

**Solutions:**
```bash
# 1. Check .env file exists
cat .env
# Should show: GOOGLE_API_KEY=AIza...

# 2. If missing, create it
echo "GOOGLE_API_KEY=your-actual-key-here" > .env

# 3. Verify key is valid at https://aistudio.google.com/app/apikey

# 4. Restart server
uvicorn src.main:app --reload
```

#### "Module not found" errors

**Problem:** Import errors when running server or tests

**Solutions:**
```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Verify activation (should show (venv) in prompt)
which python  # Should point to venv/bin/python

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. If still issues, recreate venv
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### "Port already in use"

**Problem:** `Address already in use` error when starting server

**Solutions:**
```bash
# Find process using port 8000
lsof -ti:8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 $(lsof -ti:8000)  # Linux/Mac

# Or use different port
uvicorn src.main:app --port 8001
```

#### "Database locked" error

**Problem:** `database is locked` when running operations

**Solutions:**
```bash
# 1. Close all connections to database
pkill -9 python  # Nuclear option

# 2. Reset database
rm clinic.db
python src/init_db.py

# 3. For production, migrate to PostgreSQL
# See Deployment section
```

#### "429 Quota Exceeded" from Gemini API

**Problem:** `You exceeded your current quota` error

**Root Cause:** Free tier has 50 requests/day limit

**Solutions:**
```bash
# 1. Check quota usage at https://aistudio.google.com

# 2. Wait for daily reset (resets every 24 hours)

# 3. For development, implement caching:
# - Cache common FAQ responses
# - Use mock responses in tests

# 4. For production, consider paid tier

# 5. Temporary: Run demos with fewer scenarios
python demo_interactive.py --scenario 1
```

#### Chat responses are slow or timing out

**Problem:** Responses take >10 seconds or time out

**Diagnosis:**
```bash
# Check network latency to Gemini API
curl -w "@curl-format.txt" -o /dev/null -s https://generativelanguage.googleapis.com

# Check system resources
top  # Linux/Mac
```

**Solutions:**
```bash
# 1. Check internet connection
ping google.com

# 2. Increase timeout in chatbot.py
# In ChatBot.__init__():
self.model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    # Add request_options with timeout
)

# 3. Use faster model (though 2.0 Flash is already fast)

# 4. Check API status at https://status.cloud.google.com
```

#### Tests failing with API errors

**Problem:** Tests fail due to API quota or rate limits

**Solutions:**
```bash
# 1. Run tests without API calls (use mocks)
pytest -m "not api"

# 2. Run subset of tests
pytest tests/test_todo_manager.py  # No API calls

# 3. Implement test fixtures with cached responses
# See tests/conftest.py for examples

# 4. Skip chatbot tests temporarily
pytest --ignore=tests/test_chatbot.py
```

#### Frontend not connecting to backend

**Problem:** Chat widget shows connection errors

**Solutions:**
```bash
# 1. Verify server is running
curl http://localhost:8000/health

# 2. Check CORS settings in src/main.py
# Should allow your origin

# 3. Open browser console (F12) for error details

# 4. Try curl to isolate issue
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

#### Import errors in tests

**Problem:** `ImportError: cannot import name 'ChatBot'`

**Solutions:**
```bash
# Tests use sys.path.insert(0, 'src')
# Ensure you run from project root

# Correct:
cd Topic
pytest

# Wrong:
cd Topic/tests
pytest  # Will fail with import errors
```

### Getting Help

1. **Check Documentation**:
   - [QUICKSTART.md](QUICKSTART.md) - Setup guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [DEMO_SCENARIOS.md](DEMO_SCENARIOS.md) - Usage examples

2. **Review Logs**:
   ```bash
   # Run with verbose logging
   uvicorn src.main:app --log-level debug
   
   # Capture logs to file
   python demo_interactive.py 2>&1 | tee debug.log
   ```

3. **Database Inspection**:
   ```bash
   # Check database contents
   sqlite3 clinic.db "SELECT * FROM appointments;"
   sqlite3 clinic.db "SELECT * FROM conversations;"
   ```

4. **Test Specific Components**:
   ```bash
   # Test chatbot directly
   python -c "
   import sys; sys.path.insert(0, 'src')
   from chatbot import ChatBot
   bot = ChatBot()
   print(bot.send_message('test', 'session-1'))
   "
   ```

---

## 📚 Resources

### Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Fast setup guide (5 minutes)
- **[DEMO_SCENARIOS.md](DEMO_SCENARIOS.md)**: 8 detailed conversation examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and data flows
- **[TASK9_COMPLETE.md](TASK9_COMPLETE.md)**: Testing strategy and results
- **[TASK10_COMPLETE.md](TASK10_COMPLETE.md)**: Context tracking implementation
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: Development guide

### External Resources

- **Google Gemini**:
  - [Gemini API Documentation](https://ai.google.dev/docs)
  - [Function Calling Guide](https://ai.google.dev/docs/function_calling)
  - [Get API Key](https://aistudio.google.com/app/apikey)
  - [Rate Limits & Quotas](https://ai.google.dev/gemini-api/docs/rate-limits)

- **FastAPI**:
  - [FastAPI Documentation](https://fastapi.tiangolo.com/)
  - [Tutorial](https://fastapi.tiangolo.com/tutorial/)
  - [Advanced User Guide](https://fastapi.tiangolo.com/advanced/)

- **SQLAlchemy**:
  - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
  - [ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)

- **Pytest**:
  - [Pytest Documentation](https://docs.pytest.org/)
  - [Fixtures Guide](https://docs.pytest.org/en/stable/fixture.html)

### Learning Path

**Beginner** (Week 1):
1. ✅ Complete Quick Start
2. ✅ Run demo scenarios: `python demo_interactive.py`
3. ✅ Read [DEMO_SCENARIOS.md](DEMO_SCENARIOS.md)
4. ✅ Explore web interface: `frontend/index.html`
5. ✅ Test API with curl or Postman

**Intermediate** (Week 2):
1. ✅ Read `src/chatbot.py` - understand Gemini integration
2. ✅ Read `src/main.py` - FastAPI endpoints
3. ✅ Study [ARCHITECTURE.md](ARCHITECTURE.md)
4. ✅ Run tests: `pytest -v`
5. ✅ Modify system instructions and test changes

**Advanced** (Week 3-4):
1. ✅ Add new function to chatbot
2. ✅ Create custom demo scenario
3. ✅ Write new tests
4. ✅ Modify database schema
5. ✅ Deploy to cloud platform
6. ✅ Read [.github/copilot-instructions.md](.github/copilot-instructions.md)

---

## 🤝 Contributing

Contributions are welcome! This is an educational project, so feel free to:

### Ways to Contribute

- 🐛 Report bugs or issues
- 💡 Suggest new features or improvements
- 📝 Improve documentation
- ✅ Add more test cases
- 🎨 Enhance the chat widget UI
- 🔧 Optimize performance
- 🌐 Add multi-language support

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**:
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Run tests**: `pytest --cov=src tests/`
5. **Commit changes**: `git commit -m "Add amazing feature"`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to all functions/classes
- Keep functions focused and under 50 lines
- Write descriptive commit messages

### Testing Requirements

- All new features must have tests
- Maintain >60% code coverage
- Tests must pass before PR merge
- Include integration tests for API changes

---

## 📄 License

MIT License

Copyright (c) 2025 Medical Clinic Chatbot Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## ⚠️ Disclaimer

### Educational Use Only

This project is intended **solely for educational purposes** to demonstrate:
- Conversational AI development patterns
- LLM function calling
- REST API design with FastAPI
- Database integration with SQLAlchemy
- Testing strategies for AI applications

### Not for Medical Use

⚠️ **This chatbot is NOT suitable for actual medical use without**:
- HIPAA compliance implementation
- Security audit and penetration testing
- Medical professional review and validation
- Proper error handling for medical scenarios
- Patient data encryption and privacy controls
- Authentication and authorization systems
- Comprehensive logging and audit trails
- Professional legal review

### Production Considerations

Before using in any real-world medical setting:
1. Implement comprehensive security measures
2. Add HIPAA-compliant data handling
3. Conduct thorough security audits
4. Add robust error handling
5. Implement proper authentication
6. Add comprehensive monitoring
7. Ensure regulatory compliance
8. Obtain necessary legal clearances

---

## 🎉 Acknowledgments

- **Google Gemini Team**: For the excellent free-tier LLM API
- **FastAPI**: For the amazing Python web framework
- **SQLAlchemy**: For the powerful ORM
- **Pytest**: For the comprehensive testing framework
- **Open Source Community**: For inspiration and tools

---

## 📞 Contact & Support

- **Documentation**: See docs/ directory and *.md files
- **Issues**: Open an issue on GitHub
- **Questions**: Check [QUICKSTART.md](QUICKSTART.md) and [ARCHITECTURE.md](ARCHITECTURE.md)

---

<div align="center">

**Built with ❤️ for learning and education**

⭐ **Star this repo** if you found it helpful!

[Quick Start](#-quick-start-5-minutes) •
[Documentation](#-table-of-contents) •
[Demo](#-demo-scenarios) •
[API Docs](#-api-documentation) •
[Contributing](#-contributing)

</div>

## 📚 Resources

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

## 📝 License

MIT License - feel free to use for learning and education!

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new features
- Improve conversation quality
- Add more test cases
- Enhance documentation

## ⚠️ Disclaimer

This is a learning project and NOT intended for actual medical use. For production:
- Implement HIPAA compliance
- Add security audits
- Get medical professional review
- Add proper error handling
- Implement authentication
- Use production-grade database

---

**Happy Learning! 🎓**
