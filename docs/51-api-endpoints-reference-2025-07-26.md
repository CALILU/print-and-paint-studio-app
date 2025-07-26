# API Endpoints Reference - Paint Management System
**Fecha**: 2025-07-26  
**Versión**: 1.0  
**Autor**: Analista Programador Senior

## 1. NUEVOS ENDPOINTS IMPLEMENTADOS

### 1.1 Color Preview Update

**Endpoint**: `/api/paints/update-color-preview`  
**Method**: `POST`  
**Authentication**: `@admin_required`  
**Content-Type**: `application/json`

#### Request Body:
```json
{
    "paint_id": 14546,
    "color": "#FF5733"
}
```

#### Response Success (200):
```json
{
    "success": true,
    "message": "Color preview updated successfully",
    "paint": {
        "id": 14546,
        "name": "Blanco Ink 109",
        "color_preview": "#FF5733"
    }
}
```

#### Response Error (404):
```json
{
    "success": false,
    "message": "Paint not found"
}
```

### 1.2 Image URL Update

**Endpoint**: `/api/paints/update-image-url`  
**Method**: `POST`  
**Authentication**: `@admin_required`  
**Content-Type**: `application/json`

#### Request Body:
```json
{
    "paint_id": 14546,
    "image_url": "https://example.com/paint-image.jpg"
}
```

#### Response:
```json
{
    "success": true,
    "message": "Image URL updated successfully",
    "paint": {
        "id": 14546,
        "image_url": "https://example.com/paint-image.jpg"
    }
}
```

### 1.3 Image Search

**Endpoint**: `/api/paints/search-images`  
**Method**: `POST`  
**Authentication**: `@admin_required`  
**Content-Type**: `application/json`

#### Request Body:
```json
{
    "paint_id": "14546",
    "brand": "VALLEJO",
    "name": "Blanco Ink 109",
    "page": 1
}
```

#### Response:
```json
{
    "success": true,
    "message": "Found 15 images for VALLEJO Blanco Ink",
    "paint_id": "14546",
    "search_terms": ["VALLEJO", "Blanco Ink"],
    "images": [
        {
            "url": "https://example.com/image1.jpg",
            "title": "Vallejo Model Color White",
            "source": "https://store.com",
            "width": 400,
            "height": 400,
            "site": "store.com",
            "category": "fabricantes"
        }
    ]
}
```

### 1.4 Debug Endpoints

#### 1.4.1 Test Google API
**Endpoint**: `/api/debug/test-google-api`  
**Method**: `GET`  
**Authentication**: `@admin_required`

#### Response:
```json
{
    "api_key": "AIzaSyDRLw...OnTM",
    "cx": "a4da551cd50f94b41",
    "status_code": 200,
    "headers": {...},
    "response": {
        "items": [...]
    }
}
```

#### 1.4.2 Test Color Update
**Endpoint**: `/api/debug/test-color-update/<paint_id>/<color>`  
**Method**: `GET`  
**Authentication**: `@admin_required`

## 2. MODIFICACIONES A ENDPOINTS EXISTENTES

### 2.1 Paint List Endpoint

**Endpoint**: `/api/paints`  
**Modificación**: Ahora incluye `color_preview` en la respuesta

```json
{
    "paints": [
        {
            "id": 1,
            "name": "Paint Name",
            "brand": "Brand",
            "color_preview": "#FF5733",  // Nuevo campo
            "image_url": "url"           // Actualizable
        }
    ]
}
```

## 3. ESTRUCTURA DE ERRORES

### 3.1 Códigos de Error HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | Success | Operación completada |
| 400 | Bad Request | Parámetros faltantes/inválidos |
| 401 | Unauthorized | No autenticado |
| 403 | Forbidden | Sin permisos de admin |
| 404 | Not Found | Recurso no encontrado |
| 500 | Server Error | Error interno |

### 3.2 Formato de Error Estándar

```json
{
    "success": false,
    "message": "Descripción del error",
    "error_code": "PAINT_NOT_FOUND",
    "details": {
        "field": "paint_id",
        "value": 99999
    }
}
```

## 4. RATE LIMITING

### 4.1 Google Custom Search API

- **Límite Gratuito**: 100 búsquedas/día
- **Límite por Query**: 10 resultados máximo
- **Paginación**: Hasta 100 resultados totales (10 páginas)

### 4.2 Endpoints Internos

- No hay rate limiting implementado actualmente
- Recomendación: Implementar con Flask-Limiter

## 5. AUTENTICACIÓN Y AUTORIZACIÓN

### 5.1 Decorator @admin_required

```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function
```

### 5.2 Headers Requeridos

```http
Cookie: session=<session_cookie>
Content-Type: application/json
X-Requested-With: XMLHttpRequest
```

## 6. EJEMPLOS DE USO

### 6.1 cURL Examples

#### Actualizar Color Preview:
```bash
curl -X POST https://domain.com/api/paints/update-color-preview \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"paint_id": 123, "color": "#FF5733"}'
```

#### Buscar Imágenes:
```bash
curl -X POST https://domain.com/api/paints/search-images \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"paint_id": "123", "brand": "VALLEJO", "name": "White", "page": 1}'
```

### 6.2 JavaScript Fetch Examples

```javascript
// Actualizar color
async function updateColor(paintId, color) {
    const response = await fetch('/api/paints/update-color-preview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            paint_id: paintId,
            color: color
        })
    });
    return response.json();
}

// Buscar imágenes con paginación
async function searchImages(paintId, brand, name, page = 1) {
    const response = await fetch('/api/paints/search-images', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            paint_id: paintId,
            brand: brand,
            name: name,
            page: page
        })
    });
    return response.json();
}
```

## 7. NOTAS DE IMPLEMENTACIÓN

1. Todos los endpoints requieren autenticación de administrador
2. Las respuestas siempre incluyen campo `success` booleano
3. Los IDs de pintura pueden ser string o integer
4. Las URLs de imágenes deben ser HTTPS para evitar mixed content

## 8. TESTING

### 8.1 Postman Collection

Disponible en: `/tests/postman/paint-api-collection.json`

### 8.2 Unit Tests

```python
def test_update_color_preview():
    # Test con color válido
    response = client.post('/api/paints/update-color-preview',
                          json={'paint_id': 1, 'color': '#FF5733'})
    assert response.status_code == 200
    assert response.json['success'] == True
```