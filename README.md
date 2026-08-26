# 🤖 Central de Comando Robótica por Gestos

> **Protótipo experimental de visão computacional para controle de uma central robótica por gestos, desenvolvido para rodar em dispositivos Android com Termux e hardware de recursos limitados.**

---

## 📌 Visão geral

Este projeto é um **protótipo de uma central de comando robótica controlada por gestos humanos**.

A ideia principal é permitir que uma pessoa interaja com um robô utilizando movimentos das mãos como comandos.

Por exemplo:

| Gesto              | Comando     |
| ------------------ | ----------- |
| ✊ Punho fechado    | `FIST`      |
| 🖐️ Mão aberta     | `OPEN_PALM` |
| ❓ Gesto indefinido | `UNKNOWN`   |

O projeto atualmente possui uma arquitetura composta por três partes principais:

```text
┌─────────────────────────────┐
│        USUÁRIO              │
│                             │
│       ✊   🖐️               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       CÂMERA ANDROID        │
│                             │
│   termux-camera-photo       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       PYTHON / VISÃO        │
│                             │
│ detector_gesto.py           │
│                             │
│ • segmentação de pele      │
│ • máscara                   │
│ • componentes conectados    │
│ • convex hull               │
│ • simplificação             │
│ • perfil radial             │
│ • classificação             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       ROBOT.HTML            │
│                             │
│ Interface visual            │
│ Olhos                       │
│ Boca                        │
│ Status                      │
│ Gesto detectado             │
└─────────────────────────────┘
```

A comunicação entre Python e a interface HTML ocorre através de comandos JavaScript enviados ao WebView.

---

# 🎯 Objetivo do projeto

O objetivo final não é simplesmente reconhecer uma fotografia de uma mão.

O objetivo é construir uma **central de comando por gestos**, onde o usuário possa interagir com um sistema robótico de maneira natural.

A visão de longo prazo é:

```text
                 USUÁRIO
                    │
                    ▼
              ┌───────────┐
              │   CÂMERA  │
              └─────┬─────┘
                    │
                    ▼
          ┌───────────────────┐
          │ VISÃO COMPUTACIONAL│
          └─────────┬─────────┘
                    │
             gesto reconhecido
                    │
                    ▼
          ┌───────────────────┐
          │ INTERPRETADOR     │
          │ DE COMANDOS       │
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ CENTRAL ROBÓTICA  │
          └─────────┬─────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       MOTORES             ATUADORES
```

A câmera deve funcionar continuamente e o sistema deve interpretar os movimentos sem exigir que o usuário tire uma foto a cada comando.

---

# ⚠️ Estado atual do projeto

## Protótipo — captura por fotografia

A implementação atual utiliza:

```text
Câmera
   ↓
Fotografia
   ↓
robot_foto.jpg
   ↓
Processamento
   ↓
Reconhecimento
   ↓
Comando
   ↓
Interface do robô
```

Portanto, **o sistema atual não é ainda um reconhecedor contínuo de vídeo**.

Isso é intencional.

A captura por fotografia foi utilizada como uma etapa intermediária para validar toda a cadeia de processamento antes de enfrentar o problema mais complexo de processamento contínuo de vídeo no Android.

O objetivo desta versão foi provar que é possível executar:

* captura da câmera;
* processamento de imagem;
* segmentação da mão;
* geração de máscara;
* extração geométrica;
* classificação do gesto;
* comunicação Python → JavaScript;
* atualização da interface do robô;

sem depender de bibliotecas pesadas de visão computacional.

---

# 🚧 Limitação atual: vídeo em tempo real

A principal limitação do protótipo atual é que a câmera é utilizada através do comando:

```bash
termux-camera-photo
```

Esse mecanismo captura uma fotografia individual.

Ele não fornece diretamente um fluxo contínuo de frames como:

```text
FRAME 1
FRAME 2
FRAME 3
FRAME 4
FRAME 5
...
```

Para uma central de comando por gestos realmente natural, o funcionamento desejado é:

```text
CÂMERA
  │
  ├── FRAME
  ├── FRAME
  ├── FRAME
  ├── FRAME
  ├── FRAME
  └── FRAME
       │
       ▼
   DETECTOR
       │
       ▼
    GESTO
       │
       ▼
    COMANDO
```

Assim, o usuário poderia simplesmente colocar a mão diante da câmera e realizar um gesto.

Por exemplo:

```text
Usuário:

        ✊

        ↓

Sistema detecta:

        FIST

        ↓

Central:

        COMANDO FIST
```

Sem necessidade de tirar uma fotografia manualmente.

---

# 🧠 Por que não foi utilizado MediaPipe?

A primeira abordagem considerada foi utilizar soluções prontas de reconhecimento de mãos, como MediaPipe Hand Landmarker / Gesture Recognizer.

Entretanto, o ambiente alvo possui restrições importantes.

O projeto foi desenvolvido para:

```text
Android
   +
Termux
   +
ARMv7 / armeabi-v7a
   +
Python 3.14
   +
hardware limitado
```

Durante os testes, a instalação do MediaPipe não apresentou uma distribuição compatível com o ambiente:

```bash
python -m pip install mediapipe
```

O resultado foi:

```text
No matching distribution found for mediapipe
```

A compilação manual também não foi considerada adequada para o dispositivo alvo devido ao custo computacional e à complexidade da dependência.

Portanto, foi adotada uma abordagem diferente:

> **Construir manualmente uma pequena pipeline de visão computacional utilizando Python e ferramentas disponíveis no Termux.**

---

# 💡 Filosofia da solução

A ideia deste projeto é evitar a dependência de grandes frameworks quando o problema pode ser resolvido com algoritmos relativamente simples.

Em vez de:

```text
Camera
  ↓
OpenCV
  ↓
MediaPipe
  ↓
Neural Network
  ↓
Gesture
```

o protótipo utiliza:

```text
Camera
  ↓
Imagem
  ↓
ImageMagick
  ↓
RGB
  ↓
Segmentação
  ↓
Máscara
  ↓
Componentes
  ↓
Geometria
  ↓
Perfil radial
  ↓
Gesture
```

Isso permite que o projeto seja:

* leve;
* transparente;
* modificável;
* fácil de depurar;
* adequado para hardware limitado;
* independente de frameworks pesados.

---

# 🏗️ Arquitetura

A arquitetura atual possui os seguintes componentes.

```text
robot.py
   │
   ├── câmera
   │
   ├── Termux Camera
   │
   ├── captura
   │
   ├── WebView
   │
   └── eventos
        │
        ▼
detector_gesto.py
        │
        ├── ImageMagick
        ├── segmentação
        ├── máscara
        ├── componentes
        ├── convex hull
        ├── Douglas-Peucker
        └── classificação
                │
                ▼
          FIST / OPEN_PALM / UNKNOWN
                │
                ▼
             robot.html
```

---

# 📂 Estrutura do projeto

A estrutura básica é:

```text
~/opt/

├── robot.py
├── robot.html
├── detector_gesto.py
│
├── robot_foto.jpg
│
├── gesto_mascara.png
├── gesto_detectado.png
│
├── gesto_fist.jpg
└── gesto_open_palm.jpg
```

## Arquivos principais

### `robot.py`

Responsável pela aplicação principal.

Funções principais:

* localizar a câmera frontal;
* capturar fotografia;
* criar WebView;
* carregar `robot.html`;
* receber eventos de toque;
* executar a sequência de reconhecimento;
* chamar `detector_gesto.py`;
* enviar comandos para JavaScript.

---

### `robot.html`

Responsável pela interface visual do robô.

Atualmente apresenta:

* rosto;
* olhos;
* boca;
* status;
* gesto detectado;
* animação de piscar;
* abertura e fechamento dos olhos.

A comunicação é feita através da função:

```javascript
window.robotEvent()
```

---

### `detector_gesto.py`

É o núcleo da visão computacional.

Ele recebe:

```text
robot_foto.jpg
```

e produz:

```text
FIST
OPEN_PALM
UNKNOWN
```

Também produz imagens de depuração:

```text
gesto_mascara.png
gesto_detectado.png
```

---

# 📦 Dependências

Uma das características importantes deste projeto é a quantidade extremamente pequena de dependências.

## Python

Utiliza principalmente:

```text
Python 3.14
```

e módulos da biblioteca padrão.

---

## Termux

É necessário possuir:

```text
Termux
```

e acesso ao gerenciador de pacotes:

```bash
pkg
```

---

## Termux Camera

Instalação:

```bash
pkg install termux-camera
```

---

## ImageMagick

Instalação:

```bash
pkg install imagemagick
```

O ImageMagick é utilizado para operações de imagem que seriam normalmente executadas por bibliotecas como OpenCV.

---

# 📷 Câmera

A câmera frontal é identificada automaticamente.

O projeto executa:

```bash
termux-camera-info
```

O comando retorna informações sobre as câmeras disponíveis.

O Python procura:

```json
"facing": "front"
```

Quando encontra uma câmera frontal, seu ID é utilizado na captura.

Exemplo:

```bash
termux-camera-photo -c 1 robot_foto.jpg
```

---

# 🔬 Pipeline de reconhecimento

O detector implementa uma pipeline de visão computacional composta por várias etapas.

---

## 1. Redimensionamento

A imagem original é reduzida para uma resolução máxima de aproximadamente:

```text
320 × 320
```

Isso reduz drasticamente o custo de processamento.

Para um dispositivo limitado, processar uma imagem de:

```text
1920 × 1080
```

seria desnecessário para o objetivo do protótipo.

A ideia é trabalhar com uma representação suficientemente pequena para identificar a geometria geral da mão.

---

# 🖐️ 2. Segmentação da pele

