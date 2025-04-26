-- Crear tablas si no existen
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    experience_level VARCHAR(20) DEFAULT 'beginner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_id VARCHAR(20) NOT NULL,
    channel VARCHAR(100),
    category VARCHAR(50) DEFAULT 'Sin categoría',
    technique_start_time INTEGER DEFAULT 0,
    technique_end_time INTEGER,
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    video_version INTEGER DEFAULT 1,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT video_level_uc UNIQUE (video_id, difficulty_level)
);

CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, video_id)
);

CREATE TABLE IF NOT EXISTS techniques (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar un usuario administrador por defecto si no existe
DELETE FROM users WHERE username = 'admin';
INSERT INTO users (username, email, password_hash, role, experience_level)
VALUES ('admin', 'admin@printandpaint.com', 'pbkdf2:sha256:260000$dPCO0lNq6CyKMHXS$0e3dd3523d42cb0e57baac667c7d5f5654b8bce8f3cfdb8a3dbf2dacfa278b88', 'admin', 'expert');
SELECT 'admin', 'admin@printandpaint.com', 'pbkdf2:sha256:150000$uyTXcT9C$b9a89db723d85dfff85e7b3506df9b274cfee2d75c4bf0ec0d549de310c0c32b', 'admin', 'expert'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'admin'
);

-- Insertar algunos videos de ejemplo si no existen
INSERT INTO videos (title, description, video_id, channel, category, difficulty_level, technique_start_time, technique_end_time, version)
SELECT 'Pintura de base para miniaturas', 'Aprende la técnica básica para pintar la base de tus miniaturas.', 'dQw4w9WgXcQ', 'Print and Paint', 'Pintura Base', 'beginner', 60, 180, 1
WHERE NOT EXISTS (
    SELECT 1 FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner'
);

INSERT INTO videos (title, description, video_id, channel, category, difficulty_level, technique_start_time, technique_end_time, version)
SELECT 'Técnica de sombreado avanzada', 'Aprende técnicas avanzadas de sombreado para darle profundidad a tus modelos.', 'ZZ5LpwO-An4', 'Print and Paint', 'Sombreado', 'intermediate', 120, 300, 1
WHERE NOT EXISTS (
    SELECT 1 FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate'
);

INSERT INTO videos (title, description, video_id, channel, category, difficulty_level, technique_start_time, technique_end_time, version)
SELECT 'Efectos especiales para modelos 3D', 'Cómo crear efectos de fuego, agua y electricidad en tus modelos.', '9bZkp7q19f0', 'Print and Paint', 'Efectos Especiales', 'expert', 180, 360, 1
WHERE NOT EXISTS (
    SELECT 1 FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert'
);

-- Insertar técnicas para los videos de ejemplo
INSERT INTO techniques (video_id, name, start_time, end_time)
SELECT (SELECT id FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner'), 'Aplicación de imprimación', 60, 120
WHERE EXISTS (SELECT 1 FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner')
AND NOT EXISTS (SELECT 1 FROM techniques WHERE video_id = (SELECT id FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner') AND name = 'Aplicación de imprimación');

INSERT INTO techniques (video_id, name, start_time, end_time)
SELECT (SELECT id FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner'), 'Pintura de base uniforme', 130, 180
WHERE EXISTS (SELECT 1 FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner')
AND NOT EXISTS (SELECT 1 FROM techniques WHERE video_id = (SELECT id FROM videos WHERE video_id = 'dQw4w9WgXcQ' AND difficulty_level = 'beginner') AND name = 'Pintura de base uniforme');

INSERT INTO techniques (video_id, name, start_time, end_time)
SELECT (SELECT id FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate'), 'Técnica de lavado', 120, 180
WHERE EXISTS (SELECT 1 FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate')
AND NOT EXISTS (SELECT 1 FROM techniques WHERE video_id = (SELECT id FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate') AND name = 'Técnica de lavado');

INSERT INTO techniques (video_id, name, start_time, end_time)
SELECT (SELECT id FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate'), 'Pincel seco para resaltar bordes', 210, 300
WHERE EXISTS (SELECT 1 FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate')
AND NOT EXISTS (SELECT 1 FROM techniques WHERE video_id = (SELECT id FROM videos WHERE video_id = 'ZZ5LpwO-An4' AND difficulty_level = 'intermediate') AND name = 'Pincel seco para resaltar bordes');

INSERT INTO techniques (video_id, name, start_time, end_time)
SELECT (SELECT id FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert'), 'Efecto de fuego con pintura fluorescente', 180, 240
WHERE EXISTS (SELECT 1 FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert')
AND NOT EXISTS (SELECT 1 FROM techniques WHERE video_id = (SELECT id FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert') AND name = 'Efecto de fuego con pintura fluorescente');

INSERT INTO techniques (video_id, name, start_time, end_time)
SELECT (SELECT id FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert'), 'Efectos de agua con resina transparente', 280, 360
WHERE EXISTS (SELECT 1 FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert')
AND NOT EXISTS (SELECT 1 FROM techniques WHERE video_id = (SELECT id FROM videos WHERE video_id = '9bZkp7q19f0' AND difficulty_level = 'expert') AND name = 'Efectos de agua con resina transparente');