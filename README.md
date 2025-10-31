# Backend
**Make sure set the google api key in .env at root**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app
```
# Frontend
```bash
cd react-frontend-app
npm i && npm run dev
```