# Conteúdo do relatório T3. Blocos: ("h", texto) ("p", texto) ("c", código) ("img", arquivo, legenda) ("li", texto)
A = "assets/t1-samba-ad-linux/"

IDENT = [
    ("Título do Projeto ou Proposta (se houver):", "T3: Samba 4 como AD DC e Servidor de Arquivos"),
    ("Disciplina:", "Sistemas Operacionais - CC4SO"),
    ("Estudante:", "Eduardo Andrei Staudt"),
    ("RA:", "2783045"),
    ("Nº na planilha:", "6"),
    ("Trabalho:", "T3 (Linux) do Trabalho Final, cenário Escola Saber Mais"),
    ("Servidor:", "lnx06-eduardo (192.168.106.20), Samba AD DC do realm SABERMAIS.LAN"),
    ("Data:", "12/11/2026"),
]

INTRO = [
    ("p", "Neste trabalho eu transformei um Ubuntu Server em controlador de domínio Active Directory usando o Samba 4, e no mesmo servidor montei os compartilhamentos de arquivos da Escola Saber Mais. A ideia é ter um login único para a escola inteira: o usuário entra no Windows com a conta do domínio, o Linux confere a senha pelo Kerberos e as pastas de cada departamento só abrem para quem é daquele departamento."),
    ("p", "O cenário é o meu da planilha (nº 6). A empresa é a Escola Saber Mais, com os departamentos Professores, Secretaria e Direção (escrito Direcao nas OUs e grupos). O realm Linux é SABERMAIS.LAN, com DNS sabermais.lan e NetBIOS SABERMAIS. A rede é 192.168.106.0/24 com gateway .1, o servidor Linux lnx06-eduardo fica no .20 e o cliente Windows PC-PROF01 no .50. As duas VMs estão na mesma NAT Network do VirtualBox, chamada NatSaberMais. A Figura 1 mostra o diagrama de blocos com as portas principais do DC (53 DNS, 88 Kerberos, 389 LDAP e 445 SMB)."),
    ("img", "docs/relatorio-t3/diagrama-cenario.png", "Diagrama de blocos do cenário T3 (Lab-01)", 15.5),
]

OBJ = [
    ("p", "O objetivo é provisionar o Samba 4 como AD DC do realm SABERMAIS.LAN, com DNS interno e Kerberos funcionando, criar as OUs, grupos e usuários da escola, compartilhar uma pasta por departamento mais uma Pública com ACLs POSIX por grupo, ingressar um cliente Windows no domínio e administrar o domínio pelo RSAT."),
    ("p", "Também quero mostrar o lado de Sistemas Operacionais do serviço: os processos do samba e se ele usa threads (Labs 06 e 08), as portas abertas, as chamadas de sistema que o smbd faz quando um arquivo é aberto (Lab-05), as permissões (Lab-07), os logs de autenticação e o Desafio A, em que eu quebro o DNS do servidor e recupero."),
]

MATERIAL = [
    ("li", "Hipervisor: Oracle VirtualBox 7.2.16, com as duas VMs na NAT Network NatSaberMais (192.168.106.0/24)."),
    ("li", "Servidor lnx06-eduardo: Ubuntu Server 24.04.4 LTS (kernel 6.8.0-149), 1 vCPU, 2 GB de RAM e disco de 25 GB (LVM com 12 GB na raiz). Samba 4.19.5-Ubuntu, MIT Kerberos (krb5-user 1.20.1), chrony 4.5, winbind, acl, smbclient e strace."),
    ("li", "Cliente PC-PROF01 (VM pc-cliente-sabermais): Windows 10 versão 10.0.19045, 4 vCPU, 8 GB de RAM e disco de 50 GB, com o RSAT de AD DS instalado (Usuários e Computadores do Active Directory)."),
    ("li", "Acesso ao servidor por SSH a partir do meu notebook, uma sessão tmux no console da VM para os prints e o VBoxManage screenshotpng para capturar a tela real das VMs."),
    ("li", "Documentação oficial do Samba (wiki.samba.org e páginas de manual) e as páginas de manual do Linux listadas na seção 8."),
]

