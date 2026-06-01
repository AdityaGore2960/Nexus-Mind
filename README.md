# Nexus-Mind

**AI-powered mineral prospectivity platform.** Combines geospatial ML, ensemble inference, and an interactive map interface to identify high-probability mineral exploration zones.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, Recharts, Leaflet |
| AI Service | FastAPI, Python, OpenAI / Gemini APIs |
| Infra | Docker, Docker Compose |

---

## Project Structure

```
Nexus-Mind/
├── frontend/       # Next.js web app
├── ai/             # FastAPI AI service
└── docker-compose.yml
```

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker (optional, for full-stack)

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at **http://localhost:3000**

---

### AI Service

```bash
cd ai
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Runs at **http://localhost:8000**  
API docs at **http://localhost:8000/docs**

---

### Full Stack (Docker)

```bash
docker-compose up --build
```

---

## Environment Variables

Copy the example files and fill in your keys:

```bash
cp ai/.env.example ai/.env
cp frontend/.env.local.example frontend/.env.local   # if applicable
```

| Variable | Where | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `ai/.env` | OpenAI API key |
| `GOOGLE_API_KEY` | `ai/.env` | Gemini API key (optional) |

---

## License

MIT
