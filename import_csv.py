import pandas as pd
import psycopg2

# Conexión a la base de datos
conn = psycopg2.connect(
    host='db',
    database='videos_youtube',
    user='postgres',
    password='postgres'
)

# Leer el CSV
df = pd.read_csv('/app/fixed_printpaintstudio_videos.csv', encoding='utf-8')
print(f"Leídas {len(df)} filas del CSV")

# Crear cursor
cur = conn.cursor()

# Insertar datos
count = 0
for index, row in df.iterrows():
    try:
        cur.execute('''
            INSERT INTO videos (title, description, video_id, channel, category, 
                              technique_start_time, technique_end_time, difficulty_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row['title'], 
            row['description'], 
            row['video_id'], 
            row['channel'], 
            row['category'],
            int(row['technique_start_time']) if pd.notna(row['technique_start_time']) else 0, 
            int(row['technique_end_time']) if pd.notna(row['technique_end_time']) else None, 
            row['difficulty_level']
        ))
        count += 1
    except Exception as e:
        print(f"Error en fila {index}: {e}")
        conn.rollback()
    else:
        conn.commit()

# Confirmar y cerrar
print(f'Importación completada: {count} filas insertadas exitosamente')
cur.close()
conn.close()