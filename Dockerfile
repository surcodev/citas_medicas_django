FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ---- Dependencias del sistema (mysqlclient, cairo, wkhtmltopdf) ----
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    pkg-config \
    # Compatibles con mysqlclient en Debian Bookworm
    libmariadb-dev \
    libmariadb-dev-compat \
    # Dependencias para wkhtmltopdf
    libcairo2-dev \
    fontconfig \
    xfonts-75dpi \
    xfonts-base \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libjpeg62-turbo \
    libssl3 \
    wget && \
    \
    # Descargar el archivo wkhtmltopdf válido
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb && \
    # Instalar wkhtmltopdf
    apt-get install -y --no-install-recommends ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb || true && \
    dpkg -i --force-depends wkhtmltox_0.12.6.1-3.bookworm_amd64.deb && \
    rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# ---- Instalar requirements ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copiar proyecto ----
COPY . .

EXPOSE 8000

# ---- Comando de ejecución ----
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
