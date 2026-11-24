# Gera o relatorio do T4 (vsftpd com FTPS) a partir do template da skill labs-agnaldo.
# uso: python tools/relatorio_t4.py <pasta_template_descompactado> <saida.docx>
import os, re, shutil, sys, zipfile
from PIL import Image

UN, OUT = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets", "t2-vsftpd-ftps-linux")

# ---------------------------------------------------------------- conteudo
INTRO = [
    ("p", "Aluno: Eduardo Andrei Staudt, RA 2783045, nº 6 na planilha. Trabalho: T4 (Linux), Servidor FTP vsftpd com FTPS. "
          "Servidor: lnx06-eduardo (192.168.106.20). Execução: 23 e 24/11/2026."),
    ("p", "Neste trabalho eu implantei um servidor FTP seguro na mesma VM Linux onde já roda o Samba 4 AD DC do T3. "
          "O FTP puro manda usuário, senha e arquivos em texto aberto pela rede, então usei o vsftpd com FTPS (FTP sobre TLS) "
          "para cifrar tudo. Cada usuário fica preso na própria pasta (chroot), o login anônimo fica desligado e só quem está "
          "numa lista de permitidos consegue entrar. Também liguei o vsftpd ao domínio SABERMAIS.LAN pelo PAM, para que um "
          "usuário do AD consiga logar com a senha do domínio."),
]
OBJ = [
    ("p", "O problema da Escola Saber Mais é simples: a Secretaria e os Professores trocam planos de aula e documentos e "
          "precisavam de um jeito de enviar arquivos ao servidor sem que a senha ou o conteúdo passem abertos pela rede. "
          "Com o experimento eu espero:"),
    ("li", "deixar o vsftpd funcionando com TLS obrigatório no login e nos dados, aceitando só TLS 1.2 e 1.3"),
    ("li", "prender cada usuário local na sua home com chroot e desligar o acesso anônimo"),
    ("li", "usar a faixa de portas passivas 40000 a 40100 e liberar no ufw só o necessário, sem quebrar o Samba AD do T3"),
    ("li", "integrar o login ao domínio SABERMAIS.LAN e testar acesso permitido e negado pelo Linux e pelo cliente Windows"),
    ("li", "relacionar o serviço com conceitos de SO (processos, separação de privilégio, chroot e chamadas de sistema) e "
           "fazer o Desafio A de quebra e recuperação"),
]
MAT = [
    ("li", "VirtualBox 7.2.16 no meu PC (Windows 11 Pro, AMD Ryzen 9 7900X), com a rede NAT NatSaberMais 192.168.106.0/24."),
    ("li", "VM lnx06-eduardo: Ubuntu Server 24.04.4 LTS, kernel 6.8.0-149-generic, 1 vCPU, 2 GB de RAM (1,9 GiB visíveis "
           "no free -h), disco virtual de 25 GB com volume LVM raiz de 12 GB (6,4 GB usados). IP fixo 192.168.106.20."),
    ("li", "VM pc-cliente-sabermais (PC-PROF01): Windows 10 64 bits, 4 vCPU, 8 GB de RAM, IP 192.168.106.50, membro do "
           "domínio SABERMAIS."),
    ("li", "vsftpd 3.0.5 (pacote 3.0.5-0ubuntu3.1), OpenSSL 3.0.13, ufw, lftp 4.9.2 para testes no Linux e strace."),
    ("li", "FileZilla Client no PC-PROF01 para o teste com cliente gráfico."),
    ("li", "Samba 4.19.5 AD DC já provisionado no T3 (realm SABERMAIS.LAN), usado na integração."),
    ("li", "SSH a partir do meu PC e uma sessão tmux no console da VM, onde rodei os comandos que aparecem nos prints."),
]

S = []          # secao 6
def h(t): S.append(("h", t))
def p(t): S.append(("p", t))
def li(t): S.append(("li", t))
def code(*l): S.append(("code", list(l)))
def img(f, cap, w=15.5): S.append(("img", f, cap, w))

h("6.1 Cenário")
p("A empresa é a Escola Saber Mais, com os departamentos Professores, Secretaria e Direção. O domínio Linux é "
  "SABERMAIS.LAN (NetBIOS SABERMAIS), a rede é 192.168.106.0/24 com gateway .1, o servidor Linux é o lnx06-eduardo em .20 "
  "e o cliente é o PC-PROF01 em .50. O controle do FTP usa a porta TCP 21 e os dados usam a faixa passiva 40000 a 40100.")
