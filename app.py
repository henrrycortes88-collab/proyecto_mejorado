from datetime import datetime, timedelta
import os
import base64
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from models import db, User, Task, Project, SupportTicket, Document

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Usar variable de entorno para la clave secreta o una por defecto para desarrollo
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_12345_cambiar_en_produccion')
app.secret_key = SECRET_KEY

# Lógica de Cifrado (AES-128 via Fernet)
SECURE_SALT = os.environ.get('SECURITY_SALT', 'secure_salt_123').encode()

def get_cipher():
    """Genera un objeto Fernet basado en la SECRET_KEY."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SECURE_SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    return Fernet(key)

def encrypt_data(data):
    """Cifra una cadena de texto."""
    if not data: return None
    f = get_cipher()
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """Descifra una cadena de texto."""
    if not encrypted_data: return None
    try:
        f = get_cipher()
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception:
        return "Error al descifrar datos"

# Configuración de la base de datos
db_host = os.environ.get('DB_HOST', 'login-db')
db_uri = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 
    f'postgresql://usuario:password@{db_host}:5432/login_db'
)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de extensiones
db.init_app(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.session_protection = "strong"  # Mitigación de Session Hijacking
login_manager.init_app(app)

def role_required(role):
    """Decorador para restringir acceso por rol."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Acceso no autorizado para tu nivel de privilegios.', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos por su ID."""
    return db.session.get(User, int(user_id))