S = []
def h(t): S.append(("h", t))
def p(t): S.append(("p", t))
def c(t): S.append(("c", t))
def img(f, leg, w=16.0): S.append(("img", A + f, leg, w))

h("6.1 Identificação inicial do servidor")
p("Comecei mostrando quem é a máquina: hostname completo, IP, data e o arquivo AUTORIA.txt com meu nome. Nessa hora vi que o /etc/hosts ainda tinha uma linha de restos de um laboratório anterior e que o fuso estava em UTC. Removi a linha (com backup) e ajustei o fuso, como a task pede.")
c("hostname -f\nip -br a\ndate\nhead -3 /etc/os-release\ncat /etc/hosts\nsudo timedatectl set-timezone America/Sao_Paulo")
img("01-identificacaoInicial.png", "Hostname lnx06-eduardo.sabermais.lan, IP 192.168.106.20/24, fuso -03 e /etc/hosts")
img("02-timezonePing.png", "Fuso America/Sao_Paulo e acesso à internet com 0% de perda")

h("6.2 Instalação dos pacotes")
p("Instalei o Samba e tudo que o DC precisa. O DEBIAN_FRONTEND=noninteractive evita a tela do krb5 perguntando o realm, porque o krb5.conf certo vem do provision depois.")
c("sudo DEBIAN_FRONTEND=noninteractive apt install -y acl attr samba samba-dsdb-modules \\\n  samba-vfs-modules smbclient winbind libpam-winbind libnss-winbind krb5-config krb5-user \\\n  dnsutils chrony ldb-tools strace psmisc lftp")
img("03-pacotesInstalados.png", "Samba 4.19.5 e pacotes de Kerberos, winbind, chrony e ACL instalados")

h("6.3 Preparação do DC")
p("Antes do provision tirei o snapshot 01-pre-provision. Parei os serviços avulsos smbd, nmbd e winbind, porque no modo DC quem sobe tudo é o processo samba. Parei também o systemd-resolved, que ocupa a porta 53, e o DC precisa dela porque ele mesmo é o DNS do domínio. O resolv.conf passou a apontar para o próprio servidor.")
c("sudo systemctl disable --now smbd nmbd winbind systemd-resolved\nsudo systemctl unmask samba-ad-dc\nsudo systemctl enable samba-ad-dc\nsudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bak\nprintf \"nameserver 127.0.0.1\\nsearch sabermais.lan\\n\" | sudo tee /etc/resolv.conf")
img("04-preparacaoDC.png", "Serviços avulsos inativos, samba-ad-dc habilitado e resolv.conf apontando para 127.0.0.1")

h("6.4 Provisionamento do domínio")
p("Aqui achei uma base de AD antiga em /var/lib/samba, restos de um laboratório anterior. Apaguei o conteúdo de private, sysvol e os .tdb antes de provisionar (explico na seção 7). Rodei o provision fora do tmux, com a senha passada pela entrada padrão para ela não aparecer em print nem em log.")
c("sudo samba-tool domain provision --realm=SABERMAIS.LAN --domain=SABERMAIS --server-role=dc \\\n  --dns-backend=SAMBA_INTERNAL --option=\"dns forwarder = 8.8.8.8\" --adminpass='<SENHA>'\nsudo cp /var/lib/samba/private/krb5.conf /etc/krb5.conf\nsudo systemctl start samba-ad-dc")
img("05-provisionDominio.png", "Provision como active directory domain controller do domínio sabermais.lan e serviço active (running)")

h("6.5 Validação do DNS e do Kerberos")
p("Conferi os registros SRV que os clientes usam para achar o LDAP e o KDC, pedi um ticket com kinit e listei os compartilhamentos padrão do DC.")
c("host -t SRV _ldap._tcp.sabermais.lan\nhost -t SRV _kerberos._udp.sabermais.lan\nhost -t A lnx06-eduardo.sabermais.lan\nkinit administrator\nklist\nsmbclient -L localhost -N\nsudo samba-tool domain level show")
img("06-dnsRegistrosSrv.png", "Registros SRV do LDAP (389) e do Kerberos (88) e registro A do DC")
img("07-kinitKlist.png", "TGT krbtgt/SABERMAIS.LAN emitido para administrator")
img("08-smbclientNivelDominio.png", "Compartilhamentos sysvol e netlogon e nível funcional 2008 R2")

