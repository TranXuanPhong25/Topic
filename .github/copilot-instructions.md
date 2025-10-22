# Medical Clinic Chatbot Agent - AI Development Guide

## Project Overview
An educational conversational AI chatbot for medical clinics that demonstrates appointment scheduling, FAQ handling, and task management integration. This is a learning project showcasing chatbot development patterns.

**Note**: This is an educational project. For production medical use, add HIPAA compliance, security audits, and professional medical review.

## Tech Stack (Educational-Friendly)
- **Language**: Python 3.11+ (easy to learn, great AI/ML libraries)
- **Framework**: FastAPI (modern, fast, excellent docs)
- **LLM**: Google Gemini 2.0 Flash (free tier, powerful, simple API)
- **Database**: SQLite (simple, no setup) → PostgreSQL (for scaling)
- **Testing**: pytest (standard Python testing)
- **Frontend**: Simple HTML/CSS/JavaScript chat widget

## Architecture

### Core Components
- **ChatBot** (`src/chatbot.py`): Main conversation handler using OpenAI API
- **IntentRouter** (`src/intent_router.py`): Routes user messages to appropriate handlers
- **AppointmentHandler** (`src/handlers/appointment.py`): Manages appointment scheduling
- **FAQHandler** (`src/handlers/faq.py`): Handles common questions from knowledge base
- **TodoManager** (`src/todo_manager.py`): Creates and manages tasks for clinic staff
- **KnowledgeBase** (`src/knowledge_base.py`): Stores clinic FAQs, hours, policies
- **Database** (`src/database.py`): SQLite for appointments, todos, conversations

### Data Flow
```
User Input → ChatBot (GPT-4o-mini) → Intent Detection
    ↓
IntentRouter → Specific Handler (Appointment/FAQ/Todo)
    ↓
Handler → Database (save) + Response
    ↓
Response to User (+ create todo if needed)
```

### Key Learning Concepts
- **Prompt Engineering**: Using system prompts to guide GPT behavior
- **Function Calling**: GPT decides when to call tools (schedule, create_todo)
- **State Management**: Tracking conversation context in simple dict/database
- **API Integration**: OpenAI API, database operations, REST endpoints

## Development Guidelines

### Google Gemini Integration
- Store API key in `.env` file: `GOOGLE_API_KEY=your-key`
- Use `gemini-2.0-flash-lite` for fast, free learning (generous free tier)
- System instructions define chatbot personality and capabilities
- Function calling for structured actions (appointments, todos)
- Example:
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    system_instruction="You are a helpful medical clinic assistant.",
    tools=[schedule_appointment_tool, create_todo_tool]
)

chat = model.start_chat()
response = chat.send_message("I need an appointment")
```

### Todo Management
- Simple Python class in `src/todo_manager.py`
- Task structure: `{id, title, description, priority, assignee, due_date, status, created_at}`
- Priorities: `urgent`, `high`, `medium`, `low`
- Categories: `appointment`, `followup`, `callback`, `prescription`
- Example:
```python
todo_manager = TodoManager(db)
todo_manager.create_task(
    title="Follow up with John about fever",
    description="Patient reports 3-day fever, needs nurse callback",
    priority="high",
    assignee="nurse",
    category="followup",
    due_hours=4  # Due in 4 hours
)
```

### Conversation Patterns (Gemini handles these naturally)
- **System Instructions** guide behavior: friendly, helpful, ask clarifying questions
- **Function Calling** for structured actions: Gemini decides when to schedule appointment
- **Context Tracking**: Maintained in chat session history
- **Validation**: Python code validates extracted info (dates, times, etc.)
- Example system instruction:
```python
SYSTEM_INSTRUCTION = """You are a helpful assistant for a medical clinic.
You help patients with:
- Scheduling appointments (ask for date, time, reason)
- Answering common questions about the clinic
- Creating follow-up tasks for staff

Always be friendly and professional. For medical emergencies, tell them to call 911.
Ask clarifying questions if needed. Confirm appointments before finalizing."""
```

### Appointment Scheduling Flow
1. User: "I need an appointment"
2. Bot: "I'd be happy to help! What date works for you?"
3. User: "Next Tuesday at 2pm"
4. Bot: *extracts date/time* "Great! What's the reason for your visit?"
5. User: "Annual checkup"
6. Bot: *calls schedule_appointment function* "Booked! Confirmation sent."
7. Bot: *creates reminder todo* "I've also created a reminder for our staff."

### Testing with pytest
- **Unit Tests**: Test individual functions (`tests/test_todo_manager.py`)
- **Integration Tests**: Test API endpoints (`tests/test_api.py`)
- **Conversation Tests**: Test full dialog flows with mock Gemini responses
- Example test:
```python
def test_create_appointment():
    appointment = schedule_appointment(
        patient_name="John Doe",
        date="2025-10-25",
        time="14:00",
        reason="Checkup"
    )
    assert appointment.status == "scheduled"
    assert appointment.date == "2025-10-25"
