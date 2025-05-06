# Analizador de Color de Botes de Pintura
# Este programa detecta el color hexadecimal de botes de pintura en imágenes

import os
import sys
import tempfile
import requests
from io import BytesIO
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse

class AnalizadorColorBotes:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Color de Botes de Pintura")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.imagen_url = tk.StringVar()
        self.imagen_ruta = None
        self.imagen_pil = None
        self.imagen_tk = None
        self.color_seleccionado = None
        self.region_seleccionada = None
        self.clicks = []  # Para almacenar las coordenadas de los clics
        
        # Crear widgets
        self.crear_widgets()
        
    def crear_widgets(self):
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Marco superior para entrada de URL y botones
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Etiqueta y entrada para la URL
        ttk.Label(top_frame, text="URL de la imagen:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        url_entry = ttk.Entry(top_frame, textvariable=self.imagen_url, width=70)
        url_entry.grid(row=0, column=1, padx=5)
        
        # Botones para cargar imagen
        botones_frame = ttk.Frame(top_frame)
        botones_frame.grid(row=0, column=2, padx=5)
        
        ttk.Button(botones_frame, text="Cargar desde URL", command=self.cargar_desde_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(botones_frame, text="Cargar archivo local", command=self.cargar_archivo_local).pack(side=tk.LEFT, padx=2)
        
        # Marco intermedio para la imagen y el selector de región
        mid_frame = ttk.Frame(main_frame)
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Lienzo para mostrar la imagen
        self.canvas_frame = ttk.LabelFrame(mid_frame, text="Imagen")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Añadir barras de desplazamiento al canvas
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Vincular eventos de clic
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Panel de controles y resultados
        control_frame = ttk.LabelFrame(mid_frame, text="Controles y Resultados", width=250)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # Contenido del panel de control
        inner_control = ttk.Frame(control_frame, padding=10)
        inner_control.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(inner_control, text="Instrucciones:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        instrucciones = "1. Carga una imagen de un bote de pintura\n"\
                        "2. Haz clic en la zona del color del bote\n"\
                        "3. Puedes hacer varios clics para promediar"
        ttk.Label(inner_control, text=instrucciones, wraplength=230, justify=tk.LEFT).grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        ttk.Button(inner_control, text="Detectar color automáticamente", 
                   command=self.detectar_color_auto).grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Button(inner_control, text="Calcular color de puntos seleccionados", 
                   command=self.calcular_color_seleccionado).grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Button(inner_control, text="Limpiar selección", 
                   command=self.limpiar_seleccion).grid(row=4, column=0, sticky="ew", pady=(0, 15))
        
        # Sección de resultados
        ttk.Separator(inner_control, orient=tk.HORIZONTAL).grid(row=5, column=0, sticky="ew", pady=10)
        ttk.Label(inner_control, text="Resultado:").grid(row=6, column=0, sticky="w", pady=(0, 5))
        
        # Color detectado
        result_frame = ttk.Frame(inner_control)
        result_frame.grid(row=7, column=0, sticky="ew", pady=(0, 5))
        
        self.color_muestra = tk.Canvas(result_frame, width=50, height=50, highlightthickness=1, highlightbackground="black")
        self.color_muestra.pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_info = ttk.Label(result_frame, text="Sin color detectado", wraplength=160)
        self.color_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Historial de colores detectados
        ttk.Label(inner_control, text="Historial de muestras:").grid(row=8, column=0, sticky="w", pady=(10, 5))
        
        # Frame para las muestras de color
        self.muestras_frame = ttk.Frame(inner_control)
        self.muestras_frame.grid(row=9, column=0, sticky="ew")
        
        # Botones para operaciones adicionales
        ttk.Separator(inner_control, orient=tk.HORIZONTAL).grid(row=10, column=0, sticky="ew", pady=10)
        
        ttk.Button(inner_control, text="Copiar código hexadecimal", 
                   command=self.copiar_hex).grid(row=11, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Button(inner_control, text="Guardar resultado", 
                   command=self.guardar_resultado).grid(row=12, column=0, sticky="ew", pady=(0, 5))
        
        # Marco inferior para mensajes y estado
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Listo. Carga una imagen para comenzar.")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X)
        
    def cargar_desde_url(self):
        """Carga una imagen desde la URL especificada"""
        url = self.imagen_url.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Por favor, introduce una URL válida.")
            return
        
        try:
            self.status_var.set(f"Descargando imagen desde {url}...")
            self.root.update_idletasks()
            
            # Validar URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("URL inválida")
            
            # Descargar imagen
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Cargar imagen en PIL
            imagen_bytes = BytesIO(response.content)
            self.imagen_pil = Image.open(imagen_bytes)
            self.imagen_ruta = url
            
            # Mostrar la imagen
            self.mostrar_imagen()
            self.status_var.set(f"Imagen cargada desde URL. Dimensiones: {self.imagen_pil.width}x{self.imagen_pil.height}")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error de descarga", f"No se pudo descargar la imagen: {str(e)}")
            self.status_var.set("Error al descargar la imagen.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la imagen: {str(e)}")
            self.status_var.set("Error al procesar la imagen.")
    
    def cargar_archivo_local(self):
        """Carga una imagen desde un archivo local"""
        filetypes = [
            ("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("Todos los archivos", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=filetypes
        )
        
        if not filepath:
            return  # Usuario canceló
        
        try:
            self.status_var.set(f"Cargando imagen desde {filepath}...")
            self.root.update_idletasks()
            
            # Cargar imagen en PIL
            self.imagen_pil = Image.open(filepath)
            self.imagen_ruta = filepath
            
            # Mostrar la imagen
            self.mostrar_imagen()
            self.status_var.set(f"Imagen cargada. Dimensiones: {self.imagen_pil.width}x{self.imagen_pil.height}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
            self.status_var.set("Error al cargar la imagen.")
    
    def mostrar_imagen(self):
        """Muestra la imagen en el canvas"""
        if self.imagen_pil is None:
            return
        
        # Limpiar canvas y marcadores
        self.canvas.delete("all")
        self.clicks = []
        
        # Ajustar tamaño de la imagen para visualización manteniendo la proporción
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Si el canvas aún no tiene tamaño, usar un valor predeterminado
            canvas_width = 500
            canvas_height = 400
        
        # Calcular factor de escala para ajustar la imagen al canvas
        img_width, img_height = self.imagen_pil.size
        scale_w = canvas_width / img_width if img_width > canvas_width else 1
        scale_h = canvas_height / img_height if img_height > canvas_height else 1
        scale = min(scale_w, scale_h)
        
        # Redimensionar la imagen si es necesario
        if scale < 1:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized_img = self.imagen_pil.resize((new_width, new_height), Image.LANCZOS)
            self.imagen_tk = ImageTk.PhotoImage(resized_img)
            self.scale_factor = scale
        else:
            self.imagen_tk = ImageTk.PhotoImage(self.imagen_pil)
            self.scale_factor = 1
        
        # Mostrar imagen en el canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imagen_tk)
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
    
    def on_canvas_click(self, event):
        """Maneja el evento de clic en el canvas"""
        if self.imagen_pil is None:
            return
        
        # Obtener coordenadas del clic, ajustadas por el desplazamiento y escala
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convertir a coordenadas de imagen original
        img_x = int(canvas_x / self.scale_factor)
        img_y = int(canvas_y / self.scale_factor)
        
        # Asegurarse de que las coordenadas estén dentro de la imagen
        img_width, img_height = self.imagen_pil.size
        if 0 <= img_x < img_width and 0 <= img_y < img_height:
            # Almacenar el punto seleccionado
            self.clicks.append((img_x, img_y))
            
            # Dibujar un marcador en el punto seleccionado
            marker_radius = 5
            marker_id = self.canvas.create_oval(
                canvas_x - marker_radius, canvas_y - marker_radius,
                canvas_x + marker_radius, canvas_y + marker_radius,
                outline="red", width=2, fill="yellow", tags="marker"
            )
            
            # Obtener el color del píxel
            if self.imagen_pil.mode != 'RGB':
                img_rgb = self.imagen_pil.convert('RGB')
            else:
                img_rgb = self.imagen_pil
            
            color_rgb = img_rgb.getpixel((img_x, img_y))
            color_hex = '#{:02x}{:02x}{:02x}'.format(*color_rgb)
            
            # Mostrar información del color
            self.status_var.set(f"Punto seleccionado en ({img_x}, {img_y}): {color_hex}")
            
            # Añadir a las muestras
            self.añadir_muestra_color(color_rgb, f"Punto ({img_x}, {img_y})")
    
    def añadir_muestra_color(self, color_rgb, descripcion):
        """Añade una muestra de color al historial"""
        # Convertir RGB a hexadecimal
        color_hex = '#{:02x}{:02x}{:02x}'.format(*color_rgb)
        
        # Crear un nuevo marco para esta muestra
        muestra_frame = ttk.Frame(self.muestras_frame)
        muestra_frame.pack(fill=tk.X, pady=2)
        
        # Crear un pequeño canvas para mostrar el color
        muestra_canvas = tk.Canvas(muestra_frame, width=20, height=20, 
                                   highlightthickness=1, highlightbackground="black")
        muestra_canvas.pack(side=tk.LEFT, padx=(0, 5))
        muestra_canvas.create_rectangle(0, 0, 20, 20, fill=color_hex, outline="")
        
        # Añadir la información del color
        info_text = f"{color_hex}\nRGB({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]})"
        muestra_info = ttk.Label(muestra_frame, text=info_text, font=("Arial", 8))
        muestra_info.pack(side=tk.LEFT)
    
    def calcular_color_seleccionado(self):
        """Calcula el color promedio de los puntos seleccionados"""
        if not self.clicks:
            messagebox.showinfo("Sin selección", "No hay puntos seleccionados. Haz clic en la imagen para seleccionar puntos.")
            return
        
        # Convertir la imagen a RGB si es necesario
        if self.imagen_pil.mode != 'RGB':
            img_rgb = self.imagen_pil.convert('RGB')
        else:
            img_rgb = self.imagen_pil
        
        # Calcular el color promedio
        total_r, total_g, total_b = 0, 0, 0
        for x, y in self.clicks:
            r, g, b = img_rgb.getpixel((x, y))
            total_r += r
            total_g += g
            total_b += b
        
        avg_r = round(total_r / len(self.clicks))
        avg_g = round(total_g / len(self.clicks))
        avg_b = round(total_b / len(self.clicks))
        
        self.color_seleccionado = (avg_r, avg_g, avg_b)
        color_hex = '#{:02x}{:02x}{:02x}'.format(avg_r, avg_g, avg_b)
        
        # Actualizar visualización
        self.color_muestra.delete("all")
        self.color_muestra.create_rectangle(0, 0, 50, 50, fill=color_hex, outline="")
        
        # Actualizar información del color
        info_text = f"Color: {color_hex}\nRGB: ({avg_r}, {avg_g}, {avg_b})"
        self.color_info.configure(text=info_text)
        
        self.status_var.set(f"Color calculado: {color_hex} - RGB({avg_r}, {avg_g}, {avg_b})")
    
    def detectar_color_auto(self):
        """Intenta detectar automáticamente el color del bote en la imagen"""
        if self.imagen_pil is None:
            messagebox.showinfo("Sin imagen", "Primero carga una imagen.")
            return
        
        try:
            self.status_var.set("Detectando automáticamente el color del bote...")
            self.root.update_idletasks()
            
            # Convertir a RGB si es necesario
            if self.imagen_pil.mode != 'RGB':
                img_rgb = self.imagen_pil.convert('RGB')
            else:
                img_rgb = self.imagen_pil
            
            # Convertir a array NumPy para análisis
            img_array = np.array(img_rgb)
            altura, anchura = img_array.shape[:2]
            
            # Estrategia: dividir la imagen en regiones y analizar la región central
            # Asumimos que el bote suele estar en el centro de la imagen
            
            # Definir la región central (aproximadamente el tercio central)
            x_start = anchura // 3
            x_end = anchura * 2 // 3
            y_start = altura // 3
            y_end = altura * 2 // 3
            
            # Extraer la región central
            region_central = img_array[y_start:y_end, x_start:x_end]
            
            # Aplanar para análisis
            pixels = region_central.reshape(-1, 3)
            
            # Filtrar píxeles muy claros o muy oscuros que podrían ser reflejos o sombras
            valid_pixels = []
            for p in pixels:
                r, g, b = p
                # Evitar píxeles blancos, grises o negros
                if (max(r, g, b) - min(r, g, b) > 20 and  # Tiene suficiente saturación
                    30 < r < 225 and 30 < g < 225 and 30 < b < 225):  # Evita extremos
                    valid_pixels.append(p)
            
            if not valid_pixels:
                messagebox.showinfo("Detección fallida", 
                                    "No se pudo detectar automáticamente. Por favor, selecciona manualmente puntos en el bote.")
                return
            
            # Convertir a array para cálculos
            valid_pixels = np.array(valid_pixels)
            
            # Calcular el color promedio
            avg_color = np.mean(valid_pixels, axis=0).astype(int)
            avg_r, avg_g, avg_b = avg_color
            
            self.color_seleccionado = (avg_r, avg_g, avg_b)
            color_hex = '#{:02x}{:02x}{:02x}'.format(avg_r, avg_g, avg_b)
            
            # Actualizar visualización
            self.color_muestra.delete("all")
            self.color_muestra.create_rectangle(0, 0, 50, 50, fill=color_hex, outline="")
            
            # Actualizar información del color
            info_text = f"Color: {color_hex}\nRGB: ({avg_r}, {avg_g}, {avg_b})"
            self.color_info.configure(text=info_text)
            
            # Actualizar estado
            self.status_var.set(f"Color detectado automáticamente: {color_hex}")
            
            # Mostrar la región analizada
            self.canvas.delete("region")
            scaled_x_start = x_start * self.scale_factor
            scaled_y_start = y_start * self.scale_factor
            scaled_x_end = x_end * self.scale_factor
            scaled_y_end = y_end * self.scale_factor
            
            self.canvas.create_rectangle(
                scaled_x_start, scaled_y_start, 
                scaled_x_end, scaled_y_end,
                outline="blue", width=2, dash=(5, 5), tags="region"
            )
            
            # Añadir a las muestras
            self.añadir_muestra_color((avg_r, avg_g, avg_b), "Detección automática")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la detección automática: {str(e)}")
            self.status_var.set("Error en la detección automática.")
    
    def limpiar_seleccion(self):
        """Limpia los puntos seleccionados"""
        self.canvas.delete("marker")
        self.canvas.delete("region")
        self.clicks = []
        self.status_var.set("Selección limpiada.")
    
    def copiar_hex(self):
        """Copia el código hexadecimal al portapapeles"""
        if self.color_seleccionado is None:
            messagebox.showinfo("Sin color", "No hay color detectado para copiar.")
            return
        
        color_hex = '#{:02x}{:02x}{:02x}'.format(*self.color_seleccionado)
        self.root.clipboard_clear()
        self.root.clipboard_append(color_hex)
        self.status_var.set(f"Código hexadecimal {color_hex} copiado al portapapeles.")
    
    def guardar_resultado(self):
        """Guarda el resultado en un archivo de texto"""
        if self.color_seleccionado is None:
            messagebox.showinfo("Sin resultado", "No hay resultado para guardar.")
            return
        
        try:
            # Preparar información
            r, g, b = self.color_seleccionado
            color_hex = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            
            info = f"Resultado del análisis de color\n"
            info += f"===========================\n\n"
            info += f"Imagen analizada: {self.imagen_ruta}\n\n"
            info += f"Color detectado:\n"
            info += f"- Hexadecimal: {color_hex}\n"
            info += f"- RGB: ({r}, {g}, {b})\n"
            
            # Obtener ubicación para guardar
            filetypes = [("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            filepath = filedialog.asksaveasfilename(
                title="Guardar resultado",
                defaultextension=".txt",
                filetypes=filetypes
            )
            
            if not filepath:
                return  # Usuario canceló
            
            # Guardar el archivo
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(info)
            
            self.status_var.set(f"Resultado guardado en {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el resultado: {str(e)}")
            self.status_var.set("Error al guardar el resultado.")

# Función principal para iniciar la aplicación
def main():
    root = tk.Tk()
    app = AnalizadorColorBotes(root)
    root.mainloop()

if __name__ == "__main__":
    main()