from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time
import re
import os

def configurar_driver():
    """
    Configura y retorna el driver de Chrome con opciones optimizadas
    """
    options = webdriver.ChromeOptions()
    # Opciones para mejorar el rendimiento
    options.add_argument('--disable-images')  # No cargar imágenes para ir más rápido
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Opcional: modo headless (sin ventana del navegador)
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    return driver

def obtener_enlaces_productos(driver, url_base):
    """
    Obtiene todos los enlaces a productos desde todas las páginas
    """
    enlaces = []
    pagina_actual = 1
    
    while True:
        # Construir URL con paginación
        if pagina_actual == 1:
            url = url_base
        else:
            url = f"{url_base}page/{pagina_actual}/"
        
        print(f"\n📄 Procesando página {pagina_actual}: {url}")
        
        try:
            driver.get(url)
            # Esperar a que se carguen los productos
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "products"))
            )
            time.sleep(2)  # Pausa adicional para asegurar carga completa
            
            # Buscar enlaces a productos
            elementos_productos = driver.find_elements(By.CSS_SELECTOR, "li.product a.woocommerce-LoopProduct-link")
            
            if not elementos_productos:
                print(f"   No se encontraron productos en la página {pagina_actual}")
                break
            
            # Extraer los enlaces
            for elemento in elementos_productos:
                href = elemento.get_attribute('href')
                if href and href not in enlaces:
                    enlaces.append(href)
            
            print(f"   ✓ Encontrados {len(elementos_productos)} productos en esta página")
            
            # Verificar si hay siguiente página
            try:
                siguiente = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
                pagina_actual += 1
            except NoSuchElementException:
                print("   ✓ No hay más páginas")
                break
            
        except TimeoutException:
            print(f"   ⚠️ Timeout en página {pagina_actual}")
            break
        except Exception as e:
            print(f"   ❌ Error al procesar página {pagina_actual}: {e}")
            break
    
    return enlaces

def extraer_datos_producto(driver, url):
    """
    Extrae el código del producto y la posición del expositor
    """
    try:
        driver.get(url)
        # Esperar a que se cargue el contenido principal
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product"))
        )
        time.sleep(1)  # Pausa para asegurar carga completa
        
        # Extraer código del producto
        codigo = None
        try:
            elemento_referencia = driver.find_element(By.CSS_SELECTOR, "div.referencia")
            codigo = elemento_referencia.text.strip()
        except NoSuchElementException:
            print(f"   ⚠️ No se encontró código en: {url}")
        
        # Extraer posición en expositor
        posicion = None
        try:
            # Buscar el texto que contiene "Número de posición en expositor:"
            elementos_p = driver.find_elements(By.TAG_NAME, "p")
            for p in elementos_p:
                texto = p.text
                if "Número de posición en expositor:" in texto:
                    # Extraer el número usando regex
                    match = re.search(r'Número de posición en expositor:\s*(\d+)', texto)
                    if match:
                        posicion = match.group(1)
                    break
        except Exception as e:
            print(f"   ⚠️ Error al buscar posición: {e}")
        
        # Extraer nombre del producto (opcional, para referencia)
        nombre = ""
        try:
            elemento_nombre = driver.find_element(By.CSS_SELECTOR, "h1.product_title")
            nombre = elemento_nombre.text.strip()
        except:
            pass
        
        # Detectar la categoría del producto basándose en la URL
        categoria = ""
        if "model-color" in url.lower():
            categoria = "Model Color"
        elif "model-air" in url.lower():
            categoria = "Model Air"
        elif "game-color" in url.lower():
            categoria = "Game Color"
        elif "game-air" in url.lower():
            categoria = "Game Air"
        elif "mecha-color" in url.lower():
            categoria = "Mecha Color"
        else:
            categoria = "Otro"
        
        return {
            'codigo': codigo,
            'posicion': posicion,
            'nombre': nombre,
            'categoria': categoria,
            'url': url
        }
        
    except TimeoutException:
        print(f"   ❌ Timeout al cargar: {url}")
        return None
    except Exception as e:
        print(f"   ❌ Error al procesar producto: {e}")
        return None

def cargar_datos_existentes(archivo_csv):
    """
    Carga los códigos de productos ya existentes en el CSV
    """
    codigos_existentes = set()
    if os.path.exists(archivo_csv):
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    if 'codigo' in fila and fila['codigo']:
                        codigos_existentes.add(fila['codigo'])
            print(f"📂 Archivo CSV existente encontrado con {len(codigos_existentes)} productos")
        except Exception as e:
            print(f"⚠️ Error al leer archivo existente: {e}")
    return codigos_existentes

