FROM python:3.11-slim

WORKDIR /app

# Playwright dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium + OS deps Playwright needs
RUN python -m playwright install --with-deps chromium

COPY app.py .

# Data mount points
RUN mkdir -p /data/output /data/state

ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]