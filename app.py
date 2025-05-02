from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from models import db, User, Video, Favorite, Technique, Category, Paint
from functools import wraps
import os
from datetime import datetime
from duckduckgo_search import DDGS
import random

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

# Añadir código de depuración después de crear la app Flask
@app.before_request
def debug_template_paths():
    print(f"Directorio de plantillas: {app.template_folder}")
    if hasattr(app.jinja_loader, 'searchpath'):
        print(f"Rutas de búsqueda de plantillas: {app.jinja_loader.searchpath}")
    for rule in app.url_map.iter_rules():
        print(f"Ruta: {rule}")

# Añadir esta ruta cerca de las otras rutas de API
@app.route('/api/search-images', methods=['GET'])
@admin_required
def api_search_images():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Consulta de búsqueda vacía"}), 400
    
    try:
        # Para depuración
        print(f"Iniciando búsqueda de imágenes para: {query}")
        
        # Intentar usar DuckDuckGo para buscar imágenes
        with DDGS() as ddgs:
            # Limitar a menos resultados para evitar problemas de tiempo de espera
            results = list(ddgs.images(query, safesearch='Moderate', max_results=8))
            print(f"Resultados obtenidos: {len(results)}")
        
        # Preparar resultados
        images = []
        for result in results:
            if 'image' in result and result['image']:
                images.append({
                    'url': result['image'],
                    'title': result.get('title', ''),
                    'source': result.get('url', '')
                })
        
        print(f"Imágenes procesadas: {len(images)}")
        
        # Si no se encontraron imágenes, devolver imágenes de ejemplo
        if not images:
            print("No se encontraron imágenes para la consulta")
            # Proporcionar imágenes de ejemplo si no se encontraron resultados
            placeholder_images = [
                {
                    'url': f"https://via.placeholder.com/300x200/cccccc/666666?text=No+Image+{i}",
                    'title': f"Imagen de muestra {i}",
                    'source': ""
                } for i in range(1, 5)
            ]
            
            return jsonify({"images": placeholder_images, "message": "No se encontraron imágenes. Mostrando ejemplos."})
        
        return jsonify({"images": images})
    
    except Exception as e:
        import traceback
        print(f"Error en búsqueda de imágenes: {str(e)}")
        traceback.print_exc()
        
        # Proporcionar imágenes de placeholder en caso de error
        placeholder_images = [
            {
                'url': f"https://via.placeholder.com/300x200/ffdddd/cc0000?text=Error+{i}",
                'title': f"Error en la búsqueda - Imagen {i}",
                'source': ""
            } for i in range(1, 3)
        ]
        
        return jsonify({
            "images": placeholder_images, 
            "error": str(e),
            "message": "Error al buscar imágenes. Mostrando imágenes de muestra."
        }), 200  # Devolver 200 en vez de 500 para manejar el error en el cliente 
    
# Configuración de la base de datos
db_url = os.environ.get('DATABASE_URL')
print(f"URL original de la base de datos: {db_url}")

# Verificar si la URL existe y si necesita ser modificada para SQLAlchemy
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
    print(f"URL modificada para SQLAlchemy: {db_url}")

# Si no hay URL, usar una conexión por defecto
if not db_url:
    # Para Railway, usar la URL específica que conocemos
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT') == '8080':
        db_url = 'postgresql://postgres:xGBtAyofMYhZvVxOuMbrYJHVkeQDDkGc@postgres.railway.internal:5432/railway'
        print(f"Usando URL para Railway: {db_url}")
    else:
        db_url = 'postgresql://postgres:postgres@db:5432/videos_youtube'
        print(f"Usando URL predeterminada para desarrollo local: {db_url}")

print(f"Conectando a la base de datos: {db_url}")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Esto imprimirá todas las consultas SQL
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'print_and_paint_studio_key')

# Inicializar la base de datos
db.init_app(app)

# Rutas públicas
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))  # Cambiado de admin_videos a admin_dashboard
        else:
            return redirect(url_for('user_dashboard'))
    return render_template('login.html')
# Añade esta ruta cerca de las otras rutas en tu app.py

