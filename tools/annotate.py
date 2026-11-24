"""Recorta e destaca em vermelho um screenshot do console da VM.
Console: 1280x800, fonte Terminus 16x32 -> célula 16x32 px (80 col x 25 lin).
Uso:
  python tools/annotate.py <png_original> <txt_tela> <png_saida> "<texto1>" ["<texto2>" ...]
  <txt_tela> = saída de: ssh lnx06 "tmux capture-pane -p -t demo"  (só a tela visível)
Cada texto é procurado nas linhas e ganha uma caixa vermelha.
O recorte vai da 1a à última linha com conteúdo (sem a barra do tmux), com margem.
Opções por env: CW, CH (tamanho da célula), PAD.
"""
import os, sys
from PIL import Image, ImageDraw

png, txt, out, *alvos = sys.argv[1:]
CW, CH = int(os.getenv("CW", 16)), int(os.getenv("CH", 32))
PAD = int(os.getenv("PAD", 12))
img = Image.open(png).convert("RGB")
linhas = open(txt, encoding="utf-8", errors="replace").read().split("\n")
max_lin = img.height // CH - 1  # última linha é a barra do tmux
linhas = linhas[:max_lin]
d = ImageDraw.Draw(img)
achou = 0
for i, l in enumerate(linhas):
    for a in alvos:
        c = l.find(a)
        if c >= 0:
            x0, y0 = c * CW - 6, i * CH - 3
            x1, y1 = (c + len(a)) * CW + 6, (i + 1) * CH + 3
            for k in range(3):
                d.rounded_rectangle([x0 - k, y0 - k, x1 + k, y1 + k], radius=10, outline="#ff2020")
            achou += 1
uso = [i for i, l in enumerate(linhas) if l.strip()]
if uso:
    larg = max(len(linhas[i].rstrip()) for i in uso)
    box = (0, max(0, uso[0] * CH - PAD), min(img.width, max(640, larg * CW + 40)),
           min(img.height, (uso[-1] + 1) * CH + PAD))
    img = img.crop(box)
img.save(out)
print(f"{out} ({achou} destaque(s))")
