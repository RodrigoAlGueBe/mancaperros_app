# Multi-stage build para optimizar tamaño de imagen
# ============================================

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /build

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python en directorio virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime
FROM python:3.11-slim

# Metadatos
LABEL maintainer="mancaperros_app"
LABEL description="FastAPI application for mancaperros_app"

# Instalar dependencias de runtime necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar virtual environment del builder
COPY --from=builder /opt/venv /opt/venv

# Establecer variables de entorno
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ASPNETCORE_FORWARDEDHEADERS_ENABLED=true \
    FORWARDED_ALLOW_IPS="*"

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)" || exit 1

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
