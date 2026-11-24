import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W, H = 720, 1280
FPS = 24
DURATION = 60
TOTAL = FPS * DURATION

tema = " ".join(sys.argv[1:]) or "Historia del mundo"

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(size, bold=False):
    path = bold_path if bold else font_path
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def centered(draw, text, y, size, color=(255,255,255), bold=True):
    f = font(size, bold)
    box = draw.textbbox((0,0), text, font=f)
    x = (W - (box[2]-box[0])) // 2
    draw.text((x,y), text, font=f, fill=color)

def background(draw):
    draw.rectangle((0,0,W,H), fill=(10,20,38))
    for x in range(0,W,60):
        draw.line((x,0,x,H), fill=(22,40,58), width=1)
    for y in range(0,H,60):
        draw.line((0,y,W,y), fill=(22,40,58), width=1)

def map_shape(draw, progress, scene):
    points = [
        (105,430),(155,340),(250,315),(310,360),
        (390,335),(475,390),(535,490),(495,580),
        (425,625),(350,590),(280,660),(190,600),
        (130,520)
    ]
    draw.polygon(points, fill=(28,105,112), outline=(90,220,190))
    draw.line(points + [points[0]], fill=(90,220,190), width=4)

    # Rutas animadas ilustrativas
    route = [(165,470),(245,425),(330,465),(420,430),(490,510)]
    count = max(1, int(progress * (len(route)-1)))
    for i in range(count):
        draw.line((route[i],route[i+1]), fill=(255,190,75), width=6)
    px = progress * (len(route)-1)
    idx = min(int(px),len(route)-2)
    t = px-idx
    x = int(route[idx][0]*(1-t)+route[idx+1][0]*t)
    y = int(route[idx][1]*(1-t)+route[idx+1][1]*t)
    draw.ellipse((x-12,y-12,x+12,y+12), fill=(255,220,100))

    for x,y in route:
        draw.ellipse((x-6,y-6,x+6,y+6), fill=(255,255,255))

def scene_frame(scene, progress, frame):
    img = Image.new("RGB",(W,H),(10,20,38))
    draw = ImageDraw.Draw(img)
    background(draw)

    # Encabezado
    draw.rounded_rectangle((35,45,685,125), radius=18, fill=(20,48,65))
    centered(draw, "HISTORIA EN MOVIMIENTO", 67, 27, (100,230,200))

    if scene == 0:
        centered(draw, "UN VIAJE POR", 360, 43)
        centered(draw, tema.upper()[:30], 430, 43, (255,195,90))
        centered(draw, "MAPAS • CAMBIOS • HISTORIA", 520, 23, (170,200,215))
        draw.ellipse((220,650,500,930), outline=(80,210,180), width=5)
        draw.arc((220,650,500,930), 0, int(progress*360), fill=(255,190,75), width=12)

    elif scene == 1:
        centered(draw, "EL TERRITORIO", 210, 38)
        map_shape(draw, progress, scene)
        centered(draw, "MAPA ILUSTRATIVO", 800, 25, (255,195,90))
        centered(draw, "Rutas y movimientos", 850, 23)

    elif scene == 2:
        centered(draw, "CAMBIOS Y DIMENSIONES", 210, 34)
        labels = ["Territorio","Comercio","Población","Influencia"]
        for i,label in enumerate(labels):
            y = 390 + i*145
            draw.text((65,y),label,font=font(25,True),fill=(240,245,250))
            width = int(480 * min(1, max(0, progress*1.25 - i*0.12)))
            draw.rounded_rectangle((65,y+48,645,y+85),radius=12,fill=(35,55,70))
            draw.rounded_rectangle((65,y+48,65+width,y+85),radius=12,fill=(60,190,165))
        centered(draw, "ESQUEMA VISUAL, NO CIFRAS HISTÓRICAS", 1030, 17, (255,195,90))

    elif scene == 3:
        centered(draw, "UNA LÍNEA DEL TIEMPO", 220, 37)
        y = 610
        draw.line((85,y,635,y),fill=(80,210,180),width=8)
        labels = ["INICIO","EXPANSIÓN","CAMBIO","LEGADO"]
        for i,label in enumerate(labels):
            x = 100+i*170
            draw.ellipse((x-15,y-15,x+15,y+15),fill=(255,190,75))
            draw.text((x-45,y+45),label,font=font(18,True),fill=(255,255,255))
            if progress > i/4:
                draw.ellipse((x-23,y-23,x+23,y+23),outline=(255,220,120),width=4)
        centered(draw, "ETAPAS PRINCIPALES", 850, 25, (170,210,220))

    elif scene == 4:
        centered(draw, "RUTAS Y CONEXIONES", 210, 38)
        map_shape(draw, progress, scene)
        centered(draw, "MOVIMIENTO ILUSTRATIVO", 800, 24, (255,195,90))
        draw.rounded_rectangle((75,900,645,1010),radius=20,fill=(20,48,65))
        centered(draw, "Los mapas ayudan a comprender", 925, 22)
        centered(draw, "cómo se relacionan los lugares", 960, 22)

    else:
        centered(draw, "EL LEGADO", 390, 52)
        centered(draw, tema[:45], 500, 28, (255,195,90))
        centered(draw, "La historia sigue conectándonos", 620, 25)
        draw.arc((180,730,540,1090),0,int(progress*360),fill=(80,210,180),width=10)

    # Barra de progreso
    draw.rectangle((35,1175,685,1185),fill=(35,55,70))
    draw.rectangle((35,1175,35+int(650*frame/TOTAL),1185),fill=(255,190,75))
    centered(draw, f"ESCENA {scene+1} DE 6", 1200, 19, (170,200,215))

    return np.asarray(img,dtype=np.uint8)

command = [
    ffmpeg, "-y",
    "-f","rawvideo",
    "-vcodec","rawvideo",
    "-pix_fmt","rgb24",
    "-s",f"{W}x{H}",
    "-r",str(FPS),
    "-i","-",
    "-an",
    "-c:v","libx264",
    "-pix_fmt","yuv420p",
    "-movflags","+faststart",
    "video_generado.mp4"
]

process = subprocess.Popen(command, stdin=subprocess.PIPE)

try:
    for frame in range(TOTAL):
        scene = min(5, frame // (TOTAL//6))
        progress = (frame % (TOTAL//6)) / (TOTAL//6)
        image = scene_frame(scene, progress, frame)
        process.stdin.write(image.tobytes())

    process.stdin.close()
    result = process.wait()
    if result != 0:
        raise RuntimeError("Error al crear el video")

    print("VIDEO CREADO: video_generado.mp4")

except Exception:
    process.kill()
    raise