@app.route('/')
def home():
    """Ruta principal - Redirige según el rol del usuario."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'empleado':
            return redirect(url_for('employee_dashboard'))
        elif current_user.role == 'cliente':
            return redirect(url_for('client_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    """Ruta de inicio de sesión."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Mitigación de Session Fixation
            session.clear()
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Cierre de sesión."""
    logout_user()
    return redirect(url_for('login'))


#  RUTAS DE ADMINISTRADOR 

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    """Dashboard para administradores con estadísticas."""
    
    # Obtener todos los usuarios
    users = User.query.all()
    
    # Estadísticas con manejo de errores
    try:
        total_users = User.query.count()
        total_admins = User.query.filter_by(role='admin').count()
        total_employees = User.query.filter_by(role='empleado').count()
        total_clients = User.query.filter_by(role='cliente').count()
        total_tasks = Task.query.count()
        total_projects = Project.query.count()
        total_tickets = SupportTicket.query.filter(SupportTicket.status != 'resuelto').count()
        active_tasks = Task.query.filter(Task.status != 'completada').count()
    except Exception as e:
        app.logger.error(f"Error al calcular estadísticas de admin: {str(e)}")
        total_users = total_admins = total_employees = total_clients = total_tasks = total_projects = total_tickets = active_tasks = 0
    
    return render_template('dashboard_admin.html', 
                         users=users,
                         total_users=total_users,
                         total_admins=total_admins,
                         total_employees=total_employees,
                         total_clients=total_clients,
                         total_tasks=active_tasks,
                         total_projects=total_projects,
                         total_tickets=total_tickets)


@app.route('/admin/search', methods=['GET'])
@login_required
@role_required('admin')
def admin_search():
    """Búsqueda de usuarios para administrador."""
    
    query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '')
    
    if not query and not role_filter:
        users = User.query.all()
    else:
        users_query = User.query
        
        if query:
            users_query = users_query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            )
        
        if role_filter:
            users_query = users_query.filter_by(role=role_filter)
        
        users = users_query.all()
    
    users_data = [{
        'id': u.id,
        'username': u.username,
        'email': u.email or '',
        'role': u.role,
        'created_at': u.created_at.strftime('%Y-%m-%d') if u.created_at else ''
    } for u in users]
    
    return jsonify(users_data)


@app.route('/admin/create_user', methods=['POST'])
@login_required
@role_required('admin')
@limiter.limit("5 per minute")
def create_user():
    """Crear nuevo usuario."""
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    email = request.form.get('email', '').strip()
    
    # Validación de Email
    if email:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(f'Email no válido: {str(e)}', 'error')
            return redirect(url_for('admin_dashboard'))
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('El nombre de usuario ya existe', 'error')
    else:
        new_user = User(username=username, password_hash=generate_password_hash(password), role=role, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
        
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
@limiter.limit("10 per minute")
def edit_user(user_id):
    """Editar usuario existente."""
    
    user = db.session.get(User, user_id)
    if not user:
        return "Not found", 404
    
    username = request.form.get('username')
    role = request.form.get('role')
    password = request.form.get('password')
    email = request.form.get('email', '').strip()
    
    # Validación de Email
    if email:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            flash(f'Email no válido: {str(e)}', 'error')
            return redirect(url_for('admin_dashboard'))
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user.id:
        flash('El nombre de usuario ya está en uso', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if username:
        user.username = username
    if role:
        user.role = role
    if password:
        user.password_hash = generate_password_hash(password)
    
    # Permitir borrar el email si viene vacío
    user.email = email if email else None
        
    db.session.commit()
    flash('Usuario actualizado correctamente', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
@limiter.limit("5 per minute")
def delete_user(user_id):
    """Eliminar usuario con manejo de errores robusto."""
        
    if current_user.id == user_id:
        flash('No puedes eliminar tu propia cuenta', 'error')
        return redirect(url_for('admin_dashboard'))

    user = db.session.get(User, user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        username_to_delete = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuario {username_to_delete} y todos sus datos relacionados eliminados correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al eliminar usuario {user_id}: {str(e)}")
        flash('Error al intentar eliminar el usuario. Es posible que tenga dependencias complejas.', 'error')
        
    return redirect(url_for('admin_dashboard'))


# RUTAS DE EMPLEADO 

@app.route('/employee')
@login_required
@role_required('empleado')
def employee_dashboard():
    """Dashboard para empleados."""
    
    # Tareas del empleado
    my_tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    
    # Estadísticas de tareas con manejo de errores
    try:
        pending_tasks = Task.query.filter_by(assigned_to=current_user.id, status='pendiente').count()
        in_progress_tasks = Task.query.filter_by(assigned_to=current_user.id, status='en_proceso').count()
        completed_tasks = Task.query.filter_by(assigned_to=current_user.id, status='completada').count()
        
        
        my_projects = Project.query.join(Task).filter(Task.assigned_to == current_user.id).distinct().all()
    except Exception as e:
        app.logger.error(f"Error al cargar datos de empleado: {str(e)}")
        pending_tasks = in_progress_tasks = completed_tasks = 0
        my_projects = []
    
    return render_template('dashboard_employee.html',
                         my_tasks=my_tasks,
                         pending_tasks=pending_tasks,
                         in_progress_tasks=in_progress_tasks,
                         completed_tasks=completed_tasks,
                         my_projects=my_projects)


@app.route('/employee/tasks')
@login_required
@role_required('empleado')
def employee_tasks():
    """Ver todas las tareas del empleado."""
    
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    
    tasks_query = Task.query.filter_by(assigned_to=current_user.id)
    
    if status_filter:
        tasks_query = tasks_query.filter_by(status=status_filter)
    if priority_filter:
        tasks_query = tasks_query.filter_by(priority=priority_filter)
    
    tasks = tasks_query.order_by(Task.due_date.asc()).all()
    
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'priority': t.priority,
        'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None
    } for t in tasks])


@app.route('/employee/update_task/<int:task_id>', methods=['POST'])
@login_required
@role_required('empleado')
def employee_update_task(task_id):
    """Actualizar estado de una tarea."""
    
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Not found'}), 404
    
    if task.assigned_to != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    new_status = request.form.get('status')
    if new_status:
        task.status = new_status
        if new_status == 'completada':
            task.completed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tarea actualizada'})
    
    return jsonify({'error': 'Estado no válido'}), 400


#  RUTAS DE CLIENTE 

@app.route('/client')
@login_required
@role_required('cliente')
def client_dashboard():
    """Dashboard para clientes."""
    
    # Proyectos del cliente
    my_projects = Project.query.filter_by(client_id=current_user.id).all()
    
    # Tickets del cliente
    my_tickets = SupportTicket.query.filter_by(client_id=current_user.id).order_by(SupportTicket.created_at.desc()).limit(5).all()
    
    # Estadísticas para el dashboard
    active_projects = Project.query.filter_by(client_id=current_user.id, status='activo').count()
    completed_projects = Project.query.filter_by(client_id=current_user.id, status='completado').count()
    open_tickets = SupportTicket.query.filter_by(client_id=current_user.id, status='abierto').count()
    
    # Documentos del cliente
    my_documents = Document.query.filter_by(client_id=current_user.id).all()
    
    # Nota privada descifrada (Segura, solo se descifra para la vista del dueño)
    decrypted_note = decrypt_data(current_user.encrypted_note) or ""
    
    return render_template('dashboard_client.html',
                         my_projects=my_projects,
                         my_tickets=my_tickets,
                         my_documents=my_documents,
                         decrypted_note=decrypted_note,
                         active_projects=active_projects,
                         completed_projects=completed_projects,
                         open_tickets=open_tickets)


@app.route('/client/create_ticket', methods=['POST'])
@login_required
@role_required('cliente')
@limiter.limit("3 per minute")
def client_create_ticket():
    """Crear nuevo ticket de soporte."""
    
    subject = request.form['subject']
    message = request.form['message']
    priority = request.form.get('priority', 'normal')
    
    new_ticket = SupportTicket(
        subject=subject,
        message=message,
        priority=priority,
        client_id=current_user.id
    )
    db.session.add(new_ticket)
    db.session.commit()
    
    flash('Ticket creado exitosamente', 'success')
    return redirect(url_for('client_dashboard'))


@app.route('/client/my_projects')
@login_required
@role_required('cliente')
def client_projects():
    """Ver todos los proyectos del cliente."""
    
    projects = Project.query.filter_by(client_id=current_user.id).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'status': p.status,
        'progress': p.progress,
        'deadline': p.deadline.strftime('%Y-%m-%d') if p.deadline else None
    } for p in projects])


@app.route('/client/my_tickets')
@login_required
@role_required('cliente')
def client_tickets():
    """Ver todos los tickets del cliente."""
    
    tickets = SupportTicket.query.filter_by(client_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    
    return jsonify([{
        'id': t.id,
        'subject': t.subject,
        'message': t.message,
        'status': t.status,
        'priority': t.priority,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M')
    } for t in tickets])



@app.route('/client/document/<int:doc_id>')
@login_required
def view_document(doc_id):
    """
    Ruta segura para visualizar documentos. Verifica propiedad estrictamente.
    """
    doc = db.session.get(Document, doc_id)
    if not doc:
        return "Documento no encontrado", 404
    
    # VERIFICACIÓN DE PROPIEDAD: Solo el dueño o el admin pueden ver
    if doc.client_id != current_user.id and current_user.role != 'admin':
        return "Acceso Denegado: No tienes permiso para ver este recurso", 403
    
    return f"<h1>Documento Seguro: {doc.title}</h1><p>{doc.description}</p><p>Tipo: {doc.file_type}</p><a href='/client'>Volver</a>"


@app.route('/client/notes', methods=['GET'])
@login_required
def get_notes():
    """Obtiene las notas privadas descifradas."""
    return jsonify({
        "note": decrypt_data(current_user.encrypted_note) or ""
    })


@app.route('/client/notes/update', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def update_notes():
    """Actualiza las notas cifrándolas en reposo."""
    note = request.form.get('note', '')
    current_user.encrypted_note = encrypt_data(note)
    db.session.commit()
    flash('Notas privadas actualizadas y cifradas en reposo.', 'success')
    return redirect(url_for('client_dashboard'))


@app.after_request
def add_security_headers(response):
    """Añade encabezados de seguridad a todas las respuestas."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
    return response

# Manejadores de Errores Personalizados (Prevención de Fuga de Información)
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(429)
def ratelimit_handler(e):
    flash("Has excedido el límite de solicitudes. Por favor espera un momento.", "error")
    return redirect(url_for('home'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

    # Auto-inicializar tablas y datos al arrancar
with app.app_context():
    db.create_all()
    from models import User
    if not User.query.first():
        from init_db import init_db
        init_db()
