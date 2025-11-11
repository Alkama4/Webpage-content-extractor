# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies required by Chromium
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libcairo2 \
    libpango-1.0-0 \
    libxfixes3 \
    libxcursor1 \
    libgtk-3-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libcairo-gobject2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Install Playwright browsers
RUN playwright install

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
