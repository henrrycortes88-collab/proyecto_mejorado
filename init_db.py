from app import app
from models import db, User, Task, Project, SupportTicket, Document
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_db():
    """Inicializa la base de datos con tablas y datos de ejemplo."""
    with app.app_context():
        print("Eliminando tablas existentes...")
        db.drop_all()
        
        print("Creando nuevas tablas...")
        db.create_all()

        print("Inicializando base de datos con datos de ejemplo...")

        print("Inicializando base de datos...")

        # ========== USUARIOS ==========
        admin = User(username="admin", role="admin", password_hash=generate_password_hash("admin123"), email="admin@empresa.com")
        
        empleado1 = User(username="empleado1", role="empleado", password_hash=generate_password_hash("emp123"), email="empleado1@empresa.com")
        empleado2 = User(username="empleado2", role="empleado", password_hash=generate_password_hash("emp123"), email="empleado2@empresa.com")
        
        cliente1 = User(username="cliente1", role="cliente", password_hash=generate_password_hash("cli123"), email="cliente1@correo.com")
        cliente2 = User(username="cliente2", role="cliente", password_hash=generate_password_hash("cli123"), email="cliente2@correo.com")
        cliente3 = User(username="cliente3", role="cliente", password_hash=generate_password_hash("cli123"), email="cliente3@correo.com")

        db.session.add_all([admin, empleado1, empleado2, cliente1, cliente2, cliente3])
        db.session.commit()

        # ========== PROYECTOS ==========
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

        # ========== TAREAS ==========
        # Tareas para empleado1
        tarea1 = Task(
            title="Revisar propuesta de diseño Q1",
            description="Validar los mockups del nuevo diseño del sitio web",
            status="en_proceso",
            priority="alta",
            assigned_to=empleado1.id,
            project_id=proyecto1.id,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        
        tarea2 = Task(
            title="Actualizar documentación técnica",
            description="Documentar las nuevas funcionalidades del sistema",
            status="pendiente",
            priority="media",
            assigned_to=empleado1.id,
            project_id=proyecto1.id,
            due_date=datetime.utcnow() + timedelta(days=3)
        )
        
        tarea3 = Task(
            title="Preparar presentación para cliente",
            description="Crear slides con el progreso del proyecto",
            status="pendiente",
            priority="alta",
            assigned_to=empleado1.id,
            project_id=proyecto2.id,
            due_date=datetime.utcnow() + timedelta(days=5)
        )
        
        tarea4 = Task(
            title="Code review módulo de autenticación",
            description="Revisar código del nuevo módulo de seguridad",
            status="completada",
            priority="alta",
            assigned_to=empleado1.id,
            project_id=proyecto2.id,
            due_date=datetime.utcnow() - timedelta(days=2),
            completed_at=datetime.utcnow() - timedelta(days=1)
        )

        # Tareas para empleado2
        tarea5 = Task(
            title="Optimización de base de datos",
            description="Mejorar índices y queries del sistema de reportes",
            status="en_proceso",
            priority="alta",
            assigned_to=empleado2.id,
            project_id=proyecto3.id,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        
        tarea6 = Task(
            title="Testing de integración",
            description="Ejecutar suite completa de pruebas",
            status="pendiente",
            priority="media",
            assigned_to=empleado2.id,
            project_id=proyecto3.id,
            due_date=datetime.utcnow() + timedelta(days=2)
        )
        
        tarea7 = Task(
            title="Configurar pipeline CI/CD",
            description="Setup de integración continua en el nuevo portal",
            status="pendiente",
            priority="media",
            assigned_to=empleado2.id,
            project_id=proyecto5.id,
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        
        tarea8 = Task(
            title="Reunión de seguimiento semanal",
            description="Reunión con el equipo para revisar avances",
            status="completada",
            priority="baja",
            assigned_to=empleado2.id,
            due_date=datetime.utcnow() - timedelta(days=3),
            completed_at=datetime.utcnow() - timedelta(days=3)
        )

        db.session.add_all([tarea1, tarea2, tarea3, tarea4, tarea5, tarea6, tarea7, tarea8])
        db.session.commit()

        # ========== TICKETS DE SOPORTE ==========
        ticket1 = SupportTicket(
            subject="Problema con acceso al portal",
            message="No puedo acceder a mi cuenta desde ayer, me aparece un error 500",
            status="en_proceso",
            priority="alta",
            client_id=cliente1.id
        )
        
        ticket2 = SupportTicket(
            subject="Solicitud de nueva funcionalidad",
            message="Me gustaría poder exportar los reportes en formato Excel",
            status="abierto",
            priority="normal",
            client_id=cliente1.id
        )
        
        ticket3 = SupportTicket(
            subject="Consulta sobre facturación",
            message="¿Cuándo recibiré la factura del mes pasado?",
            status="resuelto",
            priority="baja",
            client_id=cliente2.id
        )
        
        ticket4 = SupportTicket(
            subject="Error en módulo de reportes",
            message="Los gráficos no se están generando correctamente",
            status="abierto",
            priority="urgente",
            client_id=cliente2.id
        )
        
        ticket5 = SupportTicket(
            subject="Capacitación para el equipo",
            message="Necesitamos agendar una sesión de capacitación para usar el nuevo sistema",
            status="abierto",
            priority="normal",
            client_id=cliente3.id
        )

        db.session.add_all([ticket1, ticket2, ticket3, ticket4, ticket5])
        db.session.commit()

        # ========== DOCUMENTOS ==========
        doc1 = Document(
            title="Factura #2024-0234",
            description="Factura mensual de servicios",
            file_type="factura",
            client_id=cliente1.id,
            project_id=proyecto1.id
        )
        
        doc2 = Document(
            title="Contrato de Servicios 2024",
            description="Contrato anual renovado",
            file_type="contrato",
            client_id=cliente1.id
        )
        
        doc3 = Document(
            title="Reporte de Progreso Q1",
            description="Reporte trimestral de avances",
            file_type="reporte",
            client_id=cliente1.id,
            project_id=proyecto1.id
        )
        
        doc4 = Document(
            title="Manual de Usuario v2.0",
            description="Documentación del sistema actualizada",
            file_type="manual",
            client_id=cliente2.id,
            project_id=proyecto3.id
        )
        
        doc5 = Document(
            title="Propuesta Técnica Portal",
            description="Documento con especificaciones técnicas del proyecto",
            file_type="propuesta",
            client_id=cliente3.id,
            project_id=proyecto5.id
        )

        db.session.add_all([doc1, doc2, doc3, doc4, doc5])
        db.session.commit()

        print("✓ Base de datos inicializada exitosamente")
        print("\n========== CREDENCIALES DE ACCESO ==========")
        print("\nADMINISTRADOR:")
        print("  Usuario: admin")
        print("  Contraseña: admin123")
        print("\nEMPLEADOS:")
        print("  Usuario: empleado1 | Contraseña: emp123")
        print("  Usuario: empleado2 | Contraseña: emp123")
        print("\nCLIENTES:")
        print("  Usuario: cliente1 | Contraseña: cli123")
        print("  Usuario: cliente2 | Contraseña: cli123")
        print("  Usuario: cliente3 | Contraseña: cli123")
        print("\n==========================================")

if __name__ == "__main__":
    init_db()
