# 👨‍💻 Guía de Integración para Desarrolladores

## 🎯 Objetivo
Esta guía proporciona instrucciones técnicas detalladas para integrar nuevas funcionalidades en el ecosistema Print & Paint Studio.

---

## 🔧 Configuración del Entorno de Desarrollo

### **1. Requisitos Previos**

#### **Python (Scripts ETL)**
```bash
# Windows
python --version  # Python 3.8+
pip install pandas requests cloudscraper python-dotenv

# WSL/Linux
python3 --version
pip3 install pandas requests cloudscraper python-dotenv
```

#### **Node.js (Aplicación Web)**
```bash
node --version  # Node 16+
npm --version   # npm 8+
```

#### **Android Studio (Aplicación Móvil)**
- Android Studio Arctic Fox o superior
- SDK Android 30+
- Kotlin 1.5+

### **2. Variables de Entorno**

#### **Archivo `.env` para Scripts Python**
```bash
# C:\descargar_imagenes\.env
RAILWAY_API_KEY=print_and_paint_secret_key_2025
RAILWAY_API_BASE=https://print-and-paint-studio-app-production.up.railway.app
SUPABASE_URL=https://qzjhlktrosfrurwthvkw.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### **Archivo `.env.local` para Next.js**
```bash
# C:\Repositorio GitHub VSC\print-and-paint-studio-app\.env.local
DATABASE_URL=postgresql://user:pass@host:5432/railway
NEXT_PUBLIC_SUPABASE_URL=https://qzjhlktrosfrurwthvkw.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
API_KEY=print_and_paint_secret_key_2025
```

---

## 📦 Módulos y Librerías Principales

### **1. Cliente Railway API (Python)**

```python
# railway_client.py
import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class RailwayClient:
    def __init__(self):
        self.base_url = os.getenv('RAILWAY_API_BASE')
        self.api_key = os.getenv('RAILWAY_API_KEY')
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_paints(self, brand: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Obtener pinturas con filtros opcionales"""
        params = {'limit': limit}
        if brand:
            params['brand'] = brand
        
        response = requests.get(
            f"{self.base_url}/api/paints",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def update_paint(self, paint_id: int, data: Dict) -> Dict:
        """Actualizar una pintura específica"""
        response = requests.put(
            f"{self.base_url}/api/paints/{paint_id}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def create_paint(self, data: Dict) -> Dict:
        """Crear nueva pintura"""
        response = requests.post(
            f"{self.base_url}/api/paints",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
```

### **2. Cliente Supabase Storage (Python)**

```python
# supabase_storage.py
import requests
import os
from pathlib import Path
from typing import Optional

class SupabaseStorage:
    def __init__(self):
        self.base_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.bucket = 'paint-images'
        self.headers = {
            'Authorization': f'Bearer {self.service_key}'
        }
    
    def upload_image(self, local_path: str, remote_path: str) -> bool:
        """Subir imagen a Supabase Storage"""
        headers = self.headers.copy()
        headers['Content-Type'] = 'image/jpeg'
        
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{remote_path}"
        
        with open(local_path, 'rb') as file:
            response = requests.post(url, headers=headers, data=file)
        
        return response.status_code in [200, 201]
    
    def get_public_url(self, file_path: str) -> str:
        """Obtener URL pública de una imagen"""
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{file_path}"
    
    def file_exists(self, file_path: str) -> bool:
        """Verificar si un archivo existe"""
        url = f"{self.base_url}/storage/v1/object/info/{self.bucket}/{file_path}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200
```

### **3. Integración Next.js (TypeScript)**

```typescript
// lib/api-client.ts
import { Paint } from '@/types'

const API_KEY = process.env.API_KEY || ''
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || ''

export class ApiClient {
  private headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }

  async getPaints(filters?: { brand?: string; limit?: number }): Promise<Paint[]> {
    const params = new URLSearchParams()
    if (filters?.brand) params.append('brand', filters.brand)
    if (filters?.limit) params.append('limit', filters.limit.toString())

    const response = await fetch(`${API_BASE}/api/paints?${params}`, {
      headers: this.headers
    })

    if (!response.ok) throw new Error('Failed to fetch paints')
    return response.json()
  }

  async updatePaint(id: number, data: Partial<Paint>): Promise<Paint> {
    const response = await fetch(`${API_BASE}/api/paints/${id}`, {
      method: 'PUT',
      headers: this.headers,
      body: JSON.stringify(data)
    })

    if (!response.ok) throw new Error('Failed to update paint')
    return response.json()
  }
}
```

### **4. Integración Android (Kotlin)**

```kotlin
// data/api/PaintApiService.kt
import retrofit2.http.*

interface PaintApiService {
    @GET("api/paints")
    suspend fun getPaints(
        @Header("X-API-Key") apiKey: String = BuildConfig.API_KEY,
        @Query("brand") brand: String? = null,
        @Query("limit") limit: Int = 100
    ): List<Paint>

    @PUT("api/paints/{id}")
    suspend fun updatePaint(
        @Path("id") paintId: Int,
        @Body paint: PaintUpdate,
        @Header("X-API-Key") apiKey: String = BuildConfig.API_KEY
    ): Paint

    @POST("api/paints")
    suspend fun createPaint(
        @Body paint: PaintCreate,
        @Header("X-API-Key") apiKey: String = BuildConfig.API_KEY
    ): Paint
}

// data/repository/PaintRepository.kt
class PaintRepository(private val apiService: PaintApiService) {
    suspend fun searchByEan(ean: String): Paint? {
        val paints = apiService.getPaints()
        return paints.find { it.ean == ean }
    }
    
    suspend fun searchByCode(brand: String, code: String): Paint? {
        val paints = apiService.getPaints(brand = brand)
        return paints.find { it.colorCode == code }
    }
}
```

---

## 🔄 Flujos de Trabajo Comunes

### **1. Agregar Nueva Marca de Pinturas**

#### **Paso 1: Web Scraping**
```python
# scrapers/nueva_marca_scraper.py
def scrape_nueva_marca():
    # 1. Implementar scraper específico
    # 2. Guardar en JSON con estructura estándar
    # 3. Procesar y limpiar datos
    pass
```

#### **Paso 2: Procesamiento ETL**
```python
# process_nueva_marca.py
def process_nueva_marca():
    # 1. Leer JSON
    # 2. Validar datos
    # 3. Descargar imágenes
    # 4. Subir a Supabase
    # 5. Crear registros en Railway
    pass
```

#### **Paso 3: Actualizar Frontend**
```typescript
// components/BrandFilter.tsx
const BRANDS = ['AK', 'VALLEJO', 'SCALE75', 'NUEVA_MARCA'] // Agregar aquí
```

### **2. Implementar Scanner de Códigos**

#### **Android (CameraX)**
```kotlin
// scanner/BarcodeScanner.kt
class BarcodeScanner(private val repository: PaintRepository) {
    fun processBarcode(barcode: String) {
        viewModelScope.launch {
            val paint = repository.searchByEan(barcode)
            if (paint != null) {
                // Mostrar información del producto
            } else {
                // Mostrar "producto no encontrado"
            }
        }
    }
}
```

### **3. Sincronización de Imágenes**

#### **Script de Verificación**
```python
# scripts/sync_images.py
def sync_images():
    railway_client = RailwayClient()
    supabase = SupabaseStorage()
    
    # 1. Obtener productos sin imagen
    paints = railway_client.get_paints()
    sin_imagen = [p for p in paints if not p.get('image_url')]
    
    # 2. Buscar imágenes locales
    for paint in sin_imagen:
        local_path = f"imagenes/{paint['brand']}_{paint['color_code']}.jpg"
        if os.path.exists(local_path):
            # 3. Subir a Supabase
            remote_path = f"{paint['brand']}/{paint['brand']}_{paint['color_code']}.jpg"
            if supabase.upload_image(local_path, remote_path):
                # 4. Actualizar URL en Railway
                url = supabase.get_public_url(remote_path)
                railway_client.update_paint(paint['id'], {'image_url': url})
```

---

## 🧪 Testing

### **1. Tests Unitarios Python**
```python
# tests/test_railway_client.py
import pytest
from railway_client import RailwayClient

def test_get_paints():
    client = RailwayClient()
    paints = client.get_paints(brand='AK', limit=10)
    assert len(paints) <= 10
    assert all(p['brand'] == 'AK' for p in paints)
```

### **2. Tests de Integración Next.js**
```typescript
// __tests__/api/paints.test.ts
import { createMocks } from 'node-mocks-http'
import handler from '@/pages/api/paints'

describe('/api/paints', () => {
  test('returns paints with valid API key', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      headers: { 'X-API-Key': 'valid_key' }
    })
    
    await handler(req, res)
    
    expect(res._getStatusCode()).toBe(200)
    expect(JSON.parse(res._getData())).toHaveLength(100)
  })
})
```

---

## 📈 Monitoreo y Logs

### **1. Logging en Python**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesamiento.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### **2. Monitoring en Next.js**
```typescript
// lib/monitoring.ts
export function logApiCall(endpoint: string, method: string, status: number) {
  console.log({
    timestamp: new Date().toISOString(),
    endpoint,
    method,
    status,
    environment: process.env.NODE_ENV
  })
}
```

---

## 🚀 Deployment

### **1. Scripts Python (GitHub Actions)**
```yaml
# .github/workflows/sync-images.yml
name: Sync Images
on:
  schedule:
    - cron: '0 2 * * *' # Diariamente a las 2 AM
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run sync
        env:
          RAILWAY_API_KEY: ${{ secrets.RAILWAY_API_KEY }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
        run: python scripts/sync_images.py
```

### **2. Web App (Railway)**
```bash
# Railway deployment automático desde GitHub
# Configurar en Railway Dashboard:
# - Conectar repositorio GitHub
# - Configurar variables de entorno
# - Deploy automático en push a main
```

---

## 📚 Recursos Adicionales

- [Railway Documentation](https://docs.railway.app)
- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)
- [Android CameraX](https://developer.android.com/training/camerax)

---

**Última actualización**: 27/07/2025
**Versión**: 1.0.0