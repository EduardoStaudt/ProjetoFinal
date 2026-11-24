from PIL import Image, ImageDraw, ImageFont
W,H=1600,820; im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
def f(s,b=False):
    try: return ImageFont.truetype("C:/Windows/Fonts/"+("arialbd.ttf" if b else "arial.ttf"),s)
    except: return ImageFont.load_default()
def box(x0,y0,x1,y1,fill,title,lines):
    d.rounded_rectangle([x0,y0,x1,y1],radius=18,fill=fill,outline="#333",width=3)
    d.text(((x0+x1)//2,y0+30),title,font=f(30,True),fill="#111",anchor="mm")
    for i,l in enumerate(lines): d.text((x0+24,y0+70+i*34),l,font=f(24),fill="#222")
d.text((W//2,40),"Cenário T3: Escola Saber Mais (SABERMAIS.LAN)",font=f(36,True),fill="#111",anchor="mm")
# rede
d.rounded_rectangle([60,330,1540,410],radius=14,fill="#e8eef8",outline="#3b5b9a",width=3)
d.text((W//2,370),"Rede NAT do VirtualBox  NatSaberMais  192.168.106.0/24  (gateway .1)",font=f(28,True),fill="#1d3a73",anchor="mm")
box(80,470,760,790,"#fff4d6","lnx06-eduardo  (192.168.106.20)",
 ["Ubuntu Server 24.04.4  |  Samba 4.19.5","Samba AD DC do realm SABERMAIS.LAN","DNS interno, Kerberos KDC, LDAP, SMB",
  "Shares: Professores, Secretaria, Direcao, Publica","Portas: 53 DNS  88 Kerberos  389 LDAP  445 SMB","chrony com ntp_signd (hora do domínio)"])
box(840,470,1520,790,"#e3f4e3","PC-PROF01  (192.168.106.50)",
 ["Windows 10 cliente do domínio","DNS preferencial 192.168.106.20","Logon SABERMAIS"+chr(92)+"ana.souza (Professores)",
  "Acessa "+chr(92)*2+"lnx06-eduardo"+chr(92)+"Professores","RSAT / ADUC com eduardo.admin"])
for x in (420,1180): d.line([x,410,x,470],fill="#3b5b9a",width=5)
box(500,90,1100,280,"#f1e6fa","Domínio SABERMAIS",
 ["OUs e grupos: Professores, Secretaria, Direcao","6 usuários nome.sobrenome","eduardo.admin em Domain Admins"])
d.line([800,280,800,330],fill="#7a4a9a",width=4)
im.save("docs/relatorio-t3/diagrama-cenario.png"); print("ok")
