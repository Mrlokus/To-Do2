"""
Script para corregir las rutas de archivos en la base de datos
Convierte rutas completas a solo nombres de archivo
"""

from app import app, db, Task
import os

def corregir_rutas():
    """Corrige las rutas de archivos en la base de datos"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🔧 CORRECCIÓN DE RUTAS DE ARCHIVOS")
        print("="*60 + "\n")
        
        # Obtener todas las tareas con archivos
        tareas_con_archivos = Task.query.filter(Task.archivo.isnot(None)).all()
        
        if not tareas_con_archivos:
            print("✅ No hay tareas con archivos adjuntos")
            return
        
        print(f"📋 Encontradas {len(tareas_con_archivos)} tareas con archivos\n")
        
        corregidas = 0
        for tarea in tareas_con_archivos:
            archivo_original = tarea.archivo
            
            # Si el archivo tiene una ruta (contiene / o \), extraer solo el nombre
            if '/' in archivo_original or '\\' in archivo_original:
                # Extraer solo el nombre del archivo
                nombre_archivo = os.path.basename(archivo_original)
                
                print(f"🔄 Tarea #{tarea.id}: {tarea.titulo}")
                print(f"   Antes: {archivo_original}")
                print(f"   Después: {nombre_archivo}")
                
                # Actualizar en la base de datos
                tarea.archivo = nombre_archivo
                corregidas += 1
            else:
                print(f"✅ Tarea #{tarea.id}: Ya está correcta")
        
        # Guardar cambios
        if corregidas > 0:
            db.session.commit()
            print(f"\n✅ Se corrigieron {corregidas} rutas de archivos")
        else:
            print("\n✅ Todas las rutas ya estaban correctas")
        
        print("\n" + "="*60)
        print("🎉 Corrección completada")
        print("="*60 + "\n")

def verificar_archivos_fisicos():
    """Verifica que los archivos físicos existan"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("📁 VERIFICACIÓN DE ARCHIVOS FÍSICOS")
        print("="*60 + "\n")
        
        tareas_con_archivos = Task.query.filter(Task.archivo.isnot(None)).all()
        
        if not tareas_con_archivos:
            print("✅ No hay tareas con archivos adjuntos")
            return
        
        existentes = 0
        faltantes = 0
        
        for tarea in tareas_con_archivos:
            archivo_path = os.path.join('uploads', tarea.archivo)
            
            if os.path.exists(archivo_path):
                print(f"✅ Tarea #{tarea.id}: {tarea.nombre_archivo} - Existe")
                existentes += 1
            else:
                print(f"❌ Tarea #{tarea.id}: {tarea.nombre_archivo} - NO ENCONTRADO")
                print(f"   Buscando en: {archivo_path}")
                faltantes += 1
        
        print(f"\n📊 Resumen:")
        print(f"   Archivos existentes: {existentes}")
        print(f"   Archivos faltantes: {faltantes}")
        
        if faltantes > 0:
            print(f"\n⚠️  Hay {faltantes} archivos que no se encuentran")
            print("   Verifica que estén en la carpeta 'uploads/'")
        
        print("\n" + "="*60 + "\n")

def menu():
    """Menú interactivo"""
    
    while True:
        print("\n" + "="*60)
        print("🛠️  HERRAMIENTA DE CORRECCIÓN DE ARCHIVOS")
        print("="*60)
        print("\n1. Corregir rutas de archivos en la base de datos")
        print("2. Verificar archivos físicos")
        print("3. Ejecutar ambas opciones")
        print("4. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '1':
            corregir_rutas()
        elif opcion == '2':
            verificar_archivos_fisicos()
        elif opcion == '3':
            corregir_rutas()
            verificar_archivos_fisicos()
        elif opcion == '4':
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción inválida")

if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        