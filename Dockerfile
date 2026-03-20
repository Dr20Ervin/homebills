FROM python:3.10-slim

# Create a non-root user
RUN adduser --disabled-password --gecos '' myappuser

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# (Optional) If /config needs to be written to by your app, set ownership
RUN mkdir -p /config && chown -R myappuser:myappuser /config

# Install Python dependencies first (takes advantage of Docker layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files and assign ownership
COPY --chown=myappuser:myappuser . .

# Switch to the non-root user
USER myappuser

EXPOSE 5020

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5020", "run:app"]