O detector analisa os pixels da imagem.

Uma heurística baseada em RGB procura regiões compatíveis com tons de pele.

A ideia geral é identificar pixels nos quais:

```text
R ≥ G ≥ B
```

com valores mínimos adequados.

Também são considerados critérios relacionados à intensidade e saturação.

O objetivo não é determinar precisamente a cor da pele.

O objetivo é encontrar uma região aproximadamente correspondente à mão.

---

# 🎭 3. Máscara binária

Depois da segmentação, a imagem é transformada em uma máscara:

```text
1 = possível pele
0 = fundo
```

Visualmente:

```text
████████████████████
██████      ████████
████   ████   █████
███   ██████    ███
██    ███████    ██
██      ███      ██
████████████████████
```

A região correspondente à mão permanece.

O restante é descartado.

Essa máscara é salva como:

```text
gesto_mascara.png
```

---

# 🧹 4. Remoção de ruído

A segmentação por cor naturalmente pode produzir pequenos pontos incorretos.

Por exemplo:

```text
•        •
       •
   ███████
   ███████
        •
```

Por isso, o detector utiliza componentes conectados.

Componentes muito pequenos são descartados.

O limite utilizado atualmente é aproximadamente:

```text
80 pixels
```

---

# 🧩 5. Componentes conectados

A máscara é analisada utilizando uma busca em largura (BFS).

O algoritmo agrupa pixels adjacentes.

Cada agrupamento representa um componente.

Exemplo:

```text
████████       ██

████████       ██

████████

                     █

        ███
```

O algoritmo identifica cada região separadamente.

---

# 🎯 6. Seleção do candidato principal

Nem toda região de pele representa a mão.

Pode existir:

* rosto;
* braço;
* dedos isolados;
* ruído;
* outras regiões.

Por isso, cada componente recebe uma pontuação heurística.

São considerados fatores como:

* área;
* posição horizontal;
* posição vertical;
* proximidade do centro;
* distância das bordas;
* posição inferior da imagem.

A região mais compatível com uma mão recebe a maior pontuação.

---

# 🧱 7. União de componentes próximos

A segmentação pode separar partes da mesma mão.

Isso pode acontecer devido a:

* sombra;
* iluminação;
* dobras;
* pequenas falhas de segmentação;
* diferença de tonalidade entre regiões.

O detector pode unir componentes próximos.

Atualmente é considerada uma distância aproximada de:

```text
55 pixels
```

---

# 📐 8. Convex Hull

Depois de encontrar os pontos da mão, o detector calcula o:

```text
Convex Hull
```

O convex hull cria um polígono envolvendo a região detectada.

Conceitualmente:

```text
        •
      /   \
     •     •
    /       \
   •         •
    \       /
     •-----•
```

Isso fornece uma representação geométrica simples da mão.

---

# ✏️ 9. Simplificação do polígono

O convex hull pode conter muitos pontos.

Para reduzir a complexidade, é utilizado um algoritmo baseado em:

```text
Douglas-Peucker
```

O objetivo é transformar:

```text
• • • • • • • • • • •
```

em algo mais próximo de:

```text
•──────•──────•
 \            /
  •──────────•
```

mantendo a forma geral.

---

# 📊 10. Perfil radial

Esta é uma das partes mais importantes do classificador.

O centro aproximado da mão é utilizado como referência.

A partir dele, o algoritmo analisa a distância até a borda em várias direções.

São utilizados aproximadamente:

```text
72 bins
```

correspondentes a:

```text
360° / 72 = 5°
```

por direção.

Conceitualmente:

```text
             ↑
        ↖    │    ↗
          \  │  /
           \ │ /
←───────────●──────────→
           /│\
          / │ \
        ↙   │   ↘
             ↓
```

O resultado é um perfil radial da mão.

---

# 🖐️ Identificação da mão aberta

Uma mão aberta tende a apresentar várias protuberâncias.

Exemplo conceitual:

```text
       /\   /\   /\
      /  \ /  \ /  \
     /              \
    /                \
   |                  |
   |       PALMA      |
    \                /
     \______________/
```

Os dedos produzem vários picos no perfil radial.

---

# ✊ Identificação do punho

Um punho fechado tende a possuir uma geometria mais compacta:

```text
       ______
     /        \
    /          \
   |            |
   |    FIST    |
    \          /
     \________/
```

O perfil radial apresenta menos protuberâncias significativas.

---

# 🔢 Classificação atual

O perfil radial é suavizado e os picos são contabilizados.

A regra atual é aproximadamente:

```text
picos <= 3
    ↓
FIST
```

e:

```text
picos >= 4
    ↓
OPEN_PALM
```

Caso a geometria não seja suficientemente clara:

```text
UNKNOWN
```

---

# 🖼️ Sistema de depuração

O sistema gera duas imagens extremamente importantes.

## Máscara

```text
gesto_mascara.png
```

Mostra o resultado da segmentação.

Serve para responder:

> O sistema realmente encontrou a mão?

---

## Detecção

```text
gesto_detectado.png
```

Mostra a imagem original com a geometria detectada.

O arquivo pode apresentar:

* polígono;
* região detectada;
* gesto;
* número de vértices;
* quantidade de picos.

Isso permite analisar o algoritmo visualmente.

---

# 🔎 Como testar a máscara

No Termux:

```bash
termux-open gesto_mascara.png
```

---

# 🔎 Como testar a detecção

```bash
termux-open gesto_detectado.png
```

---

# 🧪 Testando o detector isoladamente

Execute:

```bash
python detector_gesto.py
```

O programa processará:

```text
robot_foto.jpg
```

e deverá retornar algo semelhante a:

```text
FIST
```

ou:

```text
OPEN_PALM
```

ou:

```text
UNKNOWN
```

---

# 📸 Fluxo completo atual

Quando o usuário toca na interface:

```text
TOUCH
  ↓
Python recebe evento
  ↓
PREPARANDO
  ↓
FECHANDO_OLHOS
  ↓
CLOSE_EYES
  ↓
PROCURANDO_CAMERA
  ↓
TIRANDO_FOTO
  ↓
termux-camera-photo
  ↓
robot_foto.jpg
  ↓
ANALISANDO_FOTO
  ↓
PENSANDO
  ↓
detector_gesto.py
  ↓
GESTO_DETECTADO
  ↓
FIST / OPEN_PALM / UNKNOWN
  ↓
Python → JavaScript
  ↓
robotEvent()
  ↓
interface atualizada
  ↓
DOUBLE_BLINK
  ↓
CONCLUIDO
```

---

# 🤖 Interface do robô

O arquivo `robot.html` funciona como uma camada visual.

O Python não precisa conhecer os detalhes da interface.

Ele simplesmente envia eventos.

Por exemplo:

```text
ACTION:PREPARANDO
```

```text
ACTION:PENSANDO
```

```text
ACTION:CONCLUIDO
```

ou o resultado:

```text
FIST
```

```text
OPEN_PALM
```

```text
UNKNOWN
```

O JavaScript interpreta esses comandos.

---

# 🔌 Comunicação Python → JavaScript

A comunicação principal é realizada através de:

```javascript
window.robotEvent(command)
```

O Python envia:

```javascript
window.robotEvent('FIST');
```

A interface recebe:

```text
FIST
```

e apresenta:

```text
✊ PUNHO DETECTADO
```

Para:

```text
OPEN_PALM
```

apresenta:

```text
🖐 MÃO ABERTA DETECTADA
```

E para:

```text
UNKNOWN
```

apresenta:

```text
❓ GESTO NÃO RECONHECIDO
```

---

# 👁️ Estados visuais

A interface possui comandos especiais para controlar os olhos.

## Fechar olhos

```text
CLOSE_EYES
```

## Abrir olhos

```text
OPEN_EYES
```

## Piscar

```text
BLINK
```

## Piscar duas vezes

```text
DOUBLE_BLINK
```

Esses eventos permitem que o reconhecimento não seja apenas uma saída textual.

O robô também pode **expressar visualmente seu estado**.

---

# 🔄 Conceito de máquina de estados

O fluxo atual pode ser interpretado como uma máquina de estados:

```text
                 ┌─────────────┐
                 │   PRONTO    │
                 └──────┬──────┘
                        │
                      TOUCH
                        │
                        ▼
                 ┌─────────────┐
                 │ PREPARANDO  │
                 └──────┬──────┘
                        ▼
                 ┌─────────────┐
                 │   CÂMERA    │
                 └──────┬──────┘
                        ▼
                 ┌─────────────┐
                 │  ANALISANDO │
                 └──────┬──────┘
                        ▼
                 ┌─────────────┐
                 │  PENSANDO   │
                 └──────┬──────┘
                        ▼
                 ┌─────────────┐
                 │   GESTO     │
                 └──────┬──────┘
                        ▼
                 ┌─────────────┐
                 │ CONCLUÍDO   │
                 └─────────────┘
```

Essa estrutura será especialmente importante na futura versão de vídeo.

---

# 🚀 Evolução planejada: vídeo em tempo real

A próxima grande evolução do projeto é substituir:

```text
FOTO
```

por:

```text
STREAM DE VÍDEO
```

A arquitetura desejada é:

```text
             CÂMERA
                │
                ▼
        ┌───────────────┐
        │ STREAM VIDEO  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ FRAME 1       │
        │ FRAME 2       │
        │ FRAME 3       │
        │ FRAME 4       │
        └───────┬───────┘
                │
                ▼
       ┌──────────────────┐
       │ DETECTOR         │
       │                  │
       │ pele             │
       │ máscara          │
       │ componentes      │
       │ geometria        │
       └────────┬─────────┘
                │
                ▼
        ┌───────────────┐
        │ CLASSIFICADOR │
        └───────┬───────┘
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
     FIST   OPEN_PALM  UNKNOWN
       │        │
       └────────┴─────────┐
                         ▼
                 CENTRAL DE COMANDO
```