img("00-diagramaBlocos.png", "Diagrama de blocos do cenário do T4 (Lab-01).")

h("6.2 Ambiente")
p("Os recursos da VM eu conferi por SSH. O nproc mostrou 1 CPU, o free -h mostrou 1,9 GiB de memória total e o df -h / "
  "mostrou o volume raiz de 12 GB com 61% de uso. A VM está na rede NAT NatSaberMais do VirtualBox, a mesma do cliente.")
code("nproc", "free -h", "df -h /", "lsb_release -ds", "uname -r")

h("6.3 Passo a passo")
p("Passo 1. Identificação. Comecei mostrando o hostname completo, o IP e a data, e atualizei o arquivo de autoria para o T4.")
code('echo "Eduardo Andrei Staudt - nº 6 - T4 vsftpd FTPS - 2026-11-23" > ~/AUTORIA.txt',
     "hostname -f", "ip -br a", "date", "cat ~/AUTORIA.txt")
img("01-identificacao.png", "Identificação: lnx06-eduardo.sabermais.lan, 192.168.106.20 e autoria do T4.")

p("Passo 2. Instalação. Instalei o vsftpd e o OpenSSL. O systemd já sobe o serviço depois da instalação.")
code("sudo apt install -y vsftpd openssl", "systemctl status vsftpd --no-pager", "vsftpd -v")
img("02-instalacaoStatus.png", "vsftpd 3.0.5 instalado e active (running).")

p("Passo 3. Certificado TLS. Gerei um certificado autoassinado RSA de 2048 bits válido por 1 ano. O -x509 gera o "
  "certificado direto em vez de um pedido para uma CA, o -nodes deixa a chave sem senha (senão o serviço pediria senha "
  "em todo start) e o chmod 600 deixa a chave privada legível só pelo root.")
code("sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\",
     "  -keyout /etc/ssl/private/vsftpd.key -out /etc/ssl/certs/vsftpd.crt \\",
     '  -subj "/CN=lnx06-eduardo.sabermais.lan/O=Escola Saber Mais"',
     "sudo chmod 600 /etc/ssl/private/vsftpd.key",
     "openssl x509 -in /etc/ssl/certs/vsftpd.crt -noout -subject -dates")
img("03-certificadoTls.png", "Certificado com CN e O da escola, chave privada -rw------- e validade até 2027.")

p("Passo 4. Usuários e lista de permitidos. Criei os usuários locais ftp.professores e ftp.secretaria, cada um com a "
  "pasta arquivos dentro da home. A senha eu passei pelo chpasswd via stdin, então ela não aparece em tela. O "
  "/etc/vsftpd.userlist virou a lista branca de quem pode logar no FTP.")
code('sudo adduser --allow-bad-names --disabled-password --gecos "" ftp.professores',
     'sudo adduser --allow-bad-names --disabled-password --gecos "" ftp.secretaria',
     "printf 'ftp.professores:<SENHA>\\nftp.secretaria:<SENHA>\\n' | sudo chpasswd",
     "sudo install -d -o ftp.professores -g ftp.professores -m 755 /home/ftp.professores/arquivos",
     "sudo install -d -o ftp.secretaria -g ftp.secretaria -m 755 /home/ftp.secretaria/arquivos",
     'printf "ftp.professores\\nftp.secretaria\\n" | sudo tee /etc/vsftpd.userlist')
img("04-usuariosUserlist.png", "Userlist, UIDs 1026 e 1027, pastas arquivos e senhas definidas (P).")

p("Passo 5. Configuração do vsftpd. Fiz backup do arquivo original (/etc/vsftpd.conf.bak) e escrevi o "
  "/etc/vsftpd.conf. Os parâmetros principais e o motivo de cada um:")
