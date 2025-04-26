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