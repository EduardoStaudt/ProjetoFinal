# T2 Windows: Remote Desktop Services (Session Host)
Mesmo SRV06-EDUARDO (único IP Windows do cenário). Prints em assets/t2-rds-win.
Problema da escola: professores acessam um desktop centralizado com os programas da escola de
qualquer máquina, sem instalar nada local.
Obs: RDSH em DC não é recomendado pela Microsoft, mas é o único servidor Windows do cenário.
Explicar isso no vídeo (pergunta de riscos). SNAPSHOT antes.

## 1. Identificação: hostname ; ipconfig ; whoami /fqdn ; Get-Date

## 2. Instalação
Install-WindowsFeature RDS-RD-Server,RDS-Licensing -IncludeManagementTools -Restart
Get-WindowsFeature RDS* | ? Installed

## 3. Licenciamento (avaliação 120 dias)
Via GPO (gpedit no servidor ou GPO no GPMC): Computer > Admin Templates > Windows Components >
Remote Desktop Services > Session Host > Licensing: "Use the specified RD license servers" = SRV06-EDUARDO,
"Set the Remote Desktop licensing mode" = Per User. Ativar o servidor de licenças no RD Licensing Manager (manual).
Get-WmiObject -Namespace root\cimv2\terminalservices -Class Win32_TerminalServiceSetting | select LicensingType

## 4. Acesso restrito a grupo do AD
New-ADGroup GG_RDP_Professores Global ; adicionar ana.souza, carlos.lima
Adicionar o grupo ao grupo local de domínio "Remote Desktop Users" (Builtin)
Em DC: Default Domain Controllers Policy > Atribuição de direitos > "Permitir logon pelos Serviços de
Área de Trabalho Remota" incluir GG_RDP_Professores (MANUAL GPMC). gpupdate /force.

## 5. Limite de sessões (GPO ou registro de política)
HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services: MaxInstanceCount=3, fSingleSessionPerUser=1,
MaxIdleTime e MaxDisconnectionTime (ms). Explicar cada valor.

## 6. Testes (MANUAL no cliente)
mstsc para 192.168.106.10 com ana.souza (OK) e carlos.lima simultâneo (OK), beatriz.rocha (negado).
Prints de cada tentativa e da mensagem de negação.

## 7. Sessões e processos (Labs 03, 06, 08)
qwinsta ; query user ; Get-Process -IncludeUserName | ? UserName -like "SABERMAIS*" | sort SessionId
tasklist /v /fi "SESSION eq 2" ; (Get-Process explorer).Threads.Count
Get-Service TermService,UmRdpService,TermServLicensing ; Get-NetTCPConnection -LocalPort 3389
Processo por sessão: csrss, winlogon, explorer em cada SessionId. TermService em svchost.

## 8. Logs
Get-WinEvent -LogName "Microsoft-Windows-TerminalServices-LocalSessionManager/Operational" -MaxEvents 10
Security 4624 LogonType 10 (RDP) e 4625 (negado)

## 9. Desafio A genérico
Stop-Service TermService -Force ; mstsc falha ; Get-NetTCPConnection 3389 vazio ; evento no log ;
Start-Service TermService ; teste ok.

## 10. Riscos: RDP exposto (só rede interna, NLA ligado), brute force (lockout policy), RDSH no DC
(privilégio), sessões abandonadas (timeouts).

## 11. Fechamento: hostname ; ipconfig ; Get-Date ; LISTA.md ; snapshot
