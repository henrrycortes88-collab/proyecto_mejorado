# Sistema de Gestión Corporativo - Versión Completa

Sistema multi-usuario completo con Flask + PostgreSQL + Docker que incluye funcionalidades completas para Administradores, Empleados y Clientes.


### Panel de Cliente
 **Mis Proyectos**
  - Ver todos los proyectos
  - Seguimiento de progreso visual
  - Estados y fechas de entrega
  
 **Sistema de Tickets de Soporte**
  - Crear nuevos tickets
  - Ver historial de tickets
  - Prioridades (Urgente, Alta, Normal, Baja)
  - Estados (Abierto, En Proceso, Resuelto)
  
**Gestión de Documentos**
  - Ver facturas
  - Contratos
  - Reportes
  - Manuales

## Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 1.29 o superior)

Para verificar las versiones:
```bash
docker --version
docker-compose --version
```

## Instalación y Uso


```bash
# Si tienes los archivos
cd proyecto_mejorado
```

### 2. Iniciar el sistema con Docker Compose

```bash
docker-compose up -d --build
```

### 3. Inicializar la base de datos

```bash
docker exec -it sistema-login-corporativo python init_db.py
```

### 4. Acceder a la aplicación

Abre tu navegador en: `http://localhost:8080`

## Credenciales de Acceso


### Clientes
- **Usuario:** `cliente1` | **Contraseña:** `cli123`
- **Usuario:** `cliente2` | **Contraseña:** `cli123`
- **Usuario:** `cliente3` | **Contraseña:** `cli123`
- **Permisos:** Ver proyectos, crear tickets, acceder a documentos


### Ver contenedores en ejecución
```bash
docker ps
```

### Acceder al contenedor
```bash
docker exec -it sistema-login-corporativo sh
```

### Reiniciar el sistema
```bash
docker-compose restart
```

### Detener el sistema
```bash
docker-compose down
```

### Eliminar todo (incluyendo datos)
```bash
docker-compose down -v
```

## 📁 Estructura del Proyecto

```
proyecto_mejorado/
├── app.py                          # Aplicación principal Flask
├── models.py                       # Modelos de base de datos
├── init_db.py                      # Script de inicialización
├── requirements.txt                # Dependencias Python
├── docker-compose.yml              # Configuración Docker Compose
├── Dockerfile                      # Imagen Docker
├── templates/
│   ├── login.html                  # Página de login
│   ├── dashboard_admin.html        # Panel administrador
│   ├── admin_reports.html          # Reportes administrador
│   ├── dashboard_employee.html     # Panel empleado
│   └── dashboard_client.html       # Panel cliente
└── README.md                       # Esta documentación
```


### Reiniciar base de datos desde cero
```bash
docker-compose down -v
docker-compose up -d
docker exec -it sistema-login-corporativo python init_db.py
```


