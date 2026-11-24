from PIL import Image, ImageDraw, ImageFont
W, H = 1800, 860
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if b else "C:/Windows/Fonts/arial.ttf", s)
def box(x1, y1, x2, y2, fill, title, lines, tc="#1f3864"):
    d.rounded_rectangle((x1, y1, x2, y2), 18, fill=fill, outline="#1f3864", width=4)
    d.text(((x1+x2)//2, y1+38), title, font=F(34, True), fill=tc, anchor="mm")
    y = y1 + 85
    for l in lines:
        d.text((x1+28, y), l, font=F(26), fill="#222"); y += 38
d.text((W//2, 40), "Escola Saber Mais  |  T4: Servidor FTP vsftpd com FTPS  |  Eduardo Andrei Staudt (nº 6)", font=F(32, True), fill="#1f3864", anchor="mm")
# rede
d.rounded_rectangle((40, 90, W-40, H-40), 26, outline="#7f7f7f", width=3)
d.text((70, 110), "Rede NAT do VirtualBox: NatSaberMais  192.168.106.0/24  (gateway 192.168.106.1)", font=F(28, True), fill="#595959")
box(90, 190, 650, 600, "#e2efda", "PC-PROF01  (.50)", [
    "Windows 10, VM pc-cliente-sabermais", "Membro do domínio SABERMAIS",
    "Cliente FTP: FileZilla", "Usuário logado: SABERMAIS" + chr(92) + "ana.souza",
    "Modo: FTP explícito sobre TLS", "(ftpes://192.168.106.20)"])
box(1110, 190, 1710, 790, "#ddebf7", "lnx06-eduardo  (.20)", [
    "Ubuntu Server 24.04.4 LTS", "lnx06-eduardo.sabermais.lan",
    "vsftpd 3.0.5 (FTPS, TLS 1.2 e 1.3)", "Samba 4 AD DC (T3) realm SABERMAIS.LAN",
    "PAM: pam_unix + pam_winbind", "chroot: /home/<usuário>",
    "Usuários FTP: ftp.professores,", "ftp.secretaria, SABERMAIS" + chr(92) + "ana.souza",
    "ufw: 22, 21, 40000:40100/tcp", "+ portas do AD (53, 88, 389, 445...)", "Certificado autoassinado RSA 2048"])
def arrow(y, label, sub, color):
    d.line((655, y, 1100, y), fill=color, width=7)
    d.polygon([(1100, y), (1076, y-15), (1076, y+15)], fill=color)
    d.text((877, y-34), label, font=F(27, True), fill=color, anchor="mm")
    d.text((877, y+32), sub, font=F(23), fill="#333", anchor="mm")
arrow(300, "Controle: TCP 21", "AUTH TLS, USER/PASS cifrados", "#c00000")
arrow(450, "Dados: TCP 40000 a 40100", "modo passivo, PROT P (cifrado)", "#2e75b6")
d.line((655, 560, 1100, 560), fill="#7f7f7f", width=4)
d.text((877, 530), "DNS do domínio (53)", font=F(23, True), fill="#595959", anchor="mm")
d.text((877, 590), "resolve lnx06-eduardo.sabermais.lan", font=F(22), fill="#595959", anchor="mm")
d.text((90, 640), "Anônimo desabilitado  |  userlist (lista branca)", font=F(24), fill="#c00000")
d.text((90, 680), "TLS 1.0 e 1.1 recusados pelo servidor", font=F(24), fill="#c00000")
im.save("assets/t2-vsftpd-ftps-linux/00-diagramaBlocos.png"); print("ok")
