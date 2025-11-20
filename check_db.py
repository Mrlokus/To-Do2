"""
Script para verificar los usuarios existentes en la base de datos
"""

from app import app, db, User
import os

def verificar_usuarios():
    """Muestra todos los usuarios en la base de datos"""
    
    # Verificar si existe la base de datos
    if not os.path.exists('todo.db'):
        print("❌ La base de datos 'todo.db' no existe")
        print("Ejecuta 'python init_db.py' para crearla")
        return
    
    with app.app_context():
        usuarios = User.query.all()
        
        if not usuarios:
            print("⚠️  No hay usuarios en la base de datos")
            print("Ejecuta 'python init_db.py' para crear usuarios de prueba")
            return
        
        print("\n" + "="*60)
        print("👥 USUARIOS EN LA BASE DE DATOS:")
        print("="*60 + "\n")
        
        for user in usuarios:
            print(f"ID: {user.id}")
            print(f"Usuario: {user.username}")
            print(f"Nombre: {user.nombre}")
            print(f"Rol: {user.role.upper()}")
            print(f"Contraseña (hash): {user.password[:30]}...")
            print("-" * 60)
        
        print(f"\n✅ Total de usuarios: {len(usuarios)}\n")
        
        # Dar instrucciones de login
        print("🔑 CREDENCIALES PARA LOGIN:")
        print("-" * 60)
        for user in usuarios:
            if user.role == 'lider':
                print(f"👔 Líder: {user.username} / lider123")
            else:
                print(f"👤 Miembro: {user.username} / miembro123")
        print()

if __name__ == '__main__':
    try:
        verificar_usuarios()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Asegúrate de que app.py esté en el mismo directorio")