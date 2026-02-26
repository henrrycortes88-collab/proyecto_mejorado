## Características de Seguridad (Hardening)

Este proyecto ha sido endurecido siguiendo las mejores prácticas de seguridad:
- **Control de Acceso (BAC)**: Decoradores `@role_required` para Admin, Empleado y Cliente.
- **Protección Criptográfica (CF)**: Cifrado Fernet para datos sensibles y derivación de claves optimizada.
- **Protección contra Diseño Inseguro (ID)**: 
    - CSRF Protection en todos los formularios.
    - Rate Limiting en el inicio de sesión para prevenir fuerza bruta.
    - Validación estricta de entradas (email-validator).
- **Cabeceras de Seguridad**: CSP, HSTS, X-Content-Type-Options, etc.

## Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 1.29 o superior)

## Instalación y Ejecución Rápida

### 1. Iniciar el sistema (Windows)
```powershell
./start.ps1
```

### 2. Iniciar el sistema (Linux/Mac)
```bash
chmod +x start.sh
./start.sh
```

### 3. Ejecución manual con Docker Compose
```bash
# Construir e iniciar contenedores
docker-compose up -d --build

# Inicializar la base de datos
docker exec -it sistema-login-corporativo python init_db.py
```

## Verificación de Seguridad
Puedes ejecutar el script de verificación para confirmar que las medidas de seguridad están activas:
```bash
docker exec -it sistema-login-corporativo python verify_hardening.py
```

## Credenciales de Acceso
... (mismo contenido que antes) ...


### Reiniciar base de datos desde cero
```bash
docker-compose down -v
docker-compose up -d
docker exec -it sistema-login-corporativo python init_db.py
```


