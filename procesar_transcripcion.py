#!/usr/bin/env python3
import re
import sys

def preprocess_srt(input_file, output_file):
    """
    Procesa un archivo SRT y extrae solo el texto de la transcripción,
    eliminando números de subtítulo, timestamps y formato.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar números de subtítulo y timestamps
    # Patrón que busca un número, seguido de una línea con timestamps
    pattern = r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n'
    content = re.sub(pattern, '', content)
    
    # Eliminar líneas vacías extras
    content = re.sub(r'\n{2,}', '\n', content)
    content = content.strip()
    
    # Guardar el texto procesado
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Archivo procesado correctamente. Texto extraído y guardado en {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python preprocess.py archivo_entrada.srt archivo_salida.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    preprocess_srt(input_file, output_file)