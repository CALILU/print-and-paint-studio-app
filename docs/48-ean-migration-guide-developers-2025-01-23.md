# 🔄 GUÍA DE MIGRACIÓN EAN - DESARROLLADORES

**Fecha**: 2025-01-23  
**Tipo**: Migration Guide  
**Aplicación**: Sistema Híbrido Android + Web  
**Prioridad**: Alta - Implementación inmediata requerida  

---

## 🚨 **INSTRUCCIONES CRÍTICAS PARA CLAUDE CODE**

### **⚠️ ANTES DE IMPLEMENTAR CUALQUIER CAMBIO:**

1. **VERIFICAR DIRECTORIO DE TRABAJO:**
   ```bash
   pwd  # CONFIRMAR ubicación actual
   
   # Para Android:
   # Debe mostrar: C:\Paintscanner
   
   # Para Web:
   # Debe mostrar: C:\Repositorio GitHub VSC\print-and-paint-studio-app
   ```

2. **NUNCA modificar archivos Android desde directorio Web**
3. **NUNCA modificar archivos Web desde directorio Android**
4. **SIEMPRE verificar que estás en el directorio correcto**

---

## 📋 **CHECKLIST DE MIGRACIÓN**

### **✅ COMPLETADO (Base de Datos)**
- [x] Campo `ean VARCHAR(13)` añadido a tabla `paints`
- [x] Constraint `UNIQUE` implementado
- [x] Índice `idx_paints_ean` creado
- [x] Modelo Web actualizado en `models.py`

### **📱 PENDIENTE - APLICACIÓN ANDROID**
- [ ] **PASO 1**: Actualizar entidad Java `Paint.java`
- [ ] **PASO 2**: Modificar `PaintDao.java` - Añadir métodos EAN
- [ ] **PASO 3**: Actualizar `PaintAdapter.java` - Mostrar EAN en UI
- [ ] **PASO 4**: Modificar `EditPaintActivity.java` - Editar EAN
- [ ] **PASO 5**: Actualizar layouts XML
- [ ] **PASO 6**: Actualizar `models.py` Flask Android
- [ ] **PASO 7**: Testing y validación

### **🌐 PENDIENTE - APLICACIÓN WEB**
- [ ] **PASO 1**: Actualizar `app.py` - Endpoints EAN
- [ ] **PASO 2**: Modificar template `paints.html`
- [ ] **PASO 3**: Añadir validación JavaScript EAN
- [ ] **PASO 4**: Incluir EAN en notificaciones Android
- [ ] **PASO 5**: Testing y deployment

---

## 📱 **MIGRACIÓN ANDROID (C:\Paintscanner)**

### **PASO 1: Entidad Paint.java**

**Archivo**: `C:\Paintscanner\app\src\main\java\com\paintscanner\data\entities\Paint.java`

```java
@Entity(tableName = "paints")
public class Paint {
    @PrimaryKey
    private int id;
    
    @ColumnInfo(name = "name")
    private String name;
    
    @ColumnInfo(name = "brand")
    private String brand;
    
    @ColumnInfo(name = "color_code")
    private String colorCode;
    
    @ColumnInfo(name = "color_type")
    private String colorType;
    
    @ColumnInfo(name = "color_family")
    private String colorFamily;
    
    @ColumnInfo(name = "image_url")
    private String imageUrl;
    
    @ColumnInfo(name = "stock")
    private int stock;
    
    @ColumnInfo(name = "price")
    private double price;
    
    @ColumnInfo(name = "description")
    private String description;
    
    @ColumnInfo(name = "color_preview")
    private String colorPreview;
    
    @ColumnInfo(name = "created_at")
    private String createdAt;
    
    // ⭐ NUEVO CAMPO A AÑADIR
    @ColumnInfo(name = "ean")
    private String ean;
    
    // Constructor vacío
    public Paint() {}
    
    // Constructor completo
    public Paint(int id, String name, String brand, String colorCode, 
                 String colorType, String colorFamily, String imageUrl, 
                 int stock, double price, String description, 
                 String colorPreview, String createdAt, String ean) {
        this.id = id;
        this.name = name;
        this.brand = brand;
        this.colorCode = colorCode;
        this.colorType = colorType;
        this.colorFamily = colorFamily;
        this.imageUrl = imageUrl;
        this.stock = stock;
        this.price = price;
        this.description = description;
        this.colorPreview = colorPreview;
        this.createdAt = createdAt;
        this.ean = ean;  // ⭐ NUEVO CAMPO
    }
    
    // Getters y Setters existentes...
    
    // ⭐ NUEVOS GETTER Y SETTER PARA EAN
    public String getEan() {
        return ean;
    }
    
    public void setEan(String ean) {
        this.ean = ean;
    }
    
    // toString() method - actualizar para incluir EAN
    @Override
    public String toString() {
        return "Paint{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", brand='" + brand + '\'' +
                ", colorCode='" + colorCode + '\'' +
                ", stock=" + stock +
                ", ean='" + ean + '\'' +
                '}';
    }
}
```