---

# ⚡ Por que vídeo é diferente?

Processar uma fotografia é relativamente simples:

```text
captura
   ↓
processamento
   ↓
resultado
```

Vídeo exige repetir isso continuamente:

```text
frame
 ↓
processa
 ↓
frame
 ↓
processa
 ↓
frame
 ↓
processa
 ↓
...
```

Em um dispositivo limitado, isso cria novos desafios:

* CPU;
* memória;
* velocidade da câmera;
* transferência dos frames;
* conversão de formatos;
* latência;
* consumo de bateria;
* temperatura;
* estabilidade;
* frequência de processamento.

Por isso, o projeto utiliza a fotografia como uma **etapa de validação arquitetural** antes da implementação de vídeo.

---

# 🧠 Futuro processamento por vídeo

Uma possível estratégia é não processar todos os frames.

Por exemplo:

```text
Câmera: 30 FPS

Processamento:

FRAME 1   → processa
FRAME 2   → ignora
FRAME 3   → ignora
FRAME 4   → processa
FRAME 5   → ignora
FRAME 6   → ignora
...
```

Isso poderia reduzir bastante o consumo.

Outra possibilidade:

```text
30 FPS da câmera
       ↓
detector executa
       ↓
5–10 FPS efetivos
```

Para reconhecimento de gestos humanos, isso pode ser suficiente dependendo da velocidade do movimento.

---

# 🧩 Estabilização do gesto

No vídeo, um único frame não deveria necessariamente disparar um comando.

Por exemplo:

```text
FRAME 1 → FIST
FRAME 2 → UNKNOWN
FRAME 3 → FIST
FRAME 4 → FIST
FRAME 5 → FIST
```

O sistema poderia interpretar:

```text
FIST
FIST
FIST
```

como um gesto confirmado.

Uma futura lógica poderia utilizar:

```text
janela temporal
        ↓
vários frames
        ↓
votação
        ↓
gesto confirmado
```

Por exemplo:

```text
Últimos 5 frames:

FIST
FIST
FIST
UNKNOWN
FIST

Resultado:

FIST
```

Isso evitaria comandos falsos.

---

# 🛡️ Anti-disparo de comandos

Uma central de comando não deve executar uma ação toda vez que um frame reconhecer o mesmo gesto.

Sem proteção:

```text
FIST
FIST
FIST
FIST
FIST
FIST
```

poderia gerar:

```text
COMANDO
COMANDO
COMANDO
COMANDO
COMANDO
COMANDO
```

Uma versão futura deverá possuir um mecanismo de estado:

```text
FIST detectado
      ↓
confirmação
      ↓
comando executado
      ↓
aguarda saída do gesto
      ↓
permite novo comando
```

Isso transforma o reconhecimento visual em um verdadeiro sistema de controle.

---

# 🎮 Expansão para comandos

Atualmente existem:

```text
FIST
OPEN_PALM
UNKNOWN
```

Mas a arquitetura permite adicionar novos gestos.

Exemplo:

```text
✊ FIST
   ↓
PARAR

🖐 OPEN_PALM
   ↓
ATIVAR

✌ VICTORY
   ↓
MODO 2

☝ ONE
   ↓
SELECIONAR

🤏 PINCH
   ↓
CONFIRMAR
```

Uma futura central poderia transformar os gestos em comandos abstratos:

```text
GESTO
  ↓
INTERPRETADOR
  ↓
COMANDO
  ↓
ROBÔ
```

Isso permite separar reconhecimento de visão e controle robótico.

---

# 🏭 Arquitetura futura recomendada

Uma arquitetura mais completa poderia ser:

```text
                   CÂMERA
                      │
                      ▼
              ┌───────────────┐
              │ FRAME CAPTURE │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ PREPROCESSING │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ HAND DETECTOR │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ CLASSIFIER    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ GESTURE FSM   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ COMMAND BUS   │
              └───────┬───────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
        ROBOT UI          ROBOT CONTROL
```

---

# 🧪 Calibração

A segmentação de pele depende bastante das condições ambientais.

Os principais fatores são:

* iluminação;
* temperatura da luz;
* sombra;
* câmera;
* distância;
* exposição automática;
* tonalidade da pele;
* fundo.

Um ambiente:

```text
luz branca
```

pode gerar um resultado diferente de:

```text
luz amarela
```

ou:

```text
luz azul
```

---

# 🎛️ Parâmetros importantes

Alguns parâmetros devem ser considerados pontos de calibração.

### Resolução

```text
320 × 320
```

### Área mínima

```text
80 pixels
```

### Distância de união

```text
55 pixels
```

### Região superior

A parte superior da imagem é parcialmente desconsiderada para reduzir a possibilidade de confundir o rosto com a mão.

