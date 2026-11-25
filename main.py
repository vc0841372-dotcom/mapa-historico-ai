import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

# Atlas histórico: video vertical animado de 60 segundos.
# Los mapas y recorridos de esta versión son ilustrativos, no fronteras históricas exactas.

W, H = 720, 1280
FPS = 24
DURATION = 60
TOTAL = FPS * DURATION

tema = " ".join(sys.argv[1:]).strip() or "Historia del mundo"
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(size, bold=False):
    try:
        return ImageFont.truetype(bold_path if bold else font_path, size)
    except Exception:
        return ImageFont.load_default()

def centered(draw, text, y, size, color=(245, 240, 220), bold=True):
    f = font(size, bold)
    box = draw.textbbox((0, 0), text, font=f)
    x = (W - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=f, fill=color)

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def background(draw, t):
    draw.rectangle((0, 0, W, H), fill=(8, 17, 31))
    for x in range(0, W, 48):
        draw.line((x, 0, x, H), fill=(19, 38, 51), width=1)
    for y in range(0, H, 48):
        draw.line((0, y, W, y), fill=(19, 38, 51), width=1)
    for k in range(7):
        yy = 300 + k * 18
        pts = []
        for x in range(25, W - 25, 12):
            y = yy + int(8 * math.sin(x / 54 + k * .7 + t * .4))
            pts.append((x, y))
        if len(pts) > 1:
            draw.line(pts, fill=(25, 58, 65), width=1)

def draw_compass(draw, cx, cy, r=42):
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(198, 166, 105), width=2)
    draw.ellipse((cx-r+7, cy-r+7, cx+r-7, cy+r-7), outline=(83, 112, 116), width=1)
    draw.polygon([(cx, cy-r+7), (cx-8, cy), (cx, cy+8), (cx+8, cy)], fill=(219, 180, 105))
    draw.polygon([(cx, cy+r-7), (cx-8, cy), (cx, cy+8), (cx+8, cy)], fill=(62, 101, 111))
    centered(draw, "N", cy-r-25, 17, (225, 205, 160), True)

def map_art(draw, progress, scene, t):
    points = [
        (92, 520), (125, 445), (175, 405), (210, 340),
        (285, 325), (330, 365), (390, 345), (445, 385),
        (510, 420), (565, 505), (535, 575), (480, 615),
        (430, 590), (385, 655), (315, 635), (270, 685),
        (205, 640), (150, 600), (112, 565)
    ]
    draw.polygon(points, fill=(25, 83, 83), outline=(111, 184, 157))
    draw.line(points + [points[0]], fill=(128, 193, 160), width=4)
    for i in range(9):
        x0 = 150 + i * 35
        y0 = 455 + int(25 * math.sin(i))
        draw.arc((x0, y0, x0 + 125, y0 + 90), 185, 350,
                 fill=(52, 119, 108), width=2)
    draw.line([(185, 430), (240, 500), (310, 470), (365, 545), (455, 470)],
              fill=(78, 145, 129), width=2)
    route = [(155, 540), (230, 475), (315, 505), (395, 445), (500, 510)]
    p = max(0.0, min(1.0, progress))
    segment = p * (len(route) - 1)
    idx = min(int(segment), len(route) - 2)
    frac = segment - idx
    for i in range(idx):
        draw.line((route[i], route[i+1]), fill=(238, 178, 88), width=6)
    if idx < len(route) - 1:
        x = int(route[idx][0] * (1-frac) + route[idx+1][0] * frac)
        y = int(route[idx][1] * (1-frac) + route[idx+1][1] * frac)
        draw.line((route[idx], (x, y)), fill=(238, 178, 88), width=6)
        pulse = 8 + int(4 * (1 + math.sin(t * 5)))
        draw.ellipse((x-pulse, y-pulse, x+pulse, y+pulse),
                     fill=(255, 211, 130), outline=(255, 242, 208), width=2)
    for x, y in route:
        draw.ellipse((x-5, y-5, x+5, y+5), fill=(245, 208, 133))

