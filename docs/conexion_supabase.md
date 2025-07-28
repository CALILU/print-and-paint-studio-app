# 📚 Documentación de Conexión a Supabase

## 🔐 Credenciales y URLs de Acceso

### 1. **URL Base de Supabase**
```
https://qzjhlktrosfrurwthvkw.supabase.co
```

### 2. **URL de Storage (S3-compatible)**
```
https://qzjhlktrosfrurwthvkw.supabase.co/storage/v1/s3
```

### 3. **Claves de API**

#### **Clave Anónima (anon)**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6amhsa3Ryb3NmcnVyd3Rodmt3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4NTExNDQsImV4cCI6MjA2ODQyNzE0NH0.s473C3yizumYy4P1a0hqleOpLp8EOENk0dPPXACqpcI
```

#### **Clave de Servicio (service_role)**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6amhsa3Ryb3NmcnVyd3Rodmt3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg1MTE0NCwiZXhwIjoyMDY4NDI3MTQ0fQ.eanEY-q6pv2qQaF3tIsrD1Tx-cxqfyspdU4kbvTbK44
```

### 4. **Credenciales de Acceso S3**
- **ID de clave de acceso**: `438c9d7f194720325d76aa138feea35e`
- **Clave de acceso secreta**: `f4f44836a2339e26282f45ef0aa11460ac3ce700c06084bfa184b8fbdd272593`

---

## 🗄️ Base de Datos Railway

### **URL de API**
```
https://print-and-paint-studio-app-production.up.railway.app
```

### **API Key**
```
print_and_paint_secret_key_2025
```

---

## 📦 Estructura de Storage en Supabase

### **Bucket Principal**
```
paint-images
```

### **Directorios**
```
paint-images/
├── AK/          # Imágenes de productos AK
├── SCALE/       # Imágenes de productos Scale75
├── VALLEJO/     # Imágenes de productos Vallejo
└── ...          # Otros fabricantes
```

---

## 🔧 Ejemplos de Conexión

### **1. Conexión con Python (requests)**

```python
import requests

# Configuración
SUPABASE_URL = "https://qzjhlktrosfrurwthvkw.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6amhsa3Ryb3NmcnVyd3Rodmt3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg1MTE0NCwiZXhwIjoyMDY4NDI3MTQ0fQ.eanEY-q6pv2qQaF3tIsrD1Tx-cxqfyspdU4kbvTbK44"
BUCKET_NAME = "paint-images"

# Headers para autenticación
headers = {
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'image/jpeg'
}

# Subir archivo
def subir_archivo(local_path, remote_path):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{remote_path}"
    with open(local_path, 'rb') as file:
        response = requests.post(url, headers=headers, data=file)
    return response.status_code == 200

# Listar archivos
def listar_archivos(prefix=""):
    url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}"
    headers_list = {
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    data = {"prefix": prefix, "limit": 1000}
    response = requests.post(url, json=data, headers=headers_list)
    return response.json()

# Obtener URL pública
def obtener_url_publica(file_path):
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_path}"
```

### **2. Conexión con boto3 (S3-compatible)**

```python
import boto3

# Configuración S3
s3_client = boto3.client(
    's3',
    endpoint_url='https://qzjhlktrosfrurwthvkw.supabase.co/storage/v1/s3',
    aws_access_key_id='438c9d7f194720325d76aa138feea35e',
    aws_secret_access_key='f4f44836a2339e26282f45ef0aa11460ac3ce700c06084bfa184b8fbdd272593',
    region_name='us-east-1'  # Región requerida aunque no se use
)

# Subir archivo
s3_client.upload_file(
    'local_file.jpg',
    'paint-images',
    'AK/AK_11001.jpg'
)

# Listar archivos
response = s3_client.list_objects_v2(
    Bucket='paint-images',
    Prefix='AK/'
)
```

---

## 🔄 Sincronización Railway ↔ Supabase

### **Actualizar URLs en Railway**

```python
import requests

RAILWAY_API_BASE = "https://print-and-paint-studio-app-production.up.railway.app"
RAILWAY_API_KEY = "print_and_paint_secret_key_2025"

def actualizar_imagen_url(paint_id, nueva_url):
    headers = {
        'X-API-Key': RAILWAY_API_KEY,
        'Content-Type': 'application/json'
    }
    
    url = f"{RAILWAY_API_BASE}/api/paints/{paint_id}"
    data = {'image_url': nueva_url}
    
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200
```

---

## 📊 Rutas y Directorios Locales

### **Directorio Principal**
```
C:\descargar_imagenes\
```

### **Subdirectorios de Imágenes**
```
C:\descargar_imagenes\json imagenes goblintrader\
├── ak\imagenes\                    # Imágenes AK descargadas
├── json_scale\imagenes\            # Imágenes Scale75
└── vallejo\imagenes\               # Imágenes Vallejo
```

### **Scripts de Conexión**
```
C:\descargar_imagenes\
├── subir_imagenes_ak_supabase.py
├── verificar_inconsistencias_supabase.py
├── actualizar_urls_railway.py
└── download_scale75_selenium_windows.py
```

---

## 🛡️ Seguridad y Mejores Prácticas

### **⚠️ IMPORTANTE**
1. **NUNCA** subir estas credenciales a repositorios públicos
2. **Usar variables de entorno** en producción
3. **Rotar las claves** periódicamente
4. **Limitar permisos** según necesidad

### **Variables de Entorno Recomendadas**
```bash
# .env file
SUPABASE_URL=https://qzjhlktrosfrurwthvkw.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
RAILWAY_API_KEY=print_and_paint_secret_key_2025
```

---

## 📝 Notas Adicionales

1. **Límites de Supabase**
   - Tamaño máximo archivo: 50MB
   - Ancho de banda: Según plan
   - Storage total: Según plan

2. **Formato de URLs Públicas**
   ```
   https://qzjhlktrosfrurwthvkw.supabase.co/storage/v1/object/public/paint-images/[DIRECTORIO]/[ARCHIVO]
   ```

3. **Convención de Nombres**
   - AK: `AK_[CODIGO].jpg` (ej: AK_AK11001.jpg)
   - Scale75: `SCALE_[CODIGO].jpg` (ej: SCALE_SCG-48.jpg)
   - Vallejo: `VALLEJO_[CODIGO].jpg` (ej: VALLEJO_70001.jpg)

---

## 🚀 Scripts Útiles

### **Verificar Conexión**
```python
def verificar_conexion_supabase():
    url = f"{SUPABASE_URL}/storage/v1/object/list/paint-images"
    headers = {'Authorization': f'Bearer {SERVICE_ROLE_KEY}'}
    
    try:
        response = requests.post(url, json={"limit": 1}, headers=headers)
        if response.status_code == 200:
            print("✅ Conexión a Supabase exitosa")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
```

---

**Última actualización**: 27 de Julio 2025
**Autor**: Sistema de Gestión de Pinturas