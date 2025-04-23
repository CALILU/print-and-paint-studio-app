import csv
import os
import re
from datetime import datetime

def fix_csv_timestamps(input_file, output_file=None):
    """
    Corrige los formatos de timestamp en las columnas J y K:
    - En columna J: Mantiene el contenido existente y añade la hora actual
    - En columna K: Elimina el " 15" del final y añade la hora actual completa
    """
    if output_file is None:
        # Crear nombre de archivo de salida basado en el de entrada
        dirname, filename = os.path.split(input_file)
        output_file = os.path.join(dirname, f"fixed_{filename}")
    
    # Obtener la hora actual en formato HH:MM:SS
    current_time = datetime.now().strftime('%H:%M:%S')
    
    rows = []
    
    # Leer el archivo CSV
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Guardar la cabecera
        rows.append(header)
        
        for row in reader:
            # Asegurarse de que la fila tiene suficientes columnas
            if len(row) > 10:  # Verifica que existan las columnas J y K
                # Columna J (índice 9) - Mantener contenido existente y añadir hora actual
                if row[9]:
                    # Si ya tiene una hora completa, dejarlo como está
                    if re.search(r'\d{2}:\d{2}:\d{2}$', row[9]):
                        pass
                    # De lo contrario, añadir la hora actual
                    else:
                        row[9] = f"{row[9].strip()} {current_time}"
                
                # Columna K (índice 10) - Eliminar " 15" y añadir hora actual
                if row[10]:
                    if row[10].lower() == 'null':
                        row[10] = ""  # Reemplazar 'NULL' con cadena vacía
                    else:
                        # Eliminar " 15" si existe al final de la cadena
                        row[10] = re.sub(r' 15$', '', row[10])
                        # Añadir la hora actual
                        row[10] = f"{row[10].strip()} {current_time}"
                
            rows.append(row)
    
    # Escribir el archivo CSV corregido
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    
    print(f"Archivo corregido guardado como: {output_file}")
    return output_file

if __name__ == "__main__":
    # Ruta del archivo CSV a corregir
    input_csv = "C:\\youtube-app\\printpaintstudio_videos.csv"
    
    # Llamar a la función para corregir el archivo
    fixed_csv = fix_csv_timestamps(input_file=input_csv)
    
    print("Formato de columnas J y K corregido exitosamente.")
    print(f"Se recomienda revisar el archivo {fixed_csv} antes de importarlo a la base de datos.")