li("listen=YES e listen_ipv6=NO: o vsftpd roda sozinho escutando IPv4 na porta 21.")
li("anonymous_enable=NO, local_enable=YES e write_enable=YES: sem anônimo, só usuários locais, com permissão de enviar arquivos. local_umask=022 faz o arquivo enviado nascer com 644.")
li("chroot_local_user=YES e allow_writeable_chroot=YES: depois do login o vsftpd chama chroot() na home do usuário, que passa a ver a home como /. O segundo libera o chroot numa pasta onde ele pode escrever.")
li("pasv_enable=YES, pasv_min_port=40000, pasv_max_port=40100 e pasv_address=192.168.106.20: modo passivo com faixa fixa, para conseguir liberar no firewall.")
li("ssl_enable=YES, rsa_cert_file e rsa_private_key_file: liga o TLS com o certificado do passo 3.")
li("force_local_logins_ssl=YES e force_local_data_ssl=YES: usuário, senha, listagens e arquivos só passam cifrados.")
li("ssl_tlsv1=NO, ssl_tlsv11=NO, ssl_tlsv12=YES e ssl_tlsv13=YES: só TLS 1.2 e 1.3. ssl_sslv2=NO e ssl_sslv3=NO desligam o SSL antigo. ssl_ciphers=HIGH deixa só cifras fortes e require_ssl_reuse=NO evita falha em clientes que não reaproveitam a sessão TLS.")
li("userlist_enable=YES, userlist_file=/etc/vsftpd.userlist e userlist_deny=NO: a lista vira lista branca.")
li("xferlog_enable=YES, log_ftp_protocol=YES, vsftpd_log_file=/var/log/vsftpd.log e dual_log_enable=YES: registram transferências e cada comando FTP. use_localtime=YES mostra os horários no fuso da máquina.")
code("sudo cp /etc/vsftpd.conf /etc/vsftpd.conf.bak", "sudo nano /etc/vsftpd.conf",
     'grep -v "^#" /etc/vsftpd.conf | pr -2 -t -w 110')
img("05-vsftpdConf.png", "vsftpd.conf final, com chroot e as opções de TLS 1.2 e 1.3.")
p("Depois reiniciei o serviço para ele ler a configuração nova.")
code("sudo systemctl restart vsftpd", "systemctl status vsftpd --no-pager -l")
img("06-restartStatus.png", "vsftpd active (running) depois do restart.")

p("Passo 6. Firewall. O ufw estava inativo. Antes de ativar eu liberei o SSH (22), o FTP (21), a faixa passiva e todas "
  "as portas do Samba AD, para não derrubar o T3. Com o ufw ativo, o padrão passa a ser bloquear o que não está liberado.")
code("sudo ufw allow 22/tcp", "sudo ufw allow 21/tcp", "sudo ufw allow 40000:40100/tcp",
     "sudo ufw allow proto tcp to any port 53,88,135,139,389,445,464,636,3268,3269",
     "sudo ufw allow proto udp to any port 53,88,123,137,138,389,464",
     "sudo ufw allow 49152:65535/tcp", "sudo ufw --force enable", "sudo ufw status numbered")
img("07-ufwStatus.png", "ufw ativo com 21, a faixa passiva e as portas do AD.")
p("Em seguida conferi que o T3 continuava funcionando. O DNS do domínio resolve o nome do servidor FTP, o SMB lista os "
  "compartilhamentos e o Kerberos emite ticket. No PC-PROF01 também abri \\\\lnx06-eduardo\\Professores pelo Explorer "
  "e a pasta abriu normalmente.")
code("host lnx06-eduardo.sabermais.lan 192.168.106.20", "smbclient -L //lnx06-eduardo.sabermais.lan -N",
     "kinit -c /tmp/krb5cc_t4 eduardo.admin   (senha digitada, não aparece)", "klist -c /tmp/krb5cc_t4",
     "KRB5CCNAME=/tmp/krb5cc_t4 smbclient //lnx06-eduardo.sabermais.lan/Publica --use-kerberos=required -c ls")
img("08-sambaAposUfw.png", "DNS, compartilhamentos e portas 21, 88, 445 e 389 depois do ufw.")
img("09-kinitSmbAposUfw.png", "Ticket krbtgt do eduardo.admin e acesso SMB com Kerberos depois do ufw.")

p("Passo 7. Integração com o domínio. O pam_winbind já estava no common-auth desde o T3. O que barrava um usuário do "
  "AD eram três coisas: ele não estava na userlist, o módulo pam_shells recusava o shell /bin/false que o winbind "
  "entrega e a home dele não existia. Coloquei auth sufficient pam_winbind.so no /etc/pam.d/vsftpd antes dos includes "
  "(com backup), adicionei SABERMAIS\\ana.souza na userlist e criei a home dela. Com sufficient, se o DC validar a senha "
  "o PAM encerra com sucesso. Usuário local continua passando pelo pam_unix e pelo pam_shells como antes.")