```

### Error Handling
- Try/except blocks for Gemini API calls (rate limits, network errors)
- Graceful fallbacks: "Sorry, I'm having trouble. Can you try again?"
- Validate user inputs (dates must be future, times during clinic hours)
- Log errors for debugging without exposing to users

## Development Workflow

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Google API key
echo "GOOGLE_API_KEY=your-key-here" > .env

# Initialize database
python src/init_db.py
```

### Daily Development
```bash
# Activate virtual environment
source venv/bin/activate

# Run the API server
python src/main.py  # Or: uvicorn src.main:app --reload

# Run tests
pytest

# Test specific file
pytest tests/test_chatbot.py -v
```

### Project Structure
```
src/
  main.py              # FastAPI app entry point
  chatbot.py           # Main ChatBot class
  todo_manager.py      # Todo operations
  database.py          # SQLite/PostgreSQL operations
  handlers/
    appointment.py     # Appointment scheduling logic
    faq.py            # FAQ responses
  knowledge_base.py    # Clinic info, FAQs
  models.py           # Data models (Appointment, Todo, etc.)
tests/
  test_chatbot.py
  test_todo_manager.py
frontend/
  index.html          # Simple chat interface
  chat.js             # Chat widget logic
```

## Key Files to Understand
- `src/main.py`: FastAPI routes (`/chat`, `/appointments`, `/todos`)
- `src/chatbot.py`: Google Gemini integration and function calling logic
- `src/todo_manager.py`: Todo CRUD operations
- `src/handlers/appointment.py`: Appointment scheduling with validation
- `src/knowledge_base.py`: FAQ database, clinic info
- `requirements.txt`: Python dependencies (google-generativeai, fastapi, sqlalchemy, pytest)

## Learning Concepts Demonstrated
1. **LLM Integration**: Using Google Gemini API for natural conversations
2. **Function Calling**: Let AI decide when to call Python functions
3. **REST API**: FastAPI endpoints for chat, appointments, todos
4. **Database**: SQLAlchemy ORM for data persistence
5. **State Management**: Tracking conversation context in chat sessions
6. **Testing**: pytest for unit and integration tests
7. **Prompt Engineering**: Crafting system instructions for desired behavior

## Clinic Configuration (Simple)
```python
CLINIC_CONFIG = {
    "name": "Happy Health Clinic",
    "hours": "Mon-Fri 9AM-5PM, Sat 9AM-12PM",
    "phone": "(555) 123-4567",
    "appointment_duration": 30,  # minutes
    "providers": ["Dr. Smith", "Dr. Johnson", "Dr. Williams"]
}
```

## Common Implementation Patterns

### Function Calling Tool Definition
```python
schedule_appointment_tool = {
    "type": "function",
    "function": {
        "name": "schedule_appointment",
        "description": "Schedule a patient appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD format"},
                "time": {"type": "string", "description": "HH:MM format"},
                "reason": {"type": "string"}
            },
            "required": ["patient_name", "date", "time", "reason"]
        }
    }
}
```

### Database Model Example
```python
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    reason = Column(String)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Extending the Chatbot
1. **Add new capabilities**: Define new function tools in `src/chatbot.py`
2. **Add FAQ topics**: Update `src/knowledge_base.py` with new Q&A
3. **Add appointment types**: Extend validation in `src/handlers/appointment.py`
4. **Improve responses**: Refine system prompt for better personality
5. **Add integrations**: Create new handlers in `src/handlers/`
