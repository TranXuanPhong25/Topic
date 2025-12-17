# Medical Diagnostic AI System

Multi-agent AI system for medical diagnosis, consultation, and appointment scheduling with RAG-enhanced knowledge retrieval.

## Prerequisites

- **Python**: 3.11.13
- **Node.js**: 16.x or higher
- **pnpm**: 8.x or higher (or npm)
- **Docker**: For MongoDB database
- **API Keys**:
  - Google Generative AI API key (for Gemini)
  - Pinecone API key (for vector database)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd Topic
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd Server
python -m venv .venv
```

#### Activate Virtual Environment

**Linux/MacOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.\.venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create `.env` file in the **root directory** (`Topic/.env`):

```env
# Google Generative AI
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=your_index_name

# MongoDB (optional, if using custom configuration)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=medical_db
```

#### Start MongoDB with Docker

```bash
cd Server
docker-compose up -d
```

This will start MongoDB on `localhost:27017`.

#### Ingest RAG Documents (First Time Only)

Before running the system for the first time, you need to ingest medical documents into the vector database:

```bash
cd Server/src/agents/document_retriever/rag
source ../../../.venv/bin/activate  # if not already activated
python index_books.py
```

This will:
- Load medical documents from `Server/src/agents/document_retriever/rag/Data/`
- Chunk and embed the documents
- Index them in Pinecone vector database

**Note:** You only need to run this once, or whenever you add new documents to the `Data/` folder.

### 3. Frontend Setup

```bash
cd Frontend
pnpm install
# or: npm install
```

## Running the System

### Development Mode

#### 1. Start Backend Server

```bash
cd Server
# Activate virtual environment first
source .venv/bin/activate  # Linux/MacOS
# or: .\.venv\Scripts\activate  # Windows

# Run FastAPI server
uvicorn src.main:app --reload
```

Backend will run on `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

#### 2. Start Frontend Development Server

Open a new terminal:

```bash
cd Frontend
pnpm dev
# or: npm run dev
```

Frontend will run on `http://localhost:5173`

### Production Mode

#### Backend

```bash
cd Server
source .venv/bin/activate

# Run without auto-reload
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd Frontend
pnpm build
pnpm preview
# or: npm run build && npm run preview
```

## System Testing

### Run Evaluation Tests

```bash
cd Server
source .venv/bin/activate

python -m src.evaluation.runner \
  --dataset src/evaluation/large_test_dataset.json \
  --output full_evaluation_report.md \
  --delay 3
```

### Run Unit Tests

```bash
cd Server
pytest
```

## Project Structure

```
Topic/
├── Frontend/           # React + Vite frontend
│   ├── src/
│   │   ├── components/ # UI components (Chat, Booking, Dialogs)
│   │   └── App.jsx     # Main application
│   └── package.json
│
├── Server/            # FastAPI backend
│   ├── src/
│   │   ├── agents/    # Multi-agent system (11 agents)
│   │   ├── models/    # Data models
│   │   ├── routes/    # API endpoints
│   │   ├── handlers/  # Business logic
│   │   └── main.py    # FastAPI application
│   ├── pyproject.toml
│   └── docker-compose.yml
│
└── .env              # Environment variables (create this)
```

## Key Features

- **Multi-Agent Diagnosis**: 11 specialized agents for medical consultation
- **RAG Pipeline**: Document retrieval with reranking
- **Appointment Scheduling**: Smart provider matching by specialty
- **Image Analysis**: Medical image interpretation
- **Interactive Chat**: Real-time consultation interface

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Use different port
uvicorn src.main:app --port 8001
```

**MongoDB connection failed:**
```bash
# Check Docker container
docker ps
# Restart MongoDB
docker-compose restart
```

**Missing dependencies:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Module not found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

**Port 5173 in use:**
```bash
# Vite will automatically use next available port
# Or specify custom port in vite.config.js
```

### API Key Issues

- Verify `.env` file is in **root directory** (`Topic/.env`)
- Check API keys are valid and have proper permissions
- Restart backend server after updating `.env`

## Documentation

- **API Documentation**: `http://localhost:8000/docs` (when server running)

