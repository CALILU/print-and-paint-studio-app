#!/usr/bin/env python3
"""
Script de migración para añadir posición de estantería a la tabla paints
y cargar los datos desde vallejo_model_color.csv
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from datetime import datetime

def get_db_connection():
    """Obtener conexión a la base de datos Railway"""
    # URL de conexión de Railway (deberás configurar esta variable de entorno)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL no está configurada")
        print("Por favor, configura la variable de entorno DATABASE_URL con la URL de conexión de Railway")
        sys.exit(1)
    
    # Parsear la URL de conexión
    url = urlparse(DATABASE_URL)
    
    connection = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        sslmode='require'
    )
    
    return connection

def add_shelf_position_column(conn):
    """Añadir la columna shelf_position a la tabla paints si no existe"""
    try:
        with conn.cursor() as cursor:
            # Verificar si la columna ya existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='paints' AND column_name='shelf_position'
            """)
            
            if cursor.fetchone():
                print("ℹ️  La columna shelf_position ya existe")
                return False
            
            # Añadir la columna
            cursor.execute("""
                ALTER TABLE paints 
                ADD COLUMN shelf_position INTEGER
            """)
            
            conn.commit()
            print("✅ Columna shelf_position añadida exitosamente")
            return True
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al añadir columna: {e}")
        return False

def load_positions_from_csv(conn, csv_path):
    """Cargar las posiciones desde el archivo CSV"""
    positions_data = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row['codigo'].strip()
                posicion = int(row['posicion'])
                positions_data[codigo] = posicion
                
        print(f"✅ Cargados {len(positions_data)} registros del CSV")
        return positions_data
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {csv_path}")
        return {}
    except Exception as e:
        print(f"❌ Error al leer CSV: {e}")
        return {}

def update_shelf_positions(conn, positions_data):
    """Actualizar las posiciones en la base de datos"""
    updated_count = 0
    not_found = []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            for codigo, posicion in positions_data.items():
                # Actualizar registros donde color_code coincida con codigo
                cursor.execute("""
                    UPDATE paints 
                    SET shelf_position = %s 
                    WHERE color_code = %s AND brand = 'VALLEJO'
                    RETURNING id, name, color_code
                """, (posicion, codigo))
                
                result = cursor.fetchall()
                
                if result:
                    updated_count += len(result)
                    for paint in result:
                        print(f"  ✓ Actualizado: {paint['name']} ({paint['color_code']}) - Posición: {posicion}")
                else:
                    not_found.append(codigo)
            
            conn.commit()
            
            print(f"\n📊 Resumen de actualización:")
            print(f"  - Pinturas actualizadas: {updated_count}")
            print(f"  - Códigos no encontrados: {len(not_found)}")
            
            if not_found and len(not_found) <= 10:
                print(f"  - Códigos no encontrados: {', '.join(not_found[:10])}")
            elif not_found:
                print(f"  - Primeros 10 códigos no encontrados: {', '.join(not_found[:10])}...")
                
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al actualizar posiciones: {e}")

def verify_update(conn):
    """Verificar que la actualización se realizó correctamente"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Contar pinturas Vallejo con posición
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM paints 
                WHERE brand = 'VALLEJO' AND shelf_position IS NOT NULL
            """)
            with_position = cursor.fetchone()['count']
            
            # Contar pinturas Vallejo sin posición
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM paints 
                WHERE brand = 'VALLEJO' AND shelf_position IS NULL
            """)
            without_position = cursor.fetchone()['count']
            
            # Mostrar algunas pinturas con posición como ejemplo
            cursor.execute("""
                SELECT name, color_code, shelf_position 
                FROM paints 
                WHERE brand = 'VALLEJO' AND shelf_position IS NOT NULL 
                ORDER BY shelf_position 
                LIMIT 5
            """)
            examples = cursor.fetchall()
            
            print(f"\n📊 Verificación final:")
            print(f"  - Pinturas VALLEJO con posición: {with_position}")
            print(f"  - Pinturas VALLEJO sin posición: {without_position}")
            
            if examples:
                print(f"\n  Ejemplos de pinturas con posición:")
                for paint in examples:
                    print(f"    • {paint['name']} ({paint['color_code']}) - Posición: {paint['shelf_position']}")
                    
    except Exception as e:
        print(f"❌ Error al verificar: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando migración de posiciones de estantería...")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ruta del archivo CSV
    csv_path = '/mnt/c/paintscanner/vallejo_model_color.csv'
    
    # Verificar que el archivo CSV existe
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encontró el archivo CSV en {csv_path}")
        sys.exit(1)
    
    # Conectar a la base de datos
    print("🔗 Conectando a la base de datos Railway...")
    conn = get_db_connection()
    
    try:
        # 1. Añadir columna si no existe
        print("\n1️⃣ Añadiendo columna shelf_position...")
        add_shelf_position_column(conn)
        
        # 2. Cargar datos del CSV
        print("\n2️⃣ Cargando datos del CSV...")
        positions_data = load_positions_from_csv(csv_path)
        
        if not positions_data:
            print("❌ No se pudieron cargar datos del CSV")
            sys.exit(1)
        
        # 3. Actualizar posiciones en la base de datos
        print(f"\n3️⃣ Actualizando {len(positions_data)} posiciones en la base de datos...")
        update_shelf_positions(conn, positions_data)
        
        # 4. Verificar actualización
        print("\n4️⃣ Verificando actualización...")
        verify_update(conn)
        
        print("\n✅ Migración completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)
        
    finally:
        conn.close()
        print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()