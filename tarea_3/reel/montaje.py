"""Parte 3 · Reel: guion.json -> voz clonada -> subtítulos -> video 9:16 con imágenes y música.

Reutiliza reel.py de la sesión 15 (voz clonada con Qwen3-TTS, narración, subtítulos con Whisper)
y le agrega lo que pide la Tarea 3: una imagen o gráfico por escena y música de fondo bajo la voz.

Uso (desde tarea_3/reel/):
    .venv-reel\\Scripts\\python.exe montaje.py --autor "Nombre Apellido" --credito-musica "Canción · Autor (Pixabay)"

La narración se guarda en narracion.wav + narracion.json: para retocar solo el video (sin volver a
generar la voz, que es lo lento) agregar --reusar-narracion.
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

import reel as R

AQUI = Path(__file__).parent

# Misma paleta que el dashboard
R.FONDO, R.TEXTO, R.SUAVE, R.ACENTO, R.CAJA = "#0b1020", "#e8ebf5", "#9aa3c4", "#ffc857", "#151d3a"
LIMITE_IMAGEN = 1240          # la imagen termina antes de los subtítulos (y = 1290)


def escena_con_imagen(e):
    """Capa de una escena: cifra grande, etiqueta y debajo la imagen o gráfico."""
    capa = Image.new("RGBA", (R.ANCHO, R.ALTO), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ancho = R.ANCHO - 2 * R.MARGEN
    y = 430
    if e.get("cifra"):
        f = R._ajustar(d, e["cifra"], "Oswald", 700, ancho, 170, 90)
        alto = -d.textbbox((0, 0), e["cifra"], font=f, anchor="ls")[1]
        y += alto
        d.text((R.MARGEN, y), e["cifra"], font=f, fill=R.ACENTO, anchor="ls")
        y += 30
    fe = R._fuente("PublicSans", 46, 600)
    for linea in R._envolver(d, e["etiqueta"], fe, ancho):
        y += 50
        d.text((R.MARGEN, y), linea, font=fe, fill=R.TEXTO, anchor="ls")
    if e.get("imagen"):
        pegar_imagen(capa, AQUI / e["imagen"], (R.MARGEN, y + 40, R.ANCHO - R.MARGEN, LIMITE_IMAGEN))
    return capa


def pegar_imagen(capa, ruta, caja):
    """Ajusta la imagen a la caja sin deformarla, con esquinas redondeadas y borde."""
    x0, y0, x1, y1 = caja
    im = Image.open(ruta).convert("RGBA")
    s = min((x1 - x0) / im.width, (y1 - y0) / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    mascara = Image.new("L", im.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *im.size), radius=22, fill=255)
    x, y = x0 + (x1 - x0 - im.width) // 2, y0 + (y1 - y0 - im.height) // 2
    capa.paste(im, (x, y), mascara)
    ImageDraw.Draw(capa).rounded_rectangle((x, y, x + im.width, y + im.height), radius=22,
                                           outline="#26305a", width=3)


def video(guion, narracion, ruta, fuente_datos, autor, musica=None, volumen=0.12):
    """Como R.video, pero con imagen por escena y la música mezclada debajo de la voz."""
    ruta = Path(ruta)
    wav = ruta.with_name("narracion.wav")
    sf.write(wav, narracion.audio, narracion.sr)
    base = R._base(guion["titulo"], fuente_datos, autor)
    capas = [escena_con_imagen(e) for e in guion["escenas"]]
    bloques = R._bloques(narracion.palabras)
    fuente_sub = R._fuente("PublicSans", 62, 800)
    dur = narracion.duracion

    cmd = [R.FFMPEG, "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.ANCHO}x{R.ALTO}", "-r", str(R.FPS), "-i", "-",
           "-i", str(wav)]
    voz = "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000"
    if musica:
        cmd += ["-stream_loop", "-1", "-i", str(musica)]
        filtro = (f"{voz}[v];[2:a]aresample=48000,volume={volumen},afade=t=in:d=1.5,"
                  f"afade=t=out:st={max(0, dur - 2.5):.2f}:d=2.5[m];"
                  f"[v][m]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        filtro = f"{voz}[a]"
    cmd += ["-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(ruta)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(dur * R.FPS)):
        proc.stdin.write(R._cuadro(base, capas, narracion, k / R.FPS, bloques, fuente_sub).tobytes())
    proc.stdin.close()
    proc.wait()
    return ruta


def guardar_narracion(n):
    sf.write(AQUI / "narracion.wav", n.audio, n.sr)
    (AQUI / "narracion.json").write_text(json.dumps(
        {"sr": n.sr, "escenas": n.escenas, "palabras": n.palabras}, ensure_ascii=False), encoding="utf-8")


def cargar_narracion():
    meta = json.loads((AQUI / "narracion.json").read_text(encoding="utf-8"))
    audio, sr = sf.read(AQUI / "narracion.wav", dtype="float32")
    return R.Narracion(audio, sr, [tuple(e) for e in meta["escenas"]], [tuple(p) for p in meta["palabras"]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voz", default="recursos/mi_voz.wav")
    ap.add_argument("--autor", required=True)
    ap.add_argument("--fuente", default="NASA/NOAA VIIRS 2021, Maus et al. (2022), INEI-BCRP")
    ap.add_argument("--musica", default="recursos/musica.mp3")
    ap.add_argument("--credito-musica", default="")
    ap.add_argument("--volumen-musica", type=float, default=0.12)
    ap.add_argument("--tts", default="Qwen/Qwen3-TTS-12Hz-0.6B-Base")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--velocidad", type=float, default=1.0)
    ap.add_argument("--reusar-narracion", action="store_true")
    a = ap.parse_args()

    t = time.time()
    guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
    if a.reusar_narracion:
        narracion = cargar_narracion()
        R._reloj("narración reutilizada", t)
    else:
        voz = R.Voz(AQUI / a.voz, modelo=a.tts, device=a.device)
        R._reloj(f"voz clonada · referencia: «{voz.texto_ref}»", t)
        narracion = R.narrar(voz, guion, velocidad=a.velocidad)
        R._reloj("narración generada", t)
        R.subtitulos(narracion, guion)
        guardar_narracion(narracion)
        R._reloj("subtítulos listos", t)
    R.a_srt(narracion, AQUI / "subtitulos.srt")
    (AQUI / "guion.json").write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nControl de calidad (WER = cuánto se aleja lo que oyó Whisper del guion; ideal < 0,15):")
    for i, e in enumerate(guion["escenas"], 1):
        if "wer" in e:
            print(f"  escena {i}: WER {e['wer']:.2f}")
    print(f"Duración: {narracion.duracion:.1f} s", "OK" if 45 <= narracion.duracion <= 75 else "(¡fuera de 45-75 s!)")

    fuente = a.fuente + (f" · Música: {a.credito_musica}" if a.credito_musica else "")
    musica = AQUI / a.musica if (AQUI / a.musica).exists() else None
    if not musica:
        print("AVISO: no encontré la música; el video saldrá solo con voz.")
    salida = video(guion, narracion, AQUI / "reel.mp4", fuente, a.autor, musica, a.volumen_musica)
    R._reloj(f"video listo: {salida}", t)

    # portada para LinkedIn: un cuadro de la escena 1
    tp = narracion.escenas[0][0] + 1.5
    R._cuadro(R._base(guion["titulo"], fuente, a.autor), [escena_con_imagen(e) for e in guion["escenas"]],
              narracion, tp, R._bloques(narracion.palabras), R._fuente("PublicSans", 62, 800)).save(AQUI / "portada.png")


if __name__ == "__main__":
    main()
