# T1 Windows: AD DS + Servidor de Arquivos
Windows Server 2022/2025 Eval, 2 vCPU, 4 GB, 40 GB, NAT Network. Prints em assets/t1-adds-arquivos-win.
Acesso: console da VM (manual) e, após o passo 1, `ssh srv06` com PowerShell.
ATENÇÃO idioma: se o Windows for pt-BR, nomes de templates/subcategorias mudam. Usar GUIDs quando indicado.

## 1. Preparo (MANUAL no console, PowerShell admin)
Rename-Computer SRV06-EDUARDO -Restart
New-NetIPAddress -InterfaceAlias Ethernet -IPAddress 192.168.106.10 -PrefixLength 24 -DefaultGateway 192.168.106.1
Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses 127.0.0.1
Set-TimeZone -Id "E. South America Standard Time"
SSH: Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 ; Start-Service sshd ;
  Set-Service sshd -StartupType Automatic ;
  New-ItemProperty HKLM:\SOFTWARE\OpenSSH -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -Force
Arquivo C:\Users\Public\Desktop\AUTORIA.txt com nome, nº 6, T1 e data.

## 2. AD DS  (SNAPSHOT antes)
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
Install-ADDSForest -DomainName sabermais.local -DomainNetbiosName SABERMAIS -InstallDns -Force (senha DSRM: pergunte)
Após reboot: Get-ADDomain ; Get-Service NTDS,DNS,Netlogon,KDC ; Resolve-DnsName -Type SRV _ldap._tcp.sabermais.local

## 3. OUs, usuários, grupos (AGDLP)
OUs: Professores, Secretaria, Direcao, Grupos (New-ADOrganizationalUnit)
Globais: GG_Professores, GG_Secretaria, GG_Direcao (-GroupScope Global -GroupCategory Security)
Locais de domínio: DL_Professores_RW, DL_Secretaria_RW, DL_Direcao_RW, DL_Publica_RW (-GroupScope DomainLocal)
Usuários do CLAUDE.md + eduardo.admin (Domain Admins) com New-ADUser -Enabled $true
Aninhamento: GG nos DL (A->G->DL->P). DL_Publica_RW recebe os 3 GG.
Conferir: Get-ADGroupMember para cada grupo.

## 4. Servidor de arquivos, compartilhamentos, NTFS, ABE
Install-WindowsFeature FS-FileServer,FS-Resource-Manager -IncludeManagementTools
C:\Dados\{Professores,Secretaria,Direcao,Publica}
Compartilhamento: New-SmbShare -FullAccess "SABERMAIS\Domain Users" -FolderEnumerationMode AccessBased
  (share amplo, NTFS restringe. Explicar que vale a mais restritiva das duas)
NTFS: desabilitar herança (icacls /inheritance:r), conceder SYSTEM e Administrators Full,
  DL_<Depto>_RW Modify (OI)(CI)M. Publica: DL_Publica_RW Modify.
Pasta base \\SRV06-EDUARDO\Dados com ABE para demonstrar que o usuário só VÊ o que pode acessar.
Get-SmbShare | ft Name,Path,FolderEnumerationMode ; icacls C:\Dados\*

## 5. FSRM
New-FsrmQuota -Path C:\Dados\Publica -Size 100MB (ou template)
New-FsrmFileScreen -Path C:\Dados\Publica -Template (Get-FsrmFileScreenTemplate)[n].Name   (escolher bloqueio de áudio/vídeo)
Testar: copiar .mp3 falso negado, ultrapassar cota.

## 6. GPO de mapeamento (MANUAL no GPMC, guiar)
GPO "Mapeamento-Unidades" vinculada ao domínio: Config. do Usuário > Preferências > Mapeamentos de Unidade
P: Publica (todos), X: \\SRV06-EDUARDO\<Depto> com Direcionamento por Item = grupo GG_<Depto>.

## 7. Auditoria
auditpol /set /subcategory:"{0CCE921D-69AE-11D9-BED3-505054503030}" /success:enable /failure:enable
SACL na pasta Direcao (Avançado > Auditoria, Everyone, falha e sucesso) (manual ou Set-Acl)
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4663,4656} -MaxEvents 5

## 8. Cliente (MANUAL)
IP .50, DNS .10, ingressar sabermais.local, logon ana.souza e beatriz.rocha.
Prints: unidades mapeadas, gpresult /r, acesso ok, acesso negado, ABE escondendo pastas.

## 9. SO
Get-Service NTDS,DNS,LanmanServer ; Get-Process lsass,dns | ft Id,Name,CPU,Threads? (use (Get-Process lsass).Threads.Count)
Get-NetTCPConnection -State Listen | ? LocalPort -in 53,88,389,445,636,3268 ; netstat -ano | findstr LISTENING
NTDS.dit em C:\Windows\NTDS, SYSVOL em C:\Windows\SYSVOL. lsass em modo usuário (PPL).

## 10. Desafio A
Stop-Service DNS ; no cliente: nslookup sabermais.local falha, logon de usuário novo falha ;
Event Viewer / Get-WinEvent ; Start-Service DNS ; testar de novo.

## 11. Fechamento: hostname ; ipconfig ; whoami /fqdn ; Get-Date ; LISTA.md ; snapshot