code("sudo cp /etc/pam.d/vsftpd /etc/pam.d/vsftpd.bak",
     'sudo sed -i "/^@include common-account/i auth\\tsufficient\\tpam_winbind.so" /etc/pam.d/vsftpd',
     "echo 'SABERMAIS\\ana.souza' | sudo tee -a /etc/vsftpd.userlist",
     "sudo install -d -o 3000015 -g 100 -m 750 /home/SABERMAIS/ana.souza",
     "lftp -u 'SABERMAIS\\ana.souza' -e \"set ftp:ssl-force true; set ssl:verify-certificate no; pwd; put /etc/hostname -o ana-teste.txt; ls; bye\" localhost")
img("10-loginDominioAna.png", "Usuário do domínio SABERMAIS\\ana.souza logando no FTPS e enviando arquivo.")
img("11-logLoginDominio.png", "Log do vsftpd: AUTH TLS, 234, OK LOGIN e OK UPLOAD da ana em \"/ana-teste.txt\".")

h("6.4 Testes positivos e negativos")
p("No próprio Linux testei com o lftp. O ftp.professores logou por TLS e enviou um arquivo. O cd .. continuou em / e o "
  "cd /etc deu 550, ou seja, ele está preso na home.")
code("lftp -u ftp.professores -e \"set ftp:ssl-force true; set ssl:verify-certificate no; put /etc/hostname -o teste.txt; ls; cd ..; quote PWD; cd /etc; bye\" localhost")
img("12-loginProfessoresChroot.png", "Teste positivo com chroot: upload ok, 257 \"/\" e 550 no /etc.")
p("Depois os testes negativos. O anônimo foi recusado com e sem TLS, o ftp.professores sem TLS foi recusado antes "
  "de mandar a senha e o eduardo, que é usuário válido do Linux mas não está na userlist, também foi recusado.")
code("for t in \"anonymous,x|set ssl:verify-certificate no\" \"anonymous,x|set ftp:ssl-allow false\" \\",
     "         \"ftp.professores,x|set ftp:ssl-allow false\" \"eduardo,x|set ssl:verify-certificate no\"",
     "do lftp -u \"${t%%|*}\" -e \"set net:max-retries 1; ${t#*|}; ls; bye\" localhost", "done")
img("13-testesNegados.png", "Testes negativos: todos recusados com 530.")
code("sudo grep -E '\"USER |530|OK LOGIN|OK UPLOAD' /var/log/vsftpd.log | tail -16",
     "sudo journalctl -u vsftpd --no-pager | grep pam_winbind | tail -1")
img("14-logsVsftpd.png", "Logs com OK LOGIN, OK UPLOAD, as recusas 530 e o pam_winbind passando a vez ao usuário local.")
p("Por fim testei do cliente Windows com o FileZilla, usando host 192.168.106.20, porta 21 e \"Requer FTP explícito "
  "sobre TLS\". Esse teste passa pelo firewall, então ele também prova as regras do ufw. O FileZilla mostrou o "
  "certificado autoassinado e a sessão em TLS 1.3, o login entrou, o upload do plano-de-aula.txt funcionou, o CWD /etc "
  "e o CWD /home deram 550 e o anonymous foi recusado.")
img("15-filezillaCertificado.png", "Certificado apresentado ao FileZilla, autoassinado, com TLS 1.3.", 11.5)
img("16-filezillaLoginOk.png", "Login do ftp.professores no FileZilla (ftpes://).", 14)
img("17-filezillaUpload.png", "Upload do plano-de-aula.txt a partir do PC-PROF01.", 14)
img("18-filezillaChroot.png", "Tentativa de sair do chroot pelo FileZilla: CWD /etc e CWD /home negados.", 14)
img("19-filezillaAnonimoNegado.png", "Login anonymous negado no FileZilla.", 14)
p("Para fechar a parte de TLS, testei cada versão com o openssl s_client. Uso SECLEVEL=0 só no cliente, para garantir "
  "que a recusa venha do servidor. TLS 1.0 e 1.1 recebem alert protocol version e TLS 1.2 e 1.3 conectam. Depois "
  "repeti um login completo para confirmar que o FTPS continuou funcionando.")