h("6.6 Hora do domínio com chrony")
p("Liberei a pasta ntp_signd para o chrony e configurei ele para atender a rede e assinar as respostas pelo socket do Samba. O Windows num domínio só aceita hora assinada pelo DC.")
c("sudo chown root:_chrony /var/lib/samba/ntp_signd\nsudo chmod 750 /var/lib/samba/ntp_signd\n# acrescentado em /etc/chrony/chrony.conf\nbindcmdaddress 192.168.106.20\nallow 192.168.106.0/24\nntpsigndsocket /var/lib/samba/ntp_signd\nsudo systemctl restart chrony\nchronyc tracking\ntimedatectl")
img("09-chronyHoraDominio.png", "Permissão do ntp_signd, chrony.conf e relógio sincronizado")

h("6.7 OUs, grupos e usuários")
p("Com o snapshot 02-dc-ok tirado, criei uma OU e um grupo por departamento, o eduardo.admin no Domain Admins e os seis usuários do cenário, cada um na OU e no grupo do seu departamento.")
c("for ou in Professores Secretaria Direcao\ndo\n  sudo samba-tool ou create \"OU=$ou,DC=sabermais,DC=lan\"\n  sudo samba-tool group add $ou --groupou=\"OU=$ou\"\ndone\nsudo samba-tool user create eduardo.admin '<SENHA>' --given-name=Eduardo --surname=Admin\nsudo samba-tool group addmembers \"Domain Admins\" eduardo.admin\nsudo samba-tool user create ana.souza '<SENHA>' --userou=\"OU=Professores\" --given-name=Ana --surname=Souza\n(idem carlos.lima, beatriz.rocha, diego.alves, fernanda.costa, marcos.pereira)\nsudo samba-tool group addmembers Professores ana.souza,carlos.lima")
img("10-ousCriadas.png", "OUs Professores, Secretaria e Direcao com seus objetos")
img("11-usuariosGrupos.png", "Usuários do domínio e membros de cada grupo")
img("12-domainAdmins.png", "eduardo.admin membro de Domain Admins")

h("6.8 Linux enxergando o domínio (NSS winbind)")
p("Coloquei winbind nas linhas passwd e group do /etc/nsswitch.conf. Assim o Linux resolve os usuários e grupos do AD e eu consigo usar esses grupos no setfacl.")
c("passwd:         files systemd winbind\ngroup:          files systemd winbind\nwbinfo -u\nwbinfo -g\ngetent group \"SABERMAIS\\professores\"\nid \"SABERMAIS\\ana.souza\"")
img("13-winbindNss.png", "wbinfo, getent e id mostrando usuários e grupos do domínio no Linux")

h("6.9 Pastas e ACLs POSIX")
p("Criei as quatro pastas com chmod 770 e dei rwx para o grupo do departamento e para o Domain Admins, com a mesma entrada como ACL default para os arquivos novos herdarem. Na Pública o grupo é o Domain Users. Usei o GID numérico porque o setfacl não aceita o nome \"domain admins\" com espaço (seção 7).")
c("sudo mkdir -p /srv/samba/{Professores,Secretaria,Direcao,Publica}\nsudo chmod 770 /srv/samba/*\n# 3000014 = SABERMAIS\\professores e 3000004 = SABERMAIS\\domain admins\nsudo setfacl -m g:3000014:rwx,d:g:3000014:rwx,g:3000004:rwx,d:g:3000004:rwx /srv/samba/Professores\ngetfacl -p /srv/samba/Professores")
img("14-aclsProfessores.png", "Pastas com ACL (+) e entradas professores:rwx e default na Professores")
img("15-aclsSecretariaDirecao.png", "ACLs das pastas Secretaria e Direcao")
img("16-aclsPublica.png", "Domain Users mapeado para o GID 100 (users) com rwx na Publica")

