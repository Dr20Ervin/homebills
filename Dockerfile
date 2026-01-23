FROM python:3.10-slim

WORKDIR /app

# 1. Update the Linux OS to fix 'deb' vulnerabilities
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /config

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5020
CMD ["python", "run.py"]