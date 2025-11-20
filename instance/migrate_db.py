"""
Script para migrar la base de datos y agregar los nuevos campos:
- prioridad
- archivo
- nombre_archivo
"""

import sqlite3
import os

def migrar_base_datos():
    """Agrega los nuevos campos a la tabla task"""
    
    db_path = 'todo.db'
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos 'todo.db'")
        print("Ejecuta 'python init_db.py' primero")
        return
    
    print("\n" + "="*60)
    print("🔄 MIGRACIÓN DE BASE DE DATOS")
    print("="*60 + "\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si las columnas ya existen
    cursor.execute("PRAGMA table_info(task)")
    columnas = [col[1] for col in cursor.fetchall()]
    
    print("📋 Columnas actuales en la tabla 'task':")
    for col in columnas:
        print(f"  • {col}")
    
    print("\n🔧 Agregando nuevas columnas...\n")
    
    # Agregar columna 'prioridad' si no existe
    if 'prioridad' not in columnas:
        try:
            cursor.execute("ALTER TABLE task ADD COLUMN prioridad VARCHAR(20) DEFAULT 'media'")
            # Actualizar todas las tareas existentes con prioridad media
            cursor.execute("UPDATE task SET prioridad = 'media' WHERE prioridad IS NULL")
            print("✅ Columna 'prioridad' agregada")
        except Exception as e:
            print(f"⚠️  Error al agregar 'prioridad': {e}")
    else:
        print("ℹ️  La columna 'prioridad' ya existe")
    
    # Agregar columna 'archivo' si no existe
    if 'archivo' not in columnas:
        try:
            cursor.execute("ALTER TABLE task ADD COLUMN archivo VARCHAR(300)")
            print("✅ Columna 'archivo' agregada")
        except Exception as e:
            print(f"⚠️  Error al agregar 'archivo': {e}")
    else:
        print("ℹ️  La columna 'archivo' ya existe")
    
    # Agregar columna 'nombre_archivo' si no existe
    if 'nombre_archivo' not in columnas:
        try:
            cursor.execute("ALTER TABLE task ADD COLUMN nombre_archivo VARCHAR(300)")
            print("✅ Columna 'nombre_archivo' agregada")
        except Exception as e:
            print(f"⚠️  Error al agregar 'nombre_archivo': {e}")
    else:
        print("ℹ️  La columna 'nombre_archivo' ya existe")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ ¡Migración completada exitosamente!")
    print("="*60)
    print("\n📁 Asegúrate de que exista la carpeta 'uploads/'")
    
    # Crear carpeta uploads si no existe
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Carpeta 'uploads/' creada")
    else:
        print("ℹ️  La carpeta 'uploads/' ya existe")
    
    print("\n🚀 Ahora puedes ejecutar la aplicación: python app.py\n")

if __name__ == '__main__':
    try:
        migrar_base_datos()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("Si el error persiste, considera recrear la base de datos con 'python init_db.py'")