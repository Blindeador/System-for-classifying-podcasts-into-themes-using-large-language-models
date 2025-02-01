import pysrt
import whisper
from pysrt import SubRipFile, SubRipItem

# Cargar el modelo base de Whisper
model = whisper.load_model("base")

# Transcribir un archivo de audio
result = model.transcribe("podcast.mp3")

# Imprimir la transcripción
print(result["text"])

subs = SubRipFile()

transcripciones = [
    ("00:00:01,000", "00:00:05,000", "Hola, bienvenidos al podcast."),
    ("00:00:06,000", "00:00:10,000", "Hoy hablaremos sobre tecnología."),
]

for idx, (start, end, text) in enumerate(transcripciones, 1):
    subs.append(SubRipItem(index=idx, start=start, end=end, text=text))

subs.save('transcripcion.srt', encoding='utf-8')

result = model.transcribe("podcast.mp3", output_format="srt")
with open("transcripcion.srt", "w") as file:
    file.write(result)

subs = pysrt.open('transcripcion.srt')

for sub in subs:
    print(f"[{sub.start}] {sub.text}")