@app.route('/health')
def health_check():
    return 'OK', 200

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
    
    # Obtener el parámetro para mostrar todos los niveles o solo el del usuario
    show_all_levels = request.args.get('show_all_levels', 'false').lower() == 'true'
    
    # Filtrar videos según el nivel de experiencia del usuario
    if show_all_levels:
        videos = Video.query.all()
    else:
        videos = Video.query.filter(Video.difficulty_level == user.experience_level).all()
    
    # Cargar técnicas para cada video
    for video in videos:
        video.techniques = Technique.query.filter_by(video_id=video.id).all()
    
    try:
        return render_template('user/videos.html', videos=videos, user=user, show_all_levels=show_all_levels)
    except Exception as e:
        print(f"Error al cargar la plantilla videos: {str(e)}")
        try:
            return render_template('user/videos.html', videos=videos, user=user, show_all_levels=show_all_levels)
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
        return render_template('user/videos.html', videos=videos, user=user, show_all_levels=True)
    except Exception as e:
        print(f"Error al cargar la plantilla videos all: {str(e)}")
        try:
            return render_template('user/videos.html', videos=videos, user=user, show_all_levels=True)
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
# A esta función
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    try:
        return render_template('admin/dashboard.html', user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla admin dashboard: {str(e)}")
        try:
            return render_template('user/admin/dashboard.html', user=user)
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

@app.route('/admin/clone-video/<int:video_id>', methods=['POST'])
@admin_required
def clone_video(video_id):
    # Obtener el video original
    original_video = Video.query.get_or_404(video_id)
    
    # Obtener el nuevo nivel de dificultad
    new_difficulty = request.form.get('difficulty_level')
    
    # Verificar que no exista ya una versión con ese nivel
    existing_version = Video.query.filter_by(
        video_id=original_video.video_id, 
        difficulty_level=new_difficulty
    ).first()
    
    if existing_version:
        flash(f'Ya existe una versión de este video para el nivel {new_difficulty}', 'danger')
        return redirect(url_for('admin_videos'))
    
    # Crear un nuevo video con los mismos datos pero diferente nivel
    new_video = Video(
        title=original_video.title,
        description=original_video.description,
        video_id=original_video.video_id,
        channel=original_video.channel,
        category=original_video.category,
        technique_start_time=original_video.technique_start_time,
        technique_end_time=original_video.technique_end_time,
        difficulty_level=new_difficulty,
        video_version=original_video.video_version + 1,  # MODIFICADO: 'video_version' en lugar de 'version'
        published_at=datetime.utcnow()
    )
    
    db.session.add(new_video)
    db.session.commit()
    
    # Redirigir a la edición del nuevo video
    flash('Video clonado correctamente. Ahora puedes personalizar esta versión.', 'success')
    return redirect(url_for('edit_video', video_id=new_video.id))

@app.route('/admin/videos', methods=['POST'])
@admin_required
def add_video():
    try:
        data = request.json
        
        print("Datos recibidos:", data)  # Para depuración
        
        # Verificar si ya existe un video con el mismo video_id y nivel de dificultad
        existing_video = Video.query.filter_by(
            video_id=data.get('video_id'),
            difficulty_level=data.get('difficulty_level', 'beginner')
        ).first()
        
        if existing_video:
            return jsonify({
                'error': 'Ya existe un video con el mismo ID de YouTube y nivel de dificultad'
            }), 400
        
        new_video = Video(
            title=data.get('title'),
            description=data.get('description'),
            video_id=data.get('video_id'),
            channel=data.get('channel'),
            category=data.get('category', 'Sin categoría'),
            category_id=data.get('category_id'),
            technique_start_time=data.get('technique_start_time', 0),
            technique_end_time=data.get('technique_end_time'),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            video_version=1,  # MODIFICADO: 'video_version' en lugar de 'version'
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
            'video_version': new_video.video_version,  # MODIFICADO: 'video_version' en lugar de 'version'
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
        'video_version': video.video_version,  # MODIFICADO: 'video_version' en lugar de 'version'
        'published_at': video.published_at.isoformat() if video.published_at else None
    })

