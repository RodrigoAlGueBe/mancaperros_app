#!/bin/bash

# Script para construir y ejecutar la imagen Docker de mancaperros_app
# ==========================================================================

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
IMAGE_NAME="mancaperros_app"
IMAGE_TAG="${1:-latest}"
REGISTRY="${2:-}"

# Funciones
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main
print_info "Iniciando construcción de imagen Docker..."
print_info "Imagen: ${IMAGE_NAME}:${IMAGE_TAG}"

# Verificar que Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile no encontrado en el directorio actual"
    exit 1
fi

# Construir imagen
print_info "Construyendo imagen..."
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

if [ $? -eq 0 ]; then
    print_info "Imagen construida exitosamente"

    # Si se proporciona registry, hacer tag y push
    if [ -n "$REGISTRY" ]; then
        print_info "Tagueando imagen para registry: ${REGISTRY}"
        docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

        print_info "Pusheando imagen a registry..."
        docker push "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        print_info "Push completado"
    fi

    # Mostrar información de la imagen
    print_info "Información de la imagen:"
    docker images "${IMAGE_NAME}:${IMAGE_TAG}"

    print_info "Para ejecutar el contenedor:"
    echo "  docker run -d -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"

else
    print_error "Error en la construcción"
    exit 1
fi
