from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task, Project, SupportTicket, Document
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Usar variable de entorno para la clave secreta o una por defecto para desarrollo
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_12345_cambiar_en_produccion')

# Configuración de la base de datos
db_host = os.environ.get('DB_HOST', 'db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 
    f'postgresql://usuario:password@{db_host}:5432/login_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


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
def login():
    """Ruta de inicio de sesión."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
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


# ==================== RUTAS DE ADMINISTRADOR ====================

@app.route('/admin')
@login_required
def admin_dashboard():
    """Dashboard para administradores con estadísticas."""
    if current_user.role != 'admin':
        return "Acceso Denegado", 403
    
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
def admin_search():
    """Búsqueda de usuarios para administrador."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403
    
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
def create_user():
    """Crear nuevo usuario."""
    if current_user.role != 'admin':
        return "Acceso Denegado", 403
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    email = request.form.get('email', '')
    
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
def edit_user(user_id):
    """Editar usuario existente."""
    if current_user.role != 'admin':
        return "Acceso Denegado", 403
    
    user = db.session.get(User, user_id)
    if not user:
        return "Not found", 404
    
    username = request.form.get('username')
    role = request.form.get('role')
    password = request.form.get('password')
    email = request.form.get('email', '')
    
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
def delete_user(user_id):
    """Eliminar usuario con manejo de errores robusto."""
    if current_user.role != 'admin':
        return "Acceso Denegado", 403
        
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


# ==================== RUTAS DE EMPLEADO ====================

@app.route('/employee')
@login_required
def employee_dashboard():
    """Dashboard para empleados."""
    if current_user.role != 'empleado':
        return "Acceso Denegado", 403
    
    # Tareas del empleado
    my_tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    
    # Estadísticas de tareas con manejo de errores
    try:
        pending_tasks = Task.query.filter_by(assigned_to=current_user.id, status='pendiente').count()
        in_progress_tasks = Task.query.filter_by(assigned_to=current_user.id, status='en_proceso').count()
        completed_tasks = Task.query.filter_by(assigned_to=current_user.id, status='completada').count()
        
        # Proyectos relacionados
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
def employee_tasks():
    """Ver todas las tareas del empleado."""
    if current_user.role != 'empleado':
        return "Acceso Denegado", 403
    
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
def employee_update_task(task_id):
    """Actualizar estado de una tarea."""
    if current_user.role != 'empleado':
        return jsonify({'error': 'Acceso denegado'}), 403
    
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


# ==================== RUTAS DE CLIENTE ====================

@app.route('/client')
@login_required
def client_dashboard():
    """Dashboard para clientes."""
    if current_user.role != 'cliente':
        return "Acceso Denegado", 403
    
    # Proyectos del cliente
    my_projects = Project.query.filter_by(client_id=current_user.id).all()
    
    # Tickets del cliente
    my_tickets = SupportTicket.query.filter_by(client_id=current_user.id).order_by(SupportTicket.created_at.desc()).limit(5).all()
    
    # Documentos del cliente
    my_documents = Document.query.filter_by(client_id=current_user.id).order_by(Document.created_at.desc()).limit(5).all()
    
    # Estadísticas con manejo de errores
    try:
        active_projects = Project.query.filter_by(client_id=current_user.id, status='activo').count()
        completed_projects = Project.query.filter_by(client_id=current_user.id, status='completado').count()
        open_tickets = SupportTicket.query.filter_by(client_id=current_user.id, status='abierto').count()
        total_documents = Document.query.filter_by(client_id=current_user.id).count()
    except Exception as e:
        app.logger.error(f"Error al cargar estadísticas de cliente: {str(e)}")
        active_projects = completed_projects = open_tickets = total_documents = 0
    
    return render_template('dashboard_client.html',
                         my_projects=my_projects,
                         my_tickets=my_tickets,
                         my_documents=my_documents,
                         active_projects=active_projects,
                         completed_projects=completed_projects,
                         open_tickets=open_tickets,
                         total_documents=total_documents)


@app.route('/client/create_ticket', methods=['POST'])
@login_required
def client_create_ticket():
    """Crear nuevo ticket de soporte."""
    if current_user.role != 'cliente':
        return "Acceso Denegado", 403
    
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
def client_projects():
    """Ver todos los proyectos del cliente."""
    if current_user.role != 'cliente':
        return "Acceso Denegado", 403
    
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
def client_tickets():
    """Ver todos los tickets del cliente."""
    if current_user.role != 'cliente':
        return "Acceso Denegado", 403
    
    tickets = SupportTicket.query.filter_by(client_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    
    return jsonify([{
        'id': t.id,
        'subject': t.subject,
        'message': t.message,
        'status': t.status,
        'priority': t.priority,
        'created_at': t.created_at.strftime('%Y-%m-%d %H:%M')
    } for t in tickets])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
