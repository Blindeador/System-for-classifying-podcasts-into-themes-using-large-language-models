from faster_whisper import WhisperModel as Whisper
from pydub import AudioSegment
import torch
import shutil
import gc
import os
import tempfile
import multiprocessing
import concurrent.futures
import time
import logging
from functools import lru_cache


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