h("6.10 Compartilhamentos")
p("No smb.conf liguei o log de autenticação no [global] e criei um bloco por pasta. O testparm conferiu a sintaxe e o smbcontrol recarregou sem derrubar ninguém.")
c("[global]\n    log level = 1 auth_audit:3\n[Professores]\n    path = /srv/samba/Professores\n    read only = no\n(idem Secretaria, Direcao e Publica)\nsudo testparm -s\nsudo smbcontrol all reload-config\nsmbclient -L lnx06-eduardo.sabermais.lan --use-kerberos=required")
img("17-testparmShares.png", "log level com auth_audit, testparm OK e os quatro compartilhamentos")
img("18-smbclientListaShares.png", "Lista de compartilhamentos autenticada pelo ticket Kerberos")

h("6.11 Testes positivos e negativos pelo Linux")
p("Pedi um ticket para a ana e outro para a beatriz, cada um num arquivo de cache separado, e testei com o smbclient. A ana gravou na Professores (positivo), foi barrada na Direcao com NT_STATUS_ACCESS_DENIED (negativo) e a beatriz listou a Pública (positivo). No disco o dono do arquivo ficou SABERMAIS\\ana.souza com a ACL herdada.")
c("kinit -c /tmp/krb5cc_ana ana.souza\nKRB5CCNAME=/tmp/krb5cc_ana smbclient //lnx06-eduardo.sabermais.lan/Professores \\\n  --use-kerberos=required -c 'put /etc/hostname teste-ana.txt'\nKRB5CCNAME=/tmp/krb5cc_ana smbclient //lnx06-eduardo.sabermais.lan/Direcao --use-kerberos=required -c 'ls'\nKRB5CCNAME=/tmp/krb5cc_bea smbclient //lnx06-eduardo.sabermais.lan/Publica --use-kerberos=required -c 'ls'\nsudo getfacl -p /srv/samba/Professores/teste-ana.txt")
img("19-anaProfessoresOk.png", "Teste positivo: ana.souza grava teste-ana.txt na Professores")
img("20-anaDirecaoNegado.png", "Teste negativo: ana.souza recebe NT_STATUS_ACCESS_DENIED na Direcao")
img("21-beatrizPublicaOk.png", "Teste positivo: beatriz.rocha lista a Publica")
img("22-arquivoDonoAcl.png", "Arquivo com dono SABERMAIS\\ana.souza e ACL herdada da pasta")

h("6.12 Cliente Windows no domínio")
p("No cliente coloquei IP 192.168.106.50, gateway .1 e DNS 192.168.106.20, só o DC, sem DNS alternativo. O nslookup achou o SRV do DC. Depois ingressei no domínio sabermais.lan com o eduardo.admin, reiniciei e entrei como SABERMAIS\\ana.souza. A conta PC-PROF01$ apareceu no DC.")
c("ipconfig | findstr IPv4\nnslookup sabermais.lan\nnslookup -type=SRV _ldap._tcp.dc._msdcs.sabermais.lan\nsudo samba-tool computer list\nwhoami\necho %LOGONSERVER%")
img("23-clienteDnsDominio.png", "Cliente .50 resolvendo sabermais.lan e o SRV do DC", 13.5)
img("24-computadorNoDominio.png", "Conta PC-PROF01$ criada no domínio")
img("25-logonAnaClienteDominio.png", "Logon sabermais\\ana.souza no PC-PROF01 com LOGONSERVER \\\\LNX06-EDUARDO", 13.5)