### Perfil radial

```text
72 bins
```

### Resolução angular

```text
5°
```

### Classificação

```text
≤ 3 picos → FIST

≥ 4 picos → OPEN_PALM
```

Esses valores não são constantes universais.

São parâmetros experimentais do protótipo.

---

# 🧪 Imagens de referência

Durante o desenvolvimento foram utilizadas imagens de referência:

```text
gesto_fist.jpg
gesto_open_palm.jpg
```

Elas podem ser criadas com:

```bash
cp robot_foto.jpg gesto_fist.jpg
```

e:

```bash
cp robot_foto.jpg gesto_open_palm.jpg
```

Entretanto, é importante destacar que:

> **A versão final do detector descrita neste projeto não depende diretamente dessas imagens para classificar o gesto.**

O classificador atual utiliza geometria e perfil radial.

As imagens de referência permanecem úteis para testes, documentação e futuras estratégias de calibração.

---

# ➕ Adicionando novos gestos

Para adicionar um novo gesto, por exemplo:

```text
VITORIA
```

pode-se criar:

```text
gesto_vitoria.jpg
```

com:

```bash
cp robot_foto.jpg gesto_vitoria.jpg
```

Depois é necessário adicionar uma estratégia de classificação correspondente.

Uma futura versão pode utilizar características como:

```text
número de picos
distância média
área
perímetro
relação altura/largura
circularidade
convexidade
ângulos
```

Isso permitiria diferenciar mais gestos sem depender de redes neurais pesadas.

---

# 📱 Ambiente alvo

O projeto foi pensado especificamente para ambientes restritos.

Exemplo:

```text
Android
├── Termux
├── Python
├── ImageMagick
└── Termux:API / Termux Camera
```

A filosofia é:

> **Fazer o máximo possível com o mínimo de dependências.**

Isso é especialmente importante quando o dispositivo possui:

* pouca RAM;
* CPU limitada;
* arquitetura ARMv7;
* pouca capacidade térmica;
* armazenamento limitado.

---

# 🚫 Dependências que o projeto evita

A solução atual não depende de:

```text
OpenCV
MediaPipe
TensorFlow
PyTorch
NumPy
CUDA
GPU
```

Isso não significa que essas tecnologias sejam ruins.

Pelo contrário: elas podem oferecer resultados muito superiores em hardware adequado.

A escolha aqui é uma consequência direta do ambiente alvo.

---

# 🧠 Possível evolução para TinyML / ML

Existe também uma possível evolução intermediária.

Em vez de utilizar apenas heurísticas:

```text
Imagem
 ↓
Geometria
 ↓
Regras
```

poderia ser utilizado um pequeno modelo:

```text
Imagem
 ↓
Pré-processamento
 ↓
Características
 ↓
TinyML
 ↓
Gesto
```

Uma arquitetura híbrida também seria possível:

```text
Segmentação manual
       ↓
Extração geométrica
       ↓
TinyML
       ↓
Classificação
```

Isso poderia oferecer maior robustez mantendo o custo computacional relativamente baixo.

---

# 🔐 Princípio de funcionamento local

O processamento atual foi pensado para ocorrer localmente no dispositivo.

A fotografia:

```text
robot_foto.jpg
```

é processada pelo próprio ambiente Python/Termux.

Não é necessário enviar a imagem para um servidor externo para realizar a classificação.

Isso é particularmente interessante para uma central robótica que precise funcionar:

* offline;
* em ambientes isolados;
* sem internet;
* com baixa latência;
* sem depender de serviços externos.

---

# ⚙️ Instalação

## 1. Instalar Termux

Instale um ambiente Termux compatível com o dispositivo.

---

## 2. Instalar câmera

```bash
pkg install termux-camera
```

---

## 3. Instalar ImageMagick

```bash
pkg install imagemagick
```

---

## 4. Verificar câmeras

```bash
termux-camera-info
```

Deve aparecer algo semelhante a:

```json
[
    {
        "id": "0",
        "facing": "back"
    },
    {
        "id": "1",
        "facing": "front"
    }
]
```

---

## 5. Testar captura

```bash
termux-camera-photo -c 1 robot_foto.jpg
```

Verifique:

```bash
ls -lh robot_foto.jpg
```

---

## 6. Executar detector

```bash
python detector_gesto.py
```

---

## 7. Executar central

```bash
python robot.py
```

---

# 🐞 Depuração

Quando algo não funcionar, a primeira etapa deve ser descobrir qual camada apresentou problema.

## Câmera

```bash
termux-camera-info
```

Depois:

```bash
termux-camera-photo -c 1 robot_foto.jpg
```

---

## Imagem

Verifique:

```bash
ls -lh robot_foto.jpg
```

---

## Máscara

Abra:

```bash
termux-open gesto_mascara.png
```

Se a mão não aparecer corretamente na máscara, o problema provavelmente está na segmentação.

---

## Polígono

Abra:

```bash
termux-open gesto_detectado.png
```

Se a máscara estiver correta, mas o polígono estiver errado, o problema provavelmente está na extração geométrica.

---

## Classificação

Se o polígono estiver correto, mas:

```text
FIST
```

for confundido com:

```text
OPEN_PALM
```

o problema provavelmente está nos parâmetros do perfil radial.

---

# 🔍 Diagnóstico por camadas

Uma forma prática de depurar é:

```text
CÂMERA
  │
  ├── falhou?
  │      ↓
  │   Termux Camera
  │
  ▼
IMAGEM
  │
  ├── existe?
  │
  ▼
MÁSCARA
  │
  ├── mão aparece?
  │
  ▼
COMPONENTE
  │
  ├── região correta?
  │
  ▼
POLÍGONO
  │
  ├── geometria correta?
  │
  ▼
PICOS
  │
  ├── quantidade correta?
  │
  ▼
GESTO
```

Isso evita tentar alterar o classificador quando, na verdade, o problema está na câmera ou na segmentação.

---

# ⚠️ Limitações conhecidas

O protótipo possui limitações importantes.

## Iluminação

A segmentação baseada em RGB é sensível à iluminação.

---

## Fundo

Cores semelhantes à pele podem ser classificadas incorretamente.

---

## Posicionamento

O algoritmo atualmente assume que a mão está aproximadamente:

```text
centralizada horizontalmente
```

e:

```text
na região inferior da imagem
```

---

## Oclusão

Mãos parcialmente escondidas podem produzir uma geometria incorreta.

---

## Distância

Uma mão muito distante pode ocupar poucos pixels.

Uma mão muito próxima pode sair parcialmente do enquadramento.

---

## Orientação

A classificação pode variar conforme:

* rotação;
* inclinação;
* posição;
* perspectiva.

---

## Vídeo

A versão atual não possui processamento contínuo de vídeo.

Esse é o principal ponto de evolução.

---

# 🧪 O que este protótipo já prova

Apesar das limitações, o projeto demonstra vários conceitos importantes.

### 1. Captura

É possível capturar imagens da câmera Android através do Termux.

### 2. Processamento

É possível processar a imagem sem OpenCV.

### 3. Segmentação

É possível isolar aproximadamente a mão utilizando regras simples.

### 4. Geometria

É possível extrair uma representação geométrica da mão.

### 5. Classificação

É possível diferenciar pelo menos dois estados:

```text
FIST
OPEN_PALM
```

### 6. Interface

É possível construir uma interface robótica usando HTML.

### 7. Integração

Python consegue controlar a interface através de JavaScript.

---

# 🤖 A verdadeira finalidade do projeto

Este projeto não deve ser interpretado apenas como:

> "um programa que identifica se uma foto contém uma mão fechada ou aberta."

Essa é apenas a primeira prova de conceito.

A finalidade maior é criar uma arquitetura para uma:

# 🧠 CENTRAL DE COMANDO POR GESTOS

onde o gesto humano seja convertido em uma ação do sistema.

Por exemplo:

```text
                 HUMANO
                    │
                    ▼
              MOVIMENTO
                    │
                    ▼
                 CÂMERA
                    │
                    ▼
            VISÃO COMPUTACIONAL
                    │
                    ▼
                 GESTO
                    │
                    ▼
           INTERPRETADOR
                    │
                    ▼
                COMANDO
                    │
             ┌──────┴──────┐
             ▼             ▼
          ROBÔ          INTERFACE
```

---

# 🌐 Visão de produto futuro

Uma versão madura poderia possuir uma interface semelhante a uma central de controle.

Por exemplo:

```text
┌──────────────────────────────────┐
│          ROBOT CONTROL           │
├──────────────────────────────────┤
│                                  │
│             🤖                   │
│                                  │
│       STATUS: ATIVO              │
│                                  │
│       GESTO: OPEN_PALM           │
│                                  │
│       COMANDO: ENABLE            │
│                                  │
├──────────────────────────────────┤
│ CAMERA: ONLINE                   │
│ DETECTOR: ONLINE                 │
│ LATÊNCIA: 85 ms                  │
│ FPS: 8                           │
└──────────────────────────────────┘
```

A interface HTML poderia evoluir para representar:

* estado do robô;
* comandos;
* sensores;
* câmera;
* reconhecimento;
* alertas;
* telemetria;
* ações;
* histórico.

---

# 🗺️ Roadmap

## Fase 1 — Protótipo atual

* [x] Termux
* [x] Python
* [x] Captura frontal
* [x] Imagem estática
* [x] Segmentação de pele
* [x] Máscara
* [x] Componentes conectados
* [x] Convex hull
* [x] Simplificação geométrica
* [x] Perfil radial
* [x] FIST
* [x] OPEN_PALM
* [x] UNKNOWN
* [x] Imagens de debug
* [x] Interface HTML
* [x] WebView
* [x] Comunicação Python → JavaScript

