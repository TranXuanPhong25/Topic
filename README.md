# Medical Clinic Chatbot - Educational Project

An AI-powered chatbot for medical clinics that demonstrates conversational AI, appointment scheduling, and task management integration using OpenAI's GPT-4.

> **Note**: This is an educational project to learn chatbot development patterns. Not for production medical use.

## 🎯 Learning Objectives

- Build conversational AI using OpenAI's GPT-4o-mini
- Implement function calling for structured actions
- Create REST APIs with FastAPI
- Manage state and context in conversations
- Integrate AI with databases and task systems
- Test AI applications with pytest

## ✨ Features

- **Natural Conversations**: Chat naturally with patients using GPT-4
- **Appointment Scheduling**: Book, view, and cancel appointments
- **FAQ Handling**: Answer common clinic questions
- **Task Management**: Auto-create follow-up tasks for staff
- **Context Tracking**: Remember conversation history
- **Simple Web UI**: Chat widget for testing

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
│OpenAI  │  │   Database   │
│GPT-4   │  │   (SQLite)   │
└────────┘  └──────────────┘
    │
    ▼
┌─────────────────┐
│ Function Tools  │  schedule_appointment, create_todo, get_faq
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Topic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Initialize database
python src/init_db.py
```

### Run the Server

```bash
# Start FastAPI server
uvicorn src.main:app --reload

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Test the Chatbot

Open `frontend/index.html` in your browser or test via curl:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an appointment next Tuesday at 2pm"}'
```

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

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chatbot.py -v

# Run with coverage
pytest --cov=src tests/
```

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

### 1. OpenAI Function Calling
The chatbot uses function calling to let GPT decide when to execute actions:

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

## 🐛 Troubleshooting

**"OpenAI API key not found"**
- Ensure `.env` file exists with `OPENAI_API_KEY=sk-...`

**"Module not found" errors**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Chat responses are slow**
- Using `gpt-4o-mini` should be fast (<2s)
- Check your internet connection
- Verify OpenAI API status

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
