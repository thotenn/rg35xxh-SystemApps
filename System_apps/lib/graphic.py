from fcntl import ioctl
from PIL import Image, ImageDraw, ImageFont
import mmap
import os

fb: int
mm: mmap.mmap
screen_width = 640
screen_height = 480
bytes_per_pixel = 4
screen_size = screen_width * screen_height * bytes_per_pixel

fontFile = {}
fontFile[15] = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 15)
fontFile[13] = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 13)
fontFile[11] = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 11)
colorBlue = "#bb7200"
colorBlueD1 = "#7f4f00"
colorGray = "#292929"
colorGrayL1 = "#383838"
colorGrayD2 = "#141414"
colorGreen = "#008f39"

activeImage: Image.Image
activeDraw: ImageDraw.ImageDraw


def screen_reset():
    ioctl(
        fb,
        0x4601,
        b"\x80\x02\x00\x00\xe0\x01\x00\x00\x80\x02\x00\x00\xc0\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00^\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\xc2\xa2\x00\x00\x1a\x00\x00\x00T\x00\x00\x00\x0c\x00\x00\x00\x1e\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    )
    ioctl(fb, 0x4611, 0)


def draw_start():
    global fb, mm
    fb = os.open("/dev/fb0", os.O_RDWR)
    mm = mmap.mmap(fb, screen_size)


def draw_end():
    global fb, mm
    mm.close()
    os.close(fb)


def crate_image():
    image = Image.new("RGBA", (screen_width, screen_height), color="black")
    return image


def draw_active(image):
    global activeImage, activeDraw
    activeImage = image
    activeDraw = ImageDraw.Draw(activeImage)


def draw_paint():
    global activeImage
    mm.seek(0)
    mm.write(activeImage.tobytes())


def draw_clear():
    global activeDraw
    activeDraw.rectangle((0, 0, screen_width, screen_height), fill="black")


def draw_text(position, text, font=15, color="white", **kwargs):
    global activeDraw
    activeDraw.text(position, text, font=fontFile[font], fill=color, **kwargs)


def draw_rectangle(position, fill=None, outline=None, width=1):
    global activeDraw
    activeDraw.rectangle(position, fill=fill, outline=outline, width=width)


def draw_rectangle_r(position, radius, fill=None, outline=None):
    global activeDraw
    activeDraw.rounded_rectangle(position, radius, fill=fill, outline=outline)


def draw_circle(position, radius, fill=None, outline="white"):
    global activeDraw
    activeDraw.ellipse(
        [position[0], position[1], position[0] + radius, position[1] + radius],
        fill=fill,
        outline=outline,
    )


def draw_log(text, fill="Black", outline="black", width=500, height=80, centered=True):
    # Center the rectangle horizontally
    x = (screen_width - width) / 2
    # Center the rectangle vertically
    y = (screen_height - height) / 2  # 80 is the height of the rectangle
    draw_rectangle_r([x, y, x + width, y + height], 5, fill=fill, outline=outline)

    # Center the text within the rectangle
    lines = text.split('\n')
    text_x = x + (width / 2 if centered else 20)
    line_height = 25  # Line height
    
    for i, line in enumerate(lines):
        text_y = y + (height / 2 if centered else 20 + (i * line_height))
        draw_text((text_x, text_y), line, anchor=("mm" if centered else "lt"))


def draw_scrollable_text(text, x, y, width, height, scroll_offset=0, fill="Black", outline="black"):
    """
    Dibuja texto con capacidad de scroll vertical.
    
    Args:
        text (str): Texto a dibujar
        x (int): Posición X
        y (int): Posición Y
        width (int): Ancho del contenedor
        height (int): Alto del contenedor
        scroll_offset (int): Desplazamiento vertical del scroll
        fill (str): Color de fondo
        outline (str): Color del borde
    """
    # Dibuja el contenedor
    draw_rectangle_r([x, y, x + width, y + height], 5, fill=fill, outline=outline)
    
    # Preparar el texto
    font_height = 20  # Altura aproximada de la fuente
    padding = 10  # Padding interno
    
    # Dividir el texto en líneas
    wrapped_lines = []
    for line in text.split('\n'):
        # Calcular cuántos caracteres caben en el ancho disponible
        chars_per_line = (width - (padding * 2)) // 10  # Aproximadamente 10px por caracter
        # Envolver el texto
        if len(line) > chars_per_line:
            while line:
                if len(line) <= chars_per_line:
                    wrapped_lines.append(line)
                    break
                split_at = line[:chars_per_line].rfind(' ')
                if split_at == -1:
                    split_at = chars_per_line
                wrapped_lines.append(line[:split_at])
                line = line[split_at:].lstrip()
        else:
            wrapped_lines.append(line)

    # Calcular líneas visibles basado en la altura
    visible_lines = (height - (padding * 2)) // font_height
    
    # Aplicar scroll_offset
    start_line = scroll_offset // font_height
    end_line = min(start_line + visible_lines, len(wrapped_lines))
    
    # Dibujar líneas visibles
    for i, line in enumerate(wrapped_lines[start_line:end_line]):
        text_y = y + padding + (i * font_height) - (scroll_offset % font_height)
        if text_y + font_height > y + height - padding:
            break
        draw_text((x + padding, text_y), line)
    
    # Dibujar indicadores de scroll si es necesario
    if start_line > 0:
        draw_text((x + width // 2, y + padding), "▲", anchor="mm")
    if end_line < len(wrapped_lines):
        draw_text((x + width // 2, y + height - padding), "▼", anchor="mm")


draw_start()
screen_reset()

imgMain = crate_image()
draw_active(imgMain)
