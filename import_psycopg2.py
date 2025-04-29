import psycopg2
import random

# Configuración para Railway desde entorno local (usando la URL pública)
host = 'shinkansen.proxy.rlwy.net'
port = '22933'
database = 'railway'
user = 'postgres'
password = 'xGBtAyofMYhZvVxOuMbrYJHVkeQDDkGc'

# Categorías y niveles de dificultad disponibles
categories = ["Pintura Base", "Sombreado", "Iluminación", "Detalles", 
              "Efectos Especiales", "Barnizado", "Peanas"]
difficulty_levels = ["beginner", "intermediate", "expert"]

# Conexión a la base de datos
print(f"Conectando a la base de datos: {host}:{port}/{database}")
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    print("Conexión establecida exitosamente")
except Exception as e:
    print(f"Error al conectar a la base de datos: {str(e)}")
    exit(1)

# Crear cursor
cur = conn.cursor()

# Obtener todos los IDs de videos
try:
    cur.execute("SELECT id FROM videos")
    video_ids = [row[0] for row in cur.fetchall()]
    print(f"Encontrados {len(video_ids)} videos para actualizar")
except Exception as e:
    print(f"Error al obtener IDs de videos: {str(e)}")
    conn.close()
    exit(1)

# Actualizar cada video con categorías y niveles de dificultad aleatorios
updated_count = 0
for video_id in video_ids:
    try:
        # Seleccionar valores aleatorios
        random_category = random.choice(categories)
        random_difficulty = random.choice(difficulty_levels)
        
        # Actualizar el registro
        cur.execute("""
            UPDATE videos 
            SET category = %s, difficulty_level = %s 
            WHERE id = %s
        """, (random_category, random_difficulty, video_id))
        
        conn.commit()
        updated_count += 1
        
        # Mostrar progreso
        if updated_count % 10 == 0 or updated_count == len(video_ids):
            print(f"Actualizados {updated_count}/{len(video_ids)} videos")
            
    except Exception as e:
        print(f"Error al actualizar video ID {video_id}: {str(e)}")
        conn.rollback()

# Mostrar resumen
print(f"\nActualización completada: {updated_count} videos actualizados")

# Mostrar distribución final
print("\nDistribución final de categorías:")
try:
    cur.execute("SELECT category, COUNT(*) FROM videos GROUP BY category ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} videos")
except Exception as e:
    print(f"Error al obtener estadísticas de categorías: {str(e)}")

print("\nDistribución final de niveles de dificultad:")
try:
    cur.execute("SELECT difficulty_level, COUNT(*) FROM videos GROUP BY difficulty_level ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} videos")
except Exception as e:
    print(f"Error al obtener estadísticas de niveles de dificultad: {str(e)}")

# Cerrar conexión
cur.close()
conn.close()
print("\nConexión cerrada")