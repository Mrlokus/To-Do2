"""
Script para inicializar la base de datos con usuarios de prueba
Ejecuta este archivo para crear la base de datos desde cero
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
import os

def init_database():
    """Inicializa la base de datos con usuarios de prueba"""
    
    with app.app_context():
        # Eliminar base de datos existente si existe
        if os.path.exists('todo.db'):
            print("⚠️  Eliminando base de datos anterior...")
            os.remove('todo.db')
        
        # Crear todas las tablas
        print("📦 Creando tablas de la base de datos...")
        db.create_all()
        
        # Verificar si ya existen usuarios
        if User.query.first():
            print("✅ Los usuarios ya existen en la base de datos")
            return
        
        # Crear un líder
        print("👔 Creando líder de equipo...")
        lider = User(
            username='lider1',
            password=generate_password_hash('lider123'),
            role='lider',
            nombre='Juan Pérez'
        )
        
        # Crear miembros del equipo
        print("👥 Creando miembros del equipo...")
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
        
        # Guardar en la base de datos
        db.session.add_all([lider, miembro1, miembro2])
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ ¡Base de datos inicializada correctamente!")
        print("="*60)
        print("\n📋 USUARIOS CREADOS:\n")
        print("👔 LÍDER DE EQUIPO:")
        print(f"   Usuario: lider1")
        print(f"   Contraseña: lider123")
        print(f"   Nombre: Juan Pérez")
        print()
        print("👤 MIEMBRO 1:")
        print(f"   Usuario: miembro1")
        print(f"   Contraseña: miembro123")
        print(f"   Nombre: María García")
        print()
        print("👤 MIEMBRO 2:")
        print(f"   Usuario: miembro2")
        print(f"   Contraseña: miembro123")
        print(f"   Nombre: Carlos López")
        print("\n" + "="*60)
        print("🚀 Ahora puedes iniciar sesión en: http://127.0.0.1:5000/login")
        print("="*60 + "\n")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error al inicializar la base de datos: {e}")
        print("Asegúrate de que app.py esté en el mismo directorio")