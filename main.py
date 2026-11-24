
import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH, HEIGHT = 720, 1280
FPS = 24
DURATION = 10

def font(size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            size
        )
    except:
        return ImageFont.load_default()

def create_frame(topic, frame):
    img = Image.new("RGB", (WIDTH, HEIGHT), "#101c32")
    draw = ImageDraw.Draw(img)

    # Fondo animado
    for y in range(HEIGHT):
        shade = int(18 + 15 * y / HEIGHT)
        draw.line((0, y, WIDTH, y),
                  fill=(8, shade, shade + 28))

    # Cuadrícula
    for x in range(0, WIDTH, 60):
        draw.line((x, 0, x, HEIGHT),
                  fill="#20334b", width=1)

    # Título
    draw.text((45, 100), "MAPA HISTÓRICO AI",
              font=font(30), fill="#43d9ff")

    draw.text((45, 210), topic[:35],
              font=font(39), fill="white")

    draw.text((45, 280), "HISTORIA • MAPAS • DATOS",
              font=font(19), fill="#a9c8df")

    # Mapa ilustrativo animado
    points = [
        (120, 510), (180, 440), (250, 470),
        (290, 550), (250, 620), (180, 610),
        (130, 560)
    ]

    offset = int(12 * math.sin(frame / 15))
    points = [(x, y + offset) for x, y in points]

    draw.polygon(points, fill="#176b83",
                 outline="#4ce5ff")

    draw.ellipse((360, 440, 580, 660),
                 outline="#43d9ff", width=4)

    draw.arc((385, 440, 555, 660),
             90, 270, fill="#43d9ff", width=2)

    draw.arc((385, 440, 555, 660),
             270, 90, fill="#43d9ff", width=2)

    # Barras estadísticas ilustrativas
    draw.text((45, 760), "ESTADÍSTICAS",
              font=font(30), fill="white")

    values = [45, 75, 60, 90]
    labels = ["DATO 1", "DATO 2", "DATO 3", "DATO 4"]

    for i, value in enumerate(values):
        y = 840 + i * 85
        draw.text((45, y), labels[i],
                  font=font(18), fill="#b8d8ed")
        draw.rounded_rectangle(
            (190, y, 630, y + 28),
            radius=10, fill="#263d55"
        )
        width = int(440 * value / 100 *
                    min(1, frame / 70))
        draw.rounded_rectangle(
            (190, y, 190 + width, y + 28),
            radius=10, fill="#20c9ee"
        )

    draw.text((45, 1190), "VIDEO GENERADO",
              font=font(19), fill="#43d9ff")

    return np.array(img)

def main():
    topic = " ".join(sys.argv[1:]).strip()

    if not topic:
        topic = input("Escribe el tema del video: ")

    print("Preparando video:", topic)

    output = "video_generado.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    import subprocess

    command = [
        ffmpeg, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-an", "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output
    ]

    process = subprocess.Popen(
        command, stdin=subprocess.PIPE
    )

    total = FPS * DURATION

    for frame in range(total):
        image = create_frame(topic, frame)
        process.stdin.write(image.tobytes())
        if frame % 24 == 0:
            print("Generando:", frame * 100 // total, "%")

    process.stdin.close()
    process.wait()

    print("VIDEO TERMINADO:", output)

if __name__ == "__main__":
    main()
  
