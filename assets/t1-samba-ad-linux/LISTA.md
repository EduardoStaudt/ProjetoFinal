# T1 Linux (T3 do enunciado): Samba 4 AD DC + Arquivos

Eduardo Andrei Staudt, RA 2783045, nº 6. Domínio SABERMAIS.LAN, DC lnx06-eduardo (192.168.106.20), cliente PC-PROF01 (192.168.106.50).
Prints crus em `raw/`, texto da tela em `logs/t1-samba-ad-linux/`.

| Print | O que prova |
|---|---|
| 01-identificacaoInicial | hostname -f lnx06-eduardo.sabermais.lan, IP 192.168.106.20/24, fuso -03, /etc/hosts, AUTORIA.txt |
| 02-timezonePing | Fuso America/Sao_Paulo e acesso à internet (0% packet loss) |
| 03-pacotesInstalados | Samba 4.19.5, winbind, krb5-user, chrony, smbclient, acl instalados |
| 04-preparacaoDC | smbd/nmbd/winbind/systemd-resolved parados, samba-ad-dc enabled, smb.conf movido, resolv.conf aponta 127.0.0.1 |
| 05-provisionDominio | Provision como active directory domain controller, SABERMAIS / sabermais.lan, serviço active (running) |
| 06-dnsRegistrosSrv | SRV _ldap (389) e _kerberos (88) e registro A do DC no DNS interno |
| 07-kinitKlist | TGT krbtgt/SABERMAIS.LAN para administrator |
| 08-smbclientNivelDominio | Shares sysvol/netlogon e nível funcional 2008 R2 |
| 09-chronyHoraDominio | ntp_signd root:_chrony 750, ntpsigndsocket no chrony.conf, relógio sincronizado |
| 10-ousCriadas | OUs Professores, Secretaria, Direcao e seus objetos |
| 11-usuariosGrupos | 6 usuários + eduardo.admin e membros de cada grupo |
| 12-domainAdmins | eduardo.admin memberOf Domain Admins |
| 13-winbindNss | nsswitch com winbind, wbinfo -u/-g, getent group e id da ana |
| 14-aclsProfessores | Pastas drwxrwx---+ e ACL/ACL default do grupo professores |
| 15-aclsSecretariaDirecao | ACLs de secretaria e direcao |
| 16-aclsPublica | Domain Users (GID 100 = users) com rwx na Publica |
| 17-testparmShares | log level auth_audit:3, testparm OK e os 4 shares |
| 18-smbclientListaShares | Lista de shares autenticada por Kerberos |
| 19-anaProfessoresOk | ana.souza grava na Professores pelo smbclient |
| 20-anaDirecaoNegado | ana.souza recebe NT_STATUS_ACCESS_DENIED na Direcao |
| 21-beatrizPublicaOk | beatriz.rocha lista a Publica |
| 22-arquivoDonoAcl | Arquivo com dono SABERMAIS\ana.souza e ACL herdada |
| 23-clienteDnsDominio | Cliente .50 resolve sabermais.lan e SRV do DC |
| 24-computadorNoDominio | Conta PC-PROF01$ criada no domínio (substitui janela de boas-vindas) |
| 25-logonAnaClienteDominio | Logon sabermais\ana.souza no PC-PROF01, LOGONSERVER \\LNX06-EDUARDO |
| 26-authAuditLogonCliente | auth_audit: WRONG_PASSWORD e OK da ana, OK do eduardo.admin, vindos do .50 |
| 27-acessoProfessoresOk | ana cria arquivo em \\lnx06-eduardo\Professores pelo Windows |
| 28-smbstatusSessaoAna | smbstatus mostra sessão SMB3 da ana e dono dos arquivos |
| 29-acessoDirecaoNegado | Windows nega \\lnx06-eduardo\Direcao para a ana |
| 30-abaSegurancaProfessores | Aba Segurança: grupo Professores com Controle total (ACL POSIX vista como NTFS) |
| 31-aducUsuariosGrupos | ADUC (RSAT) conectado ao DC Samba, OU Professores |
| 32-usuarioCriadoRsat | paula.mendes criada pelo ADUC |
| 33-usuarioRsatNoSamba | samba-tool vê paula.mendes na OU Professores e no grupo |
| 34-journalSambaAdDc | journalctl: samba 4.19.5 started, serviço Started |
| 35-logsSambaAuthAudit | /var/log/samba e linhas completas de auth_audit (falha e sucesso) |
| 36-processosPstree | Árvore de processos: samba pai, s3fs/smbd, sessão do cliente, ldap, rpc |
| 37-processosNlwp | NLWP=1 em todos: modelo multiprocesso prefork |
| 38-topThreadsSmbd | top -H nos smbd |
| 39-portasSs | Portas 53, 88, 135, 389, 445, 464, 636, 3268, 3269 e processo dono |
| 40-straceSmbd | strace no smbd: openat do teste-ana.txt e pread64 do conteúdo |
| 41-desafioQuebraResolv | Desafio A: backup do resolv.conf e troca para 8.8.8.8 |
| 42-desafioKinitFalha | kinit: Cannot find KDC, SRV NXDOMAIN |
| 43-desafioDiagnostico | resolv.conf errado e DNS do Samba ainda escutando na 53 |
| 44-desafioRecuperado | resolv.conf restaurado, SRV resolve, novo TGT |
| 45-identificacaoFinal | hostname, IP, data e serviços ativos no fim |

## Perguntas de verificação x print
- Standalone x DC: 05, 08, 31
- Horário e Kerberos (5 min, anti replay): 09, 07
- Processos e portas: 36, 37, 38, 39
- ACL POSIX x Windows: 14, 22, 30
- strace: 40

## Faltantes
- Nenhum. Janela "Bem-vindo ao domínio" não capturada (fechada), coberta por 24 e 25.
- Pendente: snapshot "03-t3-final".
