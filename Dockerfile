FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# استخدام متغير PORT من Render
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
