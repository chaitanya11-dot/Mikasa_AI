# 🧠 MIKASA AI — V1 Local Sovereign Personal AI

MIKASA is a personal AI assistant built for local operation and sovereign computing. In V1, MIKASA runs entirely on your local machine with local intelligence, conversation persistence, personalized memory, voice synthesis, speech recognition, and settings management.

---

## 🏛 Architecture

```
                      React Frontend (Vite + Tailwind CSS)
                                    │
                                    ▼
                         MIKASA Core API (FastAPI)
                                    │
             ┌──────────────────────┼──────────────────────┐
             ▼                      ▼                      ▼
    MIKASA Brain Service      Memory Service      Conversation Store
             │               (SQLite Storage)      (SQLite Storage)
             ▼
    Local Inference Runtime
        (mikasa:latest)
             │
             ▼
    Streaming SSE Response
```

---

## ⚡ Key Features

- **Local Brain:** 100% local inference powered by the local MIKASA model runtime.
- **Reliable Streaming:** Fault-tolerant Server-Sent Events (SSE) buffering that eliminates chunking errors and loading hangs.
- **Persistent Conversations:** SQLite-backed conversation and message history with auto-generated contextual titles.
- **Long-Term Memory:** Persistent user facts and preference tracking with explicit commands (`"Remember that..."`, `"What do you remember about me?"`, `"Forget that..."`).
- **Voice System:** Modular voice engine with browser speech synthesis, customizable speech rate/volume, and speech-to-text recognition.
- **Unified Identity:** Consistently identifies as **MIKASA** without exposing underlying runtime details.
- **Settings & Privacy:** Full control over response styles, memory records, themes, local data deletion, and system diagnostics.

---

## 📋 Requirements

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.10+ (tested on Python 3.12)
- **Node.js:** v18.0+ and npm
- **Local Inference Runtime:** Ollama running locally (`http://127.0.0.1:11434`) with `mikasa:latest`

---

## 🚀 Quick Start (Windows PowerShell)

### 1. Local Brain Setup
Ensure your local inference runtime is active:
```powershell
# Verify Ollama is running and has the model
ollama list
```

### 2. Backend Setup
```powershell
cd Mikasa-AI\backend

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```powershell
cd Mikasa-AI\frontend

# Install frontend dependencies
npm install

# Start Vite dev server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## ⚙️ Environment Variables

### Backend (`backend/.env`):
```env
MIKASA_VERSION=1.0.0
MIKASA_HOST=127.0.0.1
MIKASA_PORT=8000
OLLAMA_BASE_URL=http://127.0.0.1:11434
MIKASA_MODEL=mikasa:latest
MIKASA_DATA_DIR=./data
```

### Frontend (`frontend/.env`):
```env
VITE_MIKASA_CORE_URL=http://127.0.0.1:8000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | MIKASA Core health and brain status |
| `GET` | `/api/core` | Core metadata and mode |
| `POST` | `/api/chat` | SSE streaming chat endpoint with memory integration |
| `GET` | `/api/conversations` | List all saved conversations |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations/{id}` | Retrieve conversation messages |
| `PATCH` | `/api/conversations/{id}` | Rename conversation title |
| `DELETE` | `/api/conversations/{id}` | Delete conversation |
| `POST` | `/api/conversations/{id}/clear` | Clear conversation messages |
| `GET` | `/api/memory` | Retrieve all stored memories |
| `POST` | `/api/memory` | Save a new memory |
| `DELETE` | `/api/memory/{id}` | Delete a single memory |
| `DELETE` | `/api/memory` | Clear all memories |
| `GET` | `/api/voice/status` | Voice engine status |
| `POST` | `/api/voice/speak` | Synthesize speech |
| `GET` | `/api/settings` | Retrieve assistant settings |
| `POST` | `/api/settings` | Save updated settings |
| `DELETE` | `/api/settings/data` | Clear all local data |

---

## 🧪 Running Automated Tests

Run backend tests using pytest:
```powershell
cd Mikasa-AI\backend
python -m pytest tests
```

---

## 🔧 Troubleshooting

- **MIKASA Offline status in UI:** Ensure the backend is running on `127.0.0.1:8000`. Check with `curl http://127.0.0.1:8000/api/health`.
- **Local Brain Unavailable:** Ensure Ollama is running on port 11434 (`ollama serve`).
- **Microphone not working:** Ensure browser microphone permissions are allowed for `http://localhost:5173`.