@app.route('/admin/videos/<int:video_id>', methods=['PUT'])
@admin_required
def update_video(video_id):
    video = Video.query.get_or_404(video_id)
    data = request.json
    
    # Verificar si estamos cambiando el ID de YouTube o el nivel de dificultad
    if (data.get('video_id') != video.video_id or 
        data.get('difficulty_level') != video.difficulty_level):
        
        # Verificar si ya existe un video con ese ID y nivel
        existing_video = Video.query.filter(
            Video.id != video_id,  # Excluir el video actual
            Video.video_id == data.get('video_id'),
            Video.difficulty_level == data.get('difficulty_level')
        ).first()
        
        if existing_video:
            return jsonify({
                'error': 'Ya existe otro video con el mismo ID de YouTube y nivel de dificultad'
            }), 400
    
    video.title = data.get('title', video.title)
    video.description = data.get('description', video.description)
    video.video_id = data.get('video_id', video.video_id)
    video.channel = data.get('channel', video.channel)
    video.category = data.get('category', video.category)
    video.category_id = data.get('category_id', video.category_id)
    video.technique_start_time = data.get('technique_start_time', video.technique_start_time)
    video.technique_end_time = data.get('technique_end_time', video.technique_end_time)
    video.difficulty_level = data.get('difficulty_level', video.difficulty_level)
    video.video_version = data.get('video_version', video.video_version)  # MODIFICADO: 'video_version' en lugar de 'version'
    
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
        'video_version': video.video_version,  # MODIFICADO: 'video_version' en lugar de 'version'
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
    techniques = Technique.query.filter_by(video_id=video_id).order_by(Technique.start_time).all()
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
    try:
        videos = Video.query.all()
        result = []
        for video in videos:
            # Obtener las técnicas asociadas al video
            techniques = Technique.query.filter_by(video_id=video.id).order_by(Technique.start_time).all()
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
                'category_id': video.category_id,
                'technique_start_time': video.technique_start_time,
                'technique_end_time': video.technique_end_time,
                'difficulty_level': video.difficulty_level,
                'video_version': video.video_version,  # MODIFICADO: 'video_version' en lugar de 'version'
                'published_at': video.published_at.isoformat() if video.published_at else None,
                'techniques': techniques_data
            })
        return jsonify(result)
    except Exception as e:
        print(f"Error en get_videos(): {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/videos/<int:video_id>', methods=['GET'])
def api_get_video(video_id):
    try:
        video = Video.query.get_or_404(video_id)
        
        # Obtener las técnicas asociadas al video
        techniques = Technique.query.filter_by(video_id=video.id).order_by(Technique.start_time).all()
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
            'category_id': video.category_id,
            'technique_start_time': video.technique_start_time,
            'technique_end_time': video.technique_end_time,
            'difficulty_level': video.difficulty_level,
            'video_version': video.video_version,  # MODIFICADO: 'video_version' en lugar de 'version'
            'published_at': video.published_at.isoformat() if video.published_at else None,
            'techniques': techniques_data
        })
    except Exception as e:
        print(f"Error en api_get_video(): {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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
        
@app.route('/admin/categories')
@admin_required
def admin_categories():
    try:
        categories = Category.query.all()
        user = User.query.get(session['user_id'])
        print(f"Categorías obtenidas: {len(categories)}")
        print(f"Usuario obtenido: {user.username}")
        
        # Verificar que el archivo de plantilla existe
        import os
        template_path = os.path.join(app.template_folder, 'admin', 'categories.html')
        print(f"¿Existe la plantilla? {os.path.exists(template_path)}")
        
        return render_template('admin/categories.html', categories=categories, user=user)
    except Exception as e:
        import traceback
        print(f"Error en admin_categories: {str(e)}")
        print(traceback.format_exc())
        return f"Error: {str(e)}", 500

@app.route('/admin/categories', methods=['POST'])
@admin_required
def add_category():
    try:
        data = request.json
        
        name = data.get('name')
        description = data.get('description', '')
        
        # Verificar si la categoría ya existe
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            return jsonify({'error': 'Esta categoría ya existe'}), 400
        
        # Crear nueva categoría
        new_category = Category(
            name=name,
            description=description
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'id': new_category.id,
            'name': new_category.name,
            'description': new_category.description,
            'created_at': new_category.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/categories/<int:category_id>', methods=['GET'])
@admin_required
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'created_at': category.created_at.isoformat()
    })