### **PASO 2: DAO - PaintDao.java**

**Archivo**: `C:\Paintscanner\app\src\main\java\com\paintscanner\data\dao\PaintDao.java`

```java
@Dao
public interface PaintDao {
    
    // Métodos existentes...
    @Query("SELECT * FROM paints")
    List<Paint> getAllPaints();
    
    @Query("SELECT * FROM paints WHERE id = :id")
    Paint getPaintById(int id);
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertPaint(Paint paint);
    
    @Update
    void updatePaint(Paint paint);
    
    @Delete
    void deletePaint(Paint paint);
    
    // ⭐ NUEVOS MÉTODOS PARA EAN
    @Query("SELECT * FROM paints WHERE ean = :ean LIMIT 1")
    Paint findByEan(String ean);
    
    @Query("SELECT * FROM paints WHERE ean LIKE :eanPattern")
    List<Paint> searchByEan(String eanPattern);
    
    @Query("UPDATE paints SET ean = :ean WHERE id = :paintId")
    void updateEan(int paintId, String ean);
    
    @Query("SELECT COUNT(*) FROM paints WHERE ean = :ean AND id != :excludeId")
    int countPaintsByEanExcluding(String ean, int excludeId);
    
    @Query("SELECT * FROM paints WHERE ean IS NOT NULL AND ean != ''")
    List<Paint> getPaintsWithEan();
    
    @Query("SELECT * FROM paints WHERE ean IS NULL OR ean = ''")
    List<Paint> getPaintsWithoutEan();
}
```

### **PASO 3: Adapter - PaintAdapter.java**

**Archivo**: `C:\Paintscanner\app\src\main\java\com\paintscanner\presentation\adapters\PaintAdapter.java`

```java
public class PaintAdapter extends RecyclerView.Adapter<PaintAdapter.PaintViewHolder> {
    
    // Código existente...
    
    @Override
    public void onBindViewHolder(@NonNull PaintViewHolder holder, int position) {
        Paint paint = paints.get(position);
        
        // Binding existente...
        holder.textViewName.setText(paint.getName());
        holder.textViewBrand.setText(paint.getBrand());
        holder.textViewStock.setText(String.valueOf(paint.getStock()));
        
        // ⭐ NUEVO: Mostrar EAN
        if (paint.getEan() != null && !paint.getEan().isEmpty()) {
            holder.textViewEan.setText("EAN: " + paint.getEan());
            holder.textViewEan.setVisibility(View.VISIBLE);
        } else {
            holder.textViewEan.setText("Sin EAN");
            holder.textViewEan.setVisibility(View.GONE);
        }
        
        // Resto del binding...
    }
    
    public static class PaintViewHolder extends RecyclerView.ViewHolder {
        // Views existentes...
        TextView textViewName, textViewBrand, textViewStock;
        
        // ⭐ NUEVO VIEW PARA EAN
        TextView textViewEan;
        
        public PaintViewHolder(@NonNull View itemView) {
            super(itemView);
            
            // Inicialización existente...
            textViewName = itemView.findViewById(R.id.textViewName);
            textViewBrand = itemView.findViewById(R.id.textViewBrand);
            textViewStock = itemView.findViewById(R.id.textViewStock);
            
            // ⭐ NUEVA INICIALIZACIÓN
            textViewEan = itemView.findViewById(R.id.textViewEan);
        }
    }
}
```

### **PASO 4: Layout XML - item_paint.xml**