h("6.13 Testes pelo cliente e logs de autenticação")
p("Logada como ana, ela criou um arquivo na Professores pelo Explorador e foi negada na Direcao. No DC o smbstatus mostrou a sessão SMB3 da ana. Na aba Segurança da Professores o Windows mostrou a ACL que eu fiz com setfacl. No log, o auth_audit registrou as minhas duas tentativas com senha errada (NT_STATUS_WRONG_PASSWORD) e depois o logon certo (NT_STATUS_OK), tudo vindo do 192.168.106.50.")
c("sudo smbstatus -b\nsudo smbstatus -S\nsudo grep \"Auth:\" /var/log/samba/log.samba | grep ana.souza | grep 192.168.106.50")
img("26-authAuditLogonCliente.png", "auth_audit: WRONG_PASSWORD e OK da ana e OK do eduardo.admin vindos do cliente")
img("27-acessoProfessoresOk.png", "Teste positivo no Windows: ana cria ana-pelo-windows na Professores", 13.5)
img("28-smbstatusSessaoAna.png", "smbstatus com a sessão SMB3 da ana e dono dos arquivos")
img("29-acessoDirecaoNegado.png", "Teste negativo no Windows: acesso negado à Direcao", 13.5)
img("30-abaSegurancaProfessores.png", "Aba Segurança da Professores: grupo Professores com Controle total", 8.0)

h("6.14 Administração pelo RSAT")
p("Entrei no cliente como eduardo.admin, instalei o RSAT de AD DS e abri o ADUC (dsa.msc). Pelo ADUC criei a usuária paula.mendes na OU Professores e coloquei ela no grupo Professores. No DC o samba-tool já via a conta nova e o grupo atualizado.")
c("Add-WindowsCapability -Online -Name \"Rsat.ActiveDirectory.DS-LDS.Tools~~~~0.0.1.0\"\nsudo samba-tool user show paula.mendes --attributes=userPrincipalName,whenCreated,memberOf\nsudo samba-tool group listmembers Professores")
img("31-aducUsuariosGrupos.png", "ADUC conectado ao DC Samba mostrando a OU Professores", 13.5)
img("32-usuarioCriadoRsat.png", "Usuária Paula Mendes criada pelo ADUC", 13.5)
img("33-usuarioRsatNoSamba.png", "samba-tool vendo paula.mendes na OU e no grupo Professores")

h("6.15 Logs do serviço")
c("sudo journalctl -u samba-ad-dc --since today --no-pager\nls /var/log/samba/\nsudo grep \"Auth:\" /var/log/samba/log.samba | tail")
img("34-journalSambaAdDc.png", "journalctl do samba-ad-dc com a versão iniciada e o serviço Started")
img("35-logsSambaAuthAudit.png", "Pasta /var/log/samba e linhas completas do auth_audit com falha e sucesso")

h("6.16 Processos, threads, portas e syscalls")
c("pstree -ap $(systemctl show -p MainPID --value samba-ad-dc)\nps -eo pid,ppid,nlwp,comm\ntop -H -b -n1 -p $(pgrep -d, smbd)\nsudo ss -tulpn\nsudo timeout 20 strace -f -o /tmp/strace-smbd.txt -p $(pgrep -xo smbd) \\\n  -e trace=openat,read,write,pread64,fstat,getdents64,newfstatat")
img("36-processosPstree.png", "Árvore de processos do samba com smbd, sessão do cliente, ldap e rpc")
img("37-processosNlwp.png", "NLWP igual a 1 em todos os processos do Samba")
img("38-topThreadsSmbd.png", "top -H nos processos smbd")
img("39-portasSs.png", "Portas 53, 88, 135, 389, 445, 464, 636, 3268 e 3269 e o processo dono de cada uma")
img("40-straceSmbd.png", "strace no smbd: openat do teste-ana.txt e pread64 do conteúdo")

