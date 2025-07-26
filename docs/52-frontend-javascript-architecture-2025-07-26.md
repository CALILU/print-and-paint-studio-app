# Frontend JavaScript Architecture - Paint Management System
**Fecha**: 2025-07-26  
**Versión**: 1.0  
**Autor**: Analista Programador Senior

## 1. ARQUITECTURA JAVASCRIPT

### 1.1 Estructura Global de Variables

```javascript
// Image Search State Management
let currentSearchPaintId = null;    // ID de pintura actual
let currentSearchData = null;       // {paintId, brand, name}
let currentSearchPage = 1;          // Página actual de resultados
let currentSearchImages = [];       // Array acumulativo de imágenes

// Color Picker State
let currentPaintId = null;          // ID para color picker
let currentImageUrl = null;         // URL de imagen actual
let selectedColor = null;           // Color seleccionado (#RRGGBB)

// Gallery State
let allPaints = [];                 // Cache de todas las pinturas
let previousPaints = [];            // Estado anterior para comparación
```

### 1.2 Patrón de Eventos

```javascript
// Patrón 1: Event Delegation (Recomendado)
document.getElementById('paintGallery').addEventListener('click', function(e) {
    if (e.target.classList.contains('action-icon')) {
        const action = e.target.dataset.action;
        const paintId = e.target.dataset.paintId;
        handleAction(action, paintId);
    }
});

// Patrón 2: Inline Handlers (Usado por compatibilidad)
<i class="bi bi-eyedropper" onclick="openColorPicker(${paint.id}, '${paint.image_url}')"></i>
<i class="bi bi-search" onclick="openImageSearch('${paint.id}', '${paint.brand}', '${paint.name}')"></i>
```

## 2. MÓDULOS FUNCIONALES

### 2.1 Color Picker Module

#### 2.1.1 Inicialización

```javascript
function openColorPicker(paintId, imageUrl) {
    currentPaintId = paintId;
    currentImageUrl = imageUrl;
    
    const modal = new bootstrap.Modal(document.getElementById('colorPickerModal'));
    modal.show();
    
    setTimeout(() => loadImageToCanvas(), 300);
}
```

#### 2.1.2 Canvas Management

```javascript
function loadImageToCanvas() {
    const canvas = document.getElementById('colorCanvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const img = new Image();
    
    img.crossOrigin = 'anonymous';
    
    img.onload = function() {
        // Escalar imagen manteniendo aspecto
        const maxWidth = 500;
        const scale = maxWidth / img.width;
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    
    // Manejo de CORS
    if (isExternalUrl(currentImageUrl)) {
        img.src = `/proxy/image?url=${encodeURIComponent(currentImageUrl)}`;
    } else {
        img.src = currentImageUrl;
    }
}
```

#### 2.1.3 Color Extraction

```javascript
// Throttling para performance
const throttle = (func, delay) => {
    let timeoutId;
    let lastExecTime = 0;
    return function(...args) {
        const currentTime = Date.now();
        if (currentTime - lastExecTime > delay) {
            func.apply(this, args);
            lastExecTime = currentTime;
        }
    };
};

// Event handler con throttling
canvas.addEventListener('mousemove', throttle(function(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const pixelData = ctx.getImageData(x, y, 1, 1).data;
    const hex = rgbToHex(pixelData[0], pixelData[1], pixelData[2]);
    
    updateColorPreview(hex);
}, 50));
```

### 2.2 Image Search Module

#### 2.2.1 Search Initialization

```javascript
function openImageSearch(paintId, brand, name) {
    // Reset state
    currentSearchPaintId = paintId;
    currentSearchData = { paintId, brand, name };
    currentSearchPage = 1;
    currentSearchImages = [];
    
    // UI Setup
    const modal = new bootstrap.Modal(document.getElementById('imageSearchModal'));
    modal.show();
    
    // Auto-search
    setTimeout(() => searchImages(), 500);
}
```

#### 2.2.2 API Communication

```javascript
async function searchImages() {
    const requestData = {
        paint_id: currentSearchPaintId,
        brand: currentSearchData.brand,
        name: currentSearchData.name,
        page: currentSearchPage
    };
    
    try {
        const response = await fetch('/api/paints/search-images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            handleSearchResults(result.images);
        }
    } catch (error) {
        console.error('Search error:', error);
        showError('Error al buscar imágenes');
    }
}
```

#### 2.2.3 Result Management

