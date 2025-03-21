def contar_caracteres(nombre_archivo):
    """
    Función para contar caracteres en un archivo de texto.
    
    Args:
        nombre_archivo (str): Ruta al archivo de texto a analizar
        
    Returns:
        dict: Diccionario con estadísticas de caracteres
    """
    try:
        # Abrir el archivo en modo lectura
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            
        # Contar caracteres
        total_caracteres = len(contenido)
        total_sin_espacios = len(contenido.replace(" ", "").replace("\n", "").replace("\t", ""))
        total_letras = sum(1 for c in contenido if c.isalpha())
        total_numeros = sum(1 for c in contenido if c.isdigit())
        total_especiales = total_caracteres - total_letras - total_numeros - contenido.count(" ") - contenido.count("\n") - contenido.count("\t")
        total_lineas = contenido.count("\n") + 1
        
        # Crear diccionario con resultados
        resultados = {
            "Total de caracteres": total_caracteres,
            "Caracteres sin espacios en blanco": total_sin_espacios,
            "Total de letras": total_letras,
            "Total de números": total_numeros,
            "Total de caracteres especiales": total_especiales,
            "Total de líneas": total_lineas
        }
        
        return resultados
        
    except FileNotFoundError:
        return {"Error": f"El archivo '{nombre_archivo}' no fue encontrado."}
    except Exception as e:
        return {"Error": f"Ocurrió un error: {str(e)}"}

# Ejemplo de uso
if __name__ == "__main__":
    archivo = input("Ingresa la ruta del archivo de texto: ")
    resultados = contar_caracteres(archivo)
    
    # Mostrar resultados
    print("\nResultados del análisis:")
    print("-" * 30)
    for clave, valor in resultados.items():
        print(f"{clave}: {valor}")