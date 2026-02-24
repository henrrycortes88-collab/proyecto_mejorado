# Script de Inicio Rápido - Sistema de Gestión Corporativo (Windows PowerShell)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Sistema de Gestión Corporativo" -ForegroundColor Cyan
Write-Host "Instalador Docker (Windows)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Docker está instalado
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    Write-Host "Por favor instala Docker Desktop para Windows."
    exit 1
}

# Verificar si Docker Compose está instalado (incluido en Docker Desktop)
if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ docker-compose no está instalado" -ForegroundColor Red
    Write-Host "Por favor instala Docker Desktop para Windows."
    exit 1
}

Write-Host "✓ Docker está instalado" -ForegroundColor Green
Write-Host "✓ Docker Compose está instalado" -ForegroundColor Green
Write-Host ""

Write-Host "Construyendo imagen Docker..." -ForegroundColor Blue
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Imagen construida exitosamente" -ForegroundColor Green
Write-Host ""

Write-Host "Iniciando contenedores..." -ForegroundColor Blue
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar los contenedores" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Contenedores iniciados exitosamente" -ForegroundColor Green
Write-Host ""

# Esperar a que PostgreSQL esté listo
Write-Host "Esperando a que la base de datos esté lista..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Inicializar la base de datos
Write-Host "Inicializando base de datos..." -ForegroundColor Blue
docker exec -it sistema-login-corporativo python init_db.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al inicializar la base de datos" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "¡Instalación completada!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL de acceso: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "👤 Credenciales de acceso:" -ForegroundColor Cyan
Write-Host ""
Write-Host "ADMINISTRADOR:" -ForegroundColor Yellow
Write-Host "  Usuario: admin"
Write-Host "  Contraseña: admin123"
Write-Host ""
Write-Host "EMPLEADOS:" -ForegroundColor Yellow
Write-Host "  Usuario: empleado1 | Contraseña: emp123"
Write-Host "  Usuario: empleado2 | Contraseña: emp123"
Write-Host ""
Write-Host "CLIENTES:" -ForegroundColor Yellow
Write-Host "  Usuario: cliente1 | Contraseña: cli123"
Write-Host "  Usuario: cliente2 | Contraseña: cli123"
Write-Host "  Usuario: cliente3 | Contraseña: cli123"
Write-Host ""
Write-Host "📊 Comandos útiles:" -ForegroundColor Blue
Write-Host "  Ver logs:      docker-compose logs -f"
Write-Host "  Detener:       docker-compose down"
Write-Host "  Reiniciar:     docker-compose restart"
Write-Host "  Estado:        docker-compose ps"
Write-Host ""
