from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from models import db, User, Video, Favorite, Technique, Category, Paint, PaintBackup, PaintImage
from functools import wraps
import os
from datetime import datetime, timedelta
import random
from duckduckgo_search import DDGS
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Añadir código de depuración después de crear las app Flask
@app.before_request
def debug_template_paths():
    print(f"Directorio de plantillas: {app.template_folder}")
    if hasattr(app.jinja_loader, 'searchpath'):
        print(f"Rutas de búsqueda de plantillas: {app.jinja_loader.searchpath}")
    for rule in app.url_map.iter_rules():
        print(f"Ruta: {rule}") 
      

# Configuración de la base de datos
db_url = os.environ.get('DATABASE_URL')
print(f"URL original de la base de datos: {db_url}")

# Verificar si la URL existe y si necesita ser modificadas para SQLAlchemy
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
app.config['SQLALCHEMY_ECHO'] = False  # Desactivar logging SQL para mejorar rendimiento
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'print_and_paint_studio_key')

# Optimizaciones de conexión para Railway PostgreSQL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,           # Número de conexiones en el pool
    'pool_timeout': 20,       # Timeout para obtener conexión del pool
    'pool_recycle': 300,      # Reciclar conexiones cada 5 minutos
    'max_overflow': 10,       # Conexiones adicionales si el pool está lleno
    'pool_pre_ping': True,    # Verificar conexiones antes de usarlas
}

# Inicializar la base de datos
db.init_app(app)

# Sistema de cache simple para optimizar consultas frecuentes
from functools import wraps
import time

paint_cache = {}
CACHE_TIMEOUT = 300  # 5 minutos

def clear_paint_cache(paint_id=None):
    """Limpiar caché de pintura específica o todo el caché"""
    if paint_id:
        cache_key = f"paint_{paint_id}"
        if cache_key in paint_cache:
            del paint_cache[cache_key]
            print(f"🗑️ Cache cleared para paint_id: {paint_id}")
    else:
        paint_cache.clear()
        print("🗑️ Cache completamente limpiado")

