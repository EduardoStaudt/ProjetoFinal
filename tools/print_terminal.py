"""Gera PNG estilo terminal a partir de um comando e sua saída.
Uso: python tools/print_terminal.py <pasta_assets> <XX-oQueTemNoPrint> <arquivo_saida.txt> [prompt]
O .txt deve conter a(s) linha(s) de comando e a saída, exatamente como no terminal.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

pasta, nome, txt = sys.argv[1], sys.argv[2], sys.argv[3]
texto = open(txt, encoding="utf-8", errors="replace").read().expandtabs(4).rstrip("\n")
linhas = []
for l in texto.splitlines():
    while len(l) > 140:
        linhas.append(l[:140]); l = l[140:]
    linhas.append(l)
linhas = linhas[:120]

fonte = None
for f in ["DejaVuSansMono.ttf", "consola.ttf", "C:/Windows/Fonts/consola.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]:
    try:
        fonte = ImageFont.truetype(f, 15); break
    except OSError:
        pass
fonte = fonte or ImageFont.load_default()

lh, pad, barra = 20, 16, 30
larg = max(700, max((int(fonte.getlength(l)) for l in linhas), default=0) + 2 * pad)
alt = barra + pad * 2 + lh * len(linhas)
img = Image.new("RGB", (larg, alt), "#1e1e1e")
d = ImageDraw.Draw(img)
d.rectangle([0, 0, larg, barra], fill="#333333")
for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    d.ellipse([12 + i * 20, 9, 24 + i * 20, 21], fill=c)
d.text((90, 7), nome, fill="#bbbbbb", font=fonte)
y = barra + pad
for l in linhas:
    eh_prompt = ("@lnx06-eduardo" in l and "$" in l) or l.startswith("PS ")
    d.text((pad, y), l, fill="#4ec94e" if eh_prompt else "#e6e6e6", font=fonte)
    y += lh
saida = f"{pasta}/{nome}.png"
img.save(saida)
print(saida)
