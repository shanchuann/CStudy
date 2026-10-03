from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

log = Path('/home/shanchuan/CStudy/run.log').read_text(encoding='utf-8')
out = Path('/mnt/d/Markdown/assets/c-language/wsl-cstudy-run.png')
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
font = ImageFont.truetype(font_path, 23)
small = ImageFont.truetype(font_path, 18)
lines = log.rstrip().splitlines()
width = 1540
height = max(760, 84 + len(lines) * 29)
image = Image.new('RGB', (width, height), '#252831')
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, 42), fill='#30343f')
draw.text((18, 11), 'shanchuan@localhost: ~/CStudy', font=small, fill='#d8dee9')
for index, line in enumerate(lines):
    color = '#8fbcbb' if line.startswith('shanchuan@localhost') else '#d8dee9'
    draw.text((24, 58 + index * 29), line, font=font, fill=color)
image.save(out)
