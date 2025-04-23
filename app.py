from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from models import db, User, Video, Favorite, Technique
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Añadir código de depuración después de crear la app Flask
@app.before_request
def debug_template_paths():
    print(f"Directorio de plantillas: {app.template_folder}")
    if hasattr(app.jinja_loader, 'searchpath'):
        print(f"Rutas de búsqueda de plantillas: {app.jinja_loader.searchpath}")
    for rule in app.url_map.iter_rules():
        print(f"Ruta: {rule}")

# Configuración de la base de datos
db_url = os.environ.get('DATABASE_URL')
print(f"Conectando a la base de datos: {db_url}")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Esto imprimirá todas las consultas SQL
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'print_and_paint_studio_key')

# Inicializar la base de datos
db.init_app(app)

# Decoradores para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas públicas
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            return redirect(url_for('admin_videos'))
        else:
            return redirect(url_for('user_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Intento de inicio de sesión: usuario={username}, contraseña={password}")
        
        user = User.query.filter_by(username=username).first()
        print(f"Usuario encontrado: {user}")
        
        if user:
            password_check = user.check_password(password)
            print(f"Resultado de verificación de contraseña: {password_check}")
            if password_check:
                session['user_id'] = user.id
                
                if user.role == 'admin':
                    return redirect(url_for('admin_videos'))
                else:
                    return redirect(url_for('user_dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        experience_level = request.form.get('experience_level', 'beginner')
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso', 'danger')
            return render_template('register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('El correo electrónico ya está registrado', 'danger')
            return render_template('register.html')
        
        # Crear nuevo usuario
        new_user = User(username=username, email=email, experience_level=experience_level, created_at=datetime.utcnow())
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

# Rutas de usuario
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user = User.query.get(session['user_id'])
    print(f"Renderizando dashboard para usuario: {user.username}")
    print(f"Intentando cargar plantilla: user/panel.html")
    try:
        return render_template('user/dashboard.html', user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla: {str(e)}")
        # Intentar con la ruta alternativa como fallback
        try:
            return render_template('user/panel.html', user=user)
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            # Si ninguna funciona, reportar el error original
            raise e

@app.route('/user/videos')
@login_required
def user_videos():
    user = User.query.get(session['user_id'])
    
    # Filtrar videos según el nivel de experiencia del usuario
    videos = Video.query.filter(Video.difficulty_level == user.experience_level).all()
    
    # Cargar técnicas para cada video
    for video in videos:
        video.techniques = Technique.query.filter_by(video_id=video.id).all()
    
    try:
        return render_template('user/videos.html', videos=videos, user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla videos: {str(e)}")
        try:
            return render_template('user/videos.html', videos=videos, user=user)
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

@app.route('/user/videos/all')
@login_required
def user_all_videos():
    videos = Video.query.all()
    user = User.query.get(session['user_id'])
    
    # Cargar técnicas para cada video
    for video in videos:
        video.techniques = Technique.query.filter_by(video_id=video.id).all()
    
    try:
        return render_template('user/videos.html', videos=videos, user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla videos all: {str(e)}")
        try:
            return render_template('user/videos.html', videos=videos, user=user)
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

@app.route('/user/favorites')
@login_required
def user_favorites():
    user = User.query.get(session['user_id'])
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    
    videos = []
    for favorite in favorites:
        video = favorite.video
        video.techniques = Technique.query.filter_by(video_id=video.id).all()
        videos.append(video)
    
    try:
        return render_template('user/favorites.html', videos=videos, user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla favoritos: {str(e)}")
        try:
            return render_template('user/favorites.html', videos=videos, user=user)
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

@app.route('/user/favorite/add/<int:video_id>', methods=['POST'])
@login_required
def add_favorite(video_id):
    user_id = session['user_id']
    
    # Verificar si ya existe el favorito
    existing_favorite = Favorite.query.filter_by(user_id=user_id, video_id=video_id).first()
    
    if existing_favorite:
        return jsonify({'status': 'error', 'message': 'El video ya está en favoritos'})
    
    # Crear nuevo favorito
    new_favorite = Favorite(user_id=user_id, video_id=video_id)
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Video añadido a favoritos'})

@app.route('/user/favorite/remove/<int:video_id>', methods=['POST'])
@login_required
def remove_favorite(video_id):
    user_id = session['user_id']
    
    favorite = Favorite.query.filter_by(user_id=user_id, video_id=video_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Video eliminado de favoritos'})
    else:
        return jsonify({'status': 'error', 'message': 'El video no está en favoritos'})

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        email = request.form.get('email')
        experience_level = request.form.get('experience_level')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Verificar si el correo ya está en uso
        if email != user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('El correo electrónico ya está registrado por otro usuario', 'danger')
                return redirect(url_for('user_profile'))
            user.email = email
        
        # Cambiar nivel de experiencia
        user.experience_level = experience_level
        
        # Cambiar contraseña si se proporciona
        if current_password and new_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                flash('Contraseña actualizada correctamente', 'success')
            else:
                flash('La contraseña actual es incorrecta', 'danger')
                return redirect(url_for('user_profile'))
        
        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('user_profile'))
    
    try:
        return render_template('user/profile.html', user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla perfil: {str(e)}")
        try:
            return render_template('user/profile.html', user=user)
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

# Rutas de administrador
@app.route('/admin/videos')
@admin_required
def admin_dashboard():
    try:
        return render_template('admin/videos.html')
    except Exception as e:
        print(f"Error al cargar la plantilla admin dashboard: {str(e)}")
        try:
            return render_template('user/admin/videos.html')
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

@app.route('/admin/videos')
@admin_required
def admin_videos():
    videos = Video.query.all()
    user = User.query.get(session['user_id'])  # Añade esta línea para obtener el usuario actual
    try:
        return render_template('admin/videos.html', videos=videos, user=user)  # Pasa user a la plantilla
    except Exception as e:
        print(f"Error al cargar la plantilla admin videos: {str(e)}")
        try:
            return render_template('user/admin/videos.html', videos=videos, user=user)  # Pasa user aquí también
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

@app.route('/admin/videos', methods=['POST'])
@admin_required
def add_video():
    try:
        data = request.json
        
        print("Datos recibidos:", data)  # Para depuración
        
        new_video = Video(
            title=data.get('title'),
            description=data.get('description'),
            video_id=data.get('video_id'),
            channel=data.get('channel'),
            category=data.get('category', 'Sin categoría'),
            technique_start_time=data.get('technique_start_time', 0),
            technique_end_time=data.get('technique_end_time'),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            published_at=data.get('published_at')
        )
        
        db.session.add(new_video)
        db.session.commit()
        
        # Añadir técnicas si se proporcionaron
        if 'techniques' in data and data['techniques']:
            for technique_data in data['techniques']:
                new_technique = Technique(
                    video_id=new_video.id,
                    name=technique_data.get('name'),
                    start_time=technique_data.get('start_time'),
                    end_time=technique_data.get('end_time')
                )
                db.session.add(new_technique)
            db.session.commit()
        
        return jsonify({
            'id': new_video.id,
            'title': new_video.title,
            'description': new_video.description,
            'video_id': new_video.video_id,
            'channel': new_video.channel,
            'category': new_video.category,
            'technique_start_time': new_video.technique_start_time,
            'technique_end_time': new_video.technique_end_time,
            'difficulty_level': new_video.difficulty_level,
            'published_at': new_video.published_at.isoformat() if new_video.published_at else None
        }), 201
    except Exception as e:
        print("Error al guardar el video:", str(e))  # Para depuración
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/videos/<int:video_id>', methods=['GET'])
@admin_required
def get_video(video_id):
    video = Video.query.get_or_404(video_id)
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'video_id': video.video_id,
        'channel': video.channel,
        'category': video.category,
        'technique_start_time': video.technique_start_time,
        'technique_end_time': video.technique_end_time,
        'difficulty_level': video.difficulty_level,
        'published_at': video.published_at.isoformat() if video.published_at else None
    })

@app.route('/admin/videos/<int:video_id>', methods=['PUT'])
@admin_required
def update_video(video_id):
    video = Video.query.get_or_404(video_id)
    data = request.json
    
    video.title = data.get('title', video.title)
    video.description = data.get('description', video.description)
    video.video_id = data.get('video_id', video.video_id)
    video.channel = data.get('channel', video.channel)
    video.category = data.get('category', video.category)
    video.technique_start_time = data.get('technique_start_time', video.technique_start_time)
    video.technique_end_time = data.get('technique_end_time', video.technique_end_time)
    video.difficulty_level = data.get('difficulty_level', video.difficulty_level)
    
    # Actualizar técnicas si se proporcionaron
    if 'techniques' in data:
        # Eliminar todas las técnicas existentes
        Technique.query.filter_by(video_id=video.id).delete()
        
        # Agregar las nuevas técnicas
        for technique_data in data['techniques']:
            new_technique = Technique(
                video_id=video.id,
                name=technique_data.get('name'),
                start_time=technique_data.get('start_time'),
                end_time=technique_data.get('end_time')
            )
            db.session.add(new_technique)
    
    db.session.commit()
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'video_id': video.video_id,
        'channel': video.channel,
        'category': video.category,
        'technique_start_time': video.technique_start_time,
        'technique_end_time': video.technique_end_time,
        'difficulty_level': video.difficulty_level,
        'published_at': video.published_at.isoformat() if video.published_at else None
    })

@app.route('/admin/videos/<int:video_id>', methods=['DELETE'])
@admin_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    # Las técnicas se eliminarán automáticamente gracias a la relación cascade
    db.session.delete(video)
    db.session.commit()
    
    return '', 204
    
# Rutas para gestionar técnicas
@app.route('/api/videos/<int:video_id>/techniques', methods=['GET'])
def get_video_techniques(video_id):
    techniques = Technique.query.filter_by(video_id=video_id).all()
    result = []
    for technique in techniques:
        result.append({
            'id': technique.id,
            'name': technique.name,
            'start_time': technique.start_time,
            'end_time': technique.end_time
        })
    return jsonify(result)

@app.route('/api/videos/<int:video_id>/techniques', methods=['POST'])
@admin_required
def add_technique(video_id):
    try:
        # Verificar que el video existe
        video = Video.query.get_or_404(video_id)
        
        data = request.json
        new_technique = Technique(
            video_id=video_id,
            name=data.get('name'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time')
        )
        
        db.session.add(new_technique)
        db.session.commit()
        
        return jsonify({
            'id': new_technique.id,
            'name': new_technique.name,
            'start_time': new_technique.start_time,
            'end_time': new_technique.end_time
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/techniques/<int:technique_id>', methods=['PUT'])
@admin_required
def update_technique(technique_id):
    technique = Technique.query.get_or_404(technique_id)
    data = request.json
    
    technique.name = data.get('name', technique.name)
    technique.start_time = data.get('start_time', technique.start_time)
    technique.end_time = data.get('end_time', technique.end_time)
    
    db.session.commit()
    
    return jsonify({
        'id': technique.id,
        'name': technique.name,
        'start_time': technique.start_time,
        'end_time': technique.end_time
    })

@app.route('/api/techniques/<int:technique_id>', methods=['DELETE'])
@admin_required
def delete_technique(technique_id):
    technique = Technique.query.get_or_404(technique_id)
    db.session.delete(technique)
    db.session.commit()
    
    return '', 204

# API para obtener videos
@app.route('/api/videos', methods=['GET'])
def get_videos():
    videos = Video.query.all()
    result = []
    for video in videos:
        # Obtener las técnicas asociadas al video
        techniques = Technique.query.filter_by(video_id=video.id).all()
        techniques_data = []
        
        for technique in techniques:
            techniques_data.append({
                'id': technique.id,
                'name': technique.name,
                'start_time': technique.start_time,
                'end_time': technique.end_time
            })
        
        result.append({
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'video_id': video.video_id,
            'channel': video.channel,
            'category': video.category,
            'technique_start_time': video.technique_start_time,
            'technique_end_time': video.technique_end_time,
            'difficulty_level': video.difficulty_level,
            'published_at': video.published_at.isoformat() if video.published_at else None,
            'techniques': techniques_data
        })
    return jsonify(result)

@app.route('/api/videos/<int:video_id>', methods=['GET'])
def api_get_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    # Obtener las técnicas asociadas al video
    techniques = Technique.query.filter_by(video_id=video.id).all()
    techniques_data = []
    
    for technique in techniques:
        techniques_data.append({
            'id': technique.id,
            'name': technique.name,
            'start_time': technique.start_time,
            'end_time': technique.end_time
        })
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'video_id': video.video_id,
        'channel': video.channel,
        'category': video.category,
        'technique_start_time': video.technique_start_time,
        'technique_end_time': video.technique_end_time,
        'difficulty_level': video.difficulty_level,
        'published_at': video.published_at.isoformat() if video.published_at else None,
        'techniques': techniques_data
    })

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    try:
        return render_template('admin/users.html', users=users)
    except Exception as e:
        print(f"Error al cargar la plantilla admin users: {str(e)}")
        try:
            return render_template('user/admin/users.html', users=users)
        except Exception as e2:
            print(f"Error con plantilla alternativa: {str(e2)}")
            raise e

@app.route('/admin/users', methods=['POST'])
@admin_required
def add_user():
    try:
        data = request.json
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')
        experience_level = data.get('experience_level', 'beginner')
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': 'El correo electrónico ya está registrado'}), 400
        
        # Crear nuevo usuario
        new_user = User(
            username=username,
            email=email,
            role=role,
            experience_level=experience_level
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'role': new_user.role,
            'experience_level': new_user.experience_level,
            'created_at': new_user.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'experience_level': user.experience_level,
        'created_at': user.created_at.isoformat()
    })

@app.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Verificar si el nuevo nombre de usuario ya existe
    if 'username' in data and data['username'] != user.username:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
        user.username = data['username']
    
    # Verificar si el nuevo email ya existe
    if 'email' in data and data['email'] != user.email:
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'El correo electrónico ya está registrado'}), 400
        user.email = data['email']
    
    # Actualizar otros campos
    if 'role' in data:
        user.role = data['role']
    
    if 'experience_level' in data:
        user.experience_level = data['experience_level']
    
    # Actualizar contraseña si se proporciona
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'experience_level': user.experience_level,
        'created_at': user.created_at.isoformat()
    })

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    # Prevenir la eliminación del propio usuario administrador
    if user_id == session.get('user_id'):
        return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return '', 204

@app.route('/debug/db', methods=['GET'])
@admin_required
def debug_db():
    """Endpoint para depuración de la base de datos"""
    try:
        # Verifica la conexión a la base de datos
        result = db.session.execute('SELECT 1').fetchone()
        db_connection = 'OK' if result else 'ERROR'
        
        # Verifica la existencia de las tablas
        tables_info = {}
        
        # Verifica la tabla videos
        try:
            result = db.session.execute('SELECT COUNT(*) FROM videos').fetchone()
            tables_info['videos'] = f'OK ({result[0]} registros)'
        except Exception as e:
            tables_info['videos'] = f'ERROR: {str(e)}'
        
        # Verifica la tabla users
        try:
            result = db.session.execute('SELECT COUNT(*) FROM users').fetchone()
            tables_info['users'] = f'OK ({result[0]} registros)'
        except Exception as e:
            tables_info['users'] = f'ERROR: {str(e)}'
        
        # Verifica la tabla favorites
        try:
            result = db.session.execute('SELECT COUNT(*) FROM favorites').fetchone()
            tables_info['favorites'] = f'OK ({result[0]} registros)'
        except Exception as e:
            tables_info['favorites'] = f'ERROR: {str(e)}'
            
        # Verifica la tabla techniques
        try:
            result = db.session.execute('SELECT COUNT(*) FROM techniques').fetchone()
            tables_info['techniques'] = f'OK ({result[0]} registros)'
        except Exception as e:
            tables_info['techniques'] = f'ERROR: {str(e)}'
        
        # Obtén los primeros 5 videos para verificar
        try:
            videos = Video.query.limit(5).all()
            sample_videos = [{
                'id': v.id,
                'title': v.title,
                'video_id': v.video_id,
                'category': v.category,
                'difficulty_level': v.difficulty_level
            } for v in videos]
        except Exception as e:
            sample_videos = f'ERROR: {str(e)}'
        
        # Obtén los primeros 5 usuarios para verificar
        try:
            users = User.query.limit(5).all()
            sample_users = [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'experience_level': u.experience_level,
                'created_at': u.created_at.isoformat() if u.created_at else None  # Asegurarse de convertir a string ISO
            } for u in users]
        except Exception as e:
            sample_users = f'ERROR: {str(e)}'
            
        # Obtén las primeras 5 técnicas para verificar
        try:
            techniques = Technique.query.limit(5).all()
            sample_techniques = [{
                'id': t.id,
                'video_id': t.video_id,
                'name': t.name,
                'start_time': t.start_time,
                'end_time': t.end_time
            } for t in techniques]
        except Exception as e:
            sample_techniques = f'ERROR: {str(e)}'
        
        debug_info = {
            'database_connection': db_connection,
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'],
            'tables': tables_info,
            'sample_videos': sample_videos,
            'sample_users': sample_users,
            'sample_techniques': sample_techniques
        }
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/reset-db', methods=['POST'])
@admin_required
def reset_db():
    """Endpoint para reiniciar la base de datos (solo para desarrollo)"""
    try:
        # Eliminar tablas
        db.drop_all()
        
        # Recrear tablas
        db.create_all()
        
        # Crear un usuario administrador por defecto
        admin = User(
            username='admin',
            email='admin@printandpaint.com',
            role='admin',
            experience_level='expert'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        return jsonify({'message': 'Base de datos reiniciada correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        print("Verificando estado de la base de datos...")
        
        # Verificar si las tablas existen o crear si es necesario
        try:
            # Intentar ver si existe algún video (esto fallará si la tabla no existe)
            db.session.execute('SELECT 1 FROM videos LIMIT 1')
            print("Tabla 'videos' existe")
        except Exception as e:
            print(f"Creando tablas en la base de datos: {str(e)}")
            db.create_all()
            print("Tablas creadas correctamente")
        
        # Verificar si existe el usuario admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creando usuario administrador...")
            admin = User(
                username='admin',
                email='admin@printandpaint.com',
                role='admin',
                experience_level='expert'
            )
            # Generar contraseña clara para depuración
            admin.set_password('admin123')
            print(f"Hash de contraseña generado: {admin.password_hash}")
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado correctamente")
        else:
            print(f"Usuario admin ya existe: {admin.username}, {admin.email}, role: {admin.role}")
            print(f"Hash actual: {admin.password_hash}")
            # Actualizar contraseña para depuración
            admin.set_password('admin123')
            print(f"Nuevo hash: {admin.password_hash}")
            db.session.commit()
            print("Contraseña de administrador actualizada para pruebas")
            
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)