code("for v in tls1 tls1_1 tls1_2 tls1_3",
     "do openssl s_client -connect localhost:21 -starttls ftp -$v -cipher \"DEFAULT:@SECLEVEL=0\" </dev/null", "done")
img("27-opensslVersoesTls.png", "TLS 1.0 e 1.1 recusados, TLS 1.2 e 1.3 aceitos.")
img("28-loginAposTls12.png", "vsftpd e samba-ad-dc active e login, upload e remoção ok depois da troca das opções TLS.")

h("6.5 O serviço visto pelo sistema operacional")
p("Com o FileZilla conectado, olhei os processos. O vsftpd roda em modo usuário e cada conexão gera um fork(). O "
  "processo pai (PID 8025) é root e só aceita conexões. A sessão tem um processo nobody, um auxiliar de TLS também "
  "nobody e o processo do usuário ftp.professores. O kernel cuida dos sockets TCP, do chroot() e do sistema de arquivos.")
code("sudo pstree -apu $(systemctl show -p MainPID --value vsftpd)", "ps -o pid,ppid,user,cmd -C vsftpd",
     "sudo ss -tnp | grep vsftpd")
img("20-processosSessao.png", "Árvore de processos da sessão e conexão ESTAB do .50 na porta 21.")
p("No /proc dá para ver a separação de privilégio: só o listener tem Uid 0 e capabilities, os processos da sessão "
  "têm CapEff zerado e o diretório raiz do processo do usuário é /home/ftp.professores, efeito do chroot().")
code('for p in $(pgrep -x vsftpd); do printf "PID %s Uid=%s CapEff=%s root=%s\\n" $p \\',
     "  \"$(sudo awk '/^Uid/{print $2}' /proc/$p/status)\" \"$(sudo awk '/^CapEff/{print $2}' /proc/$p/status)\" \\",
     "  \"$(sudo readlink /proc/$p/root)\"", "done")
img("21-privilegioChrootProc.png", "Uid, capabilities e raiz de cada processo vsftpd no /proc.")
p("Por último prendi o strace no listener com -f (o FileZilla abre uma conexão nova para cada transferência) e enviei "
  "o boletim.txt. No processo do usuário aparecem o chroot(\".\"), o openat que cria o arquivo e devolve o descritor 8 "
  "e o write dos 6 bytes. O auxiliar de TLS decifra os dados e repassa ao processo do usuário por um socket interno.")
code("sudo strace -f -tt -e trace=openat,write,chroot -o /tmp/strace-ftp.txt -p $(systemctl show -p MainPID --value vsftpd)",
     "sudo grep -E '^3239[67] .*(chroot|STOR|boletim|Aopa)' /tmp/strace-ftp.txt")
img("22-straceUpload.png", "strace do upload: chroot, openat do boletim.txt e write dos 6 bytes (Lab-05).")

h("6.6 Desafio A: quebra e recuperação")
p("Meu número é 6 e 6 mod 3 = 0, então fiz o Desafio A genérico: parar o serviço principal, mostrar a falha, achar a "
  "causa nos logs e restaurar. Antes tirei um snapshot da VM. Com o vsftpd parado o serviço ficou inactive, o lftp deu "
  "Connection refused (com a porta fechada o kernel responde o SYN com RST), a porta 21 sumiu do ss e o journal mostrou "
  "o Stopped. O FileZilla do cliente também perdeu a conexão.")
code("sudo systemctl stop vsftpd", "systemctl is-active vsftpd",
     "timeout 10 lftp -u ftp.professores,x -e \"set net:max-retries 1; ls; bye\" localhost",
     "sudo ss -tlnp | grep ':21 ' || echo \"porta 21 fechada\"", "sudo journalctl -u vsftpd --no-pager -n 3")
img("23-desafioStop.png", "Falha: inactive, Connection refused, porta 21 fechada e Stopped no journal.")
p("Para corrigir subi o serviço de novo e conferi status, porta e journal. Depois loguei e o boletim.txt enviado antes "
  "da quebra continuava lá.")
code("sudo systemctl start vsftpd", "systemctl status vsftpd --no-pager", "sudo ss -tlnp | grep ':21 '",
     "lftp -u ftp.professores -e \"set ftp:ssl-force true; set ssl:verify-certificate no; cd arquivos; ls; bye\" localhost")
