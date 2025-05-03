from faster_whisper import WhisperModel as Whisper
from pydub import AudioSegment
import torch
import time
import shutil
import gc
import os
import tempfile
import multiprocessing
import concurrent.futures
import time
import logging
from functools import lru_cache

# Definición de la función format_time_srt
def format_time_srt(seconds):
    """Convierte segundos a formato SRT hh:mm:ss,ms"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

"""funcional tarda  2 minutos """
def transcribe_audio_to_srt(file_path, output_srt_path, chunk_size_minutes=10, model_size="tiny"):
    """
    Procesa archivos grandes dividiéndolos en fragmentos más pequeños
    para una transcripción más rápida.
    """
    # Crear directorio externo para modelos (fuera del repositorio)
    models_dir = os.path.expanduser("~/.cache/whisper_models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Crear directorio temporal para los fragmentos
    temp_dir = tempfile.mkdtemp()
    
    try:
        audio = AudioSegment.from_file(file_path)
        
        # Si el audio es menor a 20 minutos, procesarlo directamente
        if len(audio) < 20 * 60 * 1000:
            # Nota: La recursión podría causar problemas. Mejor implementar la lógica directamente aquí
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            model = Whisper(model_size, device=device, compute_type=compute_type, download_root=models_dir)
            
            segments, info = model.transcribe(
                file_path,
                beam_size=1, # número de caminos a considerar
                vad_filter=True, # filtro de voz
                vad_parameters=dict(min_silence_duration_ms=500), # duración mínima de silencio
                temperature=0, # aleatoriedad
                best_of=1  # número de transcripciones a considerar
            )
            
            # Procesar como en la función original para audios cortos
            all_segments = {}
            five_minutes_in_seconds = 5 * 60
            
            for segment in segments:
                interval_start = (segment.start // five_minutes_in_seconds) * five_minutes_in_seconds
                
                if interval_start not in all_segments:
                    all_segments[interval_start] = []
                
                all_segments[interval_start].append(segment.text.strip())
                
            # Crear archivo SRT
            srt_content = []
            current_index = 1
            sorted_intervals = sorted(all_segments.keys())
            total_duration = len(audio) / 1000  # ms a segundos
            
            for i, interval_start in enumerate(sorted_intervals):
                start_time = format_time_srt(interval_start)
                
                if i < len(sorted_intervals) - 1:
                    end_time = format_time_srt(sorted_intervals[i+1])
                else:
                    end_time = format_time_srt(total_duration)
                
                text = " ".join(all_segments[interval_start])
                srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
                current_index += 1
            
            # Guardar resultado
            with open(output_srt_path, "w", encoding="utf-8") as srt_file:
                srt_file.writelines(srt_content)
            
            print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
            return  # Mantener el mismo comportamiento de retorno
        
        # Dividir en fragmentos de {chunk_size_minutes} minutos
        chunk_size_ms = chunk_size_minutes * 60 * 1000
        chunks = []
        
        for i in range(0, len(audio), chunk_size_ms):
            chunk = audio[i:i+chunk_size_ms]
            chunk_file = os.path.join(temp_dir, f"temp_chunk_{i//chunk_size_ms}.wav")
            chunk.export(chunk_file, format="wav")
            chunks.append((chunk_file, i/1000))  # Guardar archivo y tiempo de inicio
        
        # Transcribir cada fragmento
        all_segments = {}
        five_minutes_in_seconds = 5 * 60
        
        # Cargar modelo una sola vez (fuera del bucle)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        model = Whisper(model_size, device=device, compute_type=compute_type, download_root=models_dir)
        
        for chunk_file, start_time in chunks:
            try:
                # Transcribir fragmento
                segments, _ = model.transcribe(
                    chunk_file,
                    beam_size=1,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500),
                    temperature=0.5,
                    best_of=1
                )
                
                # Procesar segmentos de este fragmento
                for segment in segments:
                    # Ajustar tiempo de inicio al tiempo global
                    global_start = segment.start + start_time
                    interval_start = (global_start // five_minutes_in_seconds) * five_minutes_in_seconds
                    
                    if interval_start not in all_segments:
                        all_segments[interval_start] = []
                    
                    all_segments[interval_start].append(segment.text.strip())
            finally:
                # Asegurarnos de eliminar el archivo temporal
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
        
        # Limpiar recursos del modelo
        del model
        if device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
        
        # Crear archivo SRT
        srt_content = []
        current_index = 1
        sorted_intervals = sorted(all_segments.keys())
        total_duration = len(audio) / 1000  # ms a segundos
        
        for i, interval_start in enumerate(sorted_intervals):
            start_time = format_time_srt(interval_start)
            
            if i < len(sorted_intervals) - 1:
                end_time = format_time_srt(sorted_intervals[i+1])
            else:
                end_time = format_time_srt(total_duration)
            
            text = " ".join(all_segments[interval_start])
            srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
            current_index += 1
        
        # Guardar resultado
        with open(output_srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.writelines(srt_content)
        
        print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
    finally:
        # Limpiar archivos temporales incluso si hay errores
        shutil.rmtree(temp_dir, ignore_errors=True)
        if 'model' in locals():
            del model
        if device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
# import os
# import subprocess
# import json
# from pydub import AudioSegment
# import tempfile

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds_int = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path, model_size="base"):
#     """Transcribe un archivo de audio usando whisper.cpp y guarda en un archivo SRT con segmentos de 5 minutos."""
    
#     # Verifica que el archivo exista
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"El archivo {file_path} no existe")
    
#     # Ruta al ejecutable whisper.cpp (ajusta según tu instalación)
#     whisper_cpp_path = '/c/Users/casa/Desktop/Universidad/TFG/System-for-classifying-podcasts-into-themes-using-large-language-models/whisper.cpp/models/ggml-base.bin'  # Cambia esto a la ruta donde tienes el ejecutable de whisper.cpp

#     # Ruta al modelo (ajusta según tu instalación)
#     model_path = f"C:/Users/casa/Desktop/Universidad/TFG/System-for-classifying-podcasts-into-themes-using-large-language-models/whisper.cpp/models/ggml-base.bin"  # Cambia esto a la ruta donde tienes los modelos
    
#     # Crear un archivo temporal para la salida JSON
#     with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
#         json_output_path = tmp_file.name
    
#     # Comando para ejecutar whisper.cpp con salida JSON
#     cmd = [
#         whisper_cpp_path,
#         "-m", model_path,
#         "-f", file_path,
#         "-oj", json_output_path,
#         "-l", "auto",  # Detección automática de idioma
#         "-pc",  # Mostrar progreso en la consola
#         "-pp",  # Procesar palabras por separado para mejor precisión
#         "-of", "srt"  # Formato de salida
#     ]
    
#     print(f"Ejecutando transcripción con whisper.cpp...")
#     process = subprocess.run(cmd, capture_output=True, text=True)
    
#     if process.returncode != 0:
#         print(f"Error al ejecutar whisper.cpp: {process.stderr}")
#         return None
    
#     # Leer el JSON de salida
#     with open(json_output_path, 'r', encoding='utf-8') as f:
#         result = json.load(f)
    
#     # Obtener la duración total del audio
#     audio = AudioSegment.from_file(file_path)
#     total_duration = len(audio) / 1000  # Convertir de ms a segundos
    
#     # Agrupar los segmentos en intervalos de 5 minutos
#     five_minutes_in_seconds = 5 * 60
#     five_minute_segments = {}
    
#     for segment in result.get('segments', []):
#         # Determinar a qué intervalo de 5 minutos pertenece este segmento
#         start_time = segment.get('start', 0)
#         interval_start = (int(start_time) // five_minutes_in_seconds) * five_minutes_in_seconds
        
#         # Si este intervalo no existe todavía, crearlo
#         if interval_start not in five_minute_segments:
#             five_minute_segments[interval_start] = []
        
#         # Añadir el texto a este intervalo
#         text = segment.get('text', '').strip()
#         if text:
#             five_minute_segments[interval_start].append(text)
    
#     # Crear el contenido SRT
#     srt_content = []
#     current_index = 1
#     sorted_intervals = sorted(five_minute_segments.keys())
    
#     for i, interval_start in enumerate(sorted_intervals):
#         start_time = format_time_srt(interval_start)
        
#         # El final de este intervalo es el inicio del siguiente, o la duración total
#         if i < len(sorted_intervals) - 1:
#             end_time = format_time_srt(sorted_intervals[i+1])
#         else:
#             end_time = format_time_srt(total_duration)
        
#         # Unir todos los textos de este intervalo
#         text = " ".join(five_minute_segments[interval_start])
        
#         # Crear la entrada SRT
#         srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#         current_index += 1
    
#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)
    
#     print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
#     # Limpiar el archivo temporal
#     os.unlink(json_output_path)
    
#     # Devolver el texto completo
#     all_texts = []
#     for interval in sorted_intervals:
#         all_texts.extend(five_minute_segments[interval])
#     return " ".join(all_texts)

# # Ejemplo de uso
# if __name__ == "__main__":
#     audio_file = "data/audio.wav"  # Cambia esto a la ruta de tu archivo de audio
#     output_file = "transcripcion.srt"     # Nombre del archivo de salida
#     transcribe_audio_to_srt(audio_file, output_file)

# import os
# import whisperx
# import torch
# from pydub import AudioSegment

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds_int = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path, model_size="base"):
#     """Transcribe un archivo de audio usando WhisperX y guarda en un archivo SRT con segmentos de 5 minutos."""
    
#     # Verifica que el archivo exista
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"El archivo {file_path} no existe")
    
#     # Determinar el dispositivo a usar
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     compute_type = "float16" if device == "cuda" else "int8"
    
#     print(f"Cargando modelo WhisperX {model_size}...")
#     # Cargar el modelo WhisperX
#     model = whisperx.load_model(model_size, device, compute_type=compute_type)
    
#     print(f"Transcribiendo audio con WhisperX...")
#     # Transcribir el audio
#     result = whisperx.transcribe(model, file_path, language="auto")
    
#     # Cargar el audio para obtener la duración total
#     audio = AudioSegment.from_file(file_path)
#     total_duration = len(audio) / 1000  # Convertir de ms a segundos
    
#     # Agrupar los segmentos en intervalos de 5 minutos
#     five_minutes_in_seconds = 5 * 60
#     five_minute_segments = {}
    
#     # Los segmentos en WhisperX están en result['segments']
#     for segment in result.get('segments', []):
#         # Determinar a qué intervalo de 5 minutos pertenece este segmento
#         start_time = segment.get('start', 0)
#         interval_start = (int(start_time) // five_minutes_in_seconds) * five_minutes_in_seconds
        
#         # Si este intervalo no existe todavía, crearlo
#         if interval_start not in five_minute_segments:
#             five_minute_segments[interval_start] = []
        
#         # Añadir el texto a este intervalo
#         text = segment.get('text', '').strip()
#         if text:
#             five_minute_segments[interval_start].append(text)
    
#     # Crear el contenido SRT
#     srt_content = []
#     current_index = 1
#     sorted_intervals = sorted(five_minute_segments.keys())
    
#     for i, interval_start in enumerate(sorted_intervals):
#         start_time = format_time_srt(interval_start)
        
#         # El final de este intervalo es el inicio del siguiente, o la duración total
#         if i < len(sorted_intervals) - 1:
#             end_time = format_time_srt(sorted_intervals[i+1])
#         else:
#             end_time = format_time_srt(total_duration)
        
#         # Unir todos los textos de este intervalo
#         text = " ".join(five_minute_segments[interval_start])
        
#         # Crear la entrada SRT
#         srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#         current_index += 1
    
#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)
    
#     print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
#     # Devolver el texto completo
#     all_texts = []
#     for interval in sorted_intervals:
#         all_texts.extend(five_minute_segments[interval])
#     return " ".join(all_texts)

# # Ejemplo de uso
# if __name__ == "__main__":
#     audio_file = "data/audio.wav"  # Cambia esto a la ruta de tu archivo de audio
#     output_file = "transcripcion.srt"     # Nombre del archivo de salida
#     transcribe_audio_to_srt(audio_file, output_file)

# import os
# import whisperx
# import torch
# from pydub import AudioSegment

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds_int = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path, model_size="base"):
#     """Transcribe un archivo de audio usando WhisperX y guarda en un archivo SRT con segmentos de 5 minutos."""

#     # Verifica que el archivo exista
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"El archivo {file_path} no existe")

#     # Determinar el dispositivo a usar
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     compute_type = "float16" if device == "cuda" else "int8"

#     print(f"Cargando modelo WhisperX {model_size}...")
#     # Cargar el modelo WhisperX
#     model = whisperx.load_model(model_size, device=device, compute_type=compute_type)

#     print(f"Transcribiendo audio con WhisperX...")
#     # Transcribir el audio
#     result = model.transcribe(file_path)

#     # Cargar el audio para obtener la duración total
#     audio = AudioSegment.from_file(file_path)
#     total_duration = len(audio) / 1000  # Convertir de ms a segundos

#     # Agrupar los segmentos en intervalos de 5 minutos
#     five_minutes_in_seconds = 5 * 60
#     five_minute_segments = {}

#     # Los segmentos en WhisperX están en result['segments']
#     for segment in result.get('segments', []):
#         # Determinar a qué intervalo de 5 minutos pertenece este segmento
#         start_time = segment.get('start', 0)
#         interval_start = (int(start_time) // five_minutes_in_seconds) * five_minutes_in_seconds

#         # Si este intervalo no existe todavía, crearlo
#         if interval_start not in five_minute_segments:
#             five_minute_segments[interval_start] = []

#         # Añadir el texto a este intervalo
#         text = segment.get('text', '').strip()
#         if text:
#             five_minute_segments[interval_start].append(text)

#     # Crear el contenido SRT
#     srt_content = []
#     current_index = 1
#     sorted_intervals = sorted(five_minute_segments.keys())

#     for i, interval_start in enumerate(sorted_intervals):
#         start_time = format_time_srt(interval_start)

#         # El final de este intervalo es el inicio del siguiente, o la duración total
#         if i < len(sorted_intervals) - 1:
#             end_time = format_time_srt(sorted_intervals[i+1])
#         else:
#             end_time = format_time_srt(total_duration)

#         # Unir todos los textos de este intervalo
#         text = " ".join(five_minute_segments[interval_start])

#         # Crear la entrada SRT
#         srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#         current_index += 1

#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)

#     print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")

#     # Devolver el texto completo
#     all_texts = []
#     for interval in sorted_intervals:
#         all_texts.extend(five_minute_segments[interval])
#     return " ".join(all_texts)
# from faster_whisper import WhisperModel as Whisper
# from pydub import AudioSegment
# import torch
# import shutil
# import gc
# import os
# import tempfile
# import multiprocessing
# import concurrent.futures
# import time
# import logging
# from functools import lru_cache

# # Configuración de logging - compatible con tu logger existente
# logger = logging.getLogger("whisper_transcriber")

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds_int = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

# # Caché para el modelo Whisper
# _whisper_model_cache = {}

# def get_whisper_model(model_size="tiny", device=None):
#     """Carga el modelo Whisper con caché para evitar recargas"""
#     if device is None:
#         device = "cuda" if torch.cuda.is_available() else "cpu"
    
#     cache_key = f"{model_size}_{device}"
#     if cache_key not in _whisper_model_cache:
#         # Crear directorio para modelos
#         models_dir = os.path.expanduser("~/.cache/whisper_models")
#         os.makedirs(models_dir, exist_ok=True)
        
#         # Configurar tipo de cómputo
#         compute_type = "float16" if device == "cuda" else "int8"
        
#         # Cargar modelo
#         logger.info(f"Cargando modelo {model_size} en {device}")
#         model = Whisper(model_size, device=device, compute_type=compute_type, download_root=models_dir)
#         _whisper_model_cache[cache_key] = (model, device)
    
#     return _whisper_model_cache[cache_key]

# def process_chunk(chunk_data):
#     """Procesa un chunk individual de audio"""
#     chunk_file, start_time, model_size = chunk_data
    
#     try:
#         # Obtener modelo y dispositivo
#         model, device = get_whisper_model(model_size)
        
#         # Transcribir segmento
#         segments, _ = model.transcribe(
#             chunk_file,
#             beam_size=1,  # Mantener igual que original para consistencia
#             vad_filter=True,
#             vad_parameters=dict(min_silence_duration_ms=500),
#             temperature=0.0  # Determinístico para mayor consistencia
#         )
        
#         # Convertir a lista para poder transportar entre procesos
#         results = []
#         for segment in segments:
#             global_start = segment.start + start_time
#             results.append((global_start, segment.text.strip()))
        
#         return results
#     except Exception as e:
#         logger.error(f"Error al procesar chunk: {e}")
#         return []
#     finally:
#         # Limpiar recursos
#         if os.path.exists(chunk_file):
#             os.remove(chunk_file)

# def transcribe_audio_to_srt(file_path, output_srt_path, chunk_size_minutes=5, model_size="tiny"):
#     """
#     Mantiene la misma firma que la función original pero con implementación optimizada.
    
