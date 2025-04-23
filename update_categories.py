import psycopg2
import random

def actualizar_categorias():
    # Categorías a asignar
    categorias = [
        "Pintura Base",
        "Sombreado",
        "Iluminacion",
        "Detalles",
        "Efectos Especiales",
        "Barnizado",
        "Peanas"
    ]
    
    # Conexión a la base de datos
    conn = psycopg2.connect(
        host="db",
        database="videos_youtube",
        user="postgres",
        password="postgres"
    )
    
    try:
        # Crear cursor
        cur = conn.cursor()
        
        # Obtener todos los IDs de videos
        cur.execute("SELECT id FROM videos")
        ids = cur.fetchall()
        
        # Contador para estadísticas
        actualizados = 0
        conteo_categorias = {cat: 0 for cat in categorias}
        
        # Asegurar distribución equitativa
        for i, video_id in enumerate(ids):
            # Asignar categorías de manera cíclica para garantizar distribución equitativa
            categoria = categorias[i % len(categorias)]
            
            # Actualizar el registro
            cur.execute(
                "UPDATE videos SET category = %s WHERE id = %s",
                (categoria, video_id[0])
            )
            
            # Incrementar contadores
            actualizados += 1
            conteo_categorias[categoria] += 1
            
            # Mostrar progreso
            if actualizados % 10 == 0:
                print(f"Actualizados {actualizados} registros...")
        
        # Confirmar cambios
        conn.commit()
        
        print(f"\n¡Proceso completado! Se actualizaron {actualizados} registros.")
        print("\nDistribución de categorías:")
        for cat, count in conteo_categorias.items():
            print(f"  {cat}: {count} videos")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    
    finally:
        # Cerrar cursor y conexión
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Iniciando actualización de categorías...")
    actualizar_categorias()