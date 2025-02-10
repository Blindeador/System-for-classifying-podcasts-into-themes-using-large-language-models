import whisper

def transcribe_audio_to_srt(file_path: str, output_srt_path: str) -> None:
    # Cargar el modelo Whisper
    model = whisper.load_model("base")
    
    # Obtener la transcripción con segmentación
    result = model.transcribe(file_path, fp16=False)
    
    # Convertir las segmentaciones a formato SRT
    srt_content = []
    
    for i, segment in enumerate(result['segments'], start=1):
        start_time = format_time_srt(segment['start'])
        end_time = format_time_srt(segment['end'])
        text = segment['text']
        
        # Crear cada entrada SRT
        srt_content.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
    
    # Escribir el contenido en el archivo SRT
    with open(output_srt_path, 'w', encoding='utf-8') as srt_file:
        srt_file.writelines(srt_content)
    
    print(f"Transcripción guardada en {output_srt_path}")

def format_time_srt(seconds: float) -> str:
    """Convierte el tiempo en segundos a formato SRT (hh:mm:ss,ms)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"