#     Args:
#         file_path: Ruta al archivo de audio a transcribir
#         output_srt_path: Ruta donde guardar el archivo SRT generado
#         chunk_size_minutes: Tamaño de los fragmentos en minutos (default: 5)
#         model_size: Tamaño del modelo Whisper (default: 'tiny')
#     """
#     # Crear directorio para modelos si no existe
#     models_dir = os.path.expanduser("~/.cache/whisper_models")
#     os.makedirs(models_dir, exist_ok=True)
    
#     # Crear directorio temporal para los fragmentos
#     temp_dir = tempfile.mkdtemp()
    
#     try:
#         # Determinar dispositivo
#         device = "cuda" if torch.cuda.is_available() else "cpu"
        
#         # Cargar audio
#         try:
#             audio = AudioSegment.from_file(file_path)
#             total_duration = len(audio) / 1000  # ms a segundos
#         except Exception as e:
#             logger.error(f"Error al cargar el audio: {e}")
#             raise
        
#         # Si el audio es corto, procesarlo directamente sin dividir
#         if len(audio) < 20 * 60 * 1000:  # Mismo umbral que original (20 min)
#             model, _ = get_whisper_model(model_size, device)
            
#             segments, info = model.transcribe(
#                 file_path,
#                 beam_size=1,
#                 vad_filter=True,
#                 vad_parameters=dict(min_silence_duration_ms=500),
#                 temperature=0,
#                 best_of=1
#             )
            
