import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

# Video vertical 9:16, 60 seconds
W, H = 720, 1280
FPS = 24
DURATION = 60
TOTAL = FPS * DURATION
tema = " ".join(sys.argv[1:]) or "Historia del mundo"
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(size, bold=False):
    try:
        return ImageFont.truetype(BOLD if bold else FONT, size)
    except OSError:
        return ImageFont.load_default()

def centered(draw, text, y, size, color=(245, 248, 250), bold=True):
    f = font(size, bold)
    box = draw.textbbox((0, 0), text, font=f)
    draw.text(((W - (box[2] - box[0])) // 2, y), text, font=f, fill=color)

def rounded(draw, xy, fill, outline=None, radius=20, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def background(draw, frame):
    draw.rectangle((0, 0, W, H), fill=(7, 17, 31))
    # Subtle cartographic grid
    for x in range(-20, W + 20, 60):
        draw.line((x, 0, x, H), fill=(17, 37, 52), width=1)
    for y in range(0, H, 60):
        draw.line((0, y, W, y), fill=(17, 37, 52), width=1)
    # Soft moving longitude curves
    for i in range(4):
        x = 80 + i * 185 + int(math.sin(frame / 90 + i) * 12)
        draw.arc((x - 100, 180, x + 100, 1080), 75, 285, fill=(18, 54, 66), width=2)
    # Decorative corner marks
    for x, y, sx, sy in [(28, 155, 1, 1), (692, 155, -1, 1),
                         (28, 1120, 1, -1), (692, 1120, -1, -1)]:
        draw.line((x, y, x + sx * 24, y), fill=(54, 119, 126), width=3)
        draw.line((x, y, x, y + sy * 24), fill=(54, 119, 126), width=3)

def header(draw, scene):
    rounded(draw, (34, 38, 686, 126), (15, 42, 57), (49, 112, 119), 18, 2)
    draw.ellipse((55, 66, 77, 88), fill=(255, 190, 78))
    draw.text((94, 61), "ATLAS HISTÓRICO", font=font(27, True), fill=(226, 241, 239))
    draw.text((94, 94), f"EXPLORACIÓN VISUAL  /  {scene + 1:02d}", font=font(13, True), fill=(105, 194, 183))

def footer(draw, frame, scene):
    rounded(draw, (35, 1160, 685, 1238), (13, 34, 49), (35, 83, 96), 16, 2)
    draw.text((55, 1173), f"SECUENCIA {scene + 1} / 6", font=font(17, True), fill=(171, 207, 210))
    draw.rectangle((55, 1208, 665, 1217), fill=(31, 59, 71))
    draw.rectangle((55, 1208, 55 + int(610 * frame / max(1, TOTAL - 1)), 1217), fill=(255, 184, 74))

def draw_compass(draw, cx=615, cy=205, angle=0):
    draw.ellipse((cx-38, cy-38, cx+38, cy+38), outline=(70, 139, 143), width=2)
    draw.line((cx, cy-27, cx, cy+27), fill=(87, 151, 153), width=2)
    draw.line((cx-27, cy, cx+27, cy), fill=(87, 151, 153), width=2)
    a = angle
    tip = (cx + int(26 * math.sin(a)), cy - int(26 * math.cos(a)))
    draw.polygon([(cx, cy), tip, (cx-5, cy+7)], fill=(255, 187, 76))
    draw.text((cx-6, cy-58), "N", font=font(15, True), fill=(225, 235, 229))

def map_art(draw, progress, variant=0):
    # Stylized landmass, intentionally illustrative rather than a real historical border
    shift = int(math.sin(progress * math.pi * 2) * 7)
    pts = [(112+shift,430),(153,340),(235,300),(295,330),(350,300),
           (410,340),(485,360),(548,440),(528,520),(480,570),
           (438,650),(360,630),(310,685),(235,645),(175,590),(125,520)]
    draw.polygon(pts, fill=(25, 91, 91), outline=(96, 205, 176))
    draw.line(pts + [pts[0]], fill=(96, 205, 176), width=4)
    # Internal terrain contours
    for k in range(4):
        yy = 390 + k * 62
        draw.arc((165, yy-45, 500, yy+80), 5, 170, fill=(48, 132, 123), width=2)
    # Water / coast accents
    for k in range(3):
        draw.arc((75-k*12, 365-k*10, 580+k*12, 690+k*10), 195, 345,
                 fill=(34, 94, 123), width=2)
    # Animated route with glowing stops
    route = [(170, 490), (250, 420), (335, 465), (420, 405), (495, 495)]
    for i in range(len(route)-1):
        draw.line((route[i], route[i+1]), fill=(90, 105, 82), width=8)
    p = progress * (len(route)-1)
    idx = min(int(p), len(route)-2)
    t = p - idx
    x = int(route[idx][0] * (1-t) + route[idx+1][0] * t)
    y = int(route[idx][1] * (1-t) + route[idx+1][1] * t)
    for i, (px, py) in enumerate(route):
        r = 10 if i <= idx else 7
        draw.ellipse((px-r, py-r, px+r, py+r), fill=(255, 211, 123), outline=(255, 245, 210), width=2)
    draw.ellipse((x-18, y-18, x+18, y+18), outline=(255, 193, 82), width=4)
    draw.ellipse((x-7, y-7, x+7, y+7), fill=(255, 229, 155))

def info_card(draw, y, number, title, detail, progress):
    rounded(draw, (65, y, 655, y+112), (15, 39, 54), (42, 91, 101), 17, 2)
    draw.ellipse((86, y+27, 142, y+83), fill=(31, 94, 91), outline=(93, 191, 165), width=2)
    centered_num = str(number)
    draw.text((114-draw.textbbox((0,0), centered_num, font=font(23, True))[2]//2, y+40),
              centered_num, font=font(23, True), fill=(255, 202, 112))
    draw.text((164, y+20), title, font=font(24, True), fill=(239, 245, 239))
    draw.text((164, y+57), detail, font=font(17), fill=(156, 190, 194))
    draw.rectangle((164, y+88, 620, y+94), fill=(31, 60, 70))
    draw.rectangle((164, y+88, 164+int(456*progress), y+94), fill=(71, 184, 157))

def scene_frame(scene, progress, frame):
    img = Image.new("RGB", (W, H), (7, 17, 31))
    draw = ImageDraw.Draw(img)
    background(draw, frame)
    header(draw, scene)
    draw_compass(draw, angle=progress * math.pi * 2)

    if scene == 0:
        centered(draw, "UN VIAJE A TRAVÉS", 340, 36, (185, 213, 211))
        centered(draw, tema.upper()[:32], 405, 43, (255, 194, 94))
        centered(draw, "DEL TIEMPO Y EL TERRITORIO", 475, 25, (228, 239, 235))
        # Layered glowing rings
        for r, color, width in [(150, (42, 116, 116), 3), (118, (67, 161, 145), 3), (82, (255, 185, 75), 4)]:
            draw.ellipse((360-r, 760-r, 360+r, 760+r), outline=color, width=width)
        draw.arc((210, 610, 510, 910), -90, -90 + int(progress*300), fill=(255, 198, 104), width=10)
        centered(draw, "MAPAS  •  RUTAS  •  MEMORIA", 960, 22, (156, 199, 196))

    elif scene == 1:
        centered(draw, "EL TERRITORIO", 205, 39)
        map_art(draw, progress)
        rounded(draw, (82, 800, 638, 930), (14, 39, 54), (43, 103, 109), 18, 2)
        centered(draw, "Una mirada al espacio", 824, 25, (255, 195, 95))
        centered(draw, "donde ocurrieron los hechos", 866, 21, (188, 213, 211))

    elif scene == 2:
        centered(draw, "PIEZAS DE UNA HISTORIA", 205, 36)
        info_card(draw, 330, 1, "TERRITORIO", "Lugares y fronteras", min(1, progress*1.25))
        info_card(draw, 475, 2, "INTERCAMBIO", "Rutas y conexiones", min(1, max(0, progress*1.25-0.12)))
        info_card(draw, 620, 3, "SOCIEDAD", "Personas y comunidades", min(1, max(0, progress*1.25-0.24)))
        info_card(draw, 765, 4, "CAMBIO", "Transformaciones en el tiempo", min(1, max(0, progress*1.25-0.36)))
        centered(draw, "ESQUEMA VISUAL ILUSTRATIVO", 970, 18, (255, 195, 95))

    elif scene == 3:
        centered(draw, "EL PASO DEL TIEMPO", 215, 38)
        y = 610
        draw.line((92, y, 628, y), fill=(65, 151, 143), width=8)
        labels = ["ORIGEN", "DESARROLLO", "TRANSFORMACIÓN", "LEGADO"]
        for i, label in enumerate(labels):
            x = 105 + i*170
            draw.ellipse((x-19, y-19, x+19, y+19), fill=(255, 188, 78), outline=(255, 229, 165), width=3)
            draw.text((x-52, y+48), label, font=font(14, True), fill=(222, 235, 229))
            if progress > i/4:
                draw.ellipse((x-29, y-29, x+29, y+29), outline=(255, 194, 95), width=3)
        rounded(draw, (80, 790, 640, 910), (15, 40, 55), (44, 101, 109), 18, 2)
        centered(draw, "Cada época deja huellas", 823, 26, (255, 196, 100))
        centered(draw, "que ayudan a explicar el presente", 865, 20, (184, 211, 207))

    elif scene == 4:
        centered(draw, "RUTAS Y CONEXIONES", 205, 38)
        map_art(draw, progress)
        # Moving small travel marker across lower route
        x = 110 + int(progress * 500)
        draw.ellipse((x-13, 895, x+13, 921), fill=(255, 190, 80), outline=(255, 237, 185), width=3)
        rounded(draw, (78, 955, 642, 1050), (15, 40, 55), (44, 101, 109), 18, 2)
        centered(draw, "Los lugares no están aislados", 980, 23)
        centered(draw, "se conectan mediante rutas e historias", 1015, 18, (169, 204, 201))

    else:
        centered(draw, "EL LEGADO", 365, 52, (255, 197, 100))
        centered(draw, tema[:38], 455, 27, (232, 241, 234))
        # Expanding rings
        for r in [90, 145, 200]:
            draw.arc((360-r, 790-r, 360+r, 790+r), 20, 20 + int(progress*300),
                     fill=(76, 178, 155), width=5)
        centered(draw, "Comprender el pasado", 1030, 26)
        centered(draw, "nos ayuda a mirar el futuro", 1070, 22, (168, 205, 200))

    footer(draw, frame, scene)
    return np.asarray(img, dtype=np.uint8)

command = [
    ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
    "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", "video_generado.mp4"
]

process = subprocess.Popen(command, stdin=subprocess.PIPE)
try:
    for frame in range(TOTAL):
        scene = min(5, frame // (TOTAL // 6))
        progress = (frame % (TOTAL // 6)) / (TOTAL // 6)
        process.stdin.write(scene_frame(scene, progress, frame).tobytes())
    process.stdin.close()
    result = process.wait()
    if result != 0:
        raise RuntimeError("Error al crear el video")
    print("VIDEO CREADO: video_generado.mp4")
except Exception:
    process.kill()
    raise