def draw_scene(frame_no):
    t = frame_no / FPS
    progress = (frame_no % (FPS * 18)) / (FPS * 18)
    scene = int(t // 15)
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    background(d, t)
    rounded(d, (38, 38, W-38, 145), 22, (13, 31, 43), (75, 113, 111), 2)
    d.text((62, 58), "ATLAS HISTÓRICO", font=font(24, True), fill=(226, 194, 133))
    d.text((62, 96), "EXPLORADOR DEL TIEMPO", font=font(15), fill=(139, 177, 170))
    draw_compass(d, 620, 92, 30)
    title = tema.upper()[:34]
    centered(d, title, 190, 30, (248, 239, 216), True)
    centered(d, "MAPA NARRATIVO ILUSTRADO", 235, 15, (135, 177, 168), False)
    rounded(d, (32, 285, W-32, 735), 26, (10, 27, 39), (65, 107, 105), 2)
    map_art(d, progress, scene, t)
    d.text((58, 315), "NORTE", font=font(13, True), fill=(156, 190, 175))
    d.text((535, 690), "SUR", font=font(13, True), fill=(156, 190, 175))
    d.line((70, 700, 165, 700), fill=(210, 180, 126), width=3)
    d.text((175, 691), "ESCALA ILUSTRATIVA", font=font(12), fill=(164, 181, 166))
    headings = ["CONTEXTO", "CAMBIOS", "LEGADO", "RECORRIDO"]
    descriptions = [
        "Un vistazo visual a los hechos y lugares que marcaron esta historia.",
        "Las rutas y regiones se transforman a lo largo del tiempo.",
        "Cada etapa deja huellas en la cultura, la sociedad y el territorio.",
        "Sigue el recorrido y descubre cómo se conectan los acontecimientos."
    ]
    card_index = min(3, int((t % 15) / 3.75))
    rounded(d, (42, 785, W-42, 1000), 22, (17, 38, 49), (76, 121, 112), 2)
    d.text((72, 817), headings[card_index], font=font(21, True), fill=(229, 190, 124))
    desc = descriptions[card_index]
    words = desc.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if d.textbbox((0,0), test, font=font(20))[2] > W - 145:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    for j, txt in enumerate(lines[:4]):
        d.text((72, 862 + j*31), txt, font=font(20), fill=(222, 228, 211))
    rounded(d, (42, 1030, W-42, 1145), 20, (12, 29, 42), (59, 99, 99), 2)
    d.text((68, 1050), "LÍNEA DEL TIEMPO", font=font(16, True), fill=(224, 190, 128))
    x1, x2, yy = 75, W-75, 1105
    d.line((x1, yy, x2, yy), fill=(77, 112, 108), width=4)
    marker_x = int(x1 + (x2-x1) * ((t % DURATION) / DURATION))
    d.line((x1, yy, marker_x, yy), fill=(235, 177, 88), width=5)
    for k in range(5):
        xx = x1 + int((x2-x1) * k / 4)
        d.ellipse((xx-6, yy-6, xx+6, yy+6), fill=(230, 194, 132))
    d.ellipse((marker_x-9, yy-9, marker_x+9, yy+9), fill=(255, 222, 151))
    centered(d, "HISTORIA • GEOGRAFÍA • MEMORIA", 1180, 15, (143, 177, 166), False)
    d.rectangle((0, 1267, W, 1280), fill=(29, 53, 58))
    d.rectangle((0, 1267, int(W * (frame_no+1) / TOTAL), 1280), fill=(218, 169, 91))
    return im

def main():
    cmd = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-", "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "video_generado.mp4"
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for frame_no in range(TOTAL):
            frame = np.asarray(draw_scene(frame_no), dtype=np.uint8)
            proc.stdin.write(frame.tobytes())
            if frame_no % (FPS * 10) == 0:
                print(f"Procesando: {frame_no // FPS}/{DURATION} segundos", flush=True)
    finally:
        if proc.stdin:
            proc.stdin.close()
    result = proc.wait()
    if result != 0:
        raise RuntimeError("FFmpeg no pudo terminar de generar el video.")
    print("Video creado: video_generado.mp4", flush=True)

if __name__ == "__main__":
    main()
