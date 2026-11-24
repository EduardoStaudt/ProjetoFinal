# Prints T4 (vsftpd com FTPS), Linux lnx06-eduardo

Eduardo Andrei Staudt, RA 2783045, nº 6. Escola Saber Mais. 23 e 24/11/2026.
Prints crus em `raw/`, textos das telas em `logs/t2-vsftpd-ftps-linux/`.

| Print | O que prova |
|---|---|
| 01-identificacao | hostname lnx06-eduardo.sabermais.lan, IP 192.168.106.20, data, AUTORIA.txt do T4 |
| 02-instalacaoStatus | vsftpd 3.0.5 instalado e active (running) |
| 03-certificadoTls | certificado autoassinado CN=lnx06-eduardo.sabermais.lan, O=Escola Saber Mais, chave privada 600, validade 1 ano |
| 04-usuariosUserlist | usuários ftp.professores e ftp.secretaria, pastas arquivos, senha definida, /etc/vsftpd.userlist |
| 05-vsftpdConf | vsftpd.conf final (chroot, passivo 40000-40100, TLS forçado, ssl_tlsv1=NO, ssl_tlsv11=NO, ssl_tlsv12=YES, ssl_tlsv13=YES, userlist). Refeito em 24/11 |
| 06-restartStatus | vsftpd active (running) após aplicar a configuração |
| 07-ufwStatus | ufw ativo só com 22, 21, faixa passiva e portas do Samba AD |
| 08-sambaAposUfw | DNS do domínio resolve o servidor FTP, compartilhamentos e portas 21/88/445/389 ativos após o ufw |
| 09-kinitSmbAposUfw | Kerberos (ticket krbtgt) e SMB com Kerberos funcionando após o ufw (T3 intacto) |
| 10-loginDominioAna | usuário do domínio SABERMAIS\ana.souza loga no FTPS via PAM winbind e faz upload |
| 11-logLoginDominio | log do vsftpd: AUTH TLS, 234, OK LOGIN e OK UPLOAD da ana (caminho "/ana-teste.txt" = chroot) |
| 12-loginProfessoresChroot | ftp.professores faz upload, 257 "/" após cd .., 550 em /etc (chroot) |
| 13-testesNegados | anônimo com e sem TLS, ftp.professores sem TLS e eduardo fora da userlist, todos 530 |
| 14-logsVsftpd | log com OK LOGIN, OK UPLOAD e as recusas 530, pam_winbind NT_STATUS_NO_SUCH_USER para usuário local |
| 15-filezillaCertificado | FileZilla no PC-PROF01 mostra o certificado (CN, O, autoassinado) e TLS 1.3 |
| 16-filezillaLoginOk | FileZilla conectado em ftpes://ftp.professores@192.168.106.20, listagem de / |
| 17-filezillaUpload | upload do plano-de-aula.txt pelo cliente Windows |
| 18-filezillaChroot | CWD /etc e CWD /home negados com 550 no FileZilla |
| 19-filezillaAnonimoNegado | login anonymous negado no FileZilla (530) |
| 20-processosSessao | pstree/ps com um processo por sessão e conexão ESTAB do cliente .50 na porta 21 |
| 21-privilegioChrootProc | /proc: só o listener é root, sessão como nobody e ftp.professores sem capabilities, raiz /home/ftp.professores |
| 22-straceUpload | strace: chroot("."), openat do boletim.txt e write dos 6 bytes no processo do usuário |
| 23-desafioStop | Desafio A: vsftpd parado, inactive, Connection refused, porta 21 fechada, Stopped no journal |
| 24-desafioStart | Desafio A: vsftpd religado, active (running), porta 21 em LISTEN, Started no journal |
| 25-desafioTesteOk | após a recuperação o login volta e o boletim.txt continua lá |
| 26-fechamento | hostname, IP, data, AUTORIA.txt, vsftpd e samba-ad-dc active |
| 27-opensslVersoesTls | com ssl_tlsv1=NO ssl_tlsv11=NO ssl_tlsv12=YES ssl_tlsv13=YES, openssl s_client -starttls ftp: TLS 1.0 e 1.1 recusados (alert protocol version), TLS 1.2 e 1.3 aceitos |
| 28-loginAposTls12 | FTPS continua funcionando após a troca das opções TLS: vsftpd e samba-ad-dc active, login, upload e remoção do teste-tls.txt |
| 29-fechamentoFinal | fechamento definitivo: hostname, IP, data, AUTORIA.txt, vsftpd e samba-ad-dc active |

Faltantes: nenhum. Prints 15 a 19 são do cliente PC-PROF01 (VM pc-cliente-sabermais).
Ajustes da execução em `docs/tasks/ajustes.md` (linhas "t2 linux").
