from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui-cambiar-en-produccion'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}

# Crear carpeta de uploads si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# ==================== MODELOS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'lider' o 'miembro'
    nombre = db.Column(db.String(100), nullable=False)
    tasks_created = db.relationship('Task', backref='creador', foreign_keys='Task.created_by')
    tasks_assigned = db.relationship('Task', backref='asignado', foreign_keys='Task.assigned_to')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # 'pendiente', 'en_progreso', 'completada'
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_completada = db.Column(db.DateTime)

# ==================== DECORADORES ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión primero', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def lider_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión primero', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'lider':
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['nombre'] = user.nombre
            flash(f'¡Bienvenido {user.nombre}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    if user.role == 'lider':
        # Líder ve todas las tareas creadas por él
        mis_tareas = Task.query.filter_by(created_by=user.id).all()
        # También ve sus tareas asignadas
        tareas_asignadas = Task.query.filter_by(assigned_to=user.id).all()
        miembros = User.query.filter_by(role='miembro').all()
        return render_template('dashboard_lider.html', 
                             mis_tareas=mis_tareas, 
                             tareas_asignadas=tareas_asignadas,
                             miembros=miembros)
    else:
        # Miembro solo ve sus tareas asignadas
        mis_tareas = Task.query.filter_by(assigned_to=user.id).all()
        return render_template('dashboard_miembro.html', mis_tareas=mis_tareas)

# ==================== GESTIÓN DE TAREAS ====================

@app.route('/tarea/crear', methods=['GET', 'POST'])
@login_required
def crear_tarea():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        assigned_to = request.form.get('assigned_to')
        
        # Para miembros, auto-asignar la tarea a ellos mismos si no especifican otro
        user = User.query.get(session['user_id'])
        if user.role == 'miembro':
            # Miembro siempre se asigna la tarea a sí mismo
            assigned_to_id = session['user_id']
        else:
            # Líder puede asignar a otros o a sí mismo
            assigned_to_id = int(assigned_to) if assigned_to else None
        
        nueva_tarea = Task(
            titulo=titulo,
            descripcion=descripcion,
            created_by=session['user_id'],
            assigned_to=assigned_to_id
        )
        
        db.session.add(nueva_tarea)
        db.session.commit()
        flash('Tarea creada exitosamente', 'success')
        return redirect(url_for('dashboard'))
    
    # Para el formulario
    user = User.query.get(session['user_id'])
    if user.role == 'lider':
        miembros = User.query.filter_by(role='miembro').all()
    else:
        miembros = []
    
    return render_template('crear_tarea.html', miembros=miembros)

@app.route('/tarea/<int:id>/actualizar', methods=['POST'])
@login_required
def actualizar_estado_tarea(id):
    tarea = Task.query.get_or_404(id)
    user = User.query.get(session['user_id'])
    
    # Verificar permisos
    if tarea.assigned_to != user.id and tarea.created_by != user.id:
        flash('No tienes permisos para modificar esta tarea', 'danger')
        return redirect(url_for('dashboard'))
    
    nuevo_estado = request.form.get('estado')
    tarea.estado = nuevo_estado
    
    if nuevo_estado == 'completada':
        tarea.fecha_completada = datetime.utcnow()
    
    db.session.commit()
    flash('Estado de tarea actualizado', 'success')
    return redirect(url_for('dashboard'))

@app.route('/tarea/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_tarea(id):
    tarea = Task.query.get_or_404(id)
    user = User.query.get(session['user_id'])
    
    # Solo el creador puede eliminar
    if tarea.created_by != user.id:
        flash('No tienes permisos para eliminar esta tarea', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(tarea)
    db.session.commit()
    flash('Tarea eliminada', 'success')
    return redirect(url_for('dashboard'))

# ==================== RUTAS PARA LÍDERES ====================

@app.route('/lider/tareas-por-miembro')
@lider_required
def tareas_por_miembro():
    miembros = User.query.filter_by(role='miembro').all()
    tareas_por_miembro = {}
    
    for miembro in miembros:
        tareas = Task.query.filter_by(assigned_to=miembro.id).all()
        tareas_por_miembro[miembro] = {
            'todas': tareas,
            'pendientes': [t for t in tareas if t.estado == 'pendiente'],
            'en_progreso': [t for t in tareas if t.estado == 'en_progreso'],
            'completadas': [t for t in tareas if t.estado == 'completada']
        }
    
    return render_template('tareas_por_miembro.html', tareas_por_miembro=tareas_por_miembro)

@app.route('/lider/miembro/<int:id>/tareas')
@lider_required
def ver_tareas_miembro(id):
    miembro = User.query.get_or_404(id)
    if miembro.role != 'miembro':
        flash('Usuario no válido', 'danger')
        return redirect(url_for('dashboard'))
    
    tareas = Task.query.filter_by(assigned_to=id).all()
    return render_template('tareas_miembro.html', miembro=miembro, tareas=tareas)

@app.route('/tarea/<int:id>/reasignar', methods=['POST'])
@lider_required
def reasignar_tarea(id):
    tarea = Task.query.get_or_404(id)
    nuevo_asignado = request.form.get('assigned_to')
    
    if nuevo_asignado:
        tarea.assigned_to = int(nuevo_asignado)
        db.session.commit()
        flash('Tarea reasignada exitosamente', 'success')
    
    return redirect(url_for('dashboard'))

# ==================== INICIALIZACIÓN ====================

@app.route('/setup')
def setup():
    """Ruta para crear usuarios de prueba - ELIMINAR EN PRODUCCIÓN"""
    db.create_all()
    
    # Verificar si ya existen usuarios
    if User.query.first():
        return "La base de datos ya está inicializada"
    
    # Crear un líder
    lider = User(
        username='lider1',
        password=generate_password_hash('lider123'),
        role='lider',
        nombre='Juan Pérez'
    )
    
    # Crear miembros del equipo
    miembro1 = User(
        username='miembro1',
        password=generate_password_hash('miembro123'),
        role='miembro',
        nombre='María García'
    )
    
    miembro2 = User(
        username='miembro2',
        password=generate_password_hash('miembro123'),
        role='miembro',
        nombre='Carlos López'
    )
    
    db.session.add_all([lider, miembro1, miembro2])
    db.session.commit()
    
    return """
    Base de datos inicializada con usuarios de prueba:<br><br>
    <b>Líder:</b> usuario: lider1, contraseña: lider123<br>
    <b>Miembro 1:</b> usuario: miembro1, contraseña: miembro123<br>
    <b>Miembro 2:</b> usuario: miembro2, contraseña: miembro123<br><br>
    <a href="/login">Ir al login</a>
    """

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)