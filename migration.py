# migration.py
import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

print("Iniciando migración de base de datos...")

# Configuración para Railway desde entorno local (usando la URL pública)
host = 'shinkansen.proxy.rlwy.net'
port = '22933'
database = 'railway'
user = 'postgres'
password = 'xGBtAyofMYhZvVxOuMbrYJHVkeQDDkGc'

# Configurar conexión y aplicación Flask
db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
print(f"Usando URL de base de datos: {db_url}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definiciones de modelos necesarias para la migración
# Importante: Estas definiciones tienen que ser exactamente iguales a las de models.py
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    experience_level = db.Column(db.String(20), default='beginner')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    video_id = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(100))
    category = db.Column(db.String(50), default='Sin categoría')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    technique_start_time = db.Column(db.Integer, default=0)
    technique_end_time = db.Column(db.Integer)
    difficulty_level = db.Column(db.String(20), default='beginner')
    video_version = db.Column(db.Integer, default=1)
    published_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Technique(db.Model):
    __tablename__ = 'techniques'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relación con los videos
    videos = db.relationship('Video', backref='category_relation', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

def migrate():
    with app.app_context():
        try:
            # Crear las nuevas tablas
            print("Creando tablas si no existen...")
            db.create_all()
            print("Tablas creadas correctamente.")
            
            # Verificar si la tabla 'categories' ya tiene registros
            categories_count = Category.query.count()
            print(f"La tabla 'categories' tiene {categories_count} registros.")
            
            # Crear algunas categorías predeterminadas si no hay ninguna
            if categories_count == 0:
                print("Creando categorías predeterminadas...")
                default_categories = [
                    Category(name="Pintura Base", description="Técnicas fundamentales de pintura"),
                    Category(name="Sombreado", description="Técnicas de sombreado y volumen"),
                    Category(name="Iluminación", description="Técnicas de iluminación y resaltado"),
                    Category(name="Detalles", description="Trabajo detallado y acabados"),
                    Category(name="Efectos Especiales", description="Efectos como fuego, agua, etc."),
                    Category(name="Barnizado", description="Técnicas de acabado y protección"),
                    Category(name="Peanas", description="Creación y decoración de peanas"),
                    Category(name="Otros", description="Otras técnicas y consejos")
                ]
                
                for category in default_categories:
                    db.session.add(category)
                
                db.session.commit()
                print(f"Se han creado {len(default_categories)} categorías predeterminadas.")
            
            # Actualizar videos existentes para asignar categorías basadas en el campo 'category'
            print("Actualizando videos existentes...")
            videos = Video.query.all()
            updated_count = 0
            
            for video in videos:
                if video.category and video.category_id is None:
                    # Buscar categoría por nombre
                    category = Category.query.filter_by(name=video.category).first()
                    if category:
                        video.category_id = category.id
                        updated_count += 1
                    else:
                        # Si no existe la categoría con ese nombre exacto, buscar si contiene el nombre
                        all_categories = Category.query.all()
                        for cat in all_categories:
                            if cat.name.lower() in video.category.lower():
                                video.category_id = cat.id
                                updated_count += 1
                                break
            
            if updated_count > 0:
                db.session.commit()
                print(f"Se actualizaron {updated_count} videos con sus respectivas categorías.")
            else:
                print("No se encontraron videos para actualizar.")
            
            print("Migración completada con éxito.")
            return True
            
        except Exception as e:
            print(f"Error durante la migración: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

# Función alternativa que usa psycopg2 directamente (similar a youtube_scraper_csv.py)
def create_categories_using_psycopg2():
    try:
        print(f"Conectando a la base de datos directamente: {host}:{port}/{database}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("Conexión establecida exitosamente")
        
        cur = conn.cursor()
        
        # Verificar si la tabla categories existe
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categories')")
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("Creando tabla categories...")
            cur.execute('''
                CREATE TABLE categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    description VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Tabla categories creada exitosamente")
        else:
            print("La tabla categories ya existe")
        
        # Verificar si hay categorías
        cur.execute("SELECT COUNT(*) FROM categories")
        categories_count = cur.fetchone()[0]
        print(f"La tabla categories tiene {categories_count} registros")
        
        if categories_count == 0:
            # Insertar categorías predeterminadas
            print("Insertando categorías predeterminadas...")
            categories = [
                ("Pintura Base", "Técnicas fundamentales de pintura"),
                ("Sombreado", "Técnicas de sombreado y volumen"),
                ("Iluminación", "Técnicas de iluminación y resaltado"),
                ("Detalles", "Trabajo detallado y acabados"),
                ("Efectos Especiales", "Efectos como fuego, agua, etc."),
                ("Barnizado", "Técnicas de acabado y protección"),
                ("Peanas", "Creación y decoración de peanas"),
                ("Otros", "Otras técnicas y consejos")
            ]
            
            for name, description in categories:
                cur.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)",
                    (name, description)
                )
            
            print(f"Se han insertado {len(categories)} categorías predeterminadas")
            
        # Verificar si videos tiene la columna category_id
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'videos' AND column_name = 'category_id'
            )
        """)
        column_exists = cur.fetchone()[0]
        
        if not column_exists:
            print("Añadiendo columna category_id a la tabla videos...")
            cur.execute("ALTER TABLE videos ADD COLUMN category_id INTEGER REFERENCES categories(id)")
            print("Columna category_id añadida exitosamente")
        else:
            print("La columna category_id ya existe en la tabla videos")
        
        # Actualizar videos existentes
        print("Actualizando videos existentes...")
        cur.execute("SELECT id, category FROM videos WHERE category_id IS NULL AND category IS NOT NULL")
        videos = cur.fetchall()
        
        updated_count = 0
        for video_id, category in videos:
            # Intentar encontrar una categoría que coincida
            cur.execute("SELECT id FROM categories WHERE name = %s", (category,))
            category_match = cur.fetchone()
            
            if category_match:
                category_id = category_match[0]
                cur.execute("UPDATE videos SET category_id = %s WHERE id = %s", (category_id, video_id))
                updated_count += 1
            else:
                # Intentar encontrar una categoría que contenga el nombre
                cur.execute("SELECT id, name FROM categories")
                all_categories = cur.fetchall()
                for cat_id, cat_name in all_categories:
                    if cat_name.lower() in category.lower():
                        cur.execute("UPDATE videos SET category_id = %s WHERE id = %s", (cat_id, video_id))
                        updated_count += 1
                        break
        
        if updated_count > 0:
            print(f"Se actualizaron {updated_count} videos con sus respectivas categorías")
        else:
            print("No se encontraron videos para actualizar")
        
        # Cerrar la conexión
        cur.close()
        conn.close()
        
        print("Migración directa completada con éxito")
        return True
        
    except Exception as e:
        print(f"Error durante la migración directa: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Intentando migrar usando SQLAlchemy...")
    success = migrate()
    
    if not success:
        print("La migración con SQLAlchemy falló. Intentando método alternativo...")
        success = create_categories_using_psycopg2()
    
    sys.exit(0 if success else 1)