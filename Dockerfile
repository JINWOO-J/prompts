FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# DB 파일 저장 경로 (볼륨 마운트 가능)
RUN mkdir -p /app/data
ENV PROMPTS_DB_PATH=/app/data/prompts.db

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