**Archivo**: `C:\Paintscanner\app\src\main\res\layout\item_paint.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.cardview.widget.CardView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_margin="8dp"
    app:cardCornerRadius="8dp"
    app:cardElevation="4dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <!-- Contenido existente -->
        <TextView
            android:id="@+id/textViewName"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Nombre de la pintura"
            android:textSize="16sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/textViewBrand"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Marca"
            android:textSize="14sp"
            android:layout_marginTop="4dp" />

        <TextView
            android:id="@+id/textViewStock"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Stock: 0"
            android:textSize="14sp"
            android:layout_marginTop="4dp" />

        <!-- ⭐ NUEVO: TextView para EAN -->
        <TextView
            android:id="@+id/textViewEan"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="EAN: "
            android:textSize="12sp"
            android:textColor="@color/secondary_text"
            android:layout_marginTop="4dp"
            android:visibility="gone"
            android:drawableStart="@drawable/ic_barcode"
            android:drawablePadding="4dp" />

    </LinearLayout>

</androidx.cardview.widget.CardView>
```

### **PASO 5: Activity - EditPaintActivity.java**

**Archivo**: `C:\Paintscanner\app\src\main\java\com\paintscanner\presentation\activities\EditPaintActivity.java`

```java
public class EditPaintActivity extends AppCompatActivity {
    
    // Views existentes...
    private TextInputEditText editTextName, editTextBrand, editTextStock;
    
    // ⭐ NUEVO VIEW PARA EAN
    private TextInputEditText editTextEan;
    
    private Paint currentPaint;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_paint);
        
        // Inicialización existente...
        editTextName = findViewById(R.id.editTextName);
        editTextBrand = findViewById(R.id.editTextBrand);
        editTextStock = findViewById(R.id.editTextStock);
        
        // ⭐ NUEVA INICIALIZACIÓN
        editTextEan = findViewById(R.id.editTextEan);
        
        // Setup validation para EAN
        setupEanValidation();
        
        // Cargar datos si es edición
        loadPaintData();
    }
    
    // ⭐ NUEVO: Validación EAN
    private void setupEanValidation() {
        editTextEan.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            
            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                validateEan(s.toString());
            }
            
            @Override
            public void afterTextChanged(Editable s) {}
        });
    }
    
    // ⭐ NUEVO: Método de validación EAN
    private void validateEan(String ean) {
        if (ean.isEmpty()) {
            // EAN vacío es válido
            editTextEan.setError(null);
            return;
        }
        
        if (!ean.matches("^[0-9]{8,13}$")) {
            editTextEan.setError("EAN debe tener 8 o 13 dígitos numéricos");
            return;
        }
        
        // Verificar si EAN ya existe (async)
        checkEanExists(ean);
    }
    
    // ⭐ NUEVO: Verificar EAN duplicado
    private void checkEanExists(String ean) {
        // Ejecutar en background thread
        new Thread(() -> {
            PaintDao paintDao = // obtener DAO
            int count = paintDao.countPaintsByEanExcluding(ean, 
                currentPaint != null ? currentPaint.getId() : -1);
            
            runOnUiThread(() -> {
                if (count > 0) {
                    editTextEan.setError("Este EAN ya existe en otra pintura");
                } else {
                    editTextEan.setError(null);
                }
            });
        }).start();
    }
    
    private void loadPaintData() {
        if (currentPaint != null) {
            // Cargar datos existentes...
            editTextName.setText(currentPaint.getName());
            editTextBrand.setText(currentPaint.getBrand());
            editTextStock.setText(String.valueOf(currentPaint.getStock()));
            
            // ⭐ NUEVO: Cargar EAN
            editTextEan.setText(currentPaint.getEan() != null ? currentPaint.getEan() : "");
        }
    }
    
    private void savePaint() {
        // Validaciones existentes...
        String name = editTextName.getText().toString().trim();
        String brand = editTextBrand.getText().toString().trim();
        String stockText = editTextStock.getText().toString().trim();
        
        // ⭐ NUEVO: Obtener EAN
        String ean = editTextEan.getText().toString().trim();
        
        // Validar EAN si no está vacío
        if (!ean.isEmpty() && !ean.matches("^[0-9]{8,13}$")) {
            editTextEan.setError("EAN debe tener 8 o 13 dígitos numéricos");
            return;
        }
        
        // Crear/actualizar pintura
        if (currentPaint == null) {
            currentPaint = new Paint();
        }
        
        currentPaint.setName(name);
        currentPaint.setBrand(brand);
        currentPaint.setStock(Integer.parseInt(stockText));
        
        // ⭐ NUEVO: Establecer EAN
        currentPaint.setEan(ean.isEmpty() ? null : ean);
        
        // Guardar en base de datos...
        savePaintToDatabase(currentPaint);
    }
}
```

