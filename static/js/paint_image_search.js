// Funcionalidad de búsqueda de imágenes para pinturas
class PaintImageSearch {
    constructor() {
        this.usedImageUrls = new Set();
        this.selectedImageUrl = '';
        this.searchResults = [];
        this.isSearching = false;
        
        // Inicializar elementos UI
        this.initUI();
    }
    
    initUI() {
        // Crear el modal de búsqueda de imágenes (si no existe)
        if (!document.getElementById('imageSearchModal')) {
            const modalHTML = `
                <div class="modal fade" id="imageSearchModal" tabindex="-1" aria-labelledby="imageSearchModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="imageSearchModalLabel">Buscador de Imágenes de Pinturas</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <label for="searchBrand" class="form-label">Marca:</label>
                                        <input type="text" class="form-control" id="searchBrand" placeholder="Ej: Vallejo, Citadel, Army Painter...">
                                    </div>
                                    <div class="col-md-6">
                                        <label for="searchColorCode" class="form-label">Código del Color:</label>
                                        <input type="text" class="form-control" id="searchColorCode" placeholder="Ej: 70.951, Mephiston Red, etc...">
                                    </div>
                                </div>
                                
                                <div class="row mb-3">
                                    <div class="col-12">
                                        <button id="btnSearch" class="btn btn-primary me-2">
                                            <i class="bi bi-search me-1"></i> Buscar Imágenes
                                        </button>
                                        <button id="btnReset" class="btn btn-outline-secondary me-2">
                                            <i class="bi bi-x-circle me-1"></i> Limpiar Resultados
                                        </button>
                                    </div>
                                </div>
                                
                                <div id="statusMessage" class="alert d-none"></div>
                                
                                <div class="text-center mt-3 mb-3 d-none" id="searchLoader">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Buscando...</span>
                                    </div>
                                    <p class="mt-2">Buscando imágenes, por favor espere...</p>
                                </div>
                                
                                <div class="row mt-4" id="previewGrid" style="display:none;">
                                    <!-- Las imágenes se cargarán aquí -->
                                </div>
                                
                                <div class="row mt-4" id="selectedImageContainer" style="display:none;">
                                    <div class="col-md-6">
                                        <h5>Imagen Seleccionada</h5>
                                        <img id="selectedImage" class="img-fluid border rounded" src="" alt="Imagen de pintura">
                                        <p id="selectedImageUrl" class="small text-muted mt-2 mb-0" style="word-break: break-all;"></p>
                                    </div>
                                    <div class="col-md-6" id="colorContainer" style="display:none;">
                                        <h5>Color Extraído</h5>
                                        <div id="colorSample" style="width: 100px; height: 100px; border: 1px solid #ddd; border-radius: 5px;"></div>
                                        <div class="mt-3">
                                            <p><strong>HEX:</strong> <span id="hexValue">-</span></p>
                                            <p><strong>RGB:</strong> <span id="rgbValue">-</span></p>
                                        </div>
                                        <button id="btnApplyColor" class="btn btn-success mt-3">
                                            <i class="bi bi-check-circle me-1"></i> Aplicar Color y URL
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Añadir modal al body
            const modalContainer = document.createElement('div');
            modalContainer.innerHTML = modalHTML;
            document.body.appendChild(modalContainer.firstElementChild);
            
            // Configurar eventos
            this.setupEvents();
        }
    }
    
    setupEvents() {
        // Botón de búsqueda
        document.getElementById('btnSearch').addEventListener('click', () => this.searchImages());
        
        // Botón de reset
        document.getElementById('btnReset').addEventListener('click', () => this.resetSearch());
        
        // Botón para aplicar color y URL
        document.getElementById('btnApplyColor').addEventListener('click', () => this.applyColorAndUrl());
        
        // Enter en los campos de búsqueda
        document.getElementById('searchBrand').addEventListener('keypress', e => {
            if (e.key === 'Enter') this.searchImages();
        });
        
        document.getElementById('searchColorCode').addEventListener('keypress', e => {
            if (e.key === 'Enter') this.searchImages();
        });
    }
    
    showModal(brand, colorCode) {
        // Llenar datos del formulario
        document.getElementById('searchBrand').value = brand || '';
        document.getElementById('searchColorCode').value = colorCode || '';
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('imageSearchModal'));
        modal.show();
        
        // Iniciar búsqueda automáticamente si hay datos
        if (brand && colorCode) {
            setTimeout(() => this.searchImages(), 500);
        }
    }
    
    showStatusMessage(message, type) {
        const statusElement = document.getElementById('statusMessage');
        statusElement.textContent = message;
        statusElement.className = `alert alert-${type}`;
        statusElement.classList.remove('d-none');
    }
    
    toggleLoader(show) {
        document.getElementById('searchLoader').classList.toggle('d-none', !show);
    }
    
    async searchImages() {
        if (this.isSearching) return;
        
        const brand = document.getElementById('searchBrand').value.trim();
        const colorCode = document.getElementById('searchColorCode').value.trim();
        
        if (!brand || !colorCode) {
            this.showStatusMessage('Por favor, ingresa la marca y el código del color.', 'warning');
            return;
        }
        
        this.isSearching = true;
        document.getElementById('previewGrid').style.display = 'none';
        document.getElementById('selectedImageContainer').style.display = 'none';
        document.getElementById('colorContainer').style.display = 'none';
        this.showStatusMessage(`Buscando imágenes para: ${brand} ${colorCode}...`, 'info');
        this.toggleLoader(true);
        document.getElementById('btnSearch').disabled = true;
        
        try {
            // Enviar solicitud al servidor
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    brand: brand,
                    color_code: colorCode,
                    used_urls: Array.from(this.usedImageUrls)
                }),
            });
            
            if (!response.ok) {
                throw new Error(`Error en la búsqueda: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                this.showStatusMessage(data.error, 'danger');
                return;
            }
            
            // Limpiar grid de previsualizaciones
            const previewGrid = document.getElementById('previewGrid');
            previewGrid.innerHTML = '';
            
            if (data.images && data.images.length > 0) {
                // Guardar resultados
                this.searchResults = data.images;
                
                // Crear filas para la cuadrícula
                const row = document.createElement('div');
                row.className = 'row';
                
                // Mostrar imágenes
                data.images.forEach((image, index) => {
                    const imageUrl = image.url;
                    
                    // Crear columna para cada imagen
                    const col = document.createElement('div');
                    col.className = 'col-md-3 mb-3';
                    
                    // Crear tarjeta
                    const card = document.createElement('div');
                    card.className = 'card h-100 cursor-pointer image-preview-card';
                    card.style.cursor = 'pointer';
                    card.style.transition = 'transform 0.2s';
                    card.addEventListener('mouseover', () => {
                        card.style.transform = 'translateY(-5px)';
                        card.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                    });
                    card.addEventListener('mouseout', () => {
                        card.style.transform = 'none';
                        card.style.boxShadow = 'none';
                    });
                    
                    // Imagen
                    const imgContainer = document.createElement('div');
                    imgContainer.style.height = '150px';
                    imgContainer.style.display = 'flex';
                    imgContainer.style.alignItems = 'center';
                    imgContainer.style.justifyContent = 'center';
                    
                    const img = document.createElement('img');
                    img.src = imageUrl;
                    img.alt = `Resultado ${index + 1}`;
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '140px';
                    img.style.objectFit = 'contain';
                    img.onerror = function() {
                        this.onerror = null;
                        this.src = 'https://via.placeholder.com/150?text=Error+de+carga';
                    };
                    
                    imgContainer.appendChild(img);
                    card.appendChild(imgContainer);
                    
                    // Agregar evento de clic
                    card.addEventListener('click', () => {
                        this.selectImage(imageUrl, card);
                    });
                    
                    col.appendChild(card);
                    row.appendChild(col);
                    
                    // Añadir a la lista de URLs usadas
                    this.usedImageUrls.add(imageUrl);
                });
                
                // Añadir a la cuadrícula
                previewGrid.appendChild(row);
                previewGrid.style.display = 'block';
                
                this.showStatusMessage(`Se encontraron ${data.images.length} imágenes. Haz clic en una para seleccionarla.`, 'success');
            } else {
                this.showStatusMessage('No se encontraron imágenes para esta búsqueda.', 'warning');
            }
        } catch (error) {
            console.error('Error en la búsqueda:', error);
            this.showStatusMessage(`Error en la búsqueda: ${error.message}`, 'danger');
        } finally {
            this.isSearching = false;
            document.getElementById('btnSearch').disabled = false;
            this.toggleLoader(false);
        }
    }
    
    selectImage(imageUrl, card) {
        // Eliminar selección anterior
        const cards = document.querySelectorAll('.image-preview-card');
        cards.forEach(c => {
            c.classList.remove('border-primary');
            c.style.borderWidth = '1px';
        });
        
        // Marcar como seleccionada
        card.classList.add('border-primary');
        card.style.borderWidth = '3px';
        
        this.selectedImageUrl = imageUrl;
        
        // Mostrar imagen seleccionada
        document.getElementById('selectedImage').src = imageUrl;
        document.getElementById('selectedImageUrl').textContent = `URL: ${imageUrl}`;
        document.getElementById('selectedImageContainer').style.display = 'flex';
        
        // Extraer color
        this.extractColor(imageUrl);
    }
    
    async extractColor(imageUrl) {
        document.getElementById('colorContainer').style.display = 'none';
        this.showStatusMessage('Extrayendo color de la imagen...', 'info');
        this.toggleLoader(true);
        
        try {
            const response = await fetch('/extract-color', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_url: imageUrl
                }),
            });
            
            if (!response.ok) {
                throw new Error(`Error en la extracción: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Mostrar el color extraído
                document.getElementById('colorSample').style.backgroundColor = data.hex;
                document.getElementById('hexValue').textContent = data.hex;
                document.getElementById('rgbValue').textContent = `RGB(${data.rgb[0]}, ${data.rgb[1]}, ${data.rgb[2]})`;
                
                document.getElementById('colorContainer').style.display = 'block';
                this.showStatusMessage(`Color extraído: ${data.hex}`, 'success');
            } else {
                this.showStatusMessage(`Error al extraer color: ${data.error}`, 'danger');
            }
        } catch (error) {
            console.error('Error al extraer color:', error);
            this.showStatusMessage(`Error al extraer color: ${error.message}`, 'danger');
        } finally {
            this.toggleLoader(false);
        }
    }
    
    applyColorAndUrl() {
        const hexColor = document.getElementById('hexValue').textContent;
        
        if (!this.selectedImageUrl || !hexColor || hexColor === '-') {
            this.showStatusMessage('No hay color o imagen seleccionada para aplicar.', 'danger');
            return;
        }
        
        try {
            console.log("Enviando mensaje a la ventana principal:", {
                type: 'colorExtraido',
                hexColor: hexColor,
                imageUrl: this.selectedImageUrl
            });
            
            // Enviar mensaje a la ventana principal
            if (window.opener && !window.opener.closed) {
                window.opener.postMessage({
                    type: 'colorExtraido',
                    hexColor: hexColor,
                    imageUrl: this.selectedImageUrl
                }, '*');
                
                this.showStatusMessage('¡Color y URL aplicados al formulario con éxito!', 'success');
                
                // Cerrar ventana después de un breve retraso
                setTimeout(() => {
                    window.close();
                }, 1000);
            } else {
                // Si no podemos comunicarnos con la ventana principal
                // mostrar el mensaje y dejar que el usuario cierre manualmente
                this.showStatusMessage('No se pudo comunicar con la ventana principal. Pulse "Volver" para regresar al formulario.', 'warning');
            }
        } catch (error) {
            console.error("Error al aplicar color y URL:", error);
            this.showStatusMessage(`Error al aplicar color: ${error.message}`, 'danger');
        }
    }

// Inicializar al cargar el documento
document.addEventListener('DOMContentLoaded', () => {
    // Crear instancia global
    window.paintImageSearch = new PaintImageSearch();
    
    // Modificar el botón de búsqueda existente
    const buscarImagenBtn = document.getElementById('buscarImagenBtn');
    if (buscarImagenBtn) {
        buscarImagenBtn.removeEventListener('click', originalBuscarImagenHandler);
        buscarImagenBtn.addEventListener('click', function() {
            const brand = document.getElementById('brand').value;
            const colorCode = document.getElementById('color_code').value;
            
            if (!brand || !colorCode) {
                alert('Por favor, ingrese la marca y el código de color antes de buscar la imagen.');
                return;
            }
            
            // Abrir el modal de búsqueda de imágenes
            window.paintImageSearch.showModal(brand, colorCode);
        });
    }
});

// Variable para guardar el manejador original del botón (por si acaso)
let originalBuscarImagenHandler = null;