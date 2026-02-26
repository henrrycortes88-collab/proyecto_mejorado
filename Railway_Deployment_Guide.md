# Guía de Despliegue en Railway.com

Esta guía te ayudará a subir tu proyecto a Railway y configurar la base de datos PostgreSQL.

## Pasos Previos
1. Asegúrate de que tu proyecto esté en un repositorio de GitHub.
2. Crea una cuenta en [Railway.com](https://railway.com/).

## Paso 1: Crear el Proyecto en Railway
1. En el dashboard de Railway, haz clic en **+ New Project**.
2. Selecciona **Deploy from GitHub repo**.
3. Elige tu repositorio `proyecto_mejorado`.
4. Railway detectará automáticamente el `Dockerfile` y comenzará el build.

## Paso 2: Agregar la Base de Datos
1. Una vez creado el proyecto, haz clic en **+ Add Service**.
2. Selecciona **Database** -> **Add PostgreSQL**.
3. Espera a que se cree la base de datos.

## Paso 3: Configurar Variables de Entorno
Ve a la pestaña **Variables** de tu servicio de la aplicación (no el de Postgres) y añade las siguientes:

| Variable | Valor | Nota |
|----------|-------|------|
| `PORT` | `8080` | Obligatorio para coincidir con el Dockerfile |
| `SECRET_KEY` | (Una cadena larga y aleatoria) | Ejemplo: `p3rso_p4ss_2024_secure` |
| `SQLALCHEMY_DATABASE_URI` | `${{Postgres.DATABASE_URL}}` | Esto vincula automáticamente la DB de Railway |

## Paso 4: Inicializar la Base de Datos
Como es la primera vez, necesitas crear las tablas y los usuarios de ejemplo:
1. Ve a la pestaña **Deployments** de tu aplicación.
2. Busca el botón **View Logs** o ve a la pestaña **Logs**.
3. En la parte superior verás una pestaña llamada **Terminal** o **Command**.
4. Ejecuta el siguiente comando:
   ```bash
   python init_db.py
   ```
5. Deberías ver el mensaje: `✓ Base de datos inicializada exitosamente`.

## Paso 5: ¡Listo!
Railway generará una URL pública (puedes verla en la pestaña **Settings** -> **Public Networking**). Ábrela y usa las credenciales de administrador:
- **Usuario**: `admin`
- **Password**: `admin123`
