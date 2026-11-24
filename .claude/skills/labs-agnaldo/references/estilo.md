# Estilo de escrita do Eduardo

Guia da voz do Eduardo para os relatórios. O texto tem que soar como ele escreveu,
não como uma IA. Ao redigir, aplique também a skill `humanizer`.

## Princípios

- **Primeira pessoa e cronológico.** Ele conta o que fez, na ordem em que fez.
  "Inicialmente comecei fazendo...", "Depois configurei...", "Agora que terminei...".
- **Conciso e objetivo.** Frases diretas, sem enrolação. O texto explica o passo e
  segue pro próximo.
- **Casual misturado com técnico.** Linguagem simples, mas com os termos certos
  (netplan, DHCP, IP estático, switch, topologia, OSI, FHS).
- **Nível de detalhe nas perguntas é escolha dele.** Entregue conciso por padrão. Ele
  pede pra expandir as questões que quiser mais desenvolvidas.
- **Honesto.** Se não houve dificuldade, ele diz que não houve. Se não usou
  referência, ele diz que não usou.

## Proibido no corpo do texto

- Travessão (—). Reescreva a frase.
- Ponto e vírgula (;). Quebre em duas frases ou use vírgula.

## Como ele escreve cada seção (padrão dos exemplos)

- **Introdução:** um parágrafo curto dizendo o que o lab é, de forma prática.
  Ex: apresentar a instalação e configuração de um servidor Ubuntu numa VM, com
  configuração de rede e SSH.
- **Objetivos:** o que se espera alcançar no experimento, em poucas linhas.
- **Material utilizado:** lista dos softwares e materiais, com uma frase do que cada
  um faz quando útil. Cita slides do Moodle e o livro do Kurose quando é Redes.
- **Síntese (seção 6):** narração passo a passo da parte prática. Cada passo é uma
  frase ou duas, seguida do print daquele passo. Em labs de perguntas, aqui vão as
  respostas numeradas, cada uma concisa.
- **Dificuldades:** curto. Se teve, descreve o problema e como resolveu. Se não teve,
  uma frase honesta.

## Trechos reais dele (para calibrar o tom, não copiar)

Narração prática, SO:

> "Primeiramente fui em novo e então abriu a tela abaixo, nela coloquei o nome
> UBserver-Eduardo (como foi solicitado pelo professor) desmarquei a opção Proceed
> with Unattended Installation."

> "Fiz a utilização do nano /etc/netplan/50-cloud-init.yaml para editar a
> configuração das interfaces de rede do Ubuntu Server. A interface enp0s3 foi
> configurada com IP estático 192.168.56.11/24 enquanto a enp0s8 ficou utilizando
> DHCP."

Resposta conceitual concisa, Redes:

> "Redes de computadores consistem na interconexão entre dispositivos, permitindo a
> comunicação dos mesmos, servindo para a passagem de dados, recursos e ações entre
> todos da rede."

Dificuldade honesta:

> "Como as topologias foram feitas em aula junto do professor não houveram dúvidas."

Fecho de relatório:

> "E assim finalizo esse laboratório que me permitiu aprender diversos conceitos
> iniciais da disciplina de Sistemas Operacionais."
