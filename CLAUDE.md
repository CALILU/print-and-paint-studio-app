# CLAUDE CODE - INSTRUCCIONES CRÍTICAS DE DESARROLLO

## IMPORTANTE: DIRECTORIOS DE TRABAJO

### ⚠️ ATENCIÓN CLAUDE CODE ⚠️

**ANTES DE REALIZAR CUALQUIER MODIFICACIÓN, DEBES:**

1. **IDENTIFICAR** qué aplicación se va a modificar
2. **ESTUDIAR AUTOMÁTICAMENTE** los directorios correspondientes
3. **TRABAJAR ÚNICAMENTE** en el directorio correcto

### 📁 ESTRUCTURA DE DIRECTORIOS

```
APLICACIÓN ANDROID (PaintScanner):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 C:\Paintscanner\
├── app/                    # Código fuente Android
├── gradle/                 # Configuración Gradle
└── [subdirectorios]       # ESTUDIAR TODOS

APLICACIÓN WEB (Print & Paint Studio):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 C:\Repositorio GitHub VSC\print-and-paint-studio-app\
├── app.py                  # Backend Flask
├── models.py              # Modelos SQLAlchemy
├── templates/             # Frontend HTML
├── static/                # Assets
├── docs/                  # Documentación técnica
└── [subdirectorios]       # ESTUDIAR TODOS
```

### 🔍 COMANDOS DE ESTUDIO AUTOMÁTICO

Cuando se mencione modificar la aplicación Android:
```bash
# EJECUTAR PRIMERO:
find C:\Paintscanner -type f -name "*.java" -o -name "*.kt" -o -name "*.xml" | head -50
ls -la C:\Paintscanner\app\src\main\java\
cat C:\Paintscanner\app\build.gradle
```

Cuando se mencione modificar la aplicación Web:
```bash
# EJECUTAR PRIMERO:
find "C:\Repositorio GitHub VSC\print-and-paint-studio-app" -type f -name "*.py" -o -name "*.html" | head -50
ls -la "C:\Repositorio GitHub VSC\print-and-paint-studio-app\"
cat "C:\Repositorio GitHub VSC\print-and-paint-studio-app\requirements.txt"
```

## 🚨 REGLAS CRÍTICAS

1. **NUNCA** modificar archivos en el directorio incorrecto
2. **SIEMPRE** verificar el path completo antes de editar
3. **CONFIRMAR** con el usuario si hay dudas sobre qué aplicación modificar

## 📋 CHECKLIST PRE-MODIFICACIÓN

- [ ] ¿Se identificó claramente qué aplicación modificar?
- [ ] ¿Se ejecutaron los comandos de estudio del directorio?
- [ ] ¿Se verificó que el archivo existe en el path correcto?
- [ ] ¿Se está trabajando en el directorio correcto?

## 🔐 ARCHIVOS CRÍTICOS POR APLICACIÓN

### Android (C:\Paintscanner\)
- `MainActivity.java/kt` - Actividad principal
- `AndroidManifest.xml` - Configuración de la app
- `build.gradle` - Dependencias
- `PaintDatabase.java/kt` - Base de datos local

### Web (C:\Repositorio GitHub VSC\print-and-paint-studio-app\)
- `app.py` - Rutas y lógica del servidor
- `models.py` - Modelos de base de datos
- `templates/admin/paints.html` - Interfaz de gestión
- `requirements.txt` - Dependencias Python

## 📊 ÚLTIMAS MODIFICACIONES IMPORTANTES

### 2025-07-26: Color Picker & Image Search
- **Archivos modificados**: 
  - `app.py` (nuevos endpoints)
  - `templates/admin/paints.html` (UI + JavaScript)
- **Documentación**: Ver `/docs/50-*.md`

### 2025-07-22: EAN Implementation
- **Archivos modificados**: 
  - `models.py` (campo EAN)
  - Migraciones de base de datos
- **Documentación**: Ver `/docs/47-*.md`

## ⚡ COMANDOS RÁPIDOS

```bash
# Android - Compilar
cd C:\Paintscanner && ./gradlew assembleDebug

# Web - Ejecutar servidor
cd "C:\Repositorio GitHub VSC\print-and-paint-studio-app" && python app.py

# Web - Instalar dependencias
pip install -r requirements.txt

# Git - Estado actual
git status
git log --oneline -10
```

## 🆘 TROUBLESHOOTING

Si Claude Code intenta modificar el directorio incorrecto:
1. DETENER inmediatamente
2. Verificar qué aplicación debe modificarse
3. Cambiar al directorio correcto
4. Reconfirmar antes de proceder

---

**RECORDATORIO FINAL**: Este archivo debe ser lo PRIMERO que Claude Code lea al iniciar cualquier sesión de desarrollo. La correcta identificación del directorio de trabajo es CRÍTICA para el éxito del proyecto.