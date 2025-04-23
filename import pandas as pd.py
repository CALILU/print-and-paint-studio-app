import pandas as pd
import psycopg2
import os

# Configuración de la conexión
conn = psycopg2.connect(
    host="db",
    database="videos_youtube",
    user="postgres",
    password="postgres"
)

# Leer el CSV
df = pd.read_csv('C:\\youtube-app\\fixed_printpaintstudio_videos.csv', encoding='utf-8')

# Opcional: Ver las primeras filas para verificar
print(df.head())

# Crear un cursor
cur = conn.cursor()

# Recorrer el DataFrame e insertar en la base de datos
for index, row in df.iterrows():
    cur.execute("""
        INSERT INTO videos (title, description, video_id, channel, category, 
                           technique_start_time, technique_end_time, difficulty_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['title'], 
        row['description'], 
        row['video_id'], 
        row['channel'], 
        row['category'],
        row['technique_start_time'], 
        row['technique_end_time'], 
        row['difficulty_level']
    ))

# Confirmar cambios y cerrar conexión
conn.commit()
cur.close()
conn.close()

print("Importación completada con éxito")