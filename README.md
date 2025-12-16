# Backend
**Make sure set the google api key and pinecone key in .env at root**
```bash
cd Server
docker-compose up -d
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements2.txt
uvicorn src.main:app

run test:
python -m src.evaluation.runner --dataset src/evaluation/large_test_dataset.json --output full_evaluation_report.md --delay 3
```
# Frontend
```bash
cd Frontend
npm i && npm run dev
```
