#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    # Verificar que existan los archivos necesarios
    archivos_necesarios = [
        "data/transcription.srt",
        "procesar_transcripcion.py",
        "num_caracteres.py",
        "models/classifier.py"
    ]
    
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            print(f"Error: No se encontró el archivo {archivo}")
            return 1

    archivo_procesado = "transcription_procesada.txt"

    # Ejecutar el procesamiento
    print("Procesando el archivo transcription.srt...")
    try:
        resultado = subprocess.run(
            ["python", "procesar_transcripcion.py", "data/transcription.srt", archivo_procesado],
            check=True,
            capture_output=True,
            text=True
        )
        print(resultado.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al procesar el archivo: {e}")
        print(e.stderr)
        return 1

    if not os.path.exists(archivo_procesado):
        print(f"Error: No se generó el archivo {archivo_procesado}")
        return 1

    print(f"Archivo procesado guardado como {archivo_procesado}")

    # Contar caracteres
    print("\nContando el número de caracteres...")
    try:
        resultado = subprocess.run(
            ["python", "num_caracteres.py", archivo_procesado],
            check=True,
            capture_output=True,
            text=True
        )
        print(resultado.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al contar caracteres: {e}")
        print(e.stderr)
        return 1

    # Clasificación del contenido
    print("\nClasificando el contenido del podcast...")
    try:
        with open(archivo_procesado, "r", encoding="utf-8") as file:
            texto = file.read()

        from models.classifier import classify_content
        resultado_clasificacion = classify_content(texto)
        print("\n--- RESULTADO DE CLASIFICACIÓN ---\n")
        print(resultado_clasificacion)
        print("\n--- FIN DE LA CLASIFICACIÓN ---\n")

    except Exception as e:
        print(f"Error durante la clasificación: {e}")
        return 1

    print("\nProceso completado con éxito.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
