# T1 Linux (T3 do enunciado): Samba 4 como AD DC + Servidor de Arquivos
VM lnx06-eduardo, Ubuntu Server 24.04, 2 vCPU, 2 GB, 20 GB, NAT Network 192.168.106.0/24.
Prints em assets/t1-samba-ad-linux. Detecte a interface com `ip -br a` antes do netplan.

## 1. Identificação inicial
hostname -f ; ip -br a ; date ; cat /etc/os-release | head -3
Criar ~/AUTORIA.txt: "Eduardo Andrei Staudt - nº 6 - T3 Samba AD - <data>"

## 2. Hostname, IP estático, hosts, fuso
sudo hostnamectl set-hostname lnx06-eduardo
Netplan (arquivo em /etc/netplan/, backup antes), permissão 600:
  network: version 2, ethernets <IF>: dhcp4 no, addresses [192.168.106.20/24],
  routes [{to: default, via: 192.168.106.1}], nameservers {addresses [8.8.8.8], search [sabermais.lan]}
sudo netplan apply   (CUIDADO: pode derrubar o SSH se o IP mudar, avisar o Eduardo antes)
/etc/hosts: remover linha 127.0.1.1, adicionar "192.168.106.20 lnx06-eduardo.sabermais.lan lnx06-eduardo"
sudo timedatectl set-timezone America/Sao_Paulo
Validar: hostname -f -> lnx06-eduardo.sabermais.lan ; ping -c2 8.8.8.8

## 3. Pacotes
sudo DEBIAN_FRONTEND=noninteractive apt install -y acl attr samba samba-dsdb-modules \
  samba-vfs-modules smbclient winbind libpam-winbind libnss-winbind krb5-config krb5-user \
  dnsutils chrony ldb-tools strace psmisc lftp

## 4. Preparar DC  (PEDIR SNAPSHOT "01-pre-provision")
sudo systemctl disable --now smbd nmbd winbind systemd-resolved
sudo systemctl unmask samba-ad-dc ; sudo systemctl enable samba-ad-dc
sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bak ; sudo mv /etc/krb5.conf /etc/krb5.conf.bak
sudo rm /etc/resolv.conf ; printf "nameserver 127.0.0.1\nsearch sabermais.lan\n" | sudo tee /etc/resolv.conf
Explicar: DC é o DNS do domínio, systemd-resolved ocuparia a porta 53.

## 5. Provisionar
sudo samba-tool domain provision --realm=SABERMAIS.LAN --domain=SABERMAIS --server-role=dc \
  --dns-backend=SAMBA_INTERNAL --option="dns forwarder = 8.8.8.8" --adminpass='<pergunte>'
sudo cp /var/lib/samba/private/krb5.conf /etc/krb5.conf
sudo systemctl start samba-ad-dc ; systemctl status samba-ad-dc --no-pager

## 6. Validar DNS e Kerberos
host -t SRV _ldap._tcp.sabermais.lan ; host -t SRV _kerberos._udp.sabermais.lan
host -t A lnx06-eduardo.sabermais.lan ; kinit administrator ; klist ; smbclient -L localhost -N
sudo samba-tool domain level show

## 7. Hora do domínio (chrony + ntp_signd)
sudo chown root:_chrony /var/lib/samba/ntp_signd ; sudo chmod 750 /var/lib/samba/ntp_signd
Adicionar em /etc/chrony/chrony.conf: bindcmdaddress 192.168.106.20 | allow 192.168.106.0/24 |
  ntpsigndsocket /var/lib/samba/ntp_signd
sudo systemctl restart chrony ; chronyc tracking ; timedatectl
(Pergunta de verificação: Kerberos tolera 5 min de diferença, tickets têm timestamp anti replay.)

## 8. OUs, grupos, usuários  (PEDIR SNAPSHOT "02-dc-ok" antes)
for ou in Professores Secretaria Direcao; do sudo samba-tool ou create "OU=$ou,DC=sabermais,DC=lan"; done
sudo samba-tool group add Professores --groupou="OU=Professores" (idem Secretaria, Direcao)
sudo samba-tool user create eduardo.admin ; sudo samba-tool group addmembers "Domain Admins" eduardo.admin
user create com --userou="OU=<Depto>" --given-name --surname para os 6 usuários do CLAUDE.md
group addmembers por departamento
Conferir: samba-tool user list ; samba-tool group listmembers <grupo> ; samba-tool ou listobjects

## 9. Linux enxergando o domínio (NSS winbind)
/etc/nsswitch.conf: "passwd: files systemd winbind" e "group: files systemd winbind"
wbinfo -u ; wbinfo -g ; getent group "SABERMAIS\professores"  (usar nome exato exibido)

## 10. Pastas e ACLs POSIX
sudo mkdir -p /srv/samba/{Professores,Secretaria,Direcao,Publica} ; chmod 770 em todas
Para cada depto: setfacl -m g:"SABERMAIS\<grupo>":rwx -m d:g:"SABERMAIS\<grupo>":rwx
  e o mesmo para "SABERMAIS\domain admins". Publica: "SABERMAIS\domain users" rwx.
getfacl /srv/samba/*

## 11. Compartilhamentos
Em /etc/samba/smb.conf: [global] log level = 1 auth_audit:3
[Professores] [Secretaria] [Direcao] [Publica] com path=/srv/samba/<x> e read only = no
sudo testparm -s ; sudo smbcontrol all reload-config ; smbclient -L localhost -U administrator

## 12. Testes pelo Linux
smbclient //localhost/Professores -U ana.souza -c 'put /etc/hostname teste-ana.txt; ls'  (OK)
smbclient //localhost/Direcao -U ana.souza -c 'ls'  (NT_STATUS_ACCESS_DENIED)
smbclient //localhost/Publica -U beatriz.rocha -c 'ls'  (OK)

## 13. Cliente Windows (MANUAL, guiar o Eduardo)
IP 192.168.106.50/24, gw .1, DNS 192.168.106.20. nslookup sabermais.lan.
Ingressar no domínio sabermais.lan (administrator). Reiniciar. Logon SABERMAIS\ana.souza.
Prints: 13-clienteIngressado, 14-logonAnaSouza, 15-acessoProfessoresOk, 16-acessoDirecaoNegado,
  17-abaSegurancaProfessores. Instalar RSAT (Recursos opcionais > RSAT AD DS),
  abrir ADUC como eduardo.admin: 18-aducUsuariosGrupos, criar um usuário pelo RSAT: 19-usuarioCriadoRsat.
  (renumerar conforme a sequência real)

## 14. Logs
sudo journalctl -u samba-ad-dc --since "15 min ago" --no-pager | tail -40
ls /var/log/samba/ ; sudo tail -30 /var/log/samba/log.samba
grep de autenticação (auth_audit) mostrando sucesso e falha

## 15. Processos, threads, portas, syscalls (Labs 03, 05, 06, 08)
systemctl status samba-ad-dc --no-pager ; pstree -ap $(systemctl show -p MainPID --value samba-ad-dc)
ps -eLf | grep -E '[s]amba|[s]mbd' | head -30 ; top -H -b -n1 -p $(pgrep -d, smbd) | head -30
sudo ss -tulpn | grep -E 'samba|smbd'   (53, 88, 135, 389, 445, 464, 636, 3268...)
sudo smbstatus   (PID do smbd da sessão do cliente)
sudo timeout 20 strace -f -p <PID> -e trace=openat,read,write,fstat,getdents64,newfstatat
  enquanto o Eduardo abre um arquivo no cliente (ou um smbclient em outro ssh). Destacar 2 syscalls.

## 16. Desafio A
sudo cp /etc/resolv.conf /root/resolv.ok ; echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
kdestroy ; kinit administrator (falha, não encontra KDC) ; host -t SRV _ldap._tcp.sabermais.lan (falha)
Diagnóstico: cat /etc/resolv.conf ; Correção: sudo cp /root/resolv.ok /etc/resolv.conf ; kinit ; klist

## 17. Fechamento
hostname -f ; ip -br a ; date. Atualizar LISTA.md. Pedir snapshot "03-t3-final".
Perguntas de verificação (item 7.6 T3): standalone x DC, horário Kerberos, processos e portas,
ACL POSIX x Windows (getfacl), strace. Garanta que existe print que suporta cada resposta.
