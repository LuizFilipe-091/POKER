# 🃏 Poker Calculator

Aplicativo em Python para calcular as chances de cada combinação de poker a partir das cartas da sua mão e da mesa.

O projeto foi pensado para ser simples e visual: você escolhe as cartas, clica em calcular e o programa mostra a probabilidade percentual de cada mão possível, como par, dois pares, trinca, sequência, flush, full house, quadra e straight flush.

## ✨ Funcionalidades

- Cálculo de probabilidade para as principais combinações de poker
- Seleção visual das cartas da mão e da mesa
- Interface gráfica em Tkinter com tema moderno
- Atualização em tempo real das chances após escolher as cartas
- Fácil de entender e expandir para outras regras ou simulações

## 📌 Combinações calculadas

- Straight Flush
- Four of a Kind
- Full House
- Flush
- Straight
- Three of a Kind
- Two Pair
- Pair

## 🧰 Requisitos

Antes de rodar o projeto, certifique-se de ter instalado:

- Python 3.10 ou superior
- pip
- GTK/Tk support disponível no sistema

## 🚀 Instalação

1. Clone o projeto:

```bash
git clone <url-do-repositorio>
cd POKER
```

2. Crie um ambiente virtual:

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## ▶️ Como executar

Na raiz do projeto, rode:

```bash
python main.py
```

## 🕹️ Como usar o aplicativo

Ao abrir a janela do programa, você verá duas áreas principais:

- Cartas da Mesa
- Sua Mão

### 1) Escolha as cartas da sua mão

Clique no botão "+" em cada um dos dois slots da seção "Sua Mão" e escolha a carta desejada.

Você pode selecionar as duas cartas do jogador.

### 2) Escolha as cartas da mesa

Na seção "Cartas da Mesa", existem cinco slots para as cartas comunitárias.

Clique em cada "+" e selecione a carta correspondente.

Você pode deixar alguns slots vazios se a mesa ainda não estiver completa.

### 3) Calcule as chances

Depois de selecionar as cartas, clique no botão:

```text
Calcular chances
```

O programa irá mostrar as porcentagens de cada mão possível com base nas cartas escolhidas.

### 4) Interprete os resultados

Os valores exibidos representam a probabilidade estimada de cada combinação aparecer nas cartas restantes.

Exemplo:

- 42.15% de Pair
- 12.80% de Flush
- 3.22% de Full House

## 📁 Estrutura do projeto

```text
POKER/
├── main.py
├── requirements.txt
├── README.md
├── imgs/
│   ├── clubs/
│   ├── diamonds/
│   ├── hearts/
│   ├── spades/
│   └── icon.ico
└── venv/
```

## 📝 Observações

- O projeto usa imagens das cartas para a interface visual.
- A lógica de probabilidade é calculada com base no conjunto de cartas restantes do baralho.
- A ferramenta é útil para aprender e testar cenários de poker em situações reais de jogo.

## 💡 Dica

Para melhor resultado, tente testar combinações simples primeiro, como:

- uma mão com par
- uma mão com cartas conectadas
- mesa com 3 cartas do mesmo naipe

Depois avance para cenários mais complexos e compare as porcentagens retornadas.

## 🧠 Objetivo do projeto

O objetivo principal é facilitar o entendimento das chances de cada combinação no poker, tornando a análise mais didática e visual para jogadores, estudantes e entusiastas do jogo.
