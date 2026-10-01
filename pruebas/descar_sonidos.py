import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pyttsx3

carpeta_destino = ""
_voz_advertida = False


def ffmpeg_exe():
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def wav_a_mp3(ruta_wav, ruta_mp3):
    exe = ffmpeg_exe()
    if not exe:
        raise RuntimeError(
            "No se encontró ffmpeg. Instálalo o ejecuta: pip install imageio-ffmpeg"
        )
    subprocess.run(
        [
            exe,
            "-y",
            "-i",
            ruta_wav,
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            ruta_mp3,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def configurar_voz(engine):
    """Prioridad: David > Mark > Zira > primera voz en inglés."""
    global _voz_advertida

    def es_ingles(v):
        if not v.languages:
            return False
        for lang in v.languages:
            lang_str = str(lang).lower()
            if lang_str.startswith("en") or "english" in lang_str:
                return True
        return False

    voices = engine.getProperty("voices")
    voz_seleccionada = None
    voz_nombre = ""

    for preferida in ("david", "mark", "zira"):
        for v in voices:
            if preferida in v.name.lower() and es_ingles(v):
                voz_seleccionada = v.id
                voz_nombre = v.name
                break
        if voz_seleccionada:
            break

    if not voz_seleccionada:
        for v in voices:
            if es_ingles(v):
                voz_seleccionada = v.id
                voz_nombre = v.name
                break

    if voz_seleccionada:
        engine.setProperty("voice", voz_seleccionada)
        if not _voz_advertida:
            print(f"Voz seleccionada: {voz_nombre}")
            if "zira" in voz_nombre.lower() or not (
                "david" in voz_nombre.lower() or "mark" in voz_nombre.lower()
            ):
                print("Nota: no se encontró David/Mark; se usa otra voz en inglés.")
            _voz_advertida = True
    else:
        print("No se encontró ninguna voz en inglés. Usando la voz por defecto.")

    engine.setProperty("rate", 150)
    engine.setProperty("volume", 1.0)
    return voz_seleccionada


def generar_audio(engine, texto, i, categoria, carpeta):
    ruta_wav = os.path.join(carpeta, f"{categoria}_{i}.wav")
    ruta_mp3 = os.path.join(carpeta, f"{categoria}_{i}.mp3")

    engine.save_to_file(texto, ruta_wav)
    engine.runAndWait()

    if not os.path.exists(ruta_wav) or os.path.getsize(ruta_wav) <= 5000:
        if os.path.exists(ruta_wav):
            os.remove(ruta_wav)
        raise RuntimeError(f"Audio inválido o vacío para: {texto}")

    try:
        wav_a_mp3(ruta_wav, ruta_mp3)
    finally:
        if os.path.exists(ruta_wav):
            os.remove(ruta_wav)


def seleccionar_carpeta():
    global carpeta_destino
    carpeta = filedialog.askdirectory()
    if carpeta:
        carpeta_destino = carpeta
        lbl_carpeta.config(text=f"Carpeta seleccionada:\n{carpeta}", fg="green")


def procesar():
    global carpeta_destino
    categoria = combo_categoria.get()
    palabras_texto = txt_palabras.get("1.0", tk.END).strip()

    if not categoria or not palabras_texto or not carpeta_destino:
        messagebox.showwarning(
            "Faltan datos",
            "Debes seleccionar la categoría, escribir palabras y elegir carpeta.",
        )
        return

    if not ffmpeg_exe():
        messagebox.showerror(
            "Falta ffmpeg",
            "Se necesita ffmpeg para guardar MP3 reales.\n"
            "Instala ffmpeg o ejecuta: pip install imageio-ffmpeg",
        )
        return

    palabras = [p.strip().upper() for p in palabras_texto.splitlines() if p.strip()]

    engine = pyttsx3.init()
    configurar_voz(engine)
    try:
        for i, word in enumerate(palabras, start=1):
            generar_audio(engine, word, i, categoria, carpeta_destino)
        messagebox.showinfo(
            "Completado",
            f"Se generaron {len(palabras)} MP3 en la categoría {categoria}.",
        )
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")
    finally:
        engine.stop()
        del engine


ventana = tk.Tk()
ventana.title("Descargar audios Spelling Bee")
ventana.geometry("650x500")

tk.Label(ventana, text="Selecciona categoría:", font=("Arial", 12)).pack(pady=5)
combo_categoria = ttk.Combobox(
    ventana, values=["A", "B"], state="readonly", font=("Arial", 12)
)
combo_categoria.pack(pady=5)

tk.Label(
    ventana, text="Escribe las palabras (una por línea):", font=("Arial", 12)
).pack(pady=5)
txt_palabras = scrolledtext.ScrolledText(ventana, width=70, height=10, font=("Arial", 11))
txt_palabras.pack(pady=5)

btn_carpeta = tk.Button(
    ventana,
    text="Seleccionar carpeta de destino",
    command=seleccionar_carpeta,
    bg="blue",
    fg="white",
    font=("Arial", 11, "bold"),
)
btn_carpeta.pack(pady=10)

lbl_carpeta = tk.Label(
    ventana, text="Ninguna carpeta seleccionada", font=("Arial", 10), fg="red"
)
lbl_carpeta.pack(pady=5)

btn = tk.Button(
    ventana,
    text="Generar Audios",
    command=procesar,
    bg="green",
    fg="white",
    font=("Arial", 13, "bold"),
)
btn.pack(pady=20)

ventana.mainloop()