img("24-desafioStart.png", "Recuperação: active (running), porta 21 em LISTEN e Started no journal.")
img("25-desafioTesteOk.png", "Login funcionando depois da recuperação, com o boletim.txt preservado.")
p("Terminei com a mesma identificação do começo, com o vsftpd e o samba-ad-dc ativos.")
img("29-fechamentoFinal.png", "Fechamento: hostname, IP, data, autoria e os dois serviços active.")

h("6.7 Perguntas de verificação")
p("1. Qual problema da empresa o servidor resolve? A Secretaria e os Professores precisam trocar documentos com o "
  "servidor. Com o FTPS a senha e os arquivos vão cifrados (Figuras 16 e 17) e cada um fica preso na própria pasta "
  "(Figuras 13 e 19).")
p("2. Quais arquivos foram alterados e o que faz cada parâmetro? O /etc/vsftpd.conf (passo 5 e Figura 6), o "
  "/etc/vsftpd.userlist, que é a lista branca (Figura 5), o /etc/pam.d/vsftpd com a linha do pam_winbind (passo 7), o "
  "certificado e a chave em /etc/ssl (Figura 4) e as regras do ufw (Figura 8).")
p("3. Quais processos, serviços e portas o servidor usa? O vsftpd.service, com um listener root na porta 21 e "
  "processos por sessão (Figuras 23 e 24). Os dados usam a faixa passiva 40000 a 40100. O vsftpd roda em modo usuário "
  "e depende do kernel para os sockets, o chroot() e a gravação no disco (Figura 25). A porta 21 em escuta aparece "
  "na Figura 9.")
p("4. Como o serviço foi integrado ao domínio? Pelo PAM, com o pam_winbind. O usuário SABERMAIS\\ana.souza logou com "
  "a senha do AD (Figuras 11 e 12). Além disso o DNS do domínio resolve lnx06-eduardo.sabermais.lan (Figura 9).")
p("5. Quais riscos existem e como foram mitigados? Para a senha em texto puro, forcei TLS só com 1.2 e 1.3 (Figuras "
  "21 e 22). O acesso anônimo ficou desligado (Figuras 14 e 20). Para o usuário não navegar pelo sistema, usei chroot "
  "(Figuras 13 e 19). As portas abertas ficaram só 21, a faixa passiva e as do AD (Figura 8). E a userlist impede que "
  "qualquer usuário do Linux logue (Figura 14). Um risco que continua é o certificado autoassinado, que o cliente "
  "precisa aceitar na primeira conexão (Figura 16). O ideal seria um certificado emitido por uma CA do domínio.")
p("E assim finalizo esse trabalho, que me fez ver na prática como um serviço de rede usa processos, privilégios e "
  "chamadas de sistema do Linux.")

DIF = [
    ("p", "Tive alguns problemas e anotei cada um com a solução:"),
    ("li", "A task pedia ssl_tlsv1_2=YES, mas o vsftpd caiu no restart com status=2/INVALIDARGUMENT e sem mensagem. Rodando o "
           "binário com strace achei o erro, que ele escreve no descritor 0: 500 OOPS: unrecognised variable in config file: "
           "ssl_tlsv1_2. O binário só aceita ssl_tlsv12 e ssl_tlsv13 (sem o segundo underline), apesar de o man do próprio "
           "pacote do Ubuntu documentar o nome com underline. Também descobri que a biblioteca OpenSSL do Ubuntu já recusa "
           "TLS 1.0 e 1.1. No final deixei as quatro opções explícitas no vsftpd.conf."),
    ("li", "O adduser recusou nomes com ponto (ftp.professores). Usei a opção --allow-bad-names."),
    ("li", "O usuário do domínio não logava. Eram três barreiras: userlist, pam_shells e home inexistente. Resolvi como "
           "descrevi no passo 7."),
    ("li", "Ativar o ufw podia derrubar o SSH e o Samba AD. Liberei antes todas as portas e testei o SMB a partir do cliente."),
    ("li", "Um login deu 530 Login incorrect. O log mostrou o TLS negociado e a recusa no pam_unix, então era senha digitada "
           "errada. Na segunda tentativa funcionou."),
    ("li", "O FileZilla mostra os horários 3 horas antes porque trata a listagem como UTC. Não afeta o serviço."),
]
REF = [
    ("li", "vsftpd, página oficial: https://security.appspot.com/vsftpd.html"),
    ("li", "Manual do vsftpd.conf no Ubuntu 24.04: https://manpages.ubuntu.com/manpages/noble/man5/vsftpd.conf.5.html"),
    ("li", "Ubuntu Server, Host files with an FTP server: https://ubuntu.com/server/docs/how-to/networking/ftp/"),
    ("li", "Manual do ufw no Ubuntu 24.04: https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html"),
    ("li", "OpenSSL 3.0, openssl-s_client: https://docs.openssl.org/3.0/man1/openssl-s_client/"),
    ("li", "chroot(2), Linux manual page: https://man7.org/linux/man-pages/man2/chroot.2.html"),
    ("li", "strace(1), Linux manual page: https://man7.org/linux/man-pages/man1/strace.1.html"),
    ("li", "RFC 4217, Securing FTP with TLS: https://www.rfc-editor.org/rfc/rfc4217"),
    ("li", "Enunciado do Trabalho Final de SO e slides da disciplina no Moodle."),
]