#             # Procesar como en la función original para mantener compatibilidad
#             all_segments = {}
#             five_minutes_in_seconds = 5 * 60
            
#             for segment in segments:
#                 interval_start = (segment.start // five_minutes_in_seconds) * five_minutes_in_seconds
                
#                 if interval_start not in all_segments:
#                     all_segments[interval_start] = []
                
#                 all_segments[interval_start].append(segment.text.strip())
                
#             # Crear archivo SRT
#             srt_content = []
#             current_index = 1
#             sorted_intervals = sorted(all_segments.keys())
            
#             for i, interval_start in enumerate(sorted_intervals):
#                 start_time = format_time_srt(interval_start)
                
#                 if i < len(sorted_intervals) - 1:
#                     end_time = format_time_srt(sorted_intervals[i+1])
#                 else:
#                     end_time = format_time_srt(total_duration)
                
#                 text = " ".join(all_segments[interval_start])
#                 srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#                 current_index += 1
            
#             # Guardar resultado
#             with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#                 srt_file.writelines(srt_content)
            
#             logger.info(f"Transcripción completada para audio corto")
#             return
        
#         # Para audios largos: dividir en fragmentos y procesar en paralelo
#         # Determinar número óptimo de workers
#         max_workers = 1  # Valor por defecto
        
