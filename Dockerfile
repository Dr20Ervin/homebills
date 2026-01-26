FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# 1. Update OS and install dependencies for PostgreSQL adapters
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Create the config directory
RUN mkdir -p /config

# 3. Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5020

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5020", "run:app"]