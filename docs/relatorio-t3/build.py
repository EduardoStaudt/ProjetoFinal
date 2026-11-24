import os, re, shutil, sys, zipfile, copy
from xml.sax.saxutils import escape
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import conteudo as C

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TPL = os.path.join(ROOT, ".claude/skills/labs-agnaldo/assets/modelo-relatorio-utfpr.docx")
OUT = os.path.join(ROOT, "docs", sys.argv[1] if len(sys.argv) > 1 else "T3-EduardoAndreiStaudt-2783045.docx")

z = zipfile.ZipFile(TPL)
files = {n: z.read(n) for n in z.namelist()}
doc = files["word/document.xml"].decode("utf8")
rels = files["word/_rels/document.xml.rels"].decode("utf8")

FONT = '<w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi" w:cstheme="majorHAnsi"/>'

def run(t, extra=""):
    return f'<w:r><w:rPr>{FONT}{extra}</w:rPr><w:t xml:space="preserve">{escape(t)}</w:t></w:r>'

def para(t, bold=False, jc="both", after=120):
    return (f'<w:p><w:pPr><w:pStyle w:val="Cabealho"/><w:spacing w:after="{after}"/><w:jc w:val="{jc}"/></w:pPr>'
            + run(t, "<w:b/><w:bCs/>" if bold else "") + '</w:p>')

def li(t, jc="both"):
    return (f'<w:p><w:pPr><w:pStyle w:val="Cabealho"/><w:spacing w:after="80"/><w:ind w:left="284" w:hanging="284"/><w:jc w:val="{jc}"/></w:pPr>'
            + run("• " + t) + '</w:p>')

def code(t):
    out = []
    lines = t.split("\n")
    for i, l in enumerate(lines):
        after = 120 if i == len(lines) - 1 else 0
        out.append(f'<w:p><w:pPr><w:pStyle w:val="Cabealho"/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>'
                   f'<w:spacing w:after="{after}"/><w:ind w:left="113"/></w:pPr>'
                   f'<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/><w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr>'
                   f'<w:t xml:space="preserve">{escape(l) if l else " "}</w:t></w:r></w:p>')
    return "".join(out)

img_n = [0]; fig_n = [0]; media = {}
def image(path, legenda, wcm):
    img_n[0] += 1; fig_n[0] += 1
    k = img_n[0]; rid = f"rIdImg{k}"; name = f"media/fig{k}.png"
    full = os.path.join(ROOT, path)
    im = Image.open(full)
    w, h = im.size
    wcm = min(wcm, 16.0); hcm = wcm * h / w
    if hcm > 11.5: hcm = 11.5; wcm = hcm * w / h
    cx, cy = int(wcm * 360000), int(hcm * 360000)
    media["word/" + name] = open(full, "rb").read()
    rels_add.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{name}"/>')
    pid = 100 + k
    drw = (f'<w:r><w:rPr><w:noProof/></w:rPr><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
           f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{pid}" name="Figura {fig_n[0]}"/>'
           f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
           f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
           f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{pid}" name="fig{k}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
           f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
           f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
           f'</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
    cap = run(f"Figura {fig_n[0]}: {legenda}", '<w:i/><w:iCs/><w:sz w:val="19"/><w:szCs w:val="19"/>')
    return (f'<w:p><w:pPr><w:pStyle w:val="Cabealho"/><w:keepLines/><w:spacing w:before="60" w:after="160"/><w:jc w:val="center"/></w:pPr>'
            + drw + '<w:r><w:br/></w:r>' + cap + '</w:p>')

rels_add = []
def render(blocks):
    out = []
    for b in blocks:
        if b[0] == "p": out.append(para(b[1]))
        elif b[0] == "h": out.append(para(b[1], bold=True, jc="left", after=80))
        elif b[0] == "c": out.append(code(b[1]))
        elif b[0] == "li": out.append(li(b[1]))
        elif b[0] == "img": out.append(image(b[1], b[2], b[3]))
    return "".join(out)

def replace_box(xml, marker, newxml):
    # troca o parágrafo-guia (o <w:p> que contém o marcador) pelo conteúdo novo
    i = xml.index(marker)
    s = xml.rfind("<w:p ", 0, i)
    e = xml.index("</w:p>", i) + len("</w:p>")
    return xml[:s] + newxml + xml[e:]

# seção 6: remover também o parágrafo da imagem de exemplo
i = doc.index('r:embed="rId9"'); s = doc.rfind("<w:p ", 0, i); e = doc.index("</w:p>", i) + 6
doc = doc[:s] + doc[e:]
rels = rels.replace('<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image2.png"/>', "")

doc = replace_box(doc, "Introdução: Situa o leitor", render(C.INTRO))
doc = replace_box(doc, "Mostra, de forma clara", render(C.OBJ))
doc = replace_box(doc, "Descrição sucinta dos softwares", render(C.MATERIAL))
doc = replace_box(doc, "Descrição dos dados colhidos", render(C.S))
doc = replace_box(doc, "Problemas ocorridos durante o proces", render(C.DIFIC))
doc = replace_box(doc, "Caso você utilize alguma informação externa", "".join(li(r, "left") for r in C.REFS))

# tabela de identificação: preencher as 4 linhas e clonar linhas extras com a mesma formatação
t0 = doc.index("<w:tbl>"); t1 = doc.index("</w:tbl>", t0)
tbl = doc[t0:t1]
rows = re.findall(r"<w:tr .*?</w:tr>", tbl, flags=re.S)
def fill_row(row, label, value):
    cells = re.findall(r"<w:tc>.*?</w:tc>", row, flags=re.S)
    left, right = cells
    if label:
        txt_runs = re.findall(r"<w:r [^>]*>.*?</w:r>|<w:r>.*?</w:r>", left, flags=re.S)
        rpr = re.search(r"<w:rPr>.*?</w:rPr>", txt_runs[0], flags=re.S).group(0)
        newleft = re.sub(r"(<w:p [^>]*>.*?</w:pPr>).*?(</w:p>)", lambda m: m.group(1) + f'<w:r>{rpr}<w:t xml:space="preserve">{escape(label)}</w:t></w:r>' + m.group(2), left, flags=re.S)
    else:
        newleft = left
    rpr_r = f'<w:rPr>{FONT}<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>'
    newright = right.replace("</w:pPr></w:p>", f'</w:pPr><w:r>{rpr_r}<w:t xml:space="preserve">{escape(value)}</w:t></w:r></w:p>')
    return row.replace(left, newleft).replace(right, newright)
newrows = [fill_row(rows[k], None, C.IDENT[k][1]) for k in range(4)]
for lab, val in C.IDENT[4:]:
    newrows.append(fill_row(rows[3], lab, val))
tbl_new = tbl
for r in rows: tbl_new = tbl_new.replace(r, "", 1)
tbl_new = tbl_new + "".join(newrows)
doc = doc[:t0] + tbl_new + doc[t1:]

rels = rels.replace("</Relationships>", "".join(rels_add) + "</Relationships>")
files["word/document.xml"] = doc.encode("utf8")
files["word/_rels/document.xml.rels"] = rels.encode("utf8")
files.update(media)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    for n, d in files.items(): zo.writestr(n, d)
print(OUT, "figuras:", fig_n[0])
