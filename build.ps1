#!/usr/bin/env pwsh

# Script para construir y ejecutar la imagen Docker de mancaperros_app (Windows PowerShell)
# ==========================================================================================

param(
    [string]$Tag = "latest",
    [string]$Registry = ""
)

# Variables
$ImageName = "mancaperros_app"
$FullImageName = "${ImageName}:${Tag}"

# Funciones
function Write-InfoMsg {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Main
Write-InfoMsg "Iniciando construcción de imagen Docker..."
Write-InfoMsg "Imagen: $FullImageName"

# Verificar que Dockerfile existe
if (-not (Test-Path "Dockerfile")) {
    Write-ErrorMsg "Dockerfile no encontrado en el directorio actual"
    exit 1
}

# Construir imagen
Write-InfoMsg "Construyendo imagen..."
docker build -t $FullImageName .

if ($LASTEXITCODE -eq 0) {
    Write-InfoMsg "Imagen construida exitosamente"

    # Si se proporciona registry, hacer tag y push
    if ($Registry -ne "") {
        $FullRegistryName = "${Registry}/${ImageName}:${Tag}"
        Write-InfoMsg "Tagueando imagen para registry: $FullRegistryName"
        docker tag $FullImageName $FullRegistryName

        Write-InfoMsg "Pusheando imagen a registry..."
        docker push $FullRegistryName
        Write-InfoMsg "Push completado"
    }

    # Mostrar información de la imagen
    Write-InfoMsg "Información de la imagen:"
    docker images $FullImageName

    Write-InfoMsg "Para ejecutar el contenedor:"
    Write-Host "  docker run -d -p 8000:8000 $FullImageName" -ForegroundColor Cyan

} else {
    Write-ErrorMsg "Error en la construcción"
    exit 1
}