### **PASO 6: Layout - activity_edit_paint.xml**

**Archivo**: `C:\Paintscanner\app\src\main\res\layout\activity_edit_paint.xml`

```xml
<!-- Contenido existente... -->

<com.google.android.material.textfield.TextInputLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:hint="Stock">
    
    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/editTextStock"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:inputType="number" />
        
</com.google.android.material.textfield.TextInputLayout>

<!-- ⭐ NUEVO: Campo EAN -->
<com.google.android.material.textfield.TextInputLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginTop="16dp"
    android:hint="Código EAN (opcional)"
    app:helperText="Código de barras EAN de 8 o 13 dígitos"
    app:counterEnabled="true"
    app:counterMaxLength="13">
    
    <com.google.android.material.textfield.TextInputEditText
        android:id="@+id/editTextEan"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:inputType="number"
        android:maxLength="13"
        android:drawableStart="@drawable/ic_barcode"
        android:drawablePadding="8dp" />
        
</com.google.android.material.textfield.TextInputLayout>

<!-- Resto del layout... -->
```

### **PASO 7: Models Flask Android**

**Archivo**: `C:\Paintscanner\models.py`

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Paint(db.Model):
    __tablename__ = 'paints'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    brand = db.Column(db.Text, nullable=False)
    color_code = db.Column(db.Text)
    color_type = db.Column(db.Text)
    color_family = db.Column(db.Text)
    image_url = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    color_preview = db.Column(db.Text)
    
    # ⭐ NUEVO CAMPO EAN
    ean = db.Column(db.String(13), unique=True, index=True)
    
    sync_status = db.Column(db.String(20), default='synced')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert Paint object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'color_code': self.color_code,
            'color_type': self.color_type,
            'color_family': self.color_family,
            'description': self.description,
            'stock': self.stock,
            'price': self.price,
            'color_preview': self.color_preview,
            'image_url': self.image_url,
            'ean': self.ean,  # ⭐ INCLUIR EAN
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Paint {self.brand} - {self.name} (EAN: {self.ean})>'
```

---

## 🌐 **MIGRACIÓN WEB (C:\Repositorio GitHub VSC\print-and-paint-studio-app)**

### **PASO 1: Endpoints Flask - app.py**

**Archivo**: `C:\Repositorio GitHub VSC\print-and-paint-studio-app\app.py`

**Modificar función `update_paint()` (línea ~2800):**

```python
@app.route('/admin/paints/<int:id>', methods=['PUT'])
@admin_required
def update_paint(id):
    """Update paint with EAN support"""
    try:
        data = request.get_json()
        paint = Paint.query.get_or_404(id)
        
        # Store old values for notification
        old_stock = paint.stock
        old_ean = paint.ean
        
        # Update fields including new EAN
        paint.name = data.get('name', paint.name)
        paint.brand = data.get('brand', paint.brand)
        paint.color_code = data.get('color_code', paint.color_code)
        paint.color_type = data.get('color_type', paint.color_type)
        paint.color_family = data.get('color_family', paint.color_family)
        paint.stock = data.get('stock', paint.stock)
        paint.price = data.get('price', paint.price)
        paint.description = data.get('description', paint.description)
        paint.color_preview = data.get('color_preview', paint.color_preview)
        
        # ⭐ NUEVO: Actualizar campo EAN
        new_ean = data.get('ean', paint.ean)
        if new_ean != paint.ean:
            # Validar EAN format si se proporciona
            if new_ean and new_ean.strip():
                ean_clean = new_ean.strip()
                if not ean_clean.isdigit() or len(ean_clean) not in [8, 13]:
                    return jsonify({'error': 'EAN debe ser de 8 o 13 dígitos numéricos'}), 400
                
                # Verificar unicidad
                existing_paint = Paint.query.filter_by(ean=ean_clean).first()
                if existing_paint and existing_paint.id != id:
                    return jsonify({'error': f'EAN {ean_clean} ya existe en otra pintura'}), 400
                
                paint.ean = ean_clean
            else:
                paint.ean = None
        
        db.session.commit()
        
        # Send notification if stock changed
        if 'stock' in data and data.get('stock') != old_stock:
            send_android_notification(id, 'stock_updated', {
                'paint_id': paint.id,
                'paint_name': paint.name,
                'old_stock': old_stock,
                'new_stock': paint.stock,
                'ean': paint.ean,  # ⭐ INCLUIR EAN EN NOTIFICACIÓN
                'source': 'web_admin'
            })
        
        return jsonify({
            'success': True,
            'paint': paint.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating paint {id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ⭐ NUEVO ENDPOINT: Búsqueda por EAN
@app.route('/admin/paints/search/ean/<string:ean>', methods=['GET'])
@admin_required
def search_paint_by_ean(ean):
    """Search paint by EAN code"""
    try:
        # Validar formato EAN
        if not ean.isdigit() or len(ean) not in [8, 13]:
            return jsonify({
                'success': False,
                'error': 'EAN debe ser de 8 o 13 dígitos numéricos'
            }), 400
        
        paint = Paint.query.filter_by(ean=ean).first()
        
        if paint:
            return jsonify({
                'success': True,
                'paint': paint.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Pintura no encontrada con EAN: {ean}'
            }), 404
            
    except Exception as e:
        app.logger.error(f"Error searching paint by EAN {ean}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ⭐ NUEVO ENDPOINT: Validar EAN único
@app.route('/admin/paints/validate-ean', methods=['POST'])
@admin_required
def validate_ean():
    """Validate if EAN is unique"""
    try:
        data = request.get_json()
        ean = data.get('ean', '').strip()
        exclude_id = data.get('exclude_id')  # Para excluir la pintura actual en edición
        
        if not ean:
            return jsonify({'valid': True, 'message': 'EAN vacío es válido'})
        
        # Validar formato
        if not ean.isdigit() or len(ean) not in [8, 13]:
            return jsonify({
                'valid': False,
                'message': 'EAN debe ser de 8 o 13 dígitos numéricos'
            })
        
        # Verificar unicidad
        query = Paint.query.filter_by(ean=ean)
        if exclude_id:
            query = query.filter(Paint.id != exclude_id)
        
        existing_paint = query.first()
        
        if existing_paint:
            return jsonify({
                'valid': False,
                'message': f'EAN {ean} ya existe en pintura: {existing_paint.name}'
            })
        else:
            return jsonify({
                'valid': True,
                'message': 'EAN disponible'
            })
            
    except Exception as e:
        app.logger.error(f"Error validating EAN: {str(e)}")
        return jsonify({'valid': False, 'error': str(e)}), 500
```

### **PASO 2: Template HTML - paints.html**

**Archivo**: `C:\Repositorio GitHub VSC\print-and-paint-studio-app\templates\admin\paints.html`

**Modificar tabla de pinturas:**

```html
<!-- En la sección de tabla -->
<table class="table table-striped table-hover" id="paintsTable">
    <thead class="table-dark">
        <tr>
            <th>ID</th>
            <th>Imagen</th>
            <th>Nombre</th>
            <th>Marca</th>
            <th>Código Color</th>
            <th>Stock</th>
            <th>Precio</th>
            <th>EAN</th> <!-- ⭐ NUEVA COLUMNA -->
            <th>Acciones</th>
        </tr>
    </thead>
    <tbody>
        {% for paint in paints %}
        <tr>
            <td>{{ paint.id }}</td>
            <td>
                <!-- Imagen existente -->
            </td>
            <td>{{ paint.name }}</td>
            <td>{{ paint.brand }}</td>
            <td>{{ paint.color_code or 'N/A' }}</td>
            <td>
                <span class="badge bg-primary">{{ paint.stock }}</span>
            </td>
            <td>
                {% if paint.price %}
                    ${{ "%.2f"|format(paint.price) }}
                {% else %}
                    N/A
                {% endif %}
            </td>
            <!-- ⭐ NUEVA CELDA EAN -->
            <td>
                {% if paint.ean %}
                    <span class="badge bg-info">
                        <i class="fas fa-barcode"></i> {{ paint.ean }}
                    </span>
                {% else %}
                    <span class="text-muted">Sin EAN</span>
                {% endif %}
            </td>
            <td>
                <!-- Botones de acción existentes -->
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Modificar modal de edición:**

```html
<!-- En el modal de edición añadir después del campo precio -->
<div class="mb-3">
    <label for="editEan" class="form-label">
        <i class="fas fa-barcode"></i> Código EAN
    </label>
    <input type="text" class="form-control" id="editEan" 
           maxlength="13" pattern="[0-9]{8,13}"
           placeholder="Código EAN de 8 o 13 dígitos (opcional)">
    <div class="form-text">
        Código de barras EAN único del producto. Deja vacío si no aplica.
    </div>
    <div class="invalid-feedback" id="eanError"></div>
</div>
```

**Añadir JavaScript para EAN:**

```html
<script>
// ⭐ NUEVO: Validación EAN en tiempo real
document.getElementById('editEan').addEventListener('input', function(e) {
    const ean = e.target.value.trim();
    const errorDiv = document.getElementById('eanError');
    
    // Reset states
    e.target.classList.remove('is-valid', 'is-invalid');
    errorDiv.textContent = '';
    
    if (ean === '') {
        // EAN vacío es válido
        e.target.classList.add('is-valid');
        return;
    }
    
    // Validar formato
    if (!/^[0-9]{8,13}$/.test(ean)) {
        e.target.classList.add('is-invalid');
        errorDiv.textContent = 'EAN debe ser de 8 o 13 dígitos numéricos';
        return;
    }
    
    // Validar unicidad (debounced)
    clearTimeout(window.eanValidationTimeout);
    window.eanValidationTimeout = setTimeout(() => {
        validateEanUniqueness(ean, e.target, errorDiv);
    }, 500);
});

// ⭐ NUEVO: Función para validar unicidad EAN
function validateEanUniqueness(ean, inputElement, errorDiv) {
    const currentPaintId = document.getElementById('editPaintId').value;
    
    fetch('/admin/paints/validate-ean', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ean: ean,
            exclude_id: currentPaintId ? parseInt(currentPaintId) : null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            inputElement.classList.remove('is-invalid');
            inputElement.classList.add('is-valid');
            errorDiv.textContent = '';
        } else {
            inputElement.classList.remove('is-valid');
            inputElement.classList.add('is-invalid');
            errorDiv.textContent = data.message;
        }
    })
    .catch(error => {
        console.error('Error validating EAN:', error);
        inputElement.classList.add('is-invalid');
        errorDiv.textContent = 'Error validando EAN';
    });
}

// ⭐ NUEVO: Función de búsqueda por EAN
function searchByEan() {
    const ean = prompt('Ingrese el código EAN a buscar:');
    if (!ean || ean.trim() === '') return;
    
    const cleanEan = ean.trim();
    
    // Validar formato
    if (!/^[0-9]{8,13}$/.test(cleanEan)) {
        alert('EAN debe ser de 8 o 13 dígitos numéricos');
        return;
    }
    
    // Buscar pintura
    fetch(`/admin/paints/search/ean/${cleanEan}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Resaltar la pintura encontrada en la tabla
            highlightPaintInTable(data.paint.id);
            // Opcionalmente abrir modal de edición
            if (confirm(`Pintura encontrada: ${data.paint.name}. ¿Desea editarla?`)) {
                editPaint(data.paint.id);
            }
        } else {
            alert(data.message || 'Pintura no encontrada');
        }
    })
    .catch(error => {
        console.error('Error searching by EAN:', error);
        alert('Error al buscar por EAN');
    });
}

