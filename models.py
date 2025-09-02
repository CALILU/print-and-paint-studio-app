from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' o 'user'
    experience_level = db.Column(db.String(20), default='beginner')  # 'beginner', 'intermediate', 'expert'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con los videos favoritos
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

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
    video_version = db.Column(db.Integer, default=1)  # Nombre correcto confirmado en DB
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con los favoritos
    favorites = db.relationship('Favorite', backref='video', lazy=True)
    
    # Relación con las técnicas
    techniques = db.relationship('Technique', backref='video', lazy=True, cascade='all, delete-orphan')
    
    # Restricción única compuesta
    __table_args__ = (db.UniqueConstraint('video_id', 'difficulty_level', name='video_level_uc'),)
    
    def __repr__(self):
        return f'<Video {self.title}>'

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Restricción única para evitar duplicados
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='user_video_uc'),)
    
    def __repr__(self):
        return f'<Favorite user_id={self.user_id} video_id={self.video_id}>'

class Technique(db.Model):
    __tablename__ = 'techniques'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)  # Tiempo en segundos donde comienza la técnica
    end_time = db.Column(db.Integer, nullable=False)  # Tiempo en segundos donde termina la técnica
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Technique {self.name} for video_id={self.video_id}>'
    
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con los videos
    videos = db.relationship('Video', backref='category_relation', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'     
    
class Paint(db.Model):
    __tablename__ = 'paints'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    brand = db.Column(db.Text, nullable=False)
    color_code = db.Column(db.Text)  # No unique constraint to avoid conflicts
    color_type = db.Column(db.Text)
    color_family = db.Column(db.Text)
    image_url = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    color_preview = db.Column(db.Text)
    ean = db.Column(db.String(13), unique=True, index=True)  # Campo EAN único con índice
    shelf_position = db.Column(db.Integer, nullable=True)  # Posición en estantería de venta
    # New fields temporarily disabled
    # volume = db.Column(db.Integer, nullable=True)
    # hex_color = db.Column(db.String(6), default='000000')  # Hex color field
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sync_status = db.Column(db.String(20), default='synced')  # 'synced', 'pending_upload'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert Paint object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'color_code': self.color_code,
            'color_type': self.color_type,
            'color_family': self.color_family,
            'description': self.description,
            'stock': self.stock,
            'price': self.price,
            'color_preview': self.color_preview,
            'image_url': self.image_url,
            'ean': self.ean,  # Campo EAN
            'shelf_position': self.shelf_position,  # Posición en estantería
            'sync_status': getattr(self, 'sync_status', 'synced'),  # Default to 'synced' if field doesn't exist
            # Temporarily disabled fields
            # 'volume': self.volume,
            # 'hex_color': self.hex_color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Paint {self.brand} - {self.name}>'

class PaintBackup(db.Model):
    __tablename__ = 'paints_backup'
    
    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer, nullable=False)  # ID original de la pintura
    name = db.Column(db.Text, nullable=False)
    brand = db.Column(db.Text, nullable=False)
    color_code = db.Column(db.Text)
    color_type = db.Column(db.Text)
    color_family = db.Column(db.Text)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    color_preview = db.Column(db.Text)
    image_url = db.Column(db.Text)
    # Fields for future expansion
    volume = db.Column(db.Integer, nullable=True)
    hex_color = db.Column(db.String(6), default='000000')
    original_created_at = db.Column(db.DateTime)  # Fecha original de creación
    backup_date = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha del backup
    backup_reason = db.Column(db.String(255), default='Manual backup')  # Razón del backup
    
    def to_dict(self):
        """Convert PaintBackup object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'original_id': self.original_id,
            'name': self.name,
            'brand': self.brand,
            'color_code': self.color_code,
            'color_type': self.color_type,
            'color_family': self.color_family,
            'description': self.description,
            'stock': self.stock,
            'price': self.price,
            'color_preview': self.color_preview,
            'image_url': self.image_url,
            'volume': self.volume,
            'hex_color': self.hex_color,
            'original_created_at': self.original_created_at.isoformat() if self.original_created_at else None,
            'backup_date': self.backup_date.isoformat() if self.backup_date else None,
            'backup_reason': self.backup_reason
        }
    
    def __repr__(self):
        return f'<PaintBackup {self.name} (Original ID: {self.original_id})>'

class PaintImage(db.Model):
    __tablename__ = 'paint_images'
    
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    imagen_url = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint unique para evitar duplicados
    __table_args__ = (db.UniqueConstraint('marca', 'codigo', name='unique_marca_codigo'),)
    
    def to_dict(self):
        """Convert PaintImage object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'marca': self.marca,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'imagen_url': self.imagen_url,
            'categoria': self.categoria,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<PaintImage {self.marca} - {self.codigo} - {self.nombre}>'

class PriceSource(db.Model):
    __tablename__ = 'price_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(255), nullable=False)
    store_url = db.Column(db.String(500), nullable=False)
    search_url_pattern = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    
    # Relación con el historial de precios
    price_history = db.relationship('PriceHistory', backref='source', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert PriceSource object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'store_name': self.store_name,
            'store_url': self.store_url,
            'search_url_pattern': self.search_url_pattern,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }
    
    def __repr__(self):
        return f'<PriceSource {self.store_name} - {"Active" if self.is_active else "Inactive"}>'

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    paint_id = db.Column(db.Integer, db.ForeignKey('paints.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('price_sources.id'), nullable=False)
    price = db.Column(db.Float)
    product_url = db.Column(db.Text)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    currency = db.Column(db.String(3), default='EUR')
    product_title = db.Column(db.Text)
    
    # Relación con Paint
    paint = db.relationship('Paint', backref='price_history')
    
    # Índices para mejorar rendimiento
    __table_args__ = (
        db.Index('idx_price_history_paint_id', 'paint_id'),
        db.Index('idx_price_history_source_id', 'source_id'),
        db.Index('idx_price_history_search_date', 'search_date'),
    )
    
    def to_dict(self):
        """Convert PriceHistory object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'paint_id': self.paint_id,
            'source_id': self.source_id,
            'price': self.price,
            'product_url': self.product_url,
            'search_date': self.search_date.isoformat() if self.search_date else None,
            'is_available': self.is_available,
            'currency': self.currency,
            'product_title': self.product_title,
            'source_name': self.source.store_name if self.source else None
        }
    
    def __repr__(self):
        return f'<PriceHistory Paint:{self.paint_id} Source:{self.source_id} Price:{self.price}€>'
