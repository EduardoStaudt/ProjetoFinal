# Trabalho Final de Sistemas Operacionais (CC4SO), Eduardo Andrei Staudt

Leia este arquivo inteiro, depois `docs/context/desc/` (enunciado + planilha do professor),
depois a task do trabalho que o Eduardo pedir em `docs/tasks/`.

## O trabalho
Prof. Agnaldo, UTFPR Santa Helena, 2026/2. 4 trabalhos, cada um vira um vídeo de no MÍNIMO
15 min (o Eduardo grava), slides e roteiro. Nesta etapa: executar e tirar prints.
Relatórios ficam para outra etapa (NÃO gerar docx agora).

| Pasta de prints | Trabalho no enunciado | Plataforma | Task |
|---|---|---|---|
| assets/t1-samba-ad-linux | T3 Samba 4 AD DC + Arquivos | Linux | docs/tasks/t1-samba-ad-linux.md |
| assets/t2-vsftpd-ftps-linux | T4 vsftpd com FTPS | Linux | docs/tasks/t2-vsftpd-ftps-linux.md |
| assets/t1-adds-arquivos-win | T1 AD DS + Servidor de Arquivos | Windows Server | docs/tasks/t1-adds-arquivos-win.md |
| assets/t2-rds-win | T2 Remote Desktop Services (Session Host) | Windows Server | docs/tasks/t2-rds-win.md |

Ordem: Linux primeiro (t1 linux, t2 linux), depois Windows.

## Cenário obrigatório (valor diferente ANULA o trabalho)
- Aluno: Eduardo Andrei Staudt, RA 2783045, nº 6 na planilha
- Empresa: Escola Saber Mais
- Departamentos (OUs e grupos): Professores, Secretaria, Direcao (escrito "Direção" só em texto)
- Domínio Windows: sabermais.local (NetBIOS SABERMAIS)
- Realm Linux: SABERMAIS.LAN (DNS sabermais.lan, NetBIOS SABERMAIS)
- Rede: 192.168.106.0/24, gateway .1, Windows Server .10, Linux .20, clientes a partir de .50
- Hostnames: SRV06-EDUARDO (Windows) e lnx06-eduardo (Linux)
- Usuários nome.sobrenome + obrigatório eduardo.admin (admin do domínio)
- Usuários padrão: ana.souza, carlos.lima (Professores) | beatriz.rocha, diego.alves (Secretaria) |
  fernanda.costa, marcos.pereira (Direcao)
- Desafio de quebra e recuperação: A (6 mod 3 = 0)

## Acesso às máquinas
- Linux: `ssh lnx06` (usuário eduardo, sudo sem senha durante o trabalho)
- Windows Server: `ssh srv06` (OpenSSH Server, shell PowerShell), quando existir
- Cliente Windows 10/11 (.50) e telas gráficas (RSAT, GPMC, FileZilla, RDP): MANUAIS.
  Pare, diga ao Eduardo exatamente onde clicar, qual print tirar e com qual nome/pasta salvar,
  e espere ele responder "feito".
- Senhas de laboratório: pergunte ao Eduardo na hora. Nunca escreva senha em arquivo.

## Como trabalhar
1. Um passo por vez. ANTES de executar, explique no chat linha por linha: o que cada comando e
   parâmetro faz e POR QUE (ele vai narrar no vídeo e ser arguido ao vivo).
2. Rode, mostre a saída resumida, siga só se der certo. Erro: diagnostique, explique, corrija.
3. Antes de etapas críticas (provision, promoção do DC, desafio) peça snapshot da VM e espere.
4. Se precisar ajustar algo da task (nome de interface, versão), anote em `docs/tasks/ajustes.md`.
5. Nada destrutivo fora da task sem perguntar.
6. Nos textos que escrever pro Eduardo: sem travessão e sem ponto e vírgula.

## Prints (padrão obrigatório): SCREENSHOT REAL da VM
- Nome: `XX-oQueTemNoPrint.png` (XX = 01, 02... na ordem, camelCase). Ex: `05-kinitKlist.png`
- Pasta: a do trabalho em `assets/` (caminho absoluto Windows no VBoxManage).
- Nomes das VMs no VirtualBox: `lnx06-eduardo`, `SRV06-EDUARDO`, `CLIENTE-WIN` (confirme com `VBoxManage list runningvms`).

### Linux (comando aparece na tela real da VM)
O Eduardo deixa logado no console da VM uma sessão `tmux new -s demo`. Para cada print:
1. `ssh lnx06 "tmux send-keys -t demo 'clear' Enter"`
2. `ssh lnx06 "tmux send-keys -t demo '<COMANDO>' Enter"` (cuidado com aspas, use script se complexo)
3. espere terminar (`sleep`, ou cheque `tmux capture-pane -p -t demo`)
4. `VBoxManage controlvm lnx06-eduardo screenshotpng "<caminho>\assets\<pasta>\XX-nome.png"`
5. Salve também o texto: `ssh lnx06 "tmux capture-pane -p -S -200 -t demo" > logs/<pasta>/XX-nome.txt`
Comandos sem valor de print podem rodar direto por `ssh lnx06` (fora do tmux).
Saída maior que a tela: tudo bem aparecer só o começo ou só o fim, desde que o comando e a
informação importante estejam visíveis. Não precisa perfeição.

### Recorte e destaque em vermelho (sempre)
1. Salve o screenshot cru em `assets/<pasta>/raw/XX-nome.png`
2. Salve a tela visível: `ssh lnx06 "tmux capture-pane -p -t demo" > logs/<pasta>/XX-nome.screen.txt`
3. Gere o final: `python tools/annotate.py assets/<pasta>/raw/XX-nome.png logs/<pasta>/XX-nome.screen.txt assets/<pasta>/XX-nome.png "<trecho importante>" ["<outro>"]`
   O script recorta só a área com texto e desenha caixa vermelha em cada trecho
   (ex: o IP, o "active (running)", o NT_STATUS_ACCESS_DENIED, a porta 445).
   Escolha 1 a 3 trechos que provam o que o print quer mostrar. Abra a imagem e confira.
Console: 1280x800, Terminus 16x32. Se a resolução/fonte mudar, ajuste CW/CH (ver tools/annotate.py).
Prints do Windows (sem txt): recorte/destaque com Pillow por coordenadas, olhando a imagem.

### Windows (servidor e cliente)
- Comandos PowerShell: rode via `ssh srv06` e, quando for print, peça ao Eduardo para deixar o
  PowerShell aberto no console, ou mostre a saída em tela com o fluxo manual.
- Telas gráficas: o Eduardo clica, avisa "pronto", e VOCÊ tira o print com
  `VBoxManage controlvm <VM> screenshotpng "<caminho>\XX-nome.png"`.

### Plano B
Se VBoxManage falhar, use `tools/print_terminal.py` (gera imagem a partir do texto) e anote em
`docs/tasks/ajustes.md` quais prints foram gerados assim.

- Primeiro e último print de cada trabalho: `hostname -f`, `ip -br a` (ou `hostname`, `ipconfig`) e `date`.
- Ao terminar cada trabalho: `assets/<pasta>/LISTA.md` com cada print e o que ele prova, marcando faltantes.

## Final da etapa
Gerar `prints-TF-SO.zip` com assets/ e logs/.
