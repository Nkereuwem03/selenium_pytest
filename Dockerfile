# Use stable Python version
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    gnupg \
    fonts-liberation \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libgl1-mesa-glx \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libxss1 \
    libxtst6 \
    libxrandr2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    ca-certificates \
    xvfb \
    firefox-esr \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/linux_signing_key.pub https://dl.google.com/linux/linux_signing_key.pub \
    && mv /tmp/linux_signing_key.pub /usr/share/keyrings/googlechrome-linux-keyring.asc \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.asc] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && google-chrome --version \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O allure-commandline.tgz https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz \
    && tar -zxf allure-commandline.tgz \
    && mv allure-2.24.0 /opt/allure \
    && ln -s /opt/allure/bin/allure /usr/local/bin/allure \
    && rm allure-commandline.tgz \
    && allure --version

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app && chown -R appuser:appuser /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN mkdir -p reports allure-results allure-report logs \
    && chown -R appuser:appuser /app

VOLUME ["/app/reports", "/app/allure-results", "/app/allure-report", "/app/logs"]

ENV DISPLAY=:99 \
    CHROME_NO_SANDBOX=1 \
    CHROME_DISABLE_GPU=1 \
    CHROME_HEADLESS=1 \
    PYTHONPATH=/app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["sh", "-c", "xvfb-run --auto-servernum --server-args='-screen 0 1920x1080x24' pytest -v --tb=short --html=reports/report.html --self-contained-html --maxfail=5 --alluredir=allure-results tests && allure generate allure-results -o allure-report --clean"]