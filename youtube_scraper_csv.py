import pandas as pd
import psycopg2
import os


#**************************************************************************************
# 
# 
# Programa para conectarse a la base de datos de railway funciona no perder el codigo
#
# 
#**************************************************************************************


# Configuración para Railway desde entorno local (usando la URL pública)
host = 'shinkansen.proxy.rlwy.net'
port = '22933'
database = 'railway'
user = 'postgres'
password = 'xGBtAyofMYhZvVxOuMbrYJHVkeQDDkGc'

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

# Ruta del archivo CSV
csv_path = os.environ.get('CSV_PATH', 'printpaintstudio_videos.csv')
print(f"Intentando leer el archivo CSV: {csv_path}")

# Leer el CSV - Saltar la primera línea que está en blanco
try:
    df = pd.read_csv(csv_path, encoding='utf-8', skiprows=1)
    print(f"Leídas {len(df)} filas del CSV (saltando la primera línea en blanco)")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo CSV en la ruta: {csv_path}")
    print("Rutas posibles a verificar:")
    print(f"- Ruta actual: {os.getcwd()}")
    print(f"- Ruta absoluta: {os.path.abspath(csv_path)}")
    exit(1)
except Exception as e:
    print(f"Error al leer el CSV: {str(e)}")
    exit(1)

# Crear cursor
cur = conn.cursor()

# Verificar que las columnas esperadas estén presentes
expected_columns = ['title', 'description', 'video_id', 'channel', 'category', 
                   'technique_start_time', 'technique_end_time', 'difficulty_level', 'video_version']
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    print(f"Error: Faltan las siguientes columnas en el CSV: {missing_columns}")
    print(f"Columnas encontradas: {df.columns.tolist()}")
    exit(1)

# Insertar datos
count = 0
for index, row in df.iterrows():
    try:
        cur.execute('''
            INSERT INTO videos (title, description, video_id, channel, category, 
                              technique_start_time, technique_end_time, difficulty_level, video_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row['title'], 
            row['description'], 
            row['video_id'], 
            row['channel'], 
            row['category'],
            int(row['technique_start_time']) if pd.notna(row['technique_start_time']) else 0, 
            int(row['technique_end_time']) if pd.notna(row['technique_end_time']) else None, 
            row['difficulty_level'],
            int(row['video_version']) if pd.notna(row['video_version']) else 1,
        ))
        count += 1
        # Commit después de cada inserción exitosa
        conn.commit()
        if index % 10 == 0:  # Mostrar progreso cada 10 filas
            print(f"Procesadas {index + 1} filas, {count} insertadas exitosamente")
    except Exception as e:
        print(f"Error en fila {index}: {e}")
        # No es necesario hacer rollback aquí ya que cada inserción tiene su propio commit

# Confirmar y cerrar
print(f'Importación completada: {count} filas insertadas exitosamente')
cur.close()
conn.close()