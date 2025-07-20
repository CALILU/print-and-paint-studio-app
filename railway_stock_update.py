import pandas as pd
import psycopg2
import os
from chardet import detect

#**************************************************************************************
# 
# 
# Programa para actualizar el stock de pinturas en Railway desde un archivo CSV
# utilizando color_code como identificador de producto
#
# 
#**************************************************************************************

def get_encoding(file_path):
    """Detecta automáticamente la codificación del archivo"""
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # Lee los primeros 10000 bytes para detectar
    result = detect(raw_data)
    return result['encoding']

# Configuración para Railway desde entorno local
host = 'shinkansen.proxy.rlwy.net'
port = '22933'
database = 'railway'
user = 'postgres'
password = 'xGBtAyofMYhZvVxOuMbrYJHVkeQDDkGc'

# Ruta del archivo CSV
csv_path = 'C:\\Vallejo\\CSV\\Base_de_datos_Army_painter.csv'
print(f"Intentando leer el archivo CSV: {csv_path}")

# Comprobar si el archivo existe
if not os.path.exists(csv_path):
    print(f"Error: No se encontró el archivo CSV en la ruta: {csv_path}")
    print("Rutas posibles a verificar:")
    print(f"- Ruta actual: {os.getcwd()}")
    print(f"- Ruta absoluta: {os.path.abspath(csv_path)}")
    exit(1)

try:
    # Detectar la codificación del archivo
    encoding = get_encoding(csv_path)
    print(f"Codificación detectada: {encoding}")
    
    # Intentar leer el CSV con la codificación detectada
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
    except Exception as e:
        print(f"Error al leer con la codificación detectada ({encoding}): {str(e)}")
        print("Intentando con otras codificaciones comunes...")
        
        # Lista de codificaciones a probar
        encodings = ['latin-1', 'utf-8', 'windows-1252', 'cp1252', 'ISO-8859-1']
        success = False
        
        for enc in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=enc)
                print(f"Éxito al leer con codificación: {enc}")
                success = True
                break
            except Exception:
                continue
                
        if not success:
            print("No se pudo leer el archivo con ninguna codificación estándar.")
            print("Intentando leer sin especificar la codificación...")
            df = pd.read_csv(csv_path, encoding_errors='replace')

    print(f"Leídas {len(df)} filas del CSV")
    
    # Mostrar información sobre las primeras filas para diagnóstico
    print("\nPrimeras 3 filas del CSV:")
    print(df.head(3))
    
    # Mostrar información sobre las columnas
    print("\nColumnas encontradas en el CSV:")
    print(df.columns.tolist())
    
    # Identificar las columnas de código y stock
    # Comprobar diferentes variantes de nombres de columna
    codigo_variants = ['codigo', 'código', 'Codigo', 'Código', 'CODIGO', 'CÓDIGO', 'code', 'CODE', 'color_code']
    stock_variants = ['stock', 'Stock', 'STOCK', 'existencias', 'Existencias', 'EXISTENCIAS', 'inventario', 'Inventario']
    
    codigo_col = None
    for variant in codigo_variants:
        if variant in df.columns:
            codigo_col = variant
            break
            
    stock_col = None
    for variant in stock_variants:
        if variant in df.columns:
            stock_col = variant
            break
    
    if not codigo_col:
        print(f"Error: No se encontró ninguna columna de código. Columnas disponibles: {df.columns.tolist()}")
        exit(1)
        
    if not stock_col:
        print(f"Error: No se encontró ninguna columna de stock. Columnas disponibles: {df.columns.tolist()}")
        exit(1)
    
    print(f"Usando columna '{codigo_col}' para el código y '{stock_col}' para el stock")
    
    # Conexión a la base de datos
    print(f"\nConectando a la base de datos: {host}:{port}/{database}")
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
    
    # Verificar la estructura de la tabla
    try:
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'paints' ORDER BY ordinal_position")
        columns = [row[0] for row in cur.fetchall()]
        print(f"\nColumnas en la tabla 'paints': {columns}")
        
        if 'color_code' not in columns:
            print("Error: La tabla 'paints' no tiene una columna 'color_code'")
            exit(1)
            
        if 'stock' not in columns:
            print("Advertencia: La tabla 'paints' no tiene una columna 'stock'")
            print("Por favor, especifique el nombre correcto de la columna de stock:")
            db_stock_col = input("> ")
        else:
            db_stock_col = 'stock'
    except Exception as e:
        print(f"Error al verificar la estructura de la tabla: {str(e)}")
        exit(1)

    # Actualizar datos
    count = 0
    count_err = 0
    
    # Usar explícitamente las columnas color_code y stock
    db_codigo_col = 'color_code'
    print(f"Usando columna '{db_codigo_col}' en la base de datos para búsqueda")
    print(f"Usando columna '{db_stock_col}' en la base de datos para actualizar el stock")
    
    # Procesar el CSV fila por fila
    for index, row in df.iterrows():
        try:
            # Obtener el código y stock del CSV
            codigo_value = str(row[codigo_col]) if not pd.isna(row[codigo_col]) else ""
            stock_value = str(row[stock_col]) if not pd.isna(row[stock_col]) else "0"
            
            # Limpiar valores
            codigo_value = codigo_value.strip()
            stock_value = stock_value.strip()
            
            if not codigo_value:
                print(f"Fila {index+1}: Código vacío, saltando...")
                count_err += 1
                continue
                
            # Verificar si el código existe en la tabla paints
            query = f"SELECT id FROM paints WHERE {db_codigo_col} = %s"
            cur.execute(query, (codigo_value,))
            result = cur.fetchone()
            
            if result:
                # El producto existe, actualizar el stock
                update_query = f"UPDATE paints SET {db_stock_col} = %s WHERE {db_codigo_col} = %s"
                cur.execute(update_query, (stock_value, codigo_value))
                conn.commit()
                count += 1
                
                # Mostrar progreso
                if index % 10 == 0 or index == len(df) - 1:
                    print(f"Procesadas {index + 1}/{len(df)} filas, {count} actualizadas exitosamente")
            else:
                print(f"Fila {index+1}: El código '{codigo_value}' no existe en la tabla paints")
                count_err += 1
                
        except Exception as e:
            print(f"Error en fila {index+1}: {str(e)}")
            if 'codigo_value' in locals():
                print(f"  Código: '{codigo_value}'")
            if 'stock_value' in locals():
                print(f"  Stock: '{stock_value}'")
            count_err += 1
            conn.rollback()
    
    # Confirmar y cerrar
    print(f'\nActualización completada:')
    print(f'- {count} filas actualizadas exitosamente')
    print(f'- {count_err} errores encontrados')
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error general: {str(e)}")