# Dockerfile Guide - mancaperros_app

## Descripción General

Este Dockerfile implementa las mejores prácticas de seguridad y optimización para una aplicación FastAPI usando una estrategia de multi-stage build.

## Características Principales

### 1. Multi-Stage Build
- **Stage 1 (Builder)**: Compila todas las dependencias de Python
- **Stage 2 (Runtime)**: Contiene solo lo necesario para ejecutar la aplicación
- **Beneficio**: Reduce el tamaño final de la imagen eliminando herramientas de compilación

### 2. Seguridad

#### Usuario No-Root
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```
- La aplicación se ejecuta con usuario `appuser` (no root)
- Reduce el riesgo de compromiso de seguridad
- Cumple con mejores prácticas de contenedores

#### Permisos de Archivos
```dockerfile
COPY --chown=appuser:appuser . .
```
- Los archivos son propiedad de `appuser`
- Evita problemas de permisos

### 3. Optimización de Tamaño

- **Imagen base**: `python:3.12-slim` (más pequeña que `python:3.12`)
- **Virtual environment**: Aísla dependencias
- **No-cache instalaciones**: `--no-cache-dir` en pip
- **Limpieza de apt**: Elimina directorios de caché (`/var/lib/apt/lists`)

### 4. Variables de Entorno

```dockerfile
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ASPNETCORE_FORWARDEDHEADERS_ENABLED=true \
    FORWARDED_ALLOW_IPS="*"
```

- `PYTHONUNBUFFERED=1`: Output sin buffer para logs en tiempo real
- `PYTHONDONTWRITEBYTECODE=1`: Evita archivos `.pyc`
- Variables de proxy headers preservadas del Dockerfile anterior

### 5. Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)" || exit 1
```

- Verifica que la aplicación esté funcionando cada 30 segundos
- Necesita `requests` en requirements.txt (ya incluido)
- Tiempo inicial de 5 segundos para que la app inicie

## Construcción y Uso

### Construir la imagen
```bash
docker build -t mancaperros_app:latest .
```

### Ejecutar el contenedor
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=mysql://user:password@host:3306/dbname \
  mancaperros_app:latest
```

### Ver logs
```bash
docker logs <container_id>
```

### Verificar health status
```bash
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

## Diferencias con el Dockerfile Anterior

| Aspecto | Anterior | Nuevo |
|---------|----------|-------|
| Build | Single-stage | Multi-stage |
| Imagen base | python:3.12.4 | python:3.12-slim |
| Usuario | root | appuser (no-root) |
| Puerto | 3100 | 8000 |
| Worker | gunicorn + UvicornWorker | uvicorn directo |
| Init DB | En CMD | Removido (ejecutar separadamente) |
| Health Check | No | Sí |

## Cambios Importantes

### 1. Puerto
El nuevo Dockerfile expone puerto **8000** (como se requería), no 3100.

### 2. Comando de inicio
Cambió de:
```bash
gunicorn main:app --bind 0.0.0.0:3100 --worker-class uvicorn.workers.UvicornWorker
```

A:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Si necesitas múltiples workers en producción, puedes crear un `docker-compose.yml` con un load balancer.

### 3. Inicialización de base de datos
El Dockerfile anterior ejecutaba `init_db.py` automáticamente. En el nuevo:
- Ejecutar manualmente antes de iniciar el contenedor
- O agregar un script de entrada personalizado
- Recomendado: Usar migrations (Alembic) en el deployment

## Tamaño Estimado

- **Anterior**: ~1.5 GB (incluye herramientas de compilación)
- **Nuevo**: ~600-700 MB (solo runtime)

## Notas de Seguridad

1. **Secretos**: No hardcodear contraseñas en el Dockerfile
2. **Variables de entorno**: Usar `docker run -e` o archivos `.env`
3. **Escaneo de vulnerabilidades**: Ejecutar `docker scan mancaperros_app:latest`
4. **Imagen base actualizada**: Monitorear actualizaciones de `python:3.12-slim`

## Troubleshooting

### Error: "Permission denied"
Verificar que `appuser` tiene permisos correctos:
```dockerfile
COPY --chown=appuser:appuser . .
```

### Error: "Module not found"
Verificar que `PATH` incluye `/opt/venv/bin`:
```dockerfile
ENV PATH="/opt/venv/bin:$PATH"
```

### Health check falla
Verificar que `/docs` es accesible en la aplicación FastAPI:
```bash
curl http://localhost:8000/docs
```

## Optimizaciones Futuras

1. **Usar distroless image**: Incluso más pequeña que slim
2. **Scan de vulnerabilidades en CI/CD**: Agregar trivy/snyk
3. **Signing de imágenes**: Usar Cosign para firma de imágenes
4. **Cache de layers**: Optimizar orden de COPY/RUN para mejor caché
