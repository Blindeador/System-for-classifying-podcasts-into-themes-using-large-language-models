from faster_whisper import WhisperModel as Whisper

# def transcribe_audio_to_srt(file_path: str, output_srt_path: str) -> None:
#     # Cargar el modelo
#     model = Whisper("base", compute_type="int8")

#     # Procesar audio y obtener segmentos
#     segments, _ = model.transcribe(file_path)

#     srt_content = []
#     for i, segment in enumerate(segments, start=1):
#         start_time = format_time_srt(segment.start)
#         end_time = format_time_srt(segment.end)
#         text = segment.text.strip()

#         # Crear cada entrada SRT
#         srt_content.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")

#     # Guardar transcripción
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)

#     print(f"Transcripción guardada en {output_srt_path}")
#     return "\n".join([s.text for s in segments])  

# def format_time_srt(seconds: float) -> str:
#     """Convierte el tiempo en segundos a formato SRT (hh:mm:ss,ms)"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

from faster_whisper import WhisperModel as Whisper
from pydub import AudioSegment
import os

# # Configuración del modelo
# model = Whisper("base", compute_type="int8")

# def split_audio(file_path, chunk_length=300000):
#     """Divide el audio en partes de `chunk_length` milisegundos (600000 ms = 10 min)."""
#     audio = AudioSegment.from_file(file_path)
#     chunks = [audio[i:i + chunk_length] for i in range(0, len(audio), chunk_length)]
#     chunk_paths = []

#     for i, chunk in enumerate(chunks):
#         chunk_path = f"{file_path}_part{i}.wav"
#         chunk.export(chunk_path, format="wav")
#         chunk_paths.append(chunk_path)

#     return chunk_paths

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path):
#     """Transcribe un archivo de audio completo en partes y guarda en un archivo SRT."""
#     chunk_paths = split_audio(file_path)
#     srt_content = []
#     full_text = []
#     current_index = 1
#     accumulated_time = 0  # Para ajustar los timestamps

#     for chunk_path in chunk_paths:
#         segments, _ = model.transcribe(chunk_path)

#         for segment in segments:
#             start_time = format_time_srt(segment.start + accumulated_time)
#             end_time = format_time_srt(segment.end + accumulated_time)
#             text = segment.text.strip()

#             srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n")
#             full_text.append(text)
#             current_index += 1

#         accumulated_time += 300  # Sumar 10 minutos en segundos
#         os.remove(chunk_path)  # Eliminar archivo temporal

#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)

#     print(f"Transcripción guardada en {output_srt_path}")
#     return " ".join(full_text)

# model = Whisper("base", compute_type="int8")

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path):
#     """Transcribe un archivo de audio completo y guarda en un archivo SRT."""
#     srt_content = []
#     full_text = []
#     current_index = 1

#     # Transcribir el archivo de audio completo
#     segments, _ = model.transcribe(file_path)

#     for segment in segments:
#         start_time = format_time_srt(segment.start)
#         end_time = format_time_srt(segment.end)
#         text = segment.text.strip()

#         srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n")
#         full_text.append(text)
#         current_index += 1

#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)

#     print(f"Transcripción guardada en {output_srt_path}")
#     return " ".join(full_text)


model = Whisper("base", compute_type="int8")

def format_time_srt(seconds):
    """Convierte segundos a formato SRT hh:mm:ss,ms"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def transcribe_audio_to_srt(file_path, output_srt_path):
    """Transcribe un archivo de audio y guarda en un archivo SRT con segmentos de 5 minutos."""
    srt_content = []
    current_index = 1
    five_minutes_in_seconds = 5 * 60  # 5 minutos en segundos
    
    # Transcribir el archivo de audio completo
    segments, info = model.transcribe(file_path)
    
    # Obtener la duración total del audio (en segundos)
    total_duration = info.duration
    
    # Crear diccionario para agrupar los textos por intervalos de 5 minutos
    five_minute_segments = {}
    
    # Agrupar los segmentos en intervalos de 5 minutos
    for segment in segments:
        # Determinar a qué intervalo de 5 minutos pertenece este segmento
        interval_start = (segment.start // five_minutes_in_seconds) * five_minutes_in_seconds
        
        # Si este intervalo no existe todavía, crearlo
        if interval_start not in five_minute_segments:
            five_minute_segments[interval_start] = []
        
        # Añadir el texto a este intervalo
        five_minute_segments[interval_start].append(segment.text.strip())
    
    # Ordenar los intervalos
    sorted_intervals = sorted(five_minute_segments.keys())
    
    # Crear las entradas SRT
    for i, interval_start in enumerate(sorted_intervals):
        start_time = format_time_srt(interval_start)
        
        # El final de este intervalo es el inicio del siguiente, o la duración total
        if i < len(sorted_intervals) - 1:
            end_time = format_time_srt(sorted_intervals[i+1])
        else:
            end_time = format_time_srt(total_duration)
        
        # Unir todos los textos de este intervalo
        text = " ".join(five_minute_segments[interval_start])
        
        # Crear la entrada SRT
        srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
        current_index += 1
    
    # Guardar en archivo SRT
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.writelines(srt_content)
    
    print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
    # Devolver el texto completo
    all_texts = []
    for interval in sorted_intervals:
        all_texts.extend(five_minute_segments[interval])
    return " ".join(all_texts)