# ---------------------------------------------------------------- xml helpers
def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
RF = '<w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi" w:cstheme="majorHAnsi"/>'
def para(t, bold=False, jc="both", after=100, before=0, ind=None, size=None, italic=False, keep=False):
    rp = RF + ("<w:b/><w:bCs/>" if bold else "") + ("<w:i/>" if italic else "") + (f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "")
    pp = f'<w:pStyle w:val="Cabealho"/>' + ("<w:keepNext/>" if keep else "") + f'<w:spacing w:before="{before}" w:after="{after}"/>' + (ind or "") + f'<w:jc w:val="{jc}"/>'
    return f'<w:p><w:pPr>{pp}<w:rPr>{rp}</w:rPr></w:pPr><w:r><w:rPr>{rp}</w:rPr><w:t xml:space="preserve">{esc(t)}</w:t></w:r></w:p>'
def bullet(t):
    return para("•  " + t, jc="left", ind='<w:ind w:left="360" w:hanging="240"/>', after=60)
def codep(lines):
    out = []
    for i, l in enumerate(lines):
        rp = '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/><w:noProof/><w:sz w:val="16"/><w:szCs w:val="16"/>'
        sp = f'<w:spacing w:before="{60 if i == 0 else 0}" w:after="{100 if i == len(lines)-1 else 0}" w:line="240" w:lineRule="auto"/>'
        out.append(f'<w:p><w:pPr><w:pStyle w:val="Cabealho"/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>{sp}'
                   f'<w:ind w:left="113" w:right="113"/><w:rPr>{rp}</w:rPr></w:pPr><w:r><w:rPr>{rp}</w:rPr>'
                   f'<w:t xml:space="preserve">{esc(l)}</w:t></w:r></w:p>')
    return "".join(out)

