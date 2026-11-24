import sys
from PIL import Image, ImageDraw
src, out, crop = sys.argv[1], sys.argv[2], tuple(map(int, sys.argv[3].split(',')))
im = Image.open(src).convert("RGB"); d = ImageDraw.Draw(im)
for b in sys.argv[4:]:
    x1,y1,x2,y2 = map(int, b.split(','))
    d.rounded_rectangle((x1-3,y1-3,x2+3,y2+3), radius=6, outline=(230,0,0), width=3)
im.crop(crop).save(out); print(out)