def main():
    """
    Función principal que coordina todo el proceso
    """
    # CONFIGURACIÓN - Cambiar aquí para diferentes categorías
    urls_categorias = [
        {
            'nombre': 'Model Air',
            'url': 'https://acrylicosvallejo.com/categoria/modelismo/model-air-2-hobby/'
        }
        # Puedes añadir más categorías aquí si necesitas procesar varias:
        # {
        #     'nombre': 'Model Color',
        #     'url': 'https://acrylicosvallejo.com/categoria/modelismo/model-color-2/'
        # }
    ]
    
    archivo_csv = "vallejo_model_color.csv"
    
    print("🚀 Iniciando web scraping de Acrílicos Vallejo")
    print("=" * 60)
    
    # Cargar datos existentes
    codigos_existentes = cargar_datos_existentes(archivo_csv)
    
    # Configurar driver
    print("\n⚙️ Configurando navegador...")
    driver = configurar_driver()
    
    try:
        todos_productos = []
        
        for categoria_info in urls_categorias:
            nombre_categoria = categoria_info['nombre']
            url_base = categoria_info['url']
            
            print(f"\n{'='*60}")
            print(f"🎨 Procesando categoría: {nombre_categoria}")
            print(f"URL: {url_base}")
            print(f"{'='*60}")
            
            # Obtener todos los enlaces a productos
            print(f"\n📋 FASE 1: Recopilando enlaces de productos de {nombre_categoria}...")
            enlaces = obtener_enlaces_productos(driver, url_base)
            print(f"\n✅ Total de productos encontrados en {nombre_categoria}: {len(enlaces)}")
            
            # Extraer datos de cada producto
            print(f"\n📋 FASE 2: Extrayendo datos de {len(enlaces)} productos...")
            print("=" * 60)
            
            productos_categoria = []
            errores = 0
            duplicados = 0
            
            for i, enlace in enumerate(enlaces, 1):
                print(f"\n[{i}/{len(enlaces)}] Procesando: {enlace}")
                
                datos = extraer_datos_producto(driver, enlace)
                
                if datos:
                    # Verificar si el producto ya existe
                    if datos['codigo'] in codigos_existentes:
                        print(f"   ⚠️ Producto ya existe en el CSV: {datos['codigo']}")
                        duplicados += 1
                    else:
                        productos_categoria.append(datos)
                        codigos_existentes.add(datos['codigo'])
                        print(f"   ✓ Código: {datos['codigo']} | Posición: {datos['posicion']} | {datos['nombre']}")
                else:
                    errores += 1
                    print(f"   ❌ Error al procesar este producto")
                
                # Pequeña pausa entre productos
                time.sleep(0.5)
            
            todos_productos.extend(productos_categoria)
            
            print(f"\n📊 Resumen {nombre_categoria}:")
            print(f"   ✅ Nuevos productos: {len(productos_categoria)}")
            print(f"   ⚠️ Duplicados omitidos: {duplicados}")
            print(f"   ❌ Errores: {errores}")
        
        # Guardar en CSV (modo append si existe, crear si no existe)
        if todos_productos:
            print("\n" + "=" * 60)
            print(f"💾 Añadiendo {len(todos_productos)} nuevos productos a {archivo_csv}...")
            
            # Determinar si el archivo existe y tiene encabezados
            archivo_existe = os.path.exists(archivo_csv) and os.path.getsize(archivo_csv) > 0
            
            with open(archivo_csv, 'a', newline='', encoding='utf-8') as archivo:
                campos = ['codigo', 'posicion', 'nombre', 'categoria', 'url']
                writer = csv.DictWriter(archivo, fieldnames=campos)
                
                # Escribir encabezados solo si el archivo no existe o está vacío
                if not archivo_existe:
                    writer.writeheader()
                    print("   📝 Creando nuevo archivo CSV con encabezados")
                else:
                    print("   ➕ Añadiendo datos al archivo CSV existente")
                
                # Escribir datos
                for producto in todos_productos:
                    writer.writerow(producto)
            
            print(f"   ✅ Datos guardados exitosamente")
        else:
            print("\n⚠️ No hay nuevos productos para añadir")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL:")
        print(f"   ✅ Nuevos productos añadidos: {len(todos_productos)}")
        print(f"   📁 Archivo CSV: {archivo_csv}")
        print(f"   📊 Total de productos en el archivo: {len(codigos_existentes)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
    
    finally:
        # Cerrar el navegador
        print("\n🔚 Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    main()