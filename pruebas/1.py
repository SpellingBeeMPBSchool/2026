import asyncio
import importlib

edge_tts = importlib.import_module("edge_tts")

async def descar_sonidos(texto):
     voice = "en-US-GuyNeural"
     communicate = edge_tts.Communicate(texto, voice)
     await communicate.save(f"C:/Users/ASUS/Documents/MISALES PASTRANA BORRERO/1102 2025/GORETTI/spelling_bee_page/assets/audios/A_.mp3")

asyncio.run(descar_sonidos("AGREEMENT"))