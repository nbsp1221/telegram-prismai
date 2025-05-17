FROM python:3.10-slim

WORKDIR /app

# Install CA certificates
RUN apt-get update && apt-get install -y ca-certificates

# Set certificate paths for Python requests and SSL modules
# This ensures proper SSL verification without disabling security
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for persistent storage
RUN mkdir -p data

# Run the bot
CMD ["python", "main.py"] 