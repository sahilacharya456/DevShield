FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN sed -i 's/Components: main/Components: main contrib non-free non-free-firmware/' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    dnsutils \
    gobuster \
    git \
    nikto \
    nmap \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system devshield \
    && adduser --system --ingroup devshield --home /home/devshield devshield \
    && mkdir -p /home/devshield/DevShield_Docs /app/exports /app/data \
    && chown -R devshield:devshield /app /home/devshield

USER devshield

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