#         if device == "cuda":
#             # Con GPU, limitamos por GPUs disponibles + 1 proceso para gestión
#             max_workers = min(4, torch.cuda.device_count() + 1)
#         else:
#             # Con CPU, usamos la mitad de los núcleos disponibles para no saturar
#             max_workers = max(1, multiprocessing.cpu_count() // 2)
        
#         # Dividir en fragmentos
#         chunk_size_ms = chunk_size_minutes * 60 * 1000
#         chunks = []
        
#         for i in range(0, len(audio), chunk_size_ms):
#             chunk = audio[i:i+chunk_size_ms]
#             if len(chunk) < 1000:  # Ignorar chunks muy pequeños
#                 continue
                
#             chunk_file = os.path.join(temp_dir, f"temp_chunk_{i//chunk_size_ms}.wav")
#             # Convertir a mono para mejor rendimiento y consistencia
#             chunk.export(chunk_file, format="wav", parameters=["-ac", "1"])
#             chunks.append((chunk_file, i/1000, model_size))
        
#         logger.info(f"Audio dividido en {len(chunks)} fragmentos para procesamiento paralelo")
        
#         # Procesar chunks en paralelo
#         all_results = []
        
#         # Uso ProcessPoolExecutor para mayor eficiencia en tareas intensivas
#         with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
#             futures = [executor.submit(process_chunk, chunk_data) for chunk_data in chunks]
            
