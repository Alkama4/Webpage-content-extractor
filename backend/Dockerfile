FROM python:3.11-slim

# RUN apt-get update && apt-get install -y \
#     wget \
#     unzip \
#     curl \
#     gnupg \
#     libnss3 \
#     libgconf-2-4 \
#     && rm -rf /var/lib/apt/lists/*

# Install Chrome
# RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
#        > /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable \
#     && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
# RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f1) \
#     && LATEST_DRIVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
#     && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$LATEST_DRIVER/chromedriver_linux64.zip" \
#     && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
#     && rm /tmp/chromedriver.zip \
#     && chmod +x /usr/local/bin/chromedriver

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
