# FanStudio AI

## Run

```bash
# MongoDB
cd backend && docker compose up -d

# Backend (from backend/)
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (from frontend/)
npm install
cp .env.example .env
npm run dev
```

API: http://127.0.0.1:8000/docs — UI: http://localhost:3000
