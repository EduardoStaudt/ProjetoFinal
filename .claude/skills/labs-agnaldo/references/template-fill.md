# Preenchendo o template sem quebrar a formatação

O template é `assets/modelo-relatorio-utfpr.docx` (MODELO GERAL DE RELATÓRIO
TÉCNICO da UTFPR). A regra número um do Eduardo é não alterar a formatação. Então
o certo é **editar** o documento existente, não gerar um novo.

## Abordagem correta

Um `.docx` é um zip de XML. Para editar preservando formatação, use a skill `docx`:

```bash
# copie o template pra um lugar de trabalho antes (o asset é a fonte da verdade)
cp assets/modelo-relatorio-utfpr.docx /tmp/lab.docx

unzip -q /tmp/lab.docx -d /tmp/unpacked/
find /tmp/unpacked -type l -delete
python <skill-docx>/scripts/merge_runs.py /tmp/unpacked/   # junta runs fragmentados
# edite /tmp/unpacked/word/document.xml no lugar, sem reformatar
(cd /tmp/unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python <skill-docx>/scripts/office/validate.py ../out.docx --original /tmp/lab.docx
```

Depois renderize pra conferir que nada quebrou:

```bash
python <skill-docx>/scripts/office/soffice.py --headless --convert-to pdf out.docx
pdftoppm -jpeg -r 100 out.pdf page && ls page-*.jpg   # olhe as imagens
```

Não recrie o documento com docx-js. Ele não abre arquivos existentes e você perderia
o logo, a numeração e as caixas.

## O que preencher em cada lugar

O template já tem os rótulos e as caixas. Você só coloca conteúdo dentro.

**Tabela da seção 1 (IDENTIFICAÇÃO)** — as células da direita estão vazias:

| Rótulo (esquerda, já existe) | O que colocar (direita, vazio) |
|---|---|
| Título do Projeto ou Proposta (se houver): | título curto do lab |
| Disciplina: | `Sistemas Operacionais - CC4SO` ou `Redes de Computadores - CC4RC` |
| Estudante: | `Eduardo Andrei Staudt` |
| RA: | `2783045` |

**Caixas de texto das seções** — cada uma tem hoje um texto-guia em itálico que deve
ser **substituído** pelo conteúdo real. Os textos-guia a procurar e trocar:

- Seção 2: "Introdução: Situa o leitor sobre o assunto a ser exposto."
- Seção 3: "Mostra, de forma clara, a finalidade do referido projeto ou relatório.
  Descreve o que se espera com a realização do experimento"
- Seção 5: "Descrição sucinta dos softwares utilizados para os procedimentos ."
- Seção 6: "Descrição dos dados colhidos na experiência, com as tabelas e/ou gráficos
  e captura dos resultados."
- Seção 7: "Problemas ocorridos durante o processo de execução do experimento"
- Seção 8: "Caso você utilize alguma informação externa, cite-a fonte aqui"

**Imagem de exemplo na seção 6:** o template traz uma imagem de topologia de exemplo
(`word/media/image2.png`) dentro da caixa da seção 6. Remova essa imagem de exemplo
quando for preencher, ela não faz parte do relatório do Eduardo.

## Imagens do Eduardo

- Entram centralizadas, encaixadas no lugar do passo que ilustram (quase sempre na
  seção 6, entre uma frase e a próxima).
- Se ainda não tiver os prints, deixe `[IMAGEM: descrição do que printar]` centralizado
  no ponto certo e liste no fim o que ele precisa capturar.

## Nome do arquivo

Salve sempre como `LAB{X}-EduardoAndreiStaudt-2783045.docx`, onde `{X}` é o número do
lab que o Eduardo passou. Coloque em `/mnt/user-data/outputs/` e entregue com
`present_files`.