rels_add, N = [], [0]
def image(fname, cap, wcm):
    N[0] += 1; n = N[0]
    src = os.path.join(A, fname)
    dst = f"fig{n:02d}.png"; shutil.copy(src, os.path.join(UN, "word", "media", dst))
    rid = f"rIdFig{n}"; rels_add.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{dst}"/>')
    w, hh = Image.open(src).size
    cx = int(wcm * 360000); cy = int(cx * hh / w)
    maxh = int(10.5 * 360000)
    if cy > maxh: cy = maxh; cx = int(cy * w / hh)
    drawing = (f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:docPr id="{100+n}" name="Figura {n}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{100+n}" name="{dst}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:ln w="6350"><a:solidFill><a:srgbClr val="A6A6A6"/></a:solidFill></a:ln></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>')
    pic = (f'<w:p><w:pPr><w:pStyle w:val="Cabealho"/><w:keepNext/><w:spacing w:before="80" w:after="40"/><w:jc w:val="center"/></w:pPr>'
           f'<w:r><w:rPr><w:noProof/></w:rPr>{drawing}</w:r></w:p>')
    return pic + para(f"Figura {n}: {cap}", jc="center", after=160, size=18, italic=True)

def headpara(title, text):
    rp = RF; rb = RF + "<w:b/><w:bCs/>"
    pp = '<w:pStyle w:val="Cabealho"/><w:keepLines/><w:widowControl/><w:spacing w:before="160" w:after="100"/><w:jc w:val="left"/>'
    return (f'<w:p><w:pPr>{pp}<w:rPr>{rp}</w:rPr></w:pPr><w:r><w:rPr>{rb}</w:rPr><w:t xml:space="preserve">{esc(title)}</w:t></w:r>'
            f'<w:r><w:rPr>{rp}</w:rPr><w:br/><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>')

def render(blocks):
    out = []
    blocks = list(blocks); merged = []
    i = 0
    while i < len(blocks):
        if blocks[i][0] == "h" and i + 1 < len(blocks) and blocks[i+1][0] == "p":
            merged.append(("hp", blocks[i][1], blocks[i+1][1])); i += 2
        else:
            merged.append(blocks[i]); i += 1
    for b in merged:
        k = b[0]
        if k == "hp": out.append(headpara(b[1], b[2])); continue
        if k == "p": out.append(para(b[1]))
        elif k == "li": out.append(bullet(b[1]))
        elif k == "h": out.append(para(b[1], bold=True, jc="left", before=160, after=80, keep=True))
        elif k == "code": out.append(codep(b[1]))
        elif k == "img": out.append(image(b[1], b[2], b[3]))
    return "".join(out)

# ---------------------------------------------------------------- aplicar no template
docp = os.path.join(UN, "word", "document.xml")
x = open(docp, encoding="utf8").read()

def fill_cell(x, label, value):
    i = x.find(f">{label}</w:t>")
    j = x.find("<w:tc>", i)
    k = x.find("</w:pPr></w:p>", j)
    run = f'<w:r><w:rPr>{RF}<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr><w:t xml:space="preserve">{esc(value)}</w:t></w:r>'
    return x[:k] + "</w:pPr>" + run + "</w:p>" + x[k+len("</w:pPr></w:p>"):]
x = fill_cell(x, "Título do Projeto ou Proposta (se houver):", "Trabalho Final T4 (Linux): Servidor FTP vsftpd com FTPS")
x = fill_cell(x, "Disciplina:", "Sistemas Operacionais - CC4SO")
x = fill_cell(x, "Estudante:", "Eduardo Andrei Staudt (nº 6 na planilha)")
x = fill_cell(x, "RA:", "2783045")

def replace_guide(x, guide_start, new_xml, also_next_para=False):
    i = x.find(guide_start)
    assert i > 0, guide_start
    ps = x.rfind("<w:p ", 0, i)
    pe = x.find("</w:p>", i) + len("</w:p>")
    if also_next_para:
        pe = x.find("</w:p>", pe) + len("</w:p>")
    return x[:ps] + new_xml + x[pe:]

FIG_FIRST = None
x = replace_guide(x, "Introdução: Situa o leitor", render(INTRO))
x = replace_guide(x, "Mostra, de forma clara, a finalidade", render(OBJ))
x = replace_guide(x, "Descrição sucinta dos softwares", render(MAT))
x = replace_guide(x, "Descrição dos dados colhidos", render(S), also_next_para=True)
x = replace_guide(x, "Problemas ocorridos durante o proces", render(DIF))
x = replace_guide(x, "Caso você utilize alguma informação externa", render(REF))
i8 = x.find('>8. </w:t>'); ps8 = x.rfind("<w:p ", 0, i8); pp8 = x.find("<w:pPr>", ps8) + len("<w:pPr>")
pst = x.find("/>", pp8) + 2
x = x[:pst] + "<w:keepNext/>" + x[pst:]
open(docp, "w", encoding="utf8").write(x)

relp = os.path.join(UN, "word", "_rels", "document.xml.rels")
r = open(relp, encoding="utf8").read()
r = re.sub(r'<Relationship Id="rId9"[^>]*image2\.png"/>', "", r)
r = r.replace("</Relationships>", "".join(rels_add) + "</Relationships>")
open(relp, "w", encoding="utf8").write(r)
m2 = os.path.join(UN, "word", "media", "image2.png")
if os.path.exists(m2): os.remove(m2)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for base, _, files in os.walk(UN):
        for f in files:
            full = os.path.join(base, f); arc = os.path.relpath(full, UN).replace("\\", "/")
            z.write(full, arc)
print("ok", OUT, "figuras:", N[0])