def cache_paint_result(timeout=CACHE_TIMEOUT):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generar clave de cache - obtener paint_id de kwargs si está disponible
            paint_id = kwargs.get('paint_id') or (args[0] if args else 'all')
            cache_key = f"paint_{paint_id}"
            current_time = time.time()
            
            print(f"🔍 Cache check para paint_id: {paint_id}, cache_key: {cache_key}")
            
            # Verificar si existe en cache y no ha expirado
            if cache_key in paint_cache:
                cached_data, cached_time = paint_cache[cache_key]
                if current_time - cached_time < timeout:
                    print(f"📦 Cache HIT para {cache_key}")
                    return cached_data
            
            # Ejecutar función y cachear resultado
            print(f"💾 Cache MISS para {cache_key} - ejecutando función")
            result = f(*args, **kwargs)
            paint_cache[cache_key] = (result, current_time)
            print(f"💾 Resultado cacheado para {cache_key}")
            
            return result
        return decorated_function
    return decorator

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
        import time
        start_time = time.time()
        
        if 'user_id' not in session:
            print(f"🚫 admin_required: No user_id in session after {time.time() - start_time:.3f}s")
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        auth_time = time.time() - start_time
        
        if not user or user.role != 'admin':
            print(f"🚫 admin_required: User {session.get('user_id')} not admin after {auth_time:.3f}s")
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
            return redirect(url_for('user_dashboard'))
        
        print(f"✅ admin_required: User {user.username} authenticated in {auth_time:.3f}s")
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/proxy/image')
def proxy_image():
    """Proxy para imágenes externas que bloquean hotlinking"""
    url = request.args.get('url')
    if not url:
        return 'URL parameter is required', 400
    
    # Validar dominios permitidos para evitar abuso
    allowed_domains = ['scale75.com', 'goblintrader.com', 'vallejo.es']
    if not any(domain in url for domain in allowed_domains):
        return 'Domain not allowed', 403
    
    print(f"Proxy request for: {url}")
    
    # Lista de User-Agents para rotar
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    import random
    selected_ua = random.choice(user_agents)
    
    # Intentar múltiples estrategias con diferentes enfoques
    strategies = [
        # Estrategia 1: Simular navegación directa a la imagen
        {
            'User-Agent': selected_ua,
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://scale75.com/',
            'Origin': 'https://scale75.com',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        # Estrategia 2: Simular visita desde buscador
        {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        },
        # Estrategia 3: Headers básicos de navegador
        {
            'User-Agent': selected_ua,
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        # Estrategia 4: Headers mínimos
        {
            'User-Agent': selected_ua,
            'Accept': '*/*',
        },
        # Estrategia 5: Curl-like headers
        {
            'User-Agent': 'curl/7.68.0',
            'Accept': '*/*',
        }
    ]
    
    for i, headers in enumerate(strategies):
        try:
            print(f"Trying strategy {i+1} for {url}")
            
            # Delay entre intentos para evitar rate limiting
            if i > 0:
                time.sleep(1)
            
            # Configurar sesión con timeout extendido
            session = requests.Session()
            session.headers.update(headers)
            
            # Configurar adaptador con reintentos
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # Hacer la petición
            response = session.get(
                url, 
                timeout=20, 
                stream=True,
                allow_redirects=True,
                verify=True
            )
            
            print(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            # Obtener el tipo de contenido
            content_type = response.headers.get('content-type', 'image/jpeg')
            print(f"Content-Type: {content_type}")
            
            # Verificar que es realmente una imagen
            if not content_type.startswith('image/'):
                print(f"Not an image, Content-Type: {content_type}")
                continue
            
            # Crear respuesta con la imagen
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            print(f"Successfully proxied image from {url}")
            return app.response_class(
                generate(),
                mimetype=content_type,
                headers={
                    'Cache-Control': 'public, max-age=3600',  # Cache por 1 hora
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )
            
        except requests.exceptions.RequestException as e:
            print(f"Strategy {i+1} failed: {e}")
            continue
        except Exception as e:
            print(f"Strategy {i+1} unexpected error: {e}")
            continue
    
    # Si todas las estrategias fallan, devolver placeholder
    print(f"All strategies failed for {url}")
    placeholder_svg = f"""<svg width="150" height="150" xmlns="http://www.w3.org/2000/svg">
        <rect width="150" height="150" fill="#f8f9fa" stroke="#dee2e6"/>
        <text x="50%" y="40%" font-size="12" fill="#6c757d" text-anchor="middle" dy=".3em">Image Error</text>
        <text x="50%" y="60%" font-size="10" fill="#6c757d" text-anchor="middle" dy=".3em">Scale75</text>
    </svg>"""
    
    return placeholder_svg, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/proxy/aggressive')
def proxy_aggressive():
    """Proxy agresivo que simula navegación completa"""
    url = request.args.get('url')
    if not url:
        return 'URL parameter is required', 400
    
    # Validar dominios permitidos
    allowed_domains = ['scale75.com', 'goblintrader.com', 'vallejo.es']
    if not any(domain in url for domain in allowed_domains):
        return 'Domain not allowed', 403
    
    print(f"Aggressive proxy request for: {url}")
    
    try:
        # Crear sesión persistente
        session = requests.Session()
        
        # Headers que imitan navegación real
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        # Paso 1: Visitar la página principal para establecer cookies
        print("Step 1: Visiting main page to establish session")
        base_url = 'https://scale75.com/'
        main_response = session.get(base_url, timeout=10)
        print(f"Main page response: {main_response.status_code}")
        
        # Paso 2: Simular navegación a una página de producto
        print("Step 2: Simulating product page navigation")
        session.headers.update({
            'Referer': base_url,
            'Sec-Fetch-Site': 'same-origin',
        })
        
        # Extraer ID del producto de la URL
        import re
        product_match = re.search(r'/(\d+)-', url)
        if product_match:
            product_id = product_match.group(1)
            # Simular visita a página del producto
            product_url = f"https://scale75.com/en/shop/{product_id}-product.html"
            try:
                product_response = session.get(product_url, timeout=10)
                print(f"Product page response: {product_response.status_code}")
            except:
                print("Product page visit failed, continuing...")
        
        # Paso 3: Solicitar la imagen con contexto completo
        print("Step 3: Requesting image with full context")
        session.headers.update({
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Referer': base_url,
        })
        
        # Petición final de la imagen
        response = session.get(url, timeout=15, stream=True)
        print(f"Image response: {response.status_code}")
        response.raise_for_status()
        
        # Verificar que es una imagen
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ValueError(f"Not an image: {content_type}")
        
        # Devolver imagen
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        print(f"Successfully proxied image with aggressive method: {url}")
        return app.response_class(
            generate(),
            mimetype=content_type,
            headers={
                'Cache-Control': 'public, max-age=7200',  # Cache por 2 horas
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        print(f"Aggressive proxy failed: {e}")
        # Devolver placeholder
        placeholder_svg = f"""<svg width="150" height="150" xmlns="http://www.w3.org/2000/svg">
            <rect width="150" height="150" fill="#fff3cd" stroke="#ffeaa7"/>
            <text x="50%" y="40%" font-size="12" fill="#856404" text-anchor="middle" dy=".3em">Aggressive Failed</text>
            <text x="50%" y="60%" font-size="10" fill="#856404" text-anchor="middle" dy=".3em">Scale75</text>
        </svg>"""
        return placeholder_svg, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/proxy/head')
def proxy_head():
    """Hace una petición HEAD para verificar si la imagen existe"""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    # Validar dominios permitidos
    allowed_domains = ['scale75.com', 'goblintrader.com', 'vallejo.es']
    if not any(domain in url for domain in allowed_domains):
        return jsonify({'error': 'Domain not allowed'}), 403
    
    try:
        # Headers básicos para petición HEAD
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://scale75.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        # Petición HEAD rápida
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        
        return jsonify({
            'url': url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'accessible': response.status_code == 200,
            'content_type': response.headers.get('content-type', 'unknown'),
            'content_length': response.headers.get('content-length', 'unknown')
        })
        
    except Exception as e:
        return jsonify({
            'url': url,
            'error': str(e),
            'accessible': False
        })

@app.route('/proxy/test')
def test_proxy():
    """Endpoint para probar URLs específicas y ver qué está pasando"""
    url = request.args.get('url')
    if not url:
        return 'URL parameter is required', 400
    
    print(f"Testing URL: {url}")
    
    try:
        # Hacer una petición simple para ver la respuesta
        response = requests.get(url, timeout=10)
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content_type': response.headers.get('content-type', 'unknown'),
            'content_length': len(response.content),
            'accessible': response.status_code == 200
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'url': url,
            'error': str(e),
            'accessible': False
        })

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
            try:
                # Use the to_dict method if available, otherwise manual construction
                if hasattr(paint, 'to_dict'):
                    paint_dict = paint.to_dict()
                else:
                    # Fallback for backwards compatibility
                    paint_dict = {
                        'id': paint.id,
                        'name': paint.name or '',
                        'brand': paint.brand or '',
                        'color_code': paint.color_code or '',
                        'color_type': getattr(paint, 'color_type', '') or '',
                        'color_family': getattr(paint, 'color_family', '') or '',
                        'image_url': getattr(paint, 'image_url', '') or '',
                        'stock': getattr(paint, 'stock', 0) or 0,
                        'price': getattr(paint, 'price', 0.0) or 0.0,
                        'description': getattr(paint, 'description', '') or '',
                        'color_preview': getattr(paint, 'color_preview', '#000000') or '#000000',
                        'sync_status': getattr(paint, 'sync_status', 'synced'),  # Default to 'synced'
                        'created_at': paint.created_at.isoformat() if paint.created_at else None
                    }
                result.append(paint_dict)
            except Exception as paint_error:
                print(f"Error processing paint {paint.id}: {str(paint_error)}")
                # Skip this paint but continue with others
                continue
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
@cache_paint_result(timeout=300)  # Cache por 5 minutos
@admin_required
def get_paint(paint_id):
    import time
    from flask import g
    
    start_time = time.time()
    print(f"🔍 GET /admin/paints/{paint_id} - Iniciando búsqueda...")
    
    try:
        # Optimización 1: Usar query más específica con only() para reducir datos transferidos
        paint = db.session.query(Paint).filter_by(id=paint_id).first()
        
        if not paint:
            print(f"❌ Pintura {paint_id} no encontrada")
            return jsonify({'error': 'Pintura no encontrada'}), 404
        
        query_time = time.time() - start_time
        print(f"✅ Pintura {paint_id} encontrada en {query_time:.3f}s")
        
        # Optimización 2: Construir respuesta más eficientemente
        response_data = {
            'id': paint.id,
            'name': paint.name or '',
            'brand': paint.brand or '',
            'color_code': paint.color_code or '',
            'color_type': paint.color_type or '',
            'color_family': paint.color_family or '',
            'image_url': paint.image_url or '',
            'stock': paint.stock or 0,
            'price': float(paint.price) if paint.price else 0.0,
            'description': paint.description or '',
            'color_preview': paint.color_preview or '#cccccc',
            'created_at': paint.created_at.isoformat() if paint.created_at else None
        }
        
        total_time = time.time() - start_time
        print(f"📤 Respuesta enviada en {total_time:.3f}s total")
        
        # Optimización 3: Cerrar explícitamente la sesión
        db.session.close()
        
        return jsonify(response_data)
        
    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ Error en get_paint después de {error_time:.3f}s: {str(e)}")
        db.session.rollback()
        db.session.close()
        return jsonify({'error': 'Error interno del servidor'}), 500

# Endpoint para limpiar caché (útil para debugging)
@app.route('/admin/clear-cache/<int:paint_id>', methods=['POST'])
@admin_required
def clear_cache_endpoint(paint_id):
    clear_paint_cache(paint_id)
    return jsonify({'status': 'success', 'message': f'Cache cleared for paint {paint_id}'})

@app.route('/admin/paints/<int:paint_id>', methods=['PUT'])
@admin_required
def update_paint(paint_id):
    paint = Paint.query.get_or_404(paint_id)
    data = request.json
    
    # Guardar el stock anterior para comparar
    old_stock = paint.stock
    
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
    
    # Enviar notificación push a Android si el stock cambió
    try:
        if 'stock' in data and data.get('stock') != old_stock:
            send_android_notification(paint_id, 'stock_updated', {
                'paint_id': paint.id,
                'paint_name': paint.name,
                'paint_code': paint.color_code,
                'brand': paint.brand,
                'old_stock': old_stock,
                'new_stock': paint.stock,
                'source': 'web_admin'
            })
            print(f"🔔 Notification sent to Android for stock update: {paint.name} (Stock: {old_stock} → {paint.stock})")
    except Exception as e:
        print(f"⚠️ Failed to send Android notification: {str(e)}")
    
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

# Endpoints para gestión de pinturas por video
@app.route('/api/videos/<int:video_id>/paints', methods=['GET'])
def get_video_paints(video_id):
    try:
        # Verificar que el video existe
        video = Video.query.get_or_404(video_id)
        
        # Obtener pinturas asociadas al video usando SQL directo
        query = """
        SELECT p.id, p.name, p.brand, p.color_code, p.color_preview, p.description, p.color_type, p.color_family
        FROM paints p
        INNER JOIN video_paints vp ON p.id = vp.paint_id
        WHERE vp.video_id = :video_id
        ORDER BY p.name
        """
        
        result = db.session.execute(query, {'video_id': video_id})
        paints = result.fetchall()
        
        paint_list = []
        for paint in paints:
            paint_list.append({
                'id': paint[0],
                'name': paint[1],
                'brand': paint[2],
                'color_code': paint[3],
                'color_preview': paint[4],
                'description': paint[5],
                'color_type': paint[6],
                'color_family': paint[7]
            })
        
        return jsonify(paint_list)
        
    except Exception as e:
        print(f"Error en get_video_paints: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<int:video_id>/paints', methods=['POST'])
@admin_required
def save_video_paints(video_id):
    try:
        # Verificar que el video existe
        video = Video.query.get_or_404(video_id)
        
        data = request.get_json()
        paint_ids = data.get('paint_ids', [])
        
        # Eliminar asociaciones existentes
        delete_query = "DELETE FROM video_paints WHERE video_id = :video_id"
        db.session.execute(delete_query, {'video_id': video_id})
        
        # Insertar nuevas asociaciones
        if paint_ids:
            for paint_id in paint_ids:
                # Verificar que la pintura existe
                paint = Paint.query.get(paint_id)
                if paint:
                    insert_query = "INSERT INTO video_paints (video_id, paint_id) VALUES (:video_id, :paint_id)"
                    db.session.execute(insert_query, {'video_id': video_id, 'paint_id': paint_id})
        
        db.session.commit()
        
        return jsonify({
            'message': 'Pinturas asociadas correctamente',
            'video_id': video_id,
            'paint_count': len(paint_ids)
        })
        
    except Exception as e:
        print(f"Error en save_video_paints: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

# Modificar/Añadir estas funciones en app.py  
@app.route('/save-to-db', methods=['POST'])
@admin_required
def save_to_db():
    """Guardar una URL de imagen en la base de datos local"""
    try:
        data = request.json
        brand = data.get('brand')
        color_code = data.get('color_code')
        image_url = data.get('image_url')
        
        if not all([brand, color_code, image_url]):
            return jsonify({"success": False, "error": "Faltan datos requeridos"})
        
        # En una implementación real, guardarías esto en una base de datos
        # Aquí simplemente devolvemos éxito
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al guardar en la base de datos: {str(e)}"})

# ====================================================
# PAINT MANAGEMENT ENDPOINTS FOR ANDROID APP
# ====================================================

# Configuración API Key para Android
API_KEY = os.environ.get('API_KEY', 'print_and_paint_secret_key_2025')

# ⭐ ENDPOINT CRÍTICO - POST /api/paints para Android
@app.route('/api/paints', methods=['POST'])
def create_paint_android():
    """Create paint from Android app - CRITICAL ENDPOINT"""
    try:
        # Verificar API key
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({
                "success": False,
                "data": None,
                "message": "Invalid or missing API key"
            }), 401
        
        # Validar datos JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "data": None,
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        
        # Log básico para debugging
        print(f"📥 POST /api/paints - Received data from Android")
        
        # Validar campos requeridos (validación simple como antes)
        required_fields = ['name', 'brand', 'color_code']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return jsonify({
                "success": False,
                "data": None,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Verificar si ya existe una pintura con ese código
        existing_paint = Paint.query.filter_by(color_code=data['color_code']).first()
        if existing_paint:
            return jsonify({
                "success": False,
                "data": {
                    "id": existing_paint.id,
                    "name": existing_paint.name,
                    "brand": existing_paint.brand,
                    "color_code": existing_paint.color_code
                },
                "message": f"Paint with code {data['color_code']} already exists"
            }), 409
        
        # Crear nueva pintura
        new_paint = Paint(
            name=data['name'],
            brand=data['brand'],
            color_code=data['color_code'],
            color_type=data.get('color_type', 'Acrílica'),
            color_family=data.get('color_family', 'Base'),
            description=data.get('description', ''),
            stock=data.get('stock', 1),
            price=data.get('price', 0.0),
            color_preview=data.get('color_preview', '#757575'),
            image_url=data.get('image_url', ''),
            created_at=datetime.utcnow()
        )
        
        # Guardar en base de datos
        db.session.add(new_paint)
        db.session.commit()
        
        # Retornar respuesta para Android
        return jsonify({
            "success": True,
            "data": {
                "id": new_paint.id,
                "color_code": new_paint.color_code,
                "name": new_paint.name,
                "brand": new_paint.brand,
                "remote_id": new_paint.id  # Para sincronización Android
            },
            "message": f"Paint {new_paint.color_code} created successfully"
        }), 201
        
    except Exception as e:
        print(f"Error en create_paint_android(): {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error creating paint: {str(e)}"
        }), 500

# ⭐ ENDPOINT CRÍTICO - PUT /api/paints/{id} para Android
@app.route('/api/paints/<int:id>', methods=['PUT'])
def update_paint_android(id):
    """Update existing paint from Android app - CRITICAL ENDPOINT"""
    try:
        # Verificar API key
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({
                "success": False,
                "data": None,
                "message": "Invalid or missing API key"
            }), 401
        
        # Validar datos JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "data": None,
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        
        # Buscar la pintura existente
        paint = Paint.query.get(id)
        if not paint:
            return jsonify({
                "success": False,
                "data": None,
                "message": f"Paint with id {id} not found"
            }), 404
        
        # Actualizar campos enviados
        if 'name' in data:
            paint.name = data['name']
        if 'brand' in data:
            paint.brand = data['brand']
        if 'color_code' in data:
            new_color_code = data['color_code']
            # Para actualizaciones desde Android, ignorar color_code si está vacío o es problemático
            if not new_color_code or new_color_code.strip() == "" or new_color_code == "0":
                print(f"⚠️ Ignoring invalid/empty color_code in update for paint {id}")
            elif paint.color_code != new_color_code:
                # Solo verificar duplicados si el código realmente está cambiando
                existing = Paint.query.filter(Paint.color_code == new_color_code, Paint.id != id).first()
                if existing:
                    return jsonify({
                        "success": False,
                        "data": None,
                        "message": f"Another paint with code {new_color_code} already exists"
                    }), 409
                paint.color_code = new_color_code
                print(f"🔄 Color code updated for paint {id}: {paint.color_code} → {new_color_code}")
            else:
                print(f"✅ Color code unchanged for paint {id}: {paint.color_code}")
        if 'color_type' in data:
            paint.color_type = data['color_type']
        if 'color_family' in data:
            paint.color_family = data['color_family']
        if 'description' in data:
            paint.description = data['description']
        if 'stock' in data:
            # Android envía el stock como valor absoluto, no como incremento
            # Para actualizaciones desde Android, reemplazar el stock completamente
            new_stock = data['stock']
            old_stock = paint.stock if paint.stock is not None else 0
            paint.stock = new_stock
            print(f"🔄 Stock replaced: {old_stock} → {new_stock} for paint {paint.name} (ID: {id})")
        if 'price' in data:
            paint.price = data['price']
        if 'color_preview' in data:
            paint.color_preview = data['color_preview']
        if 'image_url' in data:
            paint.image_url = data['image_url']
        if 'ean' in data:
            paint.ean = data['ean']
        if 'volume' in data:
            # Handle volume field (can be null)
            volume_value = data['volume']
            if volume_value is not None and volume_value != "":
                try:
                    paint.volume = int(volume_value)
                except (ValueError, TypeError):
                    print(f"Invalid volume value: {volume_value}, keeping existing")
            else:
                paint.volume = None  # Allow null volumes
        
        # Actualizar fecha de modificación
        paint.updated_at = datetime.utcnow()
        
        # 📱 Marcar como modificado desde Android para mostrar en galería web
        if hasattr(paint, 'sync_status'):
            paint.sync_status = 'pending_upload'
        
        # Guardar cambios
        db.session.commit()
        
        # Enviar notificación push a Android si el stock cambió (desde aplicación externa como nuestro script de testing)
        try:
            if 'stock' in data and data.get('stock') != old_stock:
                send_android_notification(id, 'stock_updated', {
                    'paint_id': paint.id,
                    'paint_name': paint.name,
                    'paint_code': paint.color_code,
                    'brand': paint.brand,
                    'old_stock': old_stock,
                    'new_stock': paint.stock,
                    'source': 'external_api'
                })
                print(f"📱 Android notification sent: {paint.name} stock {old_stock} → {paint.stock}")
        except Exception as e:
            print(f"⚠️ Failed to send Android notification: {str(e)}")
        
        # Retornar respuesta para Android
        return jsonify({
            "success": True,
            "data": {
                "id": paint.id,
                "name": paint.name,
                "brand": paint.brand,
                "color_code": paint.color_code,
                "color_type": paint.color_type,
                "color_family": paint.color_family,
                "image_url": paint.image_url,
                "stock": paint.stock,
                "price": paint.price,
                "description": paint.description,
                "color_preview": paint.color_preview,
                "created_at": paint.created_at.isoformat() if paint.created_at else None,
                "updated_at": paint.updated_at.isoformat() if paint.updated_at else None,
                "remote_id": paint.id  # Para sincronización Android
            },
            "message": f"Paint {paint.color_code} updated successfully"
        }), 200
        
    except Exception as e:
        print(f"Error en update_paint_android(): {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error updating paint: {str(e)}"
        }), 500

# Endpoint para búsqueda por código específico
@app.route('/api/paints/<color_code>', methods=['GET'])
def get_paint_by_code_android(color_code):
    """Get specific paint by color code for Android"""
    try:
        # Verificar API key
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({
                "success": False,
                "data": None,
                "message": "Invalid or missing API key"
            }), 401
        
        paint = Paint.query.filter_by(color_code=color_code).first()
        
        if paint:
            paint_data = {
                'id': paint.id,
                'name': paint.name,
                'brand': paint.brand,
                'color_code': paint.color_code,
                'color_type': paint.color_type,
                'color_family': paint.color_family,
                'description': paint.description,
                'stock': paint.stock,
                'price': paint.price,
                'color_preview': paint.color_preview,
                'image_url': paint.image_url,
                'created_at': paint.created_at.isoformat() if paint.created_at else None
            }
            return jsonify({
                "success": True,
                "data": paint_data,
                "message": f"Paint {color_code} found"
            }), 200
        else:
            return jsonify({
                "success": False,
                "data": None,
                "message": f"Paint with code {color_code} not found"
            }), 404
            
    except Exception as e:
        print(f"Error en get_paint_by_code_android(): {str(e)}")
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error retrieving paint: {str(e)}"
        }), 500

# Upload image endpoint for Android
@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload image file from Android app"""
    try:
        # Verify API key
        api_key = request.headers.get('X-API-Key')
        if api_key != 'print_and_paint_secret_key_2025':
            return jsonify({
                "success": False,
                "data": None,
                "message": "Invalid or missing API key"
            }), 401
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "data": None,
                "message": "No image file provided"
            }), 400
        
        file = request.files['image']
        paint_id = request.form.get('paint_id')
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "data": None,
                "message": "No file selected"
            }), 400
        
        if file and allowed_file(file.filename):
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"paint_{paint_id}_{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(upload_dir, filename)
            
            # Save file
            file.save(filepath)
            
            # Generate URL for web access
            image_url = f"/static/uploads/{filename}"
            
            # Update paint record if paint_id provided
            if paint_id:
                paint = Paint.query.get(paint_id)
                if paint:
                    paint.image_url = image_url
                    paint.updated_at = datetime.utcnow()
                    db.session.commit()
            
            return jsonify({
                "success": True,
                "data": {
                    "image_url": image_url,
                    "filename": filename
                },
                "message": "Image uploaded successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "data": None,
                "message": "Invalid file type. Only JPG, PNG, GIF allowed"
            }), 400
            
    except Exception as e:
        print(f"Error in upload_image(): {str(e)}")
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error uploading image: {str(e)}"
        }), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Debug page for images
@app.route('/debug/images')
def debug_images_page():
    """Debug page to visualize image URLs"""
    return render_template('debug_images.html')

# Debug endpoint to check image URLs
@app.route('/api/debug/images', methods=['GET'])
def debug_images():
    """Debug endpoint to check which paints have image URLs"""
    try:
        paints = Paint.query.all()
        
        debug_data = []
        for paint in paints:
            debug_data.append({
                "id": paint.id,
                "name": paint.name,
                "brand": paint.brand,
                "color_code": paint.color_code,
                "image_url": paint.image_url,
                "has_image_url": paint.image_url is not None and paint.image_url != "",
                "created_at": paint.created_at.isoformat() if paint.created_at else None
            })
        
        # Estadísticas
        total_paints = len(debug_data)
        with_images = len([p for p in debug_data if p["has_image_url"]])
        without_images = total_paints - with_images
        
        return jsonify({
            "success": True,
            "data": {
                "paints": debug_data,
                "stats": {
                    "total_paints": total_paints,
                    "with_images": with_images,
                    "without_images": without_images,
                    "percentage_with_images": round((with_images / total_paints * 100) if total_paints > 0 else 0, 2)
                }
            },
            "message": f"Debug data for {total_paints} paints"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error retrieving debug data: {str(e)}"
        }), 500

# Health check específico para Android
@app.route('/api/health', methods=['GET'])
def health_check_android():
    """Health check endpoint for Android app"""
    return jsonify({
        "success": True,
        "data": "OK",
        "message": "API is healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/test/android', methods=['POST'])
def test_android_connection():
    """Endpoint de diagnóstico para probar la conectividad desde Android"""
    try:
        # Verificar headers
        api_key = request.headers.get('X-API-Key')
        content_type = request.headers.get('Content-Type')
        
        print(f"🔍 Android test request:")
        print(f"   - API Key: '{api_key}'")
        print(f"   - Content-Type: '{content_type}'")
        print(f"   - Valid API Key: {api_key == API_KEY}")
        
        # Verificar autenticación
        if api_key != API_KEY:
            return jsonify({
                "success": False,
                "message": f"Invalid API key. Expected: {API_KEY[:10]}..., Got: {api_key[:10] if api_key else 'None'}..."
            }), 401
        
        # Verificar JSON
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400
        
        return jsonify({
            "success": True,
            "message": "Android connection test successful",
            "data": {
                "received_fields": list(data.keys()),
                "api_key_valid": True,
                "content_type": content_type
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Test failed: {str(e)}"
        }), 500

# Endpoint de test para verificar POST
@app.route('/api/test-paint', methods=['POST'])
def test_paint_creation():
    """Test endpoint to verify POST functionality"""
    try:
        data = request.get_json()
        return jsonify({
            "success": True,
            "data": data,
            "message": "POST /api/paints endpoint is working",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Test error: {str(e)}"
        }), 500

# ==================== PAINT IMAGES SEARCH - NUEVO ENDPOINT ====================

@app.route('/api/paint-images/search', methods=['GET'])
def search_paint_images():
    """
    Buscar imágenes de pinturas por marca y código
    
    Parámetros de consulta:
    - marca: Marca de la pintura (VALLEJO, AK, GAMES WORKSHOP, etc.)
    - codigo: Código de la pintura
    - nombre: Búsqueda por nombre (opcional)
    - limit: Límite de resultados (default: 50)
    
    Respuesta:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "marca": "VALLEJO",
                "codigo": "70951",
                "nombre": "Blanco",
                "imagen_url": "https://...",
                "categoria": "Model Color"
            }
        ],
        "total": 1,
        "message": "Búsqueda completada exitosamente"
    }
    """
    try:
        # Obtener parámetros de consulta
        marca = request.args.get('marca', '').strip().upper()
        codigo = request.args.get('codigo', '').strip()
        nombre = request.args.get('nombre', '').strip()
        limit = min(int(request.args.get('limit', 50)), 200)  # Máximo 200 resultados
        
        print(f"🔍 Paint image search - marca: '{marca}', codigo: '{codigo}', nombre: '{nombre}'")
        
        # Construir consulta base
        query = PaintImage.query
        
        # Filtrar por marca si se especifica
        if marca:
            query = query.filter(PaintImage.marca == marca)
        
        # Filtrar por código si se especifica
        if codigo:
            query = query.filter(PaintImage.codigo.ilike(f'%{codigo}%'))
        
        # Filtrar por nombre si se especifica
        if nombre:
            query = query.filter(PaintImage.nombre.ilike(f'%{nombre}%'))
        
        # Aplicar límite y ordenar
        results = query.order_by(PaintImage.marca, PaintImage.codigo).limit(limit).all()
        
        # Convertir a diccionario
        paint_images = [paint_image.to_dict() for paint_image in results]
        
        print(f"📊 Found {len(paint_images)} paint images")
        
        return jsonify({
            "success": True,
            "data": paint_images,
            "total": len(paint_images),
            "message": f"Búsqueda completada exitosamente - {len(paint_images)} resultados"
        })
        
    except Exception as e:
        print(f"❌ Error searching paint images: {str(e)}")
        return jsonify({
            "success": False,
            "data": [],
            "total": 0,
            "message": f"Error en la búsqueda: {str(e)}"
        }), 500

@app.route('/api/paint-images/<marca>/<codigo>', methods=['GET'])
def get_paint_image_by_marca_codigo(marca, codigo):
    """
    Obtener imagen específica de pintura por marca y código
    
    Parámetros:
    - marca: Marca de la pintura
    - codigo: Código de la pintura
    
    Respuesta:
    {
        "success": true,
        "data": {
            "id": 1,
            "marca": "VALLEJO",
            "codigo": "70951",
            "nombre": "Blanco",
            "imagen_url": "https://...",
            "categoria": "Model Color"
        },
        "message": "Imagen encontrada exitosamente"
    }
    """
    try:
        marca = marca.strip().upper()
        codigo = codigo.strip()
        
        print(f"🔍 Searching specific paint image - marca: '{marca}', codigo: '{codigo}'")
        
        # Buscar la imagen específica
        paint_image = PaintImage.query.filter_by(marca=marca, codigo=codigo).first()
        
        if not paint_image:
            return jsonify({
                "success": False,
                "data": None,
                "message": f"No se encontró imagen para {marca} {codigo}"
            }), 404
        
        print(f"✅ Found paint image: {paint_image.nombre}")
        
        return jsonify({
            "success": True,
            "data": paint_image.to_dict(),
            "message": "Imagen encontrada exitosamente"
        })
        
    except Exception as e:
        print(f"❌ Error getting paint image: {str(e)}")
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error obteniendo imagen: {str(e)}"
        }), 500

@app.route('/api/paint-images/brands', methods=['GET'])
def get_paint_brands():
    """
    Obtener lista de marcas disponibles
    
    Respuesta:
    {
        "success": true,
        "data": ["VALLEJO", "AK", "GAMES WORKSHOP", "SCALE", "TAMIYA"],
        "message": "Marcas obtenidas exitosamente"
    }
    """
    try:
        # Obtener marcas únicas
        brands = db.session.query(PaintImage.marca).distinct().order_by(PaintImage.marca).all()
        brand_list = [brand[0] for brand in brands]
        
        print(f"📊 Found {len(brand_list)} paint brands")
        
        return jsonify({
            "success": True,
            "data": brand_list,
            "message": f"Marcas obtenidas exitosamente - {len(brand_list)} marcas"
        })
        
    except Exception as e:
        print(f"❌ Error getting paint brands: {str(e)}")
        return jsonify({
            "success": False,
            "data": [],
            "message": f"Error obteniendo marcas: {str(e)}"
        }), 500

@app.route('/api/paint-images/stats', methods=['GET'])
def get_paint_images_stats():
    """
    Obtener estadísticas de la base de datos de imágenes
    
    Respuesta:
    {
        "success": true,
        "data": {
            "total_images": 3277,
            "brands": {
                "VALLEJO": 2500,
                "AK": 400,
                "GAMES WORKSHOP": 300,
                "SCALE": 50,
                "TAMIYA": 27
            }
        },
        "message": "Estadísticas obtenidas exitosamente"
    }
    """
    try:
        # Obtener total de imágenes
        total_images = PaintImage.query.count()
        
        # Obtener conteo por marca
        brands_count = db.session.query(
            PaintImage.marca,
            db.func.count(PaintImage.id).label('count')
        ).group_by(PaintImage.marca).order_by(db.func.count(PaintImage.id).desc()).all()
        
        brands_dict = {brand: count for brand, count in brands_count}
        
        stats = {
            "total_images": total_images,
            "brands": brands_dict
        }
        
        print(f"📊 Paint images stats - Total: {total_images}, Brands: {len(brands_dict)}")
        
        return jsonify({
            "success": True,
            "data": stats,
            "message": "Estadísticas obtenidas exitosamente"
        })
        
    except Exception as e:
        print(f"❌ Error getting paint images stats: {str(e)}")
        return jsonify({
            "success": False,
            "data": None,
            "message": f"Error obteniendo estadísticas: {str(e)}"
        }), 500

# Endpoint temporal para debug - verificar sync_status
@app.route('/api/debug/sync-status', methods=['GET'])
def debug_sync_status():
    """Debug endpoint para verificar el estado de sync_status"""
    try:
        # Obtener pinturas con sync_status diferente a 'synced'
        paints = Paint.query.limit(10).all()
        result = []
        
        for paint in paints:
            sync_status = getattr(paint, 'sync_status', 'field_not_exists')
            result.append({
                'id': paint.id,
                'name': paint.name,
                'sync_status': sync_status,
                'stock': paint.stock,
                'created_at': paint.created_at.isoformat() if paint.created_at else None
            })
        
        return jsonify({
            'success': True,
            'paints': result,
            'total_checked': len(result)
        })
        
    except Exception as e:
        print(f"Error in debug sync status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint temporal para testing - establecer sync_status manualmente
@app.route('/api/debug/set-sync-status/<int:paint_id>', methods=['POST'])
@admin_required
def debug_set_sync_status(paint_id):
    """Debug endpoint para establecer sync_status manualmente"""
    try:
        data = request.get_json()
        status = data.get('status', 'pending_upload')
        
        paint = Paint.query.get(paint_id)
        if not paint:
            return jsonify({'success': False, 'error': 'Paint not found'}), 404
        
        if hasattr(paint, 'sync_status'):
            paint.sync_status = status
            db.session.commit()
            
            return jsonify({
                'success': True,
                'paint_id': paint_id,
                'name': paint.name,
                'old_status': 'synced',
                'new_status': status
            })
        else:
            return jsonify({'success': False, 'error': 'sync_status field not available'}), 400
            
    except Exception as e:
        print(f"Error setting sync status: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint temporal para debug - verificar notificaciones pendientes
@app.route('/api/debug/pending-notifications', methods=['GET'])
def debug_pending_notifications():
    """Debug endpoint para ver notificaciones pendientes"""
    try:
        notifications = getattr(app, 'pending_notifications', [])
        return jsonify({
            'success': True,
            'pending_count': len(notifications),
            'notifications': notifications,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error checking pending notifications: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoint para marcar pinturas como sincronizadas
@app.route('/api/paints/mark-synced', methods=['POST'])
@admin_required
def mark_paints_synced():
    """Marcar pinturas como sincronizadas después de procesar notificaciones de Android"""
    try:
        data = request.get_json()
        paint_ids = data.get('paint_ids', [])
        
        if not paint_ids:
            return jsonify({"success": False, "message": "No paint IDs provided"}), 400
        
        # Actualizar sync_status a 'synced' para las pinturas especificadas
        updated_count = 0
        for paint_id in paint_ids:
            paint = Paint.query.get(paint_id)
            if paint and hasattr(paint, 'sync_status'):
                paint.sync_status = 'synced'
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Marked {updated_count} paints as synced",
            "updated_count": updated_count
        })
        
    except Exception as e:
        print(f"Error marking paints as synced: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Endpoint para actualizar color preview desde selector de color
@app.route('/api/paints/update-color-preview', methods=['POST'])
@admin_required
def update_color_preview():
    """Actualizar color_preview de una pintura desde el selector de color"""
    try:
        print(f"🎨 [COLOR PICKER] Request received to update color preview")
        
        data = request.get_json()
        print(f"🎨 [COLOR PICKER] Request data: {data}")
        
        if not data:
            print(f"❌ [COLOR PICKER] No data provided")
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        paint_id = data.get('paint_id')
        color_preview = data.get('color_preview')
        
        print(f"🎨 [COLOR PICKER] Paint ID: {paint_id}, Color: {color_preview}")
        
        if not paint_id:
            print(f"❌ [COLOR PICKER] paint_id is required")
            return jsonify({"success": False, "message": "paint_id is required"}), 400
        
        if not color_preview:
            print(f"❌ [COLOR PICKER] color_preview is required")
            return jsonify({"success": False, "message": "color_preview is required"}), 400
        
        # Validar formato hexadecimal
        if not color_preview.startswith('#') or len(color_preview) != 7:
            print(f"❌ [COLOR PICKER] Invalid hex format: {color_preview}")
            return jsonify({"success": False, "message": "color_preview must be in hex format (#RRGGBB)"}), 400
        
        # Buscar la pintura
        paint = Paint.query.get(paint_id)
        if not paint:
            print(f"❌ [COLOR PICKER] Paint with id {paint_id} not found")
            return jsonify({"success": False, "message": f"Paint with id {paint_id} not found"}), 404
        
        print(f"🎨 [COLOR PICKER] Found paint: {paint.name} (Brand: {paint.brand})")
        print(f"🎨 [COLOR PICKER] Current color_preview: {paint.color_preview}")
        
        # Actualizar color_preview
        old_color = paint.color_preview
        paint.color_preview = color_preview
        
        print(f"🎨 [COLOR PICKER] Updating color_preview from {old_color} to {color_preview}")
        
        db.session.commit()
        
        print(f"✅ [COLOR PICKER] Successfully updated paint {paint_id}: {old_color} → {color_preview}")
        
        return jsonify({
            "success": True,
            "message": f"Color preview updated successfully for {paint.name}",
            "paint_id": paint_id,
            "color_preview": color_preview,
            "paint_name": paint.name,
            "old_color": old_color
        })
        
    except Exception as e:
        print(f"❌ [COLOR PICKER] Error updating color preview: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Endpoint para actualizar image_url desde buscador de imágenes
@app.route('/api/paints/update-image-url', methods=['POST'])
@admin_required
def update_image_url():
    """Actualizar image_url de una pintura desde el buscador de imágenes"""
    try:
        print(f"🖼️ [IMAGE SEARCH] Request received to update image URL")
        
        data = request.get_json()
        print(f"🖼️ [IMAGE SEARCH] Request data: {data}")
        
        if not data:
            print(f"❌ [IMAGE SEARCH] No data provided")
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        paint_id = data.get('paint_id')
        image_url = data.get('image_url')
        
        print(f"🖼️ [IMAGE SEARCH] Paint ID: {paint_id}, Image URL: {image_url}")
        
        if not paint_id:
            print(f"❌ [IMAGE SEARCH] paint_id is required")
            return jsonify({"success": False, "message": "paint_id is required"}), 400
        
        if not image_url:
            print(f"❌ [IMAGE SEARCH] image_url is required")
            return jsonify({"success": False, "message": "image_url is required"}), 400
        
        # Validar que sea una URL válida
        if not (image_url.startswith('http://') or image_url.startswith('https://')):
            print(f"❌ [IMAGE SEARCH] Invalid URL format: {image_url}")
            return jsonify({"success": False, "message": "image_url must be a valid HTTP/HTTPS URL"}), 400
        
        # Buscar la pintura
        paint = Paint.query.get(paint_id)
        if not paint:
            print(f"❌ [IMAGE SEARCH] Paint with id {paint_id} not found")
            return jsonify({"success": False, "message": f"Paint with id {paint_id} not found"}), 404
        
        print(f"🖼️ [IMAGE SEARCH] Found paint: {paint.name} (Brand: {paint.brand})")
        print(f"🖼️ [IMAGE SEARCH] Current image_url: {paint.image_url}")
        
        # Actualizar image_url
        old_url = paint.image_url
        paint.image_url = image_url
        
        print(f"🖼️ [IMAGE SEARCH] Updating image_url from {old_url} to {image_url}")
        
        db.session.commit()
        
        print(f"✅ [IMAGE SEARCH] Successfully updated paint {paint_id}: image URL updated")
        
        return jsonify({
            "success": True,
            "message": f"Image URL updated successfully for {paint.name}",
            "paint_id": paint_id,
            "image_url": image_url,
            "paint_name": paint.name,
            "old_url": old_url
        })
        
    except Exception as e:
        print(f"❌ [IMAGE SEARCH] Error updating image URL: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Endpoint para buscar imágenes usando Google Images
@app.route('/api/paints/search-images', methods=['POST'])
@admin_required
def search_high_quality_images():
    """Buscar imágenes de alta resolución usando Google Images"""
    try:
        print(f"🔍 [IMAGE SEARCH] Request received to search images")
        
        data = request.get_json()
        print(f"🔍 [IMAGE SEARCH] Request data: {data}")
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        paint_id = data.get('paint_id')
        brand = data.get('brand', '').strip()
        name = data.get('name', '').strip()
        page = data.get('page', 1)  # Página de resultados, default 1
        
        print(f"🔍 [IMAGE SEARCH] Paint ID: {paint_id}")
        print(f"🔍 [IMAGE SEARCH] Brand received: '{brand}'")
        print(f"🔍 [IMAGE SEARCH] Name received: '{name}'")
        print(f"🔍 [IMAGE SEARCH] Page: {page}")
        
        if not paint_id:
            return jsonify({"success": False, "message": "paint_id is required"}), 400
        
        # Si no se recibieron brand/name del frontend, buscar en la base de datos
        if not brand or not name:
            print(f"🔍 [IMAGE SEARCH] Missing brand/name, searching in database...")
            paint = Paint.query.get(paint_id)
            if not paint:
                return jsonify({"success": False, "message": f"Paint {paint_id} not found"}), 404
            
            brand = paint.brand or ''
            name = paint.name or ''
            print(f"🔍 [IMAGE SEARCH] From DB - Brand: '{brand}', Name: '{name}'")
        
        # Limpiar códigos numéricos del nombre
        def clean_description(text):
            """Eliminar códigos numéricos y caracteres no relevantes de la descripción"""
            import re
            if not text:
                return ""
            
            # Eliminar códigos numéricos comunes (ej: "109", "70.909", "AK-123")
            text = re.sub(r'\b\d{2,4}\b', '', text)  # Números de 2-4 dígitos
            text = re.sub(r'\b\d+\.\d+\b', '', text)  # Números con punto (70.909)
            text = re.sub(r'\b[A-Z]{1,3}-\d+\b', '', text)  # Códigos tipo AK-123
            text = re.sub(r'\b[A-Z]\d+\b', '', text)  # Códigos tipo P3, C1, etc.
            
            # Limpiar múltiples espacios y caracteres especiales
            text = re.sub(r'\s+', ' ', text)  # Múltiples espacios a uno
            text = re.sub(r'[^\w\s]', ' ', text)  # Caracteres especiales a espacios
            
            return text.strip()
        
        # Limpiar y preparar términos de búsqueda
        cleaned_name = clean_description(name)
        brand_clean = brand.strip()
        
        print(f"🔍 [IMAGE SEARCH] Original name: '{name}'")
        print(f"🔍 [IMAGE SEARCH] Cleaned name: '{cleaned_name}'")
        print(f"🔍 [IMAGE SEARCH] Brand: '{brand_clean}'")
        
        # Crear términos de búsqueda solo con marca y descripción limpia (sin códigos)
        search_terms = []
        if brand_clean:
            search_terms.append(brand_clean)
        if cleaned_name:
            search_terms.append(cleaned_name)
        
        if not search_terms:
            return jsonify({"success": False, "message": "No valid search terms after cleaning"}), 400
        
        # Diferentes variaciones de búsqueda para mejores resultados
        search_queries = []
        
        # Solo si tenemos descripción limpia
        if cleaned_name:
            search_queries.extend([
                f"{brand_clean} {cleaned_name} paint",
                f"{brand_clean} {cleaned_name} acrylic",
                f"{brand_clean} {cleaned_name}",
                f"{cleaned_name} {brand_clean} miniature",
                f"{brand_clean} paint {cleaned_name}"
            ])
        
        # Búsquedas de marca específica
        if brand_clean:
            if "vallejo" in brand_clean.lower():
                search_queries.extend([
                    "vallejo paint miniature",
                    "vallejo acrylic paint",
                    f"vallejo {cleaned_name}" if cleaned_name else "vallejo paint"
                ])
            elif "ak" in brand_clean.lower():
                search_queries.extend([
                    "ak interactive paint",
                    "ak paint miniature",
                    f"ak {cleaned_name}" if cleaned_name else "ak paint"
                ])
            else:
                search_queries.append(f"{brand_clean} paint miniature")
        
        # Remover duplicados manteniendo orden
        seen = set()
        search_queries = [q for q in search_queries if not (q in seen or seen.add(q))]
        
        print(f"🔍 [IMAGE SEARCH] Search queries: {search_queries}")
        
        # Buscar imágenes usando Google Custom Search API
        images = []
        
        # Configuración de Google Custom Search API
        GOOGLE_API_KEY = "AIzaSyDRLw6cUMLuGKFeckwpd1fQMQypNkuOnTM"
        GOOGLE_CX = "a4da551cd50f94b41"
        
        print(f"🔍 [IMAGE SEARCH] Using Google Custom Search API...")
        print(f"🔍 [IMAGE SEARCH] API Key: {GOOGLE_API_KEY[:10]}...{GOOGLE_API_KEY[-4:]}")
        print(f"🔍 [IMAGE SEARCH] CX: {GOOGLE_CX}")
        
        # Primero, hacer una consulta de prueba para verificar la API
        try:
            import requests
            test_url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&q=test"
            test_response = requests.get(test_url, timeout=5)
            print(f"🔍 [IMAGE SEARCH] API test response: {test_response.status_code}")
            if test_response.status_code != 200:
                print(f"❌ [IMAGE SEARCH] API test failed: {test_response.text[:500]}")
        except Exception as test_error:
            print(f"❌ [IMAGE SEARCH] API test error: {str(test_error)}")
        
        try:
            # Calcular el índice de inicio basado en la página
            start_index = ((page - 1) * 10) + 1  # Google usa índice basado en 1
            max_images_per_query = 10  # Google permite máximo 10 por consulta
            
            # Buscar con cada consulta hasta obtener suficientes resultados
            query_index = 0
            for query in search_queries[:3]:  # Máximo 3 consultas
                if len(images) >= 20:  # Máximo 20 imágenes por página
                    break
                    
                print(f"🔍 [IMAGE SEARCH] Google API search: '{query}' (page {page}, start {start_index + query_index * 10})")
                
                try:
                    # Llamada a Google Custom Search API
                    api_url = "https://www.googleapis.com/customsearch/v1"
                    params = {
                        'key': GOOGLE_API_KEY,
                        'cx': GOOGLE_CX,
                        'q': query,
                        'searchType': 'image',
                        'start': start_index + (query_index * 10),  # Offset para paginación
                        'num': max_images_per_query,  # 10 resultados por consulta
                        'safe': 'off'
                    }
                    
                    query_index += 1
                    
                    print(f"🔍 [IMAGE SEARCH] Making API call to: {api_url}")
                    print(f"🔍 [IMAGE SEARCH] Parameters: {params}")
                    
                    response = requests.get(api_url, params=params, timeout=15)
                    
                    print(f"🔍 [IMAGE SEARCH] Response status: {response.status_code}")
                    print(f"🔍 [IMAGE SEARCH] Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"🔍 [IMAGE SEARCH] Response data keys: {list(data.keys())}")
                        
                        items = data.get('items', [])
                        
                        print(f"  📸 Google API returned {len(items)} images for '{query}'")
                        
                        if len(items) == 0:
                            print(f"❌ [IMAGE SEARCH] No items in response. Full response: {data}")
                        
                        for item in items:
                            if len(images) >= 15:
                                break
                            
                            print(f"🔍 [IMAGE SEARCH] Processing item: {list(item.keys())}")
                            
                            # Extraer información de la imagen
                            image_url = item.get('link', '')
                            title = item.get('title', '')
                            display_link = item.get('displayLink', '')
                            image_info = item.get('image', {})
                            
                            print(f"  📸 Found image URL: {image_url[:100]}...")
                            
                            # Obtener dimensiones si están disponibles
                            width = image_info.get('width', 400)
                            height = image_info.get('height', 400)
                            
                            # Validar URL
                            if (image_url and 
                                image_url.startswith(('http://', 'https://')) and
                                not any(img['url'] == image_url for img in images)):
                                
                                # Determinar categoría por dominio
                                category = 'general'
                                site_name = display_link or 'Google Images'
                                
                                # Categorizar según el dominio
                                if display_link:
                                    domain_lower = display_link.lower()
                                    if any(d in domain_lower for d in ['vallejo', 'ak-interactive', 'scale75', 'greenstuff']):
                                        category = 'fabricantes'
                                    elif any(d in domain_lower for d in ['e-minis', 'goblintrader', 'bandua', 'frikland']):
                                        category = 'tiendas_espana'
                                    elif any(d in domain_lower for d in ['games-workshop', 'citadel', 'warhammer']):
                                        category = 'fabricantes'
                                
                                images.append({
                                    'url': image_url,
                                    'title': title[:100] if title else f"{brand_clean} {cleaned_name}",
                                    'source': f"https://{display_link}" if display_link else image_url,
                                    'width': int(width) if width else 400,
                                    'height': int(height) if height else 400,
                                    'site': site_name[:30],  # Limitar longitud
                                    'category': category
                                })
                                
                                print(f"  ✅ Added image from {display_link}: {title[:50]}...")
                            else:
                                print(f"  ❌ Skipped invalid URL: {image_url[:100]}...")
                        
                        print(f"✅ [IMAGE SEARCH] Google API found {len(images)} total images so far")
                        
                    else:
                        print(f"❌ [IMAGE SEARCH] Google API HTTP error: {response.status_code}")
                        print(f"❌ [IMAGE SEARCH] Error response: {response.text}")
                        
                except Exception as api_error:
                    print(f"❌ [IMAGE SEARCH] Google API exception for '{query}': {str(api_error)}")
                    import traceback
                    print(f"❌ [IMAGE SEARCH] Traceback: {traceback.format_exc()}")
                    continue
            
        except ImportError as import_error:
            print(f"❌ [IMAGE SEARCH] Import error: {import_error}")
        
        # Fallback: Si Google API falla completamente, usar URLs de referencia
        if len(images) == 0:
            print(f"🔍 [IMAGE SEARCH] Google API failed, providing reference images...")
            
            reference_images = [
                "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=400&fit=crop",
                "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=400&fit=crop",
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop"
            ]
            
            for i, ref_url in enumerate(reference_images):
                images.append({
                    'url': ref_url,
                    'title': f"{brand_clean} {cleaned_name} - Imagen de referencia {i+1}",
                    'source': 'unsplash.com',
                    'width': 400,
                    'height': 400,
                    'site': 'Referencia',
                    'category': 'general'
                })
            
            print(f"✅ [IMAGE SEARCH] Added {len(images)} reference images")
        
        # Filtrar imágenes por calidad y relevancia
        filtered_images = []
        seen_urls = set()
        
        for img in images:
            # Filtrar por tamaño mínimo, URLs válidas y no duplicados
            if (img['url'] and 
                img['url'] not in seen_urls and
                img['url'].startswith(('http://', 'https://')) and
                img['width'] >= 200 and 
                img['height'] >= 200):
                filtered_images.append(img)
                seen_urls.add(img['url'])
        
        # Ordenar por tamaño (las más grandes primero) para mejor calidad
        filtered_images.sort(key=lambda x: x['width'] * x['height'], reverse=True)
        
        print(f"✅ [IMAGE SEARCH] Found {len(filtered_images)} quality images")
        
        return jsonify({
            "success": True,
            "message": f"Found {len(filtered_images)} images for {brand} {name}",
            "paint_id": paint_id,
            "search_terms": search_terms,
            "images": filtered_images[:20]  # Máximo 20 imágenes para el frontend
        })
        
    except Exception as e:
        print(f"❌ [IMAGE SEARCH] Error in search endpoint: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# Endpoint de debug para probar Google API
@app.route('/api/debug/test-google-api', methods=['GET'])
@admin_required
def debug_test_google_api():
    """Debug endpoint para probar Google Custom Search API"""
    try:
        import requests
        
        GOOGLE_API_KEY = "AIzaSyDRLw6cUMLuGKFeckwpd1fQMQypNkuOnTM"
        GOOGLE_CX = "a4da551cd50f94b41"
        
        # Test básico
        test_url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CX,
            'q': 'vallejo paint',
            'searchType': 'image',
            'num': 1
        }
        
        response = requests.get(test_url, params=params, timeout=10)
        
        result = {
            "api_key": f"{GOOGLE_API_KEY[:10]}...{GOOGLE_API_KEY[-4:]}",
            "cx": GOOGLE_CX,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response": response.json() if response.status_code == 200 else response.text[:500]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

# Endpoint de debug para verificar acceso a la base de datos
@app.route('/api/debug/test-color-update/<int:paint_id>/<color>', methods=['GET'])
@admin_required
def debug_test_color_update(paint_id, color):
    """Debug endpoint para probar actualización de color_preview"""
    try:
        print(f"🔧 [DEBUG] Testing color update for paint {paint_id} with color {color}")
        
        # Buscar la pintura
        paint = Paint.query.get(paint_id)
        if not paint:
            return jsonify({"success": False, "message": f"Paint {paint_id} not found"}), 404
        
        old_color = paint.color_preview
        test_color = f"#{color}" if not color.startswith('#') else color
        
        print(f"🔧 [DEBUG] Current color: {old_color}")
        print(f"🔧 [DEBUG] Setting color to: {test_color}")
        
        paint.color_preview = test_color
        db.session.commit()
        
        # Verificar que se guardó
        db.session.refresh(paint)
        new_color = paint.color_preview
        
        print(f"🔧 [DEBUG] Verified color in DB: {new_color}")
        
        return jsonify({
            "success": True,
            "paint_id": paint_id,
            "paint_name": paint.name,
            "old_color": old_color,
            "set_color": test_color,
            "verified_color": new_color,
            "message": "Debug test completed successfully"
        })
        
    except Exception as e:
        print(f"❌ [DEBUG] Error in debug test: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== BACKUP SYSTEM - STEP 1 ====================

@app.route('/admin/paints/backup', methods=['POST'])
@admin_required
def create_backup():
    """Create a backup of all paints - Step 1: Basic backup endpoint"""
    try:
        print(f"🔄 Backup creation started at {datetime.utcnow()}")
        # Get all paints
        paints = Paint.query.all()
        
        if not paints:
            return jsonify({
                "success": False,
                "message": "No hay pinturas para respaldar"
            }), 400
        
        # Check if a backup already exists with the same timestamp (within 1 minute)
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_backup = PaintBackup.query.filter(
            PaintBackup.backup_date >= one_minute_ago
        ).first()
        
        if recent_backup:
            return jsonify({
                "success": False,
                "message": "Ya existe un backup reciente (creado hace menos de 1 minuto). Espera antes de crear otro."
            }), 400

        # Clear any existing backups first (keep only the most recent backup)
        PaintBackup.query.delete()
        
        # Create backup entries
        backup_count = 0
        backup_reason = request.json.get('reason', 'Manual backup') if request.is_json else 'Manual backup'
        
        for paint in paints:
            backup = PaintBackup(
                original_id=paint.id,
                name=paint.name,
                brand=paint.brand,
                color_code=paint.color_code,
                color_type=paint.color_type,
                color_family=paint.color_family,
                description=paint.description,
                stock=paint.stock,
                price=paint.price,
                color_preview=paint.color_preview,
                image_url=paint.image_url,
                original_created_at=paint.created_at,
                backup_reason=backup_reason
            )
            
            db.session.add(backup)
            backup_count += 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Backup creado exitosamente. {backup_count} pinturas respaldadas.",
            "data": {
                "backup_count": backup_count,
                "total_paints": len(paints),
                "backup_date": datetime.utcnow().isoformat()
            }
        }), 201
        
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al crear backup: {str(e)}"
        }), 500

@app.route('/admin/paints/backups', methods=['GET'])
@admin_required
def list_backups():
    """List all paint backups - Step 2: Improved backup listing with grouping"""
    try:
        # Get unique backup sessions (grouped by backup_date truncated to second and reason)
        backup_sessions = db.session.query(
            db.func.date_trunc('second', PaintBackup.backup_date).label('backup_session'),
            PaintBackup.backup_reason,
            db.func.count(PaintBackup.id).label('paint_count'),
            db.func.min(PaintBackup.backup_date).label('exact_date')
        ).group_by(
            db.func.date_trunc('second', PaintBackup.backup_date),
            PaintBackup.backup_reason
        ).order_by(db.func.min(PaintBackup.backup_date).desc()).all()
        
        backup_list = []
        for session in backup_sessions:
            backup_list.append({
                'backup_date': session.exact_date.isoformat() if session.exact_date else None,
                'backup_reason': session.backup_reason,
                'paint_count': session.paint_count,
                'formatted_date': session.exact_date.strftime('%d/%m/%Y, %H:%M:%S') if session.exact_date else 'Unknown'
            })
        
        return jsonify({
            "success": True,
            "data": backup_list,
            "message": f"Se encontraron {len(backup_list)} sesiones de backup"
        }), 200
        
    except Exception as e:
        print(f"Error listing backups: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error al listar backups: {str(e)}"
        }), 500

@app.route('/admin/init-backup-tables', methods=['POST'])
@admin_required
def init_backup_tables():
    """Initialize backup tables - Step 2.5: Create backup table if not exists"""
    try:
        # Create all tables including PaintBackup
        db.create_all()
        
        # Verify the table was created
        result = db.engine.execute("SELECT to_regclass('paints_backup')")
        table_exists = result.scalar() is not None
        
        if table_exists:
            return jsonify({
                "success": True,
                "message": "Tabla paints_backup creada/verificada exitosamente"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Error: No se pudo crear la tabla paints_backup"
            }), 500
        
    except Exception as e:
        print(f"Error initializing backup tables: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error al inicializar tablas de backup: {str(e)}"
        }), 500

@app.route('/admin/paints/clear', methods=['DELETE'])
@admin_required
def clear_paints():
    """Clear all paints from main table - Step 3: Clear paints endpoint"""
    try:
        # Safety check: ensure there's a recent backup
        recent_backup = PaintBackup.query.first()
        if not recent_backup:
            return jsonify({
                "success": False,
                "message": "No se puede limpiar: No existe ningún backup. Crea un backup primero."
            }), 400
        
        # Get current paint count before deletion
        paint_count = Paint.query.count()
        
        if paint_count == 0:
            return jsonify({
                "success": False,
                "message": "No hay pinturas para eliminar"
            }), 400
        
        # Delete all paints
        deleted_count = Paint.query.delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Se eliminaron {deleted_count} pinturas de la tabla principal",
            "data": {
                "deleted_count": deleted_count,
                "backup_exists": True,
                "clear_date": datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"Error clearing paints: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al limpiar pinturas: {str(e)}"
        }), 500

@app.route('/admin/paints/restore', methods=['POST'])
@admin_required
def restore_paints():
    """Restore paints from backup - Step 4: Restore endpoint"""
    try:
        # Check if backup exists
        backups = PaintBackup.query.all()
        if not backups:
            return jsonify({
                "success": False,
                "message": "No hay backups disponibles para restaurar"
            }), 400
        
        # Check if main table already has data
        existing_paints = Paint.query.count()
        if existing_paints > 0:
            return jsonify({
                "success": False,
                "message": f"La tabla principal ya tiene {existing_paints} pinturas. Limpia la tabla primero si quieres restaurar desde backup."
            }), 400
        
        # Restore paints from backup
        restored_count = 0
        
        for backup in backups:
            # Create new paint from backup data
            paint = Paint(
                name=backup.name,
                brand=backup.brand,
                color_code=backup.color_code,
                color_type=backup.color_type,
                color_family=backup.color_family,
                description=backup.description,
                stock=backup.stock,
                price=backup.price,
                color_preview=backup.color_preview,
                image_url=backup.image_url,
                created_at=backup.original_created_at or backup.backup_date
            )
            
            db.session.add(paint)
            restored_count += 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Restauración exitosa. {restored_count} pinturas restauradas desde backup",
            "data": {
                "restored_count": restored_count,
                "total_backups": len(backups),
                "restore_date": datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"Error restoring paints: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al restaurar pinturas: {str(e)}"
        }), 500

@app.route('/admin/paints/clear-backups', methods=['DELETE'])
@admin_required
def clear_old_backups():
    """Clear old backup entries - Clean up duplicate backups"""
    try:
        # Count current backups
        backup_count = PaintBackup.query.count()
        
        if backup_count == 0:
            return jsonify({
                "success": False,
                "message": "No hay backups para limpiar"
            }), 400
        
        # Delete all backups
        deleted_count = PaintBackup.query.delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Se eliminaron {deleted_count} entradas de backup antiguas",
            "data": {
                "deleted_count": deleted_count
            }
        }), 200
        
    except Exception as e:
        print(f"Error clearing old backups: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al limpiar backups antiguos: {str(e)}"
        }), 500

# =====================================================
# ENDPOINTS DE NOTIFICACIONES WEB PARA ACTUALIZACIONES ANDROID → WEB
# =====================================================

# Variable global para mantener notificaciones pendientes
if not hasattr(app, 'pending_notifications'):
    app.pending_notifications = []

@app.route('/api/web-notify/paint-updated', methods=['POST'])
def notify_paint_updated():
    """
    Endpoint para recibir notificaciones de Android cuando se actualiza una pintura
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No se proporcionaron datos JSON'}), 400
        
        # Log de la notificación
        action = data.get('action', 'unknown')
        paint_name = data.get('paint_name', 'Desconocido')
        paint_id = data.get('paint_id')
        source = data.get('source', 'unknown')
        
        print(f"🔔 Notificación web recibida: {action} - {paint_name} (ID: {paint_id}) desde {source}")
        
        # Almacenar notificación para clientes web conectados
        notification = {
            'type': 'paint_update',
            'action': action,
            'paint_id': paint_id,
            'paint_name': paint_name,
            'paint_code': data.get('paint_code'),
            'paint_brand': data.get('paint_brand'),
            'timestamp': datetime.now().isoformat(),
            'source': source
        }
        
        # Almacenar en lista en memoria
        app.pending_notifications.append(notification)
        
        # Mantener solo las últimas 100 notificaciones para evitar problemas de memoria
        if len(app.pending_notifications) > 100:
            app.pending_notifications = app.pending_notifications[-100:]
        
        print(f"✅ Notificación almacenada exitosamente. Total pendientes: {len(app.pending_notifications)}")
        
        return jsonify({
            'success': True, 
            'message': f'Notificación recibida para {paint_name}',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error procesando notificación web: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/web-notify/paint-created', methods=['POST'])
def notify_paint_created():
    """
    Endpoint para recibir notificaciones de Android cuando se crea una pintura nueva
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No se proporcionaron datos JSON'}), 400
        
        # Log de la notificación
        paint_name = data.get('paint_name', 'Desconocido')
        paint_id = data.get('paint_id')
        source = data.get('source', 'unknown')
        
        print(f"🔔 Notificación web recibida: CREADA - {paint_name} (ID: {paint_id}) desde {source}")
        
        # Almacenar notificación
        notification = {
            'type': 'paint_create',
            'action': 'created',
            'paint_id': paint_id,
            'paint_name': paint_name,
            'paint_code': data.get('paint_code'),
            'paint_brand': data.get('paint_brand'),
            'timestamp': datetime.now().isoformat(),
            'source': source
        }
        
        app.pending_notifications.append(notification)
        
        # Mantener solo las últimas 100 notificaciones
        if len(app.pending_notifications) > 100:
            app.pending_notifications = app.pending_notifications[-100:]
        
        print(f"✅ Notificación de creación almacenada exitosamente. Total pendientes: {len(app.pending_notifications)}")
        
        return jsonify({
            'success': True, 
            'message': f'Notificación de creación recibida para {paint_name}',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error procesando notificación de creación: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/web-notify/get-notifications', methods=['GET'])
def get_pending_notifications():
    """
    Endpoint para que la web app obtenga las notificaciones pendientes
    La web app puede llamar esto periódicamente o cuando necesite actualizar
    """
    try:
        # Obtener todas las notificaciones pendientes
        notifications = app.pending_notifications.copy()
        
        # Limpiar las notificaciones después de enviarlas
        app.pending_notifications.clear()
        
        print(f"📤 Enviando {len(notifications)} notificaciones a la web app")
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo notificaciones: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/web-notify/status', methods=['GET'])
def notification_status():
    """
    Endpoint para verificar el estado del sistema de notificaciones
    """
    try:
        return jsonify({
            'success': True,
            'status': 'activo',
            'pending_count': len(app.pending_notifications),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo estado de notificaciones: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# =====================================================
# ENDPOINTS DE DEBUGGING PARA DIAGNÓSTICO DE STOCK
# =====================================================

@app.route('/api/debug/paint/<int:paint_id>', methods=['GET'])
def debug_paint_stock(paint_id):
    """
    Endpoint de debugging para verificar el estado real de una pintura en Railway
    """
    try:
        paint = Paint.query.get(paint_id)
        if not paint:
            return jsonify({
                "success": False,
                "message": f"Paint with ID {paint_id} not found"
            }), 404
        
        # Información completa de la pintura
        debug_info = {
            "success": True,
            "paint_data": {
                "id": paint.id,
                "name": paint.name,
                "brand": paint.brand,
                "color_code": paint.color_code,
                "stock": paint.stock,
                "price": paint.price,
                "description": paint.description,
                "image_url": paint.image_url,
                "created_at": paint.created_at.isoformat() if paint.created_at else None
            },
            "query_info": {
                "table_name": "paints",
                "query_time": datetime.now().isoformat()
            }
        }
        
        print(f"🔍 DEBUG - Paint {paint_id} info:")
        print(f"   - Name: {paint.name}")
        print(f"   - Stock: {paint.stock}")
        print(f"   - Created: {paint.created_at}")
        
        return jsonify(debug_info)
        
    except Exception as e:
        print(f"❌ Error in debug endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Debug error: {str(e)}"
        }), 500

@app.route('/api/debug/all-paints', methods=['GET'])
def debug_all_paints():
    """
    Endpoint para ver TODAS las pinturas en Railway (limitado a 50 para no sobrecargar)
    """
    try:
        paints = Paint.query.order_by(Paint.created_at.desc()).limit(50).all()
        
        debug_info = {
            "success": True,
            "total_count": Paint.query.count(),
            "showing_latest": len(paints),
            "paints": []
        }
        
        for paint in paints:
            debug_info["paints"].append({
                "id": paint.id,
                "name": paint.name,
                "brand": paint.brand,
                "color_code": paint.color_code,
                "stock": paint.stock,
                "created_at": paint.created_at.isoformat() if paint.created_at else None
            })
        
        print(f"🔍 DEBUG - Total paints in Railway: {debug_info['total_count']}")
        print(f"🔍 DEBUG - Latest 50 paints retrieved")
        
        return jsonify(debug_info)
        
    except Exception as e:
        print(f"❌ Error in debug all paints: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Debug error: {str(e)}"
        }), 500

@app.route('/api/debug/search-paint/<color_code>', methods=['GET'])
def debug_search_paint_by_code(color_code):
    """
    Buscar pintura por color_code para debugging
    """
    try:
        paints = Paint.query.filter_by(color_code=color_code).all()
        
        debug_info = {
            "success": True,
            "search_code": color_code,
            "found_count": len(paints),
            "paints": []
        }
        
        for paint in paints:
            debug_info["paints"].append({
                "id": paint.id,
                "name": paint.name,
                "brand": paint.brand,
                "color_code": paint.color_code,
                "stock": paint.stock,
                "created_at": paint.created_at.isoformat() if paint.created_at else None
            })
        
        print(f"🔍 DEBUG - Search for code '{color_code}': {len(paints)} results")
        
        return jsonify(debug_info)
        
    except Exception as e:
        print(f"❌ Error in debug search: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Debug error: {str(e)}"
        }), 500

@app.route('/api/debug/paint-count-by-brand', methods=['GET'])
def debug_paint_count_by_brand():
    """
    Contar pinturas por marca para debugging
    """
    try:
        from sqlalchemy import func
        
        # Contar pinturas por marca
        brand_counts = db.session.query(
            Paint.brand,
            func.count(Paint.id).label('count'),
            func.sum(Paint.stock).label('total_stock')
        ).group_by(Paint.brand).all()
        
        debug_info = {
            "success": True,
            "total_brands": len(brand_counts),
            "brands": []
        }
        
        for brand, count, total_stock in brand_counts:
            debug_info["brands"].append({
                "brand": brand,
                "paint_count": count,
                "total_stock": total_stock or 0
            })
        
        print(f"🔍 DEBUG - Total brands: {len(brand_counts)}")
        
        return jsonify(debug_info)
        
    except Exception as e:
        print(f"❌ Error in debug brand count: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Debug error: {str(e)}"
        }), 500

# ==================== SISTEMA DE NOTIFICACIONES WEB → ANDROID ====================

# Variables globales para mantener notificaciones pendientes para Android
if not hasattr(app, 'pending_android_notifications'):
    app.pending_android_notifications = []
if not hasattr(app, 'sent_notification_ids'):
    app.sent_notification_ids = set()

def send_android_notification(paint_id, action, data):
    """
    Función para enviar notificaciones a Android
    """
    try:
        import uuid
        notification_id = str(uuid.uuid4())
        
        notification = {
            'id': notification_id,
            'type': 'paint_update',
            'action': action,
            'paint_id': paint_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'sent': False
        }
        
        app.pending_android_notifications.append(notification)
        
        # Mantener solo las últimas 100 notificaciones
        if len(app.pending_android_notifications) > 100:
            app.pending_android_notifications = app.pending_android_notifications[-100:]
        
        return True
    except Exception as e:
        print(f"❌ Error sending Android notification: {str(e)}")
        return False

@app.route('/api/android-notify/get-notifications', methods=['GET'])
def get_android_notifications():
    """
    Endpoint para que Android obtenga las notificaciones pendientes
    Solo retorna notificaciones que no han sido enviadas previamente
    """
    try:
        if not hasattr(app, 'pending_android_notifications'):
            app.pending_android_notifications = []
        if not hasattr(app, 'sent_notification_ids'):
            app.sent_notification_ids = set()
        
        # Limpiar notificaciones antiguas (más de 5 minutos) y IDs de enviados antiguos
        current_time = datetime.utcnow()
        valid_notifications = []
        valid_sent_ids = set()
        
        for notif in app.pending_android_notifications:
            try:
                # Manejar diferentes formatos de timestamp
                timestamp_str = notif['timestamp'].replace('Z', '+00:00').replace('+00:00', '')
                notif_time = datetime.fromisoformat(timestamp_str)
                time_diff = (current_time - notif_time).total_seconds()
                
                # 🔧 MEJORADO: Limpiar notificaciones que han estado demasiado tiempo sin confirmación
                # Si una notificación tiene delivered_at pero no se ha confirmado en 2 minutos, permitir reenvío
                delivered_at = notif.get('delivered_at')
                if delivered_at and not notif.get('sent', False):
                    try:
                        delivered_time = datetime.fromisoformat(delivered_at.replace('Z', '+00:00').replace('+00:00', ''))
                        delivery_diff = (current_time - delivered_time).total_seconds()
                        if delivery_diff > 120:  # 2 minutos desde entrega
                            print(f"🔄 Reactivating unconfirmed notification {notif.get('id')} (delivered {delivery_diff:.1f}s ago)")
                            # Remover metadata de entrega para permitir reenvío
                            if 'delivered_at' in notif:
                                del notif['delivered_at']
                    except Exception:
                        pass
                
                if time_diff < 300:  # Menor a 5 minutos
                    valid_notifications.append(notif)
                    if notif.get('sent', False):
                        valid_sent_ids.add(notif.get('id'))
                else:
                    print(f"🗑️ Removing old notification {notif.get('id')} (age: {time_diff:.1f}s)")
            except Exception as parse_error:
                print(f"⚠️ Error parsing notification timestamp: {parse_error}")
                # Mantener notificación si no se puede parsear timestamp (asumir reciente)
                valid_notifications.append(notif)
        
        app.pending_android_notifications = valid_notifications
        app.sent_notification_ids = valid_sent_ids
        
        # Obtener solo notificaciones no enviadas (incluye las que tienen delivered_at pero no están confirmadas)
        new_notifications = [
            notif for notif in app.pending_android_notifications 
            if not notif.get('sent', False) and notif.get('id') not in app.sent_notification_ids and not notif.get('delivered_at')
        ]
        
        # 🔧 FIX: NO marcar como enviadas inmediatamente
        # Las notificaciones solo se marcarán como enviadas cuando Android confirme que las procesó
        # mediante el endpoint /api/android-notify/confirm-processed
        
        # Crear copias de las notificaciones para enviar (sin modificar las originales)
        notifications_to_send = []
        for notif in new_notifications:
            notification_copy = notif.copy()
            # Agregar metadata de envío para tracking temporal
            notification_copy['delivered_at'] = datetime.utcnow().isoformat()
            notifications_to_send.append(notification_copy)
        
        print(f"📤 Sending {len(notifications_to_send)} new notifications to Android (total pending: {len(app.pending_android_notifications)})")
        
        return jsonify({
            'success': True,
            'notifications': notifications_to_send,
            'count': len(notifications_to_send),
            'total_pending': len(app.pending_android_notifications),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error getting Android notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/android-notify/status', methods=['GET'])
def android_notification_status():
    """
    Endpoint para verificar el estado del sistema de notificaciones para Android
    """
    try:
        if not hasattr(app, 'pending_android_notifications'):
            app.pending_android_notifications = []
        if not hasattr(app, 'sent_notification_ids'):
            app.sent_notification_ids = set()
        
        # Contar notificaciones por estado
        sent_count = sum(1 for n in app.pending_android_notifications if n.get('sent', False))
        unsent_count = len(app.pending_android_notifications) - sent_count
        
        return jsonify({
            'success': True,
            'status': 'active',
            'total_pending': len(app.pending_android_notifications),
            'sent_count': sent_count,
            'unsent_count': unsent_count,
            'sent_ids_tracked': len(app.sent_notification_ids),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error getting Android notification status: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/android-notify/test-notification', methods=['POST'])
def create_test_notification():
    """
    ENDPOINT TEMPORAL - Crear notificación de testing para verificar que Android funciona
    """
    try:
        if not hasattr(app, 'pending_android_notifications'):
            app.pending_android_notifications = []
        
        # Get Blanco Hueso data
        paint = Paint.query.filter_by(name='Blanco Hueso').first()
        if not paint:
            return jsonify({
                'success': False,
                'message': 'Blanco Hueso not found'
            }), 404
        
        # Create test notification
        old_stock = paint.stock
        new_stock = old_stock + 1
        
        # Update stock
        paint.stock = new_stock
        db.session.commit()
        
        # Send notification
        send_android_notification(paint.id, 'stock_updated', {
            'paint_id': paint.id,
            'paint_name': paint.name,
            'paint_code': paint.color_code,
            'brand': paint.brand,
            'old_stock': old_stock,
            'new_stock': new_stock,
            'source': 'test_endpoint'
        })
        
        print(f"🧪 TEST: Created notification for {paint.name} stock {old_stock} → {new_stock}")
        
        return jsonify({
            'success': True,
            'message': f'Test notification created for {paint.name}',
            'paint_name': paint.name,
            'old_stock': old_stock,
            'new_stock': new_stock,
            'notification_count': len(app.pending_android_notifications),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error creating test notification: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/android-notify/confirm-processed', methods=['POST'])
def confirm_notifications_processed():
    """
    Endpoint para que Android confirme que procesó las notificaciones
    Acepta tanto processed_count como notification_ids para mayor flexibilidad
    """
    try:
        data = request.get_json()
        processed_count = data.get('processed_count', 0)
        notification_ids = data.get('notification_ids', [])
        
        if not hasattr(app, 'pending_android_notifications'):
            app.pending_android_notifications = []
        if not hasattr(app, 'sent_notification_ids'):
            app.sent_notification_ids = set()
        
        initial_count = len(app.pending_android_notifications)
        
        # Método 1: Por IDs específicos (más preciso)
        if notification_ids:
            # Primero marcar las notificaciones como enviadas antes de removerlas
            for notif in app.pending_android_notifications:
                if notif.get('id') in notification_ids:
                    notif['sent'] = True
                    notif['processed_at'] = datetime.utcnow().isoformat()
                    if 'id' in notif:
                        app.sent_notification_ids.add(notif['id'])
            
            # Luego remover las notificaciones confirmadas
            app.pending_android_notifications = [
                notif for notif in app.pending_android_notifications
                if notif.get('id') not in notification_ids
            ]
            print(f"✅ Android confirmed processing {len(notification_ids)} notifications by ID")
        
        # Método 2: Por cantidad (compatibilidad con implementación anterior)
        elif processed_count > 0:
            # Remover las primeras N notificaciones enviadas
            sent_notifications = [n for n in app.pending_android_notifications if n.get('sent', False)]
            to_remove = sent_notifications[:processed_count]
            
            for notif in to_remove:
                if notif in app.pending_android_notifications:
                    app.pending_android_notifications.remove(notif)
                if 'id' in notif:
                    app.sent_notification_ids.discard(notif['id'])
            
            print(f"✅ Android confirmed processing {processed_count} notifications by count")
        
        removed_count = initial_count - len(app.pending_android_notifications)
        
        return jsonify({
            'success': True,
            'remaining_count': len(app.pending_android_notifications),
            'removed_count': removed_count,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error confirming processed notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/android-notify/debug', methods=['GET'])
def debug_android_notifications():
    """
    Endpoint de debugging para inspeccionar el estado completo de las notificaciones
    """
    try:
        if not hasattr(app, 'pending_android_notifications'):
            app.pending_android_notifications = []
        if not hasattr(app, 'sent_notification_ids'):
            app.sent_notification_ids = set()
        
        # Analizar estado de las notificaciones
        total_count = len(app.pending_android_notifications)
        sent_count = sum(1 for n in app.pending_android_notifications if n.get('sent', False))
        delivered_count = sum(1 for n in app.pending_android_notifications if n.get('delivered_at'))
        unsent_count = total_count - sent_count
        
        # Detalles de cada notificación
        notification_details = []
        for notif in app.pending_android_notifications:
            notification_details.append({
                'id': notif.get('id'),
                'action': notif.get('action'),
                'paint_id': notif.get('paint_id'),
                'timestamp': notif.get('timestamp'),
                'sent': notif.get('sent', False),
                'delivered_at': notif.get('delivered_at'),
                'processed_at': notif.get('processed_at'),
                'source': notif.get('data', {}).get('source')
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_notifications': total_count,
                'sent_count': sent_count,
                'unsent_count': unsent_count,
                'delivered_count': delivered_count,
                'sent_ids_tracked': len(app.sent_notification_ids)
            },
            'notifications': notification_details,
            'sent_ids': list(app.sent_notification_ids),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error debugging Android notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/android-notify/clear', methods=['POST'])
def clear_android_notifications():
    """
    Endpoint para limpiar manualmente las notificaciones (útil para debugging)
    """
    try:
        if not hasattr(app, 'pending_android_notifications'):
            app.pending_android_notifications = []
        if not hasattr(app, 'sent_notification_ids'):
            app.sent_notification_ids = set()
        
        data = request.get_json() or {}
        clear_type = data.get('type', 'all')  # 'all', 'sent', 'old'
        
        initial_count = len(app.pending_android_notifications)
        initial_sent_ids = len(app.sent_notification_ids)
        
        if clear_type == 'all':
            app.pending_android_notifications = []
            app.sent_notification_ids = set()
            print("🧹 Cleared all Android notifications")
        
        elif clear_type == 'sent':
            app.pending_android_notifications = [
                notif for notif in app.pending_android_notifications 
                if not notif.get('sent', False)
            ]
            app.sent_notification_ids = set()
            print("🧹 Cleared sent Android notifications")
        
        elif clear_type == 'old':
            current_time = datetime.utcnow()
            app.pending_android_notifications = [
                notif for notif in app.pending_android_notifications
                if (current_time - datetime.fromisoformat(notif['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))).total_seconds() < 60
            ]
            print("🧹 Cleared old Android notifications (>1 minute)")
        
        final_count = len(app.pending_android_notifications)
        final_sent_ids = len(app.sent_notification_ids)
        
        return jsonify({
            'success': True,
            'type': clear_type,
            'removed': {
                'notifications': initial_count - final_count,
                'sent_ids': initial_sent_ids - final_sent_ids
            },
            'remaining': {
                'notifications': final_count,
                'sent_ids': final_sent_ids
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error clearing Android notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

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
