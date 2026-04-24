FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["python", "-m", "streamlit", "run", "dashboard.py", "--server.port", "7860", "--server.address", "0.0.0.0"]