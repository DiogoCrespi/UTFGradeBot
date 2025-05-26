FROM python:3.11-slim

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libx11-xcb1 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libpango1.0-0 \
    libcups2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Instala o Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Cria e configura o diretório da aplicação
WORKDIR /app

# Copia os arquivos de requisitos e código
COPY requirements.txt .
COPY run_scraper_med_CC.py .
COPY run_filtro_horarios.py .
COPY config/ ./config/
COPY db/ ./db/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Cria diretório para o ChromeDriver
RUN mkdir -p /app/chromedriver

# Instala o ChromeDriver versão 136.0.7103.113
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /app/chromedriver/ \
    && chmod +x /app/chromedriver/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64

# Configura variáveis de ambiente para o Chrome
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/app/chromedriver/chromedriver

# Define o comando padrão
CMD ["python", "run_scraper_med_CC.py"]
