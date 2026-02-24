#!/bin/bash

# Script de Inicio Rápido - Sistema de Gestión Corporativo
# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Sistema de Gestión Corporativo${NC}"
echo -e "${BLUE}Instalador Docker${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Por favor instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Por favor instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker está instalado${NC}"
echo -e "${GREEN}✓ Docker Compose está instalado${NC}"
echo ""

echo -e "${BLUE}Construyendo imagen Docker...${NC}"
docker-compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al construir la imagen${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Imagen construida exitosamente${NC}"
echo ""

echo -e "${BLUE}Iniciando contenedores...${NC}"
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al iniciar los contenedores${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Contenedores iniciados exitosamente${NC}"
echo ""

# Esperar a que PostgreSQL esté listo
echo -e "${BLUE}Esperando a que la base de datos esté lista...${NC}"
sleep 5

# Inicializar la base de datos
echo -e "${BLUE}Inicializando base de datos...${NC}"
docker exec -it sistema-login-corporativo python init_db.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al inicializar la base de datos${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}¡Instalación completada!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}🌐 URL de acceso:${NC} http://localhost:8080"
echo ""
echo -e "${BLUE}👤 Credenciales de acceso:${NC}"
echo ""
echo -e "${YELLOW}ADMINISTRADOR:${NC}"
echo "  Usuario: admin"
echo "  Contraseña: admin123"
echo ""
echo -e "${YELLOW}EMPLEADOS:${NC}"
echo "  Usuario: empleado1 | Contraseña: emp123"
echo "  Usuario: empleado2 | Contraseña: emp123"
echo ""
echo -e "${YELLOW}CLIENTES:${NC}"
echo "  Usuario: cliente1 | Contraseña: cli123"
echo "  Usuario: cliente2 | Contraseña: cli123"
echo "  Usuario: cliente3 | Contraseña: cli123"
echo ""
echo -e "${BLUE}📊 Comandos útiles:${NC}"
echo "  Ver logs:      docker-compose logs -f"
echo "  Detener:       docker-compose down"
echo "  Reiniciar:     docker-compose restart"
echo "  Estado:        docker-compose ps"
echo ""
