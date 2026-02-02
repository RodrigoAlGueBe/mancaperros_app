# Docker Quick Start - mancaperros_app

## Requisitos Previos

- Docker instalado y en ejecución
- Docker Desktop (en Windows/Mac)
- Archivo `requirements.txt` actualizado

## Construcción Rápida

### En Linux/Mac
```bash
# Con tag por defecto (latest)
./build.sh

# Con tag personalizado
./build.sh v1.0.0

# Con push a registry
./build.sh v1.0.0 ghcr.io/myorg
```

### En Windows (PowerShell)
```powershell
# Con tag por defecto (latest)
.\build.ps1

# Con tag personalizado
.\build.ps1 -Tag v1.0.0

# Con push a registry
.\build.ps1 -Tag v1.0.0 -Registry ghcr.io/myorg
```

### Manual (Cualquier plataforma)
```bash
docker build -t mancaperros_app:latest .
```

## Ejecución del Contenedor

### Básico
```bash
docker run -d -p 8000:8000 mancaperros_app:latest
```

### Con variables de entorno
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=mysql://user:password@host:3306/dbname \
  -e ENVIRONMENT=production \
  mancaperros_app:latest
```

### Con archivo .env
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  mancaperros_app:latest
```

### Con volumen para persistencia
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  mancaperros_app:latest
```

### Con todos los flags (producción)
```bash
docker run -d \
  --name mancaperros \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v mancaperros_data:/app/data \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  mancaperros_app:latest
```

## Verificación

### Ver logs
```bash
docker logs mancaperros
docker logs -f mancaperros  # seguimiento en tiempo real
```

### Ver estado de health check
```bash
docker inspect --format='{{.State.Health.Status}}' mancaperros
```

### Acceder a la API
```bash
# Swagger UI
open http://localhost:8000/docs

# ReDoc
open http://localhost:8000/redoc

# Health check
curl http://localhost:8000/healthz
```

### Ejecutar comando en contenedor
```bash
docker exec mancaperros python -m pytest tests/
docker exec mancaperros python init_db.py
```

### Entrar a shell del contenedor
```bash
docker exec -it mancaperros /bin/bash
```

## Gestión de Contenedores

### Ver contenedores en ejecución
```bash
docker ps
```

### Ver todos los contenedores
```bash
docker ps -a
```

### Detener contenedor
```bash
docker stop mancaperros
```

### Iniciar contenedor detenido
```bash
docker start mancaperros
```

### Remover contenedor
```bash
docker rm mancaperros
```

### Ver logs históricos
```bash
docker logs mancaperros | head -100
```

## Gestión de Imágenes

### Ver imágenes locales
```bash
docker images
```

### Remover imagen
```bash
docker rmi mancaperros_app:latest
```

### Ver tamaño de imagen
```bash
docker images --format "table {{.Repository}}\t{{.Size}}"
```

### Inspeccionar imagen
```bash
docker inspect mancaperros_app:latest
```

## Troubleshooting

### El contenedor se detiene inmediatamente
```bash
# Ver logs del error
docker logs mancaperros

# Ejecutar sin detach para ver el output
docker run -it mancaperros_app:latest
```

### Puerto 8000 ya en uso
```bash
# Usar otro puerto
docker run -d -p 8001:8000 mancaperros_app:latest

# O encontrar qué usa el puerto
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows
```

### Health check falla
```bash
# Probar endpoint de health manualmente
curl -v http://localhost:8000/docs

# Aumentar timeout en Dockerfile si es necesario
```

### Problemas de permisos
```bash
# El contenedor se ejecuta como usuario 'appuser' (no root)
# Si necesitas permisos especiales, usa --user flag

docker run -d -p 8000:8000 --user root mancaperros_app:latest
```

## Desarrollo Local

### Construir sin cache (fuerza rebuild)
```bash
docker build --no-cache -t mancaperros_app:latest .
```

### Construir con BuildKit (más rápido)
```bash
DOCKER_BUILDKIT=1 docker build -t mancaperros_app:latest .
```

### Multistage build - ver layers
```bash
docker build --progress=plain -t mancaperros_app:latest .
```

## Optimización

### Ver tamaño de layers
```bash
docker history mancaperros_app:latest
```

### Analizar imagen
```bash
# Con dive (requiere instalación)
dive mancaperros_app:latest
```

### Scan de vulnerabilidades
```bash
docker scan mancaperros_app:latest
```

## Limpieza

### Remover contenedores parados
```bash
docker container prune
```

### Remover imágenes sin usar
```bash
docker image prune
```

### Remover volúmenes sin usar
```bash
docker volume prune
```

### Limpieza completa (cuidado!)
```bash
docker system prune -a
```

## Notas

- El puerto por defecto es **8000** (cambió de 3100)
- El comando por defecto es `uvicorn` (no gunicorn)
- No se ejecuta `init_db.py` automáticamente
- El contenedor se ejecuta como usuario `appuser` (no root)
- Health check verifica endpoint `/docs` cada 30 segundos
