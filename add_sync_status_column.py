#!/usr/bin/env python3
"""
Script para agregar la columna sync_status a la tabla paints en Railway
Usando Flask-SQLAlchemy para compatibilidad
"""

import os
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Paint

def create_app():
    """Crear instancia de Flask con configuración de base de datos"""
    app = Flask(__name__)
    
    # Configurar base de datos
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        # Para Railway, usar la URL específica
        if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT') == '8080':
            db_url = 'postgresql://postgres:xGBtAyofMYhZvVxOuMbrYJHVkeQDDkGc@postgres.railway.internal:5432/railway'
        else:
            print("Error: No se encontró DATABASE_URL")
            return None
    
    # Convertir URL si es necesario
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def add_sync_status_column():
    """Agregar columna sync_status a la tabla paints si no existe"""
    
    app = create_app()
    if not app:
        return False
    
    with app.app_context():
        try:
            print("🔍 Verificando estructura de la tabla paints...")
            
            # Verificar si la columna ya existe usando raw SQL
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'paints' AND column_name = 'sync_status'
            """))
            
            if result.fetchone():
                print("✅ La columna sync_status ya existe en la tabla paints")
                return True
            
            # Agregar la columna
            print("➕ Agregando columna sync_status...")
            db.session.execute(text("""
                ALTER TABLE paints 
                ADD COLUMN sync_status VARCHAR(20) DEFAULT 'synced'
            """))
            
            # Actualizar todos los registros existentes
            print("🔄 Actualizando registros existentes...")
            result = db.session.execute(text("""
                UPDATE paints 
                SET sync_status = 'synced' 
                WHERE sync_status IS NULL
            """))
            
            # Confirmar cambios
            db.session.commit()
            
            print("✅ Columna sync_status agregada exitosamente")
            print(f"📊 Registros actualizados: {result.rowcount}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al agregar columna: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Iniciando migración de base de datos...")
    success = add_sync_status_column()
    
    if success:
        print("🎉 Migración completada exitosamente")
    else:
        print("💥 Error en la migración")
        exit(1)