@app.route('/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.json
    
    # Verificar si el nuevo nombre ya existe
    if 'name' in data and data['name'] != category.name:
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return jsonify({'error': 'Esta categoría ya existe'}), 400
        category.name = data['name']
    
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'created_at': category.created_at.isoformat()
    })

@app.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Actualizar videos que usan esta categoría
    videos_with_category = Video.query.filter_by(category_id=category_id).all()
    for video in videos_with_category:
        video.category_id = None
        video.category = 'Sin categoría'
    
    db.session.delete(category)
    db.session.commit()
    
    return '', 204

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = []
    for category in categories:
        result.append({
            'id': category.id,
            'name': category.name,
            'description': category.description
        })
    return jsonify(result)
# Rutas para la gestión de pinturas (ADMIN)
@app.route('/admin/paints')
@admin_required
def admin_paints():
    user = User.query.get(session['user_id'])
    try:
        return render_template('admin/paints.html', user=user)
    except Exception as e:
        print(f"Error al cargar la plantilla admin paints: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/api/paints', methods=['GET'])
def get_paints():
    try:
        paints = Paint.query.all()
        result = []
        for paint in paints:
            result.append({
                'id': paint.id,
                'name': paint.name,
                'brand': paint.brand,
                'color_code': paint.color_code,
                'color_type': paint.color_type,
                'color_family': paint.color_family,
                'image_url': paint.image_url,
                'stock': paint.stock,
                'price': paint.price,
                'description': paint.description,
                'color_preview': paint.color_preview,
                'created_at': paint.created_at.isoformat() if paint.created_at else None
            })
        return jsonify(result)
    except Exception as e:
        print(f"Error en get_paints(): {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/admin/paints', methods=['POST'])
@admin_required
def add_paint():
    try:
        data = request.json
        
        new_paint = Paint(
            name=data.get('name'),
            brand=data.get('brand'),
            color_code=data.get('color_code'),
            color_type=data.get('color_type'),
            color_family=data.get('color_family'),
            image_url=data.get('image_url'),
            stock=data.get('stock', 0),
            price=data.get('price'),
            description=data.get('description'),
            color_preview=data.get('color_preview')
        )
        
        db.session.add(new_paint)
        db.session.commit()
        
        return jsonify({
            'id': new_paint.id,
            'name': new_paint.name,
            'brand': new_paint.brand,
            'created_at': new_paint.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/paints/<int:paint_id>', methods=['GET'])
@admin_required
def get_paint(paint_id):
    paint = Paint.query.get_or_404(paint_id)
    return jsonify({
        'id': paint.id,
        'name': paint.name,
        'brand': paint.brand,
        'color_code': paint.color_code,
        'color_type': paint.color_type,
        'color_family': paint.color_family,
        'image_url': paint.image_url,
        'stock': paint.stock,
        'price': paint.price,
        'description': paint.description,
        'color_preview': paint.color_preview,
        'created_at': paint.created_at.isoformat() if paint.created_at else None
    })

@app.route('/admin/paints/<int:paint_id>', methods=['PUT'])
@admin_required
def update_paint(paint_id):
    paint = Paint.query.get_or_404(paint_id)
    data = request.json
    
    paint.name = data.get('name', paint.name)
    paint.brand = data.get('brand', paint.brand)
    paint.color_code = data.get('color_code', paint.color_code)
    paint.color_type = data.get('color_type', paint.color_type) 
    paint.color_family = data.get('color_family', paint.color_family)
    paint.image_url = data.get('image_url', paint.image_url)
    paint.stock = data.get('stock', paint.stock)
    paint.price = data.get('price', paint.price)
    paint.description = data.get('description', paint.description)
    paint.color_preview = data.get('color_preview', paint.color_preview)
    
    db.session.commit()
    
    return jsonify({
        'id': paint.id,
        'name': paint.name,
        'brand': paint.brand,
        'color_code': paint.color_code,
        'color_type': paint.color_type,
        'color_family': paint.color_family,
        'image_url': paint.image_url,
        'stock': paint.stock,
        'price': paint.price,
        'description': paint.description,
        'color_preview': paint.color_preview,
        'created_at': paint.created_at.isoformat() if paint.created_at else None
    })

@app.route('/admin/paints/<int:paint_id>', methods=['DELETE'])
@admin_required
def delete_paint(paint_id):
    paint = Paint.query.get_or_404(paint_id)
    db.session.delete(paint)
    db.session.commit()
    
    return '', 204

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

@app.route('/api/admin/statistics')
@admin_required
def get_admin_statistics():
    try:
        # Estadísticas de usuarios
        total_users = User.query.count()
        admin_users = User.query.filter_by(role='admin').count()
        regular_users = total_users - admin_users
        
        # Usuarios por nivel de experiencia
        beginner_users = User.query.filter_by(experience_level='beginner').count()
        intermediate_users = User.query.filter_by(experience_level='intermediate').count()
        expert_users = User.query.filter_by(experience_level='expert').count()
        
        # Estadísticas de videos
        total_videos = Video.query.count()
        
        # Videos por nivel de dificultad
        beginner_videos = Video.query.filter_by(difficulty_level='beginner').count()
        intermediate_videos = Video.query.filter_by(difficulty_level='intermediate').count()
        expert_videos = Video.query.filter_by(difficulty_level='expert').count()
        
        # Videos por categoría
        categories = db.session.query(Video.category, db.func.count(Video.id)).group_by(Video.category).all()
        categories_data = [{"name": cat[0] or "Sin categoría", "count": cat[1]} for cat in categories]
        
        # Estadísticas de favoritos
        total_favorites = Favorite.query.count()
        
        # Videos más populares (con más favoritos)
        popular_videos_query = db.session.query(
            Video.id, Video.title, db.func.count(Favorite.id).label('favorites_count')
        ).join(Favorite, Favorite.video_id == Video.id)\
        .group_by(Video.id, Video.title)\
        .order_by(db.desc('favorites_count'))\
        .limit(5)
        
        popular_videos = [
            {"id": video.id, "title": video.title, "favorites_count": video.favorites_count}
            for video in popular_videos_query
        ]
        
        return jsonify({
            "users": {
                "total": total_users,
                "admin": admin_users,
                "regular": regular_users,
                "by_level": {
                    "beginner": beginner_users,
                    "intermediate": intermediate_users,
                    "expert": expert_users
                }
            },
            "videos": {
                "total": total_videos,
                "by_level": {
                    "beginner": beginner_videos,
                    "intermediate": intermediate_videos,
                    "expert": expert_videos
                },
                "by_category": categories_data
            },
            "favorites": {
                "total": total_favorites,
                "popular_videos": popular_videos
            }
        })
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Función auxiliar para formatear duración en segundos a formato hh:mm:ss
def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

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
                'difficulty_level': v.difficulty_level,
                'video_version': v.video_version  # MODIFICADO: 'video_version' en lugar de 'version'
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
    # Este bloque solo se ejecuta en desarrollo local
    with app.app_context():
        print("Verificando estado de la base de datos...")
        try:
            db.create_all()
            print("Tablas creadas o verificadas correctamente")
            
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
        except Exception as e:
            print(f"Error al inicializar la base de datos: {str(e)}")
    
    # Para Railway, siempre usar el puerto 5000 ya que es el que espera
    port = 5000
    if not os.environ.get('RAILWAY_ENVIRONMENT'):
        # Solo en desarrollo local, usar la variable PORT
        port = int(os.environ.get('PORT', 5000))
    
    debug_mode = os.environ.get('FLASK_ENV', '') != 'production'  
    print(f"Iniciando servidor en puerto: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=False)