// Función auxiliar para resaltar pintura en tabla
function highlightPaintInTable(paintId) {
    // Remover highlights previos
    document.querySelectorAll('.table-warning').forEach(row => {
        row.classList.remove('table-warning');
    });
    
    // Resaltar fila encontrada
    const row = document.querySelector(`tr[data-paint-id="${paintId}"]`);
    if (row) {
        row.classList.add('table-warning');
        row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Modificar función existente fillEditForm para incluir EAN
function fillEditForm(paint) {
    // Campos existentes...
    document.getElementById('editPaintId').value = paint.id;
    document.getElementById('editName').value = paint.name || '';
    document.getElementById('editBrand').value = paint.brand || '';
    document.getElementById('editColorCode').value = paint.color_code || '';
    document.getElementById('editStock').value = paint.stock || 0;
    document.getElementById('editPrice').value = paint.price || '';
    
    // ⭐ NUEVO: Campo EAN
    document.getElementById('editEan').value = paint.ean || '';
    
    // Reset validation states
    document.getElementById('editEan').classList.remove('is-valid', 'is-invalid');
    document.getElementById('eanError').textContent = '';
}

// Modificar función existente updatePaint para incluir EAN
function updatePaint() {
    const paintId = document.getElementById('editPaintId').value;
    const ean = document.getElementById('editEan').value.trim();
    
    // Validar EAN antes de enviar
    if (ean && !/^[0-9]{8,13}$/.test(ean)) {
        alert('EAN debe ser de 8 o 13 dígitos numéricos');
        return;
    }
    
    const paintData = {
        name: document.getElementById('editName').value,
        brand: document.getElementById('editBrand').value,
        color_code: document.getElementById('editColorCode').value,
        stock: parseInt(document.getElementById('editStock').value),
        price: parseFloat(document.getElementById('editPrice').value) || null,
        ean: ean || null  // ⭐ INCLUIR EAN
    };
    
    // Resto de la función updatePaint existente...
}
</script>

<!-- ⭐ NUEVO: Botón de búsqueda por EAN en toolbar -->
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Gestión de Pinturas</h2>
    <div>
        <button type="button" class="btn btn-outline-info me-2" onclick="searchByEan()">
            <i class="fas fa-barcode"></i> Buscar por EAN
        </button>
        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addPaintModal">
            <i class="fas fa-plus"></i> Añadir Pintura
        </button>
    </div>
</div>
```

---

## 🧪 **TESTING CHECKLIST**

### **📱 Testing Android**
- [ ] Compilación sin errores
- [ ] Campo EAN visible en lista de pinturas
- [ ] Edición de EAN funcional
- [ ] Validación de formato EAN (8-13 dígitos)
- [ ] Búsqueda por EAN funcional
- [ ] Sincronización con servidor incluye EAN

### **🌐 Testing Web**
- [ ] Columna EAN visible en tabla admin
- [ ] Campo EAN en modal de edición
- [ ] Validación JavaScript funcional
- [ ] Endpoint de búsqueda por EAN
- [ ] Validación de unicidad EAN
- [ ] EAN incluido en notificaciones Android

### **🔄 Testing Integración**
- [ ] Sincronización EAN Android ↔ Web
- [ ] Notificaciones incluyen campo EAN
- [ ] Constraint UNIQUE funciona correctamente
- [ ] Performance de búsquedas por EAN

---

## 🚀 **DEPLOYMENT STEPS**

### **Android Deployment**
```bash
cd "C:\Paintscanner"
./gradlew clean
./gradlew build
./gradlew installDebug  # Para testing
# Generar APK para distribución cuando todo esté probado
```

### **Web Deployment**
```bash
cd "C:\Repositorio GitHub VSC\print-and-paint-studio-app"
# Testing local
python app.py

# Deployment a Railway
git add .
git commit -m "Add EAN field support to Paint model and UI

- Add EAN column with UNIQUE constraint
- Update Paint model with EAN field
- Add EAN search functionality
- Include EAN in Android notifications
- Add EAN validation and UI components

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main  # Auto-deploy to Railway
```

---

## 📊 **SUCCESS METRICS**

### **Funcionalidad**
- ✅ EAN field visible en ambas aplicaciones
- ✅ Búsqueda por EAN <100ms response time
- ✅ Validación preventing duplicates
- ✅ Sincronización EAN Android ↔ Web
- ✅ Zero constraint violations in production

### **Performance**
- ✅ Database queries with EAN index <50ms
- ✅ UI responsive con nuevo campo
- ✅ No memory leaks from new functionality
- ✅ Network sync includes EAN without overhead

---

**🔄 Documentado por**: Claude Code Assistant  
**📅 Fecha**: 2025-01-23  
**🎯 Objetivo**: Migración EAN completa en sistema híbrido  
**📋 Próxima revisión**: Post-implementación testing results