h("6.17 Desafio A: DNS do servidor apontando para fora")
p("Meu número é 6 e 6 mod 3 = 0, então o desafio é o A. Com o snapshot 02b-pre-desafio tirado, guardei o resolv.conf bom e troquei o DNS do servidor para o 8.8.8.8. O kinit falhou com Cannot find KDC e o SRV deu NXDOMAIN, porque o krb5.conf procura o KDC pelo DNS e o Google não conhece a zona sabermais.lan. No diagnóstico o cat mostrou o nameserver errado enquanto o dns do Samba continuava escutando na 53, ou seja, o serviço estava no ar e o problema era o servidor não perguntar para ele mesmo. Restaurei o arquivo e o kinit voltou a funcionar.")
c("sudo cp /etc/resolv.conf /root/resolv.ok\necho \"nameserver 8.8.8.8\" | sudo tee /etc/resolv.conf\nkdestroy\nkinit administrator\nhost -t SRV _ldap._tcp.sabermais.lan\ncat /etc/resolv.conf\nsudo cp /root/resolv.ok /etc/resolv.conf\nkinit administrator\nklist")
img("41-desafioQuebraResolv.png", "Desafio A: backup do resolv.conf e troca para 8.8.8.8")
img("42-desafioKinitFalha.png", "Falha: kinit sem KDC e SRV com NXDOMAIN")
img("43-desafioDiagnostico.png", "Diagnóstico: resolv.conf errado e DNS do Samba ainda na porta 53")
img("44-desafioRecuperado.png", "Recuperação: resolv.conf restaurado, SRV resolvendo e novo TGT")

h("6.18 Respostas às perguntas de verificação")
p("Samba standalone x AD DC (Figuras 6, 9 e 32). No Lab-09 o Samba era só um servidor de arquivos com usuários locais do próprio Linux (smbpasswd). Como AD DC ele vira o dono do domínio: guarda a base do AD em sam.ldb, faz DNS, Kerberos e LDAP, e o Windows ingressa nele e é administrado pelo ADUC como se fosse um DC da Microsoft. O provision mostrou o papel active directory domain controller, o DC publicou sysvol e netlogon e o RSAT abriu as OUs dele.")
p("Kerberos e horário (Figuras 8 e 10). O ticket do Kerberos carrega um carimbo de hora para evitar replay, ou seja, alguém capturar o pacote e reenviar depois. Por isso o KDC recusa quem estiver com mais de 5 minutos de diferença. No servidor o chrony está sincronizado com o ntp.br e assina as respostas pelo ntp_signd, que é o que o cliente do domínio aceita.")
p("Processos e portas (Figuras 37 a 40). O samba é um processo pai que cria um master por serviço (s3fs com o smbd, ldap, kdc, dns, rpc, nbt) e cada master cria workers antes de precisar deles. Cada cliente SMB ganha um smbd próprio, o smbd[192.168.10...] da ana na árvore. Todos têm NLWP 1, então o Samba AD trabalha com vários processos e não com threads. O ss mostrou 53 no dns[master], 88 e 464 no kdc, 135 no rpc, 389, 636, 3268 e 3269 no ldap e 445 no smbd.")
p("ACL POSIX x Windows (Figuras 15, 23 e 31). A entrada group:SABERMAIS\\professores:rwx do getfacl aparece no Windows como Controle total para o grupo Professores. A linha default vira a herança para arquivos e subpastas, o other::--- vira Todos sem permissão e o dono e o grupo dono viram PROPRIETÁRIO CRIADOR e GRUPO CRIADOR. Quem traduz isso é o Samba, o kernel só enxerga a ACL POSIX.")
p("strace (Figura 41). Liguei o strace no smbd pai com -f e acessei o teste-ana.txt como ana. O smbd novo da conexão fez openat(38, \"teste-ana.txt\", ...) para abrir o arquivo e pread64(46, \"lnx06-eduardo\\n\", 14, 0) para ler o conteúdo. São chamadas de sistema em que o processo, em modo usuário, pede ao kernel para mexer no sistema de arquivos.")

h("6.19 Encerramento")
p("No fim mostrei de novo hostname, IP, data e os serviços ativos e tirei o snapshot 03-t3-final.")
img("45-identificacaoFinal.png", "Identificação final com hostname, IP, data e serviços ativos")
p("E assim finalizo o T3, que me fez juntar quase todos os labs do semestre num servidor só.")

DIFIC = [
    ("p", "Restos de um laboratório anterior. A VM já tinha uma base de AD antiga em /var/lib/samba e linhas antigas no /etc/hosts e em /var/log/samba. Se eu provisionasse por cima, o samba-tool ia falhar ou misturar os dois domínios, e o nome errado podia aparecer em print. Com snapshot tirado, apaguei private, sysvol, os .tdb e o bind-dns, removi a linha do hosts e movi os logs antigos para /root/logs-antigos."),
    ("p", "ACL com nome que tem espaço. O setfacl não aceita o grupo SABERMAIS\\domain admins por causa do espaço no nome. Resolvi buscando o GID com getent group e usando o número no setfacl. O getfacl mostra o nome de volta, com o espaço escrito como \\040."),
    ("p", "Domain Users virou users. No getfacl da Pública aparece group:users em vez de domain users. Isso é o Samba DC mapeando o Domain Users para o GID 100 do grupo local users. Não mudei nada, a pasta continua liberada para todo usuário do domínio."),
    ("p", "Logon da ana com senha errada. No cliente a ana dava senha incorreta. Liguei o auth_audit em tempo real com smbcontrol all debug \"1 auth_audit:3\", porque o reload não tinha aplicado o log level no processo que já rodava, e o log mostrou NT_STATUS_WRONG_PASSWORD. Comparei a conta dela com a do eduardo.admin e eram iguais. No fim o erro era meu, eu estava digitando a senha errada. Essas tentativas viraram o teste negativo de autenticação da Figura 27."),
    ("p", "Aba Segurança fechando o Explorador. Como as pastas foram criadas pelo Linux, o grupo dono era root e o Samba entregava ao Windows um SID de grupo Unix sem nome. Troquei o grupo dono para domain admins com chgrp e a aba abriu."),
    ("p", "Sessão do administrador no lugar da ana. Na primeira tentativa do teste pelo Explorador a conexão SMB era do eduardo.admin, e o arquivo saiu com dono BUILTIN\\administrators. Vi isso no smbstatus, apaguei o arquivo, fiz logoff e repeti como ana."),
    ("p", "Outros ajustes menores: o print da janela de boas-vindas do domínio foi fechado sem querer e foi substituído pelas Figuras 25 e 26, o cliente não registrou o próprio nome no DNS (não afetou nada) e no strace incluí o pread64, porque o smbd lê arquivos com ele e não com read."),
]

REFS = [
    "SAMBA TEAM. Setting up Samba as an Active Directory Domain Controller. Disponível em: https://wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller",
    "SAMBA TEAM. Samba AD DC Port Usage. Disponível em: https://wiki.samba.org/index.php/Samba_AD_DC_Port_Usage",
    "SAMBA TEAM. Linux and Unix DNS Configuration. Disponível em: https://wiki.samba.org/index.php/Linux_and_Unix_DNS_Configuration",
    "SAMBA TEAM. Time Synchronisation. Disponível em: https://wiki.samba.org/index.php/Time_Synchronisation",
    "SAMBA TEAM. Setting up a Share Using POSIX ACLs. Disponível em: https://wiki.samba.org/index.php/Setting_up_a_Share_Using_POSIX_ACLs",
    "SAMBA TEAM. Joining a Windows Client or Server to a Domain. Disponível em: https://wiki.samba.org/index.php/Joining_a_Windows_Client_or_Server_to_a_Domain",
    "SAMBA TEAM. Installing RSAT. Disponível em: https://wiki.samba.org/index.php/Installing_RSAT",
    "SAMBA TEAM. Configuring Logging on a Samba Server. Disponível em: https://wiki.samba.org/index.php/Configuring_Logging_on_a_Samba_Server",
    "SAMBA TEAM. smb.conf(5) e samba-tool(8). Disponível em: https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html e https://www.samba.org/samba/docs/current/man-html/samba-tool.8.html",
    "CHRONY PROJECT. chrony.conf(5), versão 4.5. Disponível em: https://chrony-project.org/doc/4.5/chrony.conf.html",
    "LINUX MAN-PAGES. strace(1), setfacl(1) e nsswitch.conf(5). Disponível em: https://man7.org/linux/man-pages/man1/strace.1.html, https://man7.org/linux/man-pages/man1/setfacl.1.html e https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html",
    "MICROSOFT. Remote Server Administration Tools (RSAT) for Windows. Disponível em: https://learn.microsoft.com/en-us/troubleshoot/windows-server/system-management-components/remote-server-administration-tools",
]