```javascript
function handleSearchResults(newImages) {
    if (currentSearchPage === 1) {
        currentSearchImages = newImages;
    } else {
        currentSearchImages = [...currentSearchImages, ...newImages];
    }
    
    displayImageGallery(currentSearchImages);
    updateLoadMoreButton(newImages.length);
}

function displayImageGallery(images) {
    const gallery = document.getElementById('imageGallery');
    gallery.innerHTML = '';
    
    images.forEach((image, index) => {
        const card = createImageCard(image, index);
        gallery.appendChild(card);
    });
}
```

### 2.3 Utility Functions

#### 2.3.1 Color Utilities

```javascript
function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b)
        .toString(16).slice(1).toUpperCase();
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}
```

#### 2.3.2 URL Utilities

```javascript
function isExternalUrl(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname !== window.location.hostname;
    } catch {
        return false;
    }
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
```

## 3. ERROR HANDLING

### 3.1 Global Error Handler

```javascript
window.addEventListener('error', function(e) {
    console.error('Global error:', e);
    
    // Específico para errores de imagen
    if (e.target.tagName === 'IMG') {
        handleImageError(e.target);
    }
});

function handleImageError(imgElement, urlPreview) {
    imgElement.parentElement.innerHTML = `
        <div class="error-placeholder">
            <i class="bi bi-image text-muted"></i>
            <small>Error al cargar imagen</small>
        </div>
    `;
}
```

### 3.2 API Error Handling

```javascript
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Unknown error');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}
```

## 4. PERFORMANCE OPTIMIZATION

### 4.1 Debouncing & Throttling

```javascript
// Debounce para inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Uso en búsqueda
const debouncedSearch = debounce(searchImages, 300);
```

### 4.2 Image Lazy Loading

```javascript
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            observer.unobserve(img);
        }
    });
});

document.querySelectorAll('img.lazy').forEach(img => {
    imageObserver.observe(img);
});
```

## 5. MODAL LIFECYCLE

### 5.1 Bootstrap Modal Events

```javascript
// Limpieza al cerrar modales
document.getElementById('colorPickerModal').addEventListener('hidden.bs.modal', function() {
    // Limpiar canvas
    const canvas = document.getElementById('colorCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Reset variables
    currentPaintId = null;
    currentImageUrl = null;
    selectedColor = null;
});

document.getElementById('imageSearchModal').addEventListener('hidden.bs.modal', function() {
    // Reset search state
    currentSearchPaintId = null;
    currentSearchData = null;
    currentSearchPage = 1;
    currentSearchImages = [];
    
    // Limpiar UI
    document.getElementById('imageGallery').innerHTML = '';
    document.getElementById('loadMoreContainer').style.display = 'none';
});
```

## 6. TESTING & DEBUG

### 6.1 Console Logging Strategy

```javascript
// Logging levels
const LOG_LEVELS = {
    DEBUG: '🐛',
    INFO: '📘',
    SUCCESS: '✅',
    WARNING: '⚠️',
    ERROR: '❌'
};

function log(level, module, message, data = null) {
    if (process.env.NODE_ENV === 'production' && level === 'DEBUG') return;
    
    const prefix = `${LOG_LEVELS[level]} [${module}]`;
    
    if (data) {
        console.log(prefix, message, data);
    } else {
        console.log(prefix, message);
    }
}

// Uso
log('INFO', 'IMAGE SEARCH', 'Starting search', { page: 1 });
```

### 6.2 Debug Mode

```javascript
// Enable debug mode
window.DEBUG_MODE = localStorage.getItem('debug') === 'true';

function debug(...args) {
    if (window.DEBUG_MODE) {
        console.log('[DEBUG]', ...args);
    }
}
```

## 7. BROWSER COMPATIBILITY

### 7.1 Feature Detection

```javascript
// Canvas support
if (!document.createElement('canvas').getContext) {
    showError('Tu navegador no soporta Canvas');
    return;
}

// IntersectionObserver support
if (!('IntersectionObserver' in window)) {
    // Fallback to eager loading
    document.querySelectorAll('img.lazy').forEach(img => {
        img.src = img.dataset.src;
    });
}
```

### 7.2 Polyfills

```javascript
// Object.assign polyfill
if (!Object.assign) {
    Object.assign = function(target, ...sources) {
        sources.forEach(source => {
            Object.keys(source).forEach(key => {
                target[key] = source[key];
            });
        });
        return target;
    };
}
```

## 8. SECURITY CONSIDERATIONS

### 8.1 XSS Prevention

```javascript
// Siempre escapar HTML dinámico
function createSafeHTML(template, data) {
    return template.replace(/\${(\w+)}/g, (match, key) => {
        return escapeHtml(data[key] || '');
    });
}
```

### 8.2 CSRF Protection

```javascript
// Include CSRF token in requests
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content;
}

fetch(url, {
    headers: {
        'X-CSRF-Token': getCSRFToken()
    }
});
```