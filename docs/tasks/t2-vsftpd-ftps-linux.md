# T2 Linux (T4 do enunciado): vsftpd com FTPS
Mesma VM lnx06-eduardo, após snapshot "03-t3-final". Prints em assets/t2-vsftpd-ftps-linux.
Problema da escola: secretaria e professores trocam arquivos (planos de aula, documentos) por FTP
com criptografia, cada um preso na sua pasta.

## 1. Identificação: hostname -f ; ip -br a ; date ; cat ~/AUTORIA.txt (atualizar para T4)

## 2. Instalação
sudo apt install -y vsftpd openssl ; systemctl status vsftpd --no-pager ; vsftpd -v 2>&1 || true

## 3. Certificado TLS autoassinado
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/vsftpd.key -out /etc/ssl/certs/vsftpd.crt \
  -subj "/CN=lnx06-eduardo.sabermais.lan/O=Escola Saber Mais"
sudo chmod 600 /etc/ssl/private/vsftpd.key ; openssl x509 -in /etc/ssl/certs/vsftpd.crt -noout -subject -dates

## 4. Usuários locais e lista de permitidos
sudo adduser --gecos "" ftp.professores ; sudo adduser --gecos "" ftp.secretaria (senha: pergunte)
mkdir ~/arquivos em cada home, dono do usuário
printf "ftp.professores\nftp.secretaria\n" | sudo tee /etc/vsftpd.userlist

## 5. /etc/vsftpd.conf (backup .bak, depois escrever e explicar CADA parâmetro)
listen=YES / listen_ipv6=NO / anonymous_enable=NO / local_enable=YES / write_enable=YES / local_umask=022
chroot_local_user=YES / allow_writeable_chroot=YES
pasv_enable=YES / pasv_min_port=40000 / pasv_max_port=40100 / pasv_address=192.168.106.20
ssl_enable=YES / rsa_cert_file=/etc/ssl/certs/vsftpd.crt / rsa_private_key_file=/etc/ssl/private/vsftpd.key
force_local_logins_ssl=YES / force_local_data_ssl=YES / ssl_tlsv1_2=YES / ssl_sslv2=NO / ssl_sslv3=NO
require_ssl_reuse=NO / ssl_ciphers=HIGH
userlist_enable=YES / userlist_file=/etc/vsftpd.userlist / userlist_deny=NO
xferlog_enable=YES / log_ftp_protocol=YES / vsftpd_log_file=/var/log/vsftpd.log / dual_log_enable=YES
sudo systemctl restart vsftpd ; systemctl status vsftpd --no-pager

## 6. Firewall
sudo ufw allow 22/tcp ; 21/tcp ; 40000:40100/tcp
Samba (não quebrar o T3): 53, 88, 135, 139, 389, 445, 464, 636, 3268, 3269/tcp, 53,88,123,137,138,389,464/udp, 49152:65535/tcp
sudo ufw enable ; sudo ufw status numbered
Conferir que kinit e smbclient continuam funcionando.

## 7. Integração com o domínio (T3)
Tentar login de usuário do domínio no vsftpd via PAM:
  /etc/pam.d/vsftpd: auth sufficient pam_winbind.so antes do common-auth, account idem.
  Incluir "SABERMAIS\ana.souza" (ou formato aceito) na userlist, testar.
Se funcionar: print. Se não (DC Samba não recomenda winbind PAM no DC), registrar o erro real
e a justificativa técnica em docs/tasks/ajustes.md. O vídeo pode explicar isso (enunciado aceita).
Integração mínima garantida: DNS do domínio resolve o servidor FTP (host lnx06-eduardo.sabermais.lan).

## 8. Testes (no Linux, com lftp)
OK: lftp -u ftp.professores -e "set ftp:ssl-force true; set ssl:verify-certificate no; ls; put /etc/hostname -o teste.txt; ls; bye" localhost
Chroot: mesmo comando com "cd /; pwd; ls" (continua na home)
Anônimo negado: lftp -u anonymous,x -e "set ssl:verify-certificate no; ls; bye" localhost
Sem TLS negado: lftp -u ftp.professores -e "set ftp:ssl-allow false; ls; bye" localhost
Fora da userlist negado: usuário eduardo
Logs: sudo tail -30 /var/log/vsftpd.log ; sudo journalctl -u vsftpd --no-pager | tail

## 9. Cliente (MANUAL)
FileZilla no cliente Windows: host 192.168.106.20, "Requer FTP explícito sobre TLS", aceitar certificado.
Prints: certificado, login ok, upload, tentativa de sair do chroot, login anônimo negado.

## 10. SO
systemctl status vsftpd ; pstree -ap $(systemctl show -p MainPID --value vsftpd) durante sessão ativa
(um processo por conexão, separação de privilégio) ; ps -o pid,user,cmd -C vsftpd ; sudo ss -tulpn | grep vsftpd
Modo usuário: vsftpd. Kernel: sockets TCP, chroot() syscall, sistema de arquivos.
Opcional: strace -f -p <pid sessão> -e trace=chroot,openat,read,write durante um put.

## 11. Desafio A genérico
sudo systemctl stop vsftpd ; teste lftp falha (connection refused) ; ss -tulpn sem porta 21 ;
journalctl -u vsftpd mostra stop ; sudo systemctl start vsftpd ; teste ok.

## 12. Riscos e mitigação (resumo para o vídeo)
Senha em texto puro -> TLS forçado | anônimo -> desabilitado | travessia de diretório -> chroot |
portas abertas -> ufw só 21 e faixa passiva | usuários quaisquer -> userlist.

## 13. Fechamento: hostname -f ; ip -br a ; date ; LISTA.md ; snapshot "04-t4-final"
