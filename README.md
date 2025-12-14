# Backend
**Make sure set the google api key in .env at root**
```bash
cd Server
docker-compose up -d
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install pyproject.toml
uvicorn src.main:app
```
# Frontend
```bash
cd Frontend
npm i && npm run dev
```
