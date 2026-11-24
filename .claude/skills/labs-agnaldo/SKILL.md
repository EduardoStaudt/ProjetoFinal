---
name: labs-agnaldo
description: >
  Gera relatórios de laboratório do Eduardo para Sistemas Operacionais (CC4SO) e
  Redes de Computadores (CC4RC) do professor Agnaldo na UTFPR, no template oficial
  e no estilo de escrita dele. Use SEMPRE que o Eduardo mencionar um laboratório,
  lab, relatório de aula prática, Packet Tracer, máquina virtual, VirtualBox, comandos
  Linux, FHS, topologias de rede, modelo OSI, ou enviar um enunciado dessas matérias,
  mesmo que não peça explicitamente pra "montar o relatório". Dispara também quando ele
  pedir pra aprender ou entender o conteúdo de um lab dessas disciplinas.
---

# labs-agnaldo

Ajuda o Eduardo a fazer os laboratórios de Sistemas Operacionais e Redes de
Computadores. O fluxo é sempre o mesmo: primeiro ensina o conteúdo, depois
responde as questões na voz dele, depois monta o relatório no template oficial
sem mexer na formatação.

O objetivo do relatório é o que o próprio template pede: qualquer pessoa lê e
entende o que foi feito no laboratório, e o Eduardo relê meses depois e relembra
tudo pra prova. Então clareza e fidelidade ao que ele fez valem mais que texto
bonito.

## Dados fixos do Eduardo (nunca perguntar isso)

- Estudante: `Eduardo Andrei Staudt`
- RA: `2783045`
- Disciplina, sempre uma destas strings exatas:
  - `Sistemas Operacionais - CC4SO`
  - `Redes de Computadores - CC4RC`
- Nome do arquivo final: `LAB{X}-EduardoAndreiStaudt-2783045.docx`
  - O `{X}` é o número do lab. Pergunte ao Eduardo qual é, ele passa.

## Ordem de trabalho

1. Coletar o enunciado, a disciplina e o número do lab.
2. Ensinar o conteúdo com uma analogia e um diagrama ou imagem, antes de escrever qualquer coisa.
3. Redigir as respostas no estilo do Eduardo (conciso, ele pede pra expandir o que quiser).
4. Preencher o template preservando 100% da formatação.
5. Encaixar as imagens dele centralizadas nos lugares certos.
6. Salvar como `LAB{X}-EduardoAndreiStaudt-2783045.docx` e entregar.

## Passo a passo

### 1. Coletar do Eduardo

Antes de começar, tenha em mãos:

- O enunciado do laboratório (PDF ou texto).
- A disciplina: SO (CC4SO) ou Redes (CC4RC). Dá pra inferir pelo enunciado, mas confirme.
- O número do lab `{X}` pro nome do arquivo.
- As imagens ou prints, se ele já tiver. A parte prática é dele (montar a topologia
  no Packet Tracer, rodar a VM, executar os comandos), então os prints vêm dele.

### 2. Ensinar antes de escrever

O Eduardo sempre quer entender o conteúdo antes. Então, para os conceitos que o
laboratório cobre:

- Explique com uma analogia concreta.
- Mostre um diagrama ou imagem. Use a ferramenta de diagramas (visualizer) para
  esquemas próprios, ou busca de imagens para fotos reais de equipamentos, telas,
  topologias, etc.
- Só depois disso comece a redigir o relatório.

Exemplos de conteúdo por matéria: em Redes costuma ser topologias, tipos de rede
(PAN LAN CAN MAN WAN), modelo OSI, dispositivos e cabos, serviços de rede. Em SO
costuma ser FHS e diretórios do Linux, comandos de terminal, instalação e
configuração de servidor, SSH, netplan, VirtualBox.

### 3. Redigir no estilo do Eduardo

Leia `references/estilo.md` e siga a voz dele. Resumo:

- Primeira pessoa, narração do que ele fez, na ordem em que fez.
- Português casual misturado com técnico. Direto e objetivo, como nos exemplos.
- Conciso por padrão. Nas questões numeradas ele escolhe o nível de detalhe:
  entregue conciso e ele pede pra expandir as que quiser.
