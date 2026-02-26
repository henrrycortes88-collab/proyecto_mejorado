from app import app, encrypt_data
from models import db, User, Task, Project, SupportTicket, Document
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_db():
    """Inicializa la base de datos con tablas y datos de ejemplo."""
    with app.app_context():
        print("Creando tablas si no existen...")
        db.create_all()

        # Si ya hay usuarios, no insertar datos de nuevo
        if User.query.first():
            print("✓ Base de datos ya inicializada, omitiendo inserción de datos.")
            return

        print("Inicializando base de datos con datos de ejemplo...")

        #  USUARIOS 
        admin = User(
            username="admin", 
            role="admin", 
            password_hash=generate_password_hash("admin123"), 
            email="admin@empresa.com",
            encrypted_note=encrypt_data("Nota de administrador: Revisar logs cada 24h.")
        )
        
        empleado1 = User(
            username="empleado1", 
            role="empleado", 
            password_hash=generate_password_hash("emp123"), 
            email="empleado1@empresa.com",
            encrypted_note=encrypt_data("Nota de empleado: Clave de oficina 4455.")
        )
        empleado2 = User(username="empleado2", role="empleado", password_hash=generate_password_hash("emp123"), email="empleado2@empresa.com")
        
        cliente1 = User(
            username="cliente1", 
            role="cliente", 
            password_hash=generate_password_hash("cli123"), 
            email="cliente1@correo.com",
            encrypted_note=encrypt_data("Mi nota secreta: PIN de seguridad 9988.")
        )
        cliente2 = User(username="cliente2", role="cliente", password_hash=generate_password_hash("cli123"), email="cliente2@correo.com")
        cliente3 = User(username="cliente3", role="cliente", password_hash=generate_password_hash("cli123"), email="cliente3@correo.com")

        db.session.add_all([admin, empleado1, empleado2, cliente1, cliente2, cliente3])
        db.session.commit()

        # PROYECTOS
        proyecto1 = Project(
            name="Rediseño Web Corporativo",
            description="Renovación completa del sitio web de la empresa",
            status="activo",
            progress=75,
            client_id=cliente1.id,
            deadline=datetime.utcnow() + timedelta(days=15)
        )
        
        proyecto2 = Project(
            name="App Mobile v2.0",
            description="Desarrollo de la nueva versión de la aplicación móvil",
            status="activo",
            progress=45,
            client_id=cliente1.id,
            deadline=datetime.utcnow() + timedelta(days=30)
        )

        proyecto3 = Project(
            name="Sistema de Reportes",
            description="Implementación de sistema de reportes automatizados",
            status="activo",
            progress=90,
            client_id=cliente2.id,
            deadline=datetime.utcnow() + timedelta(days=2)
        )
        
        proyecto4 = Project(
            name="Migración a Cloud",
            description="Migración de infraestructura a servicios en la nube",
            status="completado",
            progress=100,
            client_id=cliente2.id,
            deadline=datetime.utcnow() - timedelta(days=5)
        )
        
        proyecto5 = Project(
            name="Portal de Clientes",
            description="Desarrollo de portal web para clientes",
            status="activo",
            progress=30,
            client_id=cliente3.id,
            deadline=datetime.utcnow() + timedelta(days=45)
        )

        db.session.add_all([proyecto1, proyecto2, proyecto3, proyecto4, proyecto5])
        db.session.commit()

        # TAREAS
        tarea1 = Task(
            title="Revisar propuesta de diseño Q1",
            status="en_proceso",
            priority="alta",
            assigned_to=empleado1.id,
            project_id=proyecto1.id,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        
        tarea2 = Task(
            title="Actualizar documentación técnica",
            status="pendiente",
            priority="media",
            assigned_to=empleado1.id,
            project_id=proyecto1.id,
            due_date=datetime.utcnow() + timedelta(days=3)
        )
        
        db.session.add_all([tarea1, tarea2])
        db.session.commit()

        # DOCUMENTOS
        doc1 = Document(
            title="Factura Enero 2024",
            description="Factura por servicios de consultoría IT",
            file_type="factura",
            client_id=cliente1.id,
            project_id=proyecto1.id
        )
        
        doc2 = Document(
            title="Contrato Marco de Servicios",
            description="Términos y condiciones legales del servicio",
            file_type="contrato",
            client_id=cliente1.id,
            project_id=proyecto1.id
        )

        doc3 = Document(
            title="Reporte de Avance Semanal",
            description="Resumen de hitos logrados en la semana 4",
            file_type="reporte",
            client_id=cliente2.id,
            project_id=proyecto3.id
        )

        db.session.add_all([doc1, doc2, doc3])
        db.session.commit()

        # TICKETS
        ticket1 = SupportTicket(
            subject="Problema con acceso al portal",
            message="No puedo acceder a mi cuenta desde ayer",
            status="en_proceso",
            priority="alta",
            client_id=cliente1.id
        )
        
        db.session.add(ticket1)
        db.session.commit()

        print("✓ Base de datos inicializada exitosamente")
        print("\n========== CREDENCIALES DE ACCESO ==========")
        print("ADMIN: admin | admin123")
        print("EMPLEADOS: empleado1, empleado2 | emp123")
        print("CLIENTES: cliente1, cliente2, cliente3 | cli123")
        print("==========================================")

if __name__ == "__main__":
    init_db()