---

## Fase 2 — Reconhecimento temporal

* [ ] Captura contínua
* [ ] Processamento de frames
* [ ] Controle de FPS
* [ ] Buffer temporal
* [ ] Votação entre frames
* [ ] Estabilização do gesto
* [ ] Anti-repetição de comandos

---

## Fase 3 — Vídeo

* [ ] Stream de câmera
* [ ] Processamento contínuo
* [ ] Otimização de CPU
* [ ] Redução de resolução
* [ ] Controle de frequência
* [ ] Monitoramento de latência

---

## Fase 4 — Mais gestos

* [ ] VICTORY
* [ ] ONE
* [ ] TWO
* [ ] THUMBS_UP
* [ ] THUMBS_DOWN
* [ ] PINCH
* [ ] Outros gestos personalizados

---

## Fase 5 — Central de comando

* [ ] Mapeamento gesto → comando
* [ ] Máquina de estados
* [ ] Confirmação de comandos
* [ ] Histórico
* [ ] Telemetria
* [ ] Estados do robô
* [ ] Interface avançada

---

## Fase 6 — TinyML opcional

* [ ] Dataset
* [ ] Extração de características
* [ ] Treinamento
* [ ] Modelo pequeno
* [ ] Inferência local
* [ ] Comparação heurística × ML

---

# 🧭 Princípio de desenvolvimento

O projeto segue uma estratégia incremental.

Em vez de tentar construir imediatamente:

```text
vídeo
+
IA
+
robô
+
interface
+
controle
```

a implementação começa com uma cadeia mínima funcional:

```text
FOTO
 ↓
MÁSCARA
 ↓
GEOMETRIA
 ↓
GESTO
 ↓
INTERFACE
```

Depois essa cadeia poderá evoluir para:

```text
VÍDEO
 ↓
FRAMES
 ↓
MÁSCARA
 ↓
GEOMETRIA
 ↓
GESTO
 ↓
ESTABILIZAÇÃO
 ↓
COMANDO
 ↓
ROBÔ
```

Isso permite validar cada etapa individualmente.

---

# 🏁 Conclusão

Este projeto é um **protótipo de uma futura central de comando robótica baseada em gestos**.

A implementação atual deliberadamente utiliza fotografia porque a captura contínua de vídeo representa uma etapa técnica diferente e mais exigente no ambiente Android/Termux utilizado.

A fotografia não é o objetivo final.

Ela é uma ferramenta de desenvolvimento utilizada para validar a cadeia completa:

```text
CÂMERA
  ↓
IMAGEM
  ↓
SEGMENTAÇÃO
  ↓
MÁSCARA
  ↓
MÃO
  ↓
GEOMETRIA
  ↓
CLASSIFICAÇÃO
  ↓
GESTO
  ↓
JAVASCRIPT
  ↓
ROBÔ
```

O próximo passo natural é transformar:

```text
robot_foto.jpg
```

em um fluxo contínuo de frames.

A partir daí, o projeto poderá evoluir de um simples detector de gestos para uma verdadeira **interface homem-máquina baseada em visão computacional**, capaz de interpretar movimentos em tempo real e transformá-los em comandos para uma central robótica.

A arquitetura foi mantida simples propositalmente para que seja possível executar o máximo de processamento localmente, mesmo em dispositivos Android de baixo consumo e sem depender de frameworks pesados.

---

# 📜 Licença

Este projeto pode ser utilizado como base experimental, educacional e de pesquisa.

Antes de utilizar o sistema para controlar equipamentos físicos, motores ou atuadores reais, recomenda-se implementar mecanismos adicionais de segurança, confirmação e tratamento de falhas.

---

# 🤝 Contribuições

Possíveis áreas de contribuição:

* otimização da segmentação;
* melhoria do detector de mãos;
* novos classificadores;
* novos gestos;
* processamento por vídeo;
* redução de consumo de CPU;
* estabilização temporal;
* TinyML;
* interface da central;
* integração com robôs;
* comunicação com sensores;
* telemetria.

---

# ⭐ Status

```text
PROJETO: Central de Comando por Gestos
VERSÃO: Protótipo
PLATAFORMA: Android + Termux
LINGUAGEM: Python + JavaScript/HTML
VISÃO: Processamento local
CLASSIFICAÇÃO: Heurística geométrica
ENTRADA ATUAL: Fotografia
ENTRADA FUTURA: Vídeo em tempo real

STATUS:

🟢 Captura
🟢 Segmentação
🟢 Máscara
🟢 Geometria
🟢 FIST
🟢 OPEN_PALM
🟢 WebView
🟢 Interface
🟡 Vídeo em tempo real
🟡 Reconhecimento temporal
🟡 Central robótica completa
```

> **Este protótipo é o primeiro estágio de uma arquitetura maior: transformar movimentos humanos em comandos para uma central robótica, utilizando visão computacional local e hardware acessível.**