- Aplique a skill `humanizer` no texto, o relatório tem que soar escrito por ele,
  não por IA.

**Regras de texto que não podem ser quebradas:**

- Proibido travessão (—) no corpo do texto.
- Proibido ponto e vírgula (;) no corpo do texto.

### 4. Seções do relatório

O template tem estas seções, nesta ordem. Repare que **não existe seção 4**, o
template pula de 3 para 5. Mantenha exatamente assim.

- **1. IDENTIFICAÇÃO** — tabela. Preencha: Título do Projeto (um título curto pro
  lab), Disciplina (a string exata), Estudante, RA.
- **2. INTRODUÇÃO** — parágrafo curto situando o assunto do lab.
- **3. OBJETIVOS DO RELATÓRIO PROPOSTO** — o que se espera com o experimento.
- **5. MATERIAL UTILIZADO** — softwares e materiais usados (Packet Tracer, VirtualBox,
  PuTTY, slides do Moodle, livro do Kurose em Redes, etc, conforme o lab).
- **6. SÍNTESE DAS ATIVIDADES REALIZADAS** (máx 1 página) — o coração do relatório.
  Narração passo a passo do que foi feito, com as imagens encaixadas. Em labs de
  perguntas, é aqui que entram as respostas numeradas.
- **7. DIFICULDADES ENCONTRADAS** (máx 1 página) — problemas no processo. Se não
  houve, escreva algo curto e honesto no estilo dos exemplos.
- **8. REFERÊNCIAS BIBLIOGRÁFICAS** — ver regra abaixo.

**Referências:** só entram se o Eduardo passar as fontes. Se ele não passar, use a
linha padrão dele, por exemplo: "Não foram utilizadas referências bibliográficas
externas, foram utilizados apenas os materiais disponibilizados no Moodle." Nunca
invente referências.

### 5. Imagens

O Eduardo faz a parte prática e manda os prints. A skill coloca esses prints
**dentro do relatório, encaixados nos devidos lugares, sempre centralizados.**

- O lugar natural da maioria é a seção 6, seguindo a narração passo a passo (texto
  do passo, depois a imagem daquele passo, depois o próximo passo).
- Se ele ainda não mandou os prints, deixe um placeholder centralizado no formato
  `[IMAGEM: descrição do que printar aqui]` e, no fim da conversa, liste tudo que
  ele precisa printar pra completar o relatório.

### 6. Preencher o template

Leia `references/template-fill.md`. Pontos principais:

- Use o template que vem com a skill: `assets/modelo-relatorio-utfpr.docx`.
- **Edite** o documento (descompacta, mexe no `word/document.xml`, recompacta). Não
  recrie o documento do zero, senão perde a formatação. Use a skill `docx`.
- Preserve tudo: logo da UTFPR, cabeçalho de instruções, numeração das seções,
  caixas e tabela. Só coloque conteúdo dentro do que já existe.

### 7. Entregar

- Salve como `LAB{X}-EduardoAndreiStaudt-2783045.docx` em `/mnt/user-data/outputs/`.
- Entregue com `present_files`.
- Se faltam prints, liste em uma lista curta o que ele precisa capturar.

## Regras invioláveis (resumo)

1. Nunca altere a formatação do template.
2. Nunca use travessão (—) nem ponto e vírgula (;) no corpo do texto.
3. Nome do arquivo sempre `LAB{X}-EduardoAndreiStaudt-2783045`, perguntando o `{X}`.
4. Disciplina sempre exata: `Sistemas Operacionais - CC4SO` ou `Redes de Computadores - CC4RC`.
5. Referências só se o Eduardo fornecer.
6. Ensine o conteúdo com analogia e diagrama antes de escrever.
7. Imagens sempre centralizadas, encaixadas no lugar certo.

## Arquivos da skill

- `assets/modelo-relatorio-utfpr.docx` — o template oficial. Sempre parta deste.
- `references/estilo.md` — a voz do Eduardo e trechos reais de exemplo.
- `references/template-fill.md` — como preencher o docx sem quebrar a formatação.