#             for future in concurrent.futures.as_completed(futures):
#                 try:
#                     chunk_results = future.result()
#                     all_results.extend(chunk_results)
#                 except Exception as exc:
#                     logger.error(f"Error en procesamiento paralelo: {exc}")
        
#         # Ordenar por tiempo de inicio
#         all_results.sort(key=lambda x: x[0])
        
#         # Agrupar resultados por intervalos de 5 minutos para mantener formato consistente
#         all_segments = {}
#         five_minutes_in_seconds = 5 * 60
        
#         for global_start, text in all_results:
#             interval_start = (global_start // five_minutes_in_seconds) * five_minutes_in_seconds
            
#             if interval_start not in all_segments:
#                 all_segments[interval_start] = []
            
#             all_segments[interval_start].append(text)
        
#         # Crear archivo SRT - mismo formato que original
#         srt_content = []
#         current_index = 1
#         sorted_intervals = sorted(all_segments.keys())
        
#         for i, interval_start in enumerate(sorted_intervals):
#             start_time = format_time_srt(interval_start)
            
#             if i < len(sorted_intervals) - 1:
#                 end_time = format_time_srt(sorted_intervals[i+1])
#             else:
#                 end_time = format_time_srt(total_duration)
            
#             text = " ".join(all_segments[interval_start])
#             srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#             current_index += 1
        
#         # Guardar resultado
#         with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#             srt_file.writelines(srt_content)
        
#         logger.info(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
#     finally:
#         # Limpiar archivos temporales y recursos
#         shutil.rmtree(temp_dir, ignore_errors=True)
#         gc.collect()
#         if device == "cuda":
#             torch.cuda.empty_cache()
# Ejemplo de uso
if __name__ == "__main__":
    audio_file = "data/audio.wav"  # Cambia esto a la ruta de tu archivo de audio
    output_file = "transcripcion.srt"     # Nombre del archivo de salida
    time.start = time.time()
    transcribe_audio_to_srt(audio_file, output_file)
    time.end = time.time()
    print(f"Tiempo de ejecución: {time.end - time.start} segundos")
