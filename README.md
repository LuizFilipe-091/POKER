# 🃏 Poker Calculator

Aplicativo desktop desenvolvido em Python para calcular as probabilidades de formação das principais mãos de poker a partir das cartas do jogador e das cartas comunitárias da mesa.

O programa possui uma interface gráfica visual na qual o usuário pode selecionar as cartas da própria mão e da mesa, visualizar as cartas escolhidas e calcular as chances de formar diferentes combinações de poker.

O cálculo considera as cartas já utilizadas e o conjunto de cartas restantes de um baralho padrão de 52 cartas. Dependendo da quantidade de cartas que ainda faltam na mesa, o programa utiliza cálculo por **outs** ou enumeração completa das combinações possíveis.

---

## ✨ Funcionalidades

* Seleção visual das cartas do jogador
* Seleção das cartas comunitárias da mesa
* Suporte para até 2 cartas na mão do jogador
* Suporte para até 5 cartas comunitárias
* Impedimento da seleção de cartas que já estão em uso
* Remoção individual das cartas selecionadas
* Cálculo das probabilidades das principais mãos de poker
* Tratamento especial para sequência com Ás baixo (`A-2-3-4-5`)
* Identificação de Flush e Straight Flush
* Cálculo baseado nas cartas restantes do baralho
* Cálculo exato de probabilidades quando faltam duas ou mais cartas
* Cálculo através de outs quando falta apenas uma carta comunitária
* Execução dos cálculos em uma thread separada para evitar travamentos da interface
* Interface gráfica utilizando `ttkbootstrap`
* Imagens reais das cartas exibidas na interface
* Tema visual escuro com elementos dourados e verdes
* Janela principal com tamanho fixo e centralizada

---

## 📌 Combinações calculadas

O aplicativo calcula a probabilidade de formação das seguintes categorias:

* **Pair** — Um par
* **Two Pair** — Dois pares
* **Three of a Kind** — Trinca
* **Straight** — Sequência
* **Flush** — Flush
* **Full House** — Full House
* **Four of a Kind** — Quadra
* **Straight Flush** — Straight Flush

Essas categorias são armazenadas internamente no programa e avaliadas através da função `hand_indicators`.

---

## 🧠 Como o cálculo funciona

O programa utiliza um baralho padrão de **52 cartas**, representado pela classe `Card` e armazenado na classe `Game`. Cada carta possui um rank, um naipe e o caminho para sua imagem correspondente.

Depois que o usuário seleciona as cartas, o programa identifica quais cartas ainda estão disponíveis no baralho:

```text
Baralho completo
       ↓
Cartas do jogador + cartas da mesa
       ↓
Remoção das cartas utilizadas
       ↓
Cartas restantes
       ↓
Cálculo das possibilidades
       ↓
Probabilidade de cada mão
```

A função `calculate_hand_probabilities()` é responsável por realizar esse processo.

### Cálculo com uma carta restante

Quando falta apenas uma carta comunitária, o programa calcula os **outs** para cada categoria e transforma a quantidade de cartas favoráveis em uma porcentagem baseada nas cartas restantes.

Por exemplo:

```text
Outs favoráveis
       ÷
Cartas restantes
       × 100
       =
Probabilidade
```

Essa abordagem é utilizada quando `missing_cards_count == 1`.

### Cálculo com duas ou mais cartas restantes

Quando ainda faltam duas ou mais cartas comunitárias, o programa realiza uma enumeração das combinações possíveis de cartas restantes utilizando `itertools.combinations`.

Cada combinação é analisada e contabilizada caso forme determinada categoria de poker.

Isso permite obter uma probabilidade baseada na totalidade das combinações possíveis dentro do baralho restante.

---

## ♠️ Tratamento de Sequências

O programa possui uma função auxiliar chamada `_has_straight()` responsável por verificar se existe uma sequência de pelo menos cinco valores consecutivos.

Um tratamento especial é realizado para o Ás.

O Ás normalmente possui valor `14`, mas também pode funcionar como valor `1` para permitir a sequência:

```text
A → 2 → 3 → 4 → 5
```

Esse cenário é conhecido como **Wheel**.

---

## 🃏 Interface gráfica

A interface foi construída utilizando:

* `ttkbootstrap`
* `PIL`
* `ImageTk`
* `Tkinter`

O programa utiliza um tema escuro e uma paleta personalizada com tons de preto, verde e dourado.

A janela principal possui tamanho fixo de:

```text
1040 × 660 pixels
```

e é automaticamente centralizada na tela.

### Áreas principais

A interface é dividida em três áreas principais:

#### Cartas da Mesa

Possui cinco espaços para representar as cartas comunitárias:

```text
[ + ] [ + ] [ + ] [ + ] [ + ]
```

Cada espaço pode receber uma carta selecionada pelo usuário.

#### Sua Mão

Possui dois espaços destinados às cartas do jogador:

```text
[ + ] [ + ]
```

Cada carta pode ser adicionada ou removida individualmente.

#### Probabilidades

O painel apresenta as probabilidades calculadas para cada uma das oito categorias:

```text
Straight Flush
Four of a Kind
Full House
Flush

Straight
Three of a Kind
Two Pair
Pair
```

Os resultados são exibidos em formato percentual com duas casas decimais.

---

## 🖱️ Seleção das cartas

Ao clicar em um dos espaços `+`, o programa abre uma janela para seleção das cartas disponíveis.

A janela apresenta as cartas organizadas por naipe:

```text
♣ Clubs
♦ Diamonds
♥ Hearts
♠ Spades
```

As cartas que já foram selecionadas para a mão ou para a mesa não ficam disponíveis para uma nova seleção.

Depois de selecionar uma carta, sua imagem é carregada e redimensionada para ser exibida diretamente no espaço correspondente da interface.

---

## 🗑️ Remoção de cartas

Depois que uma carta é adicionada, um botão `✕` é exibido no canto do espaço correspondente.

Ao clicar nesse botão, a carta é removida e o espaço volta ao estado inicial:

```text
[ + ]
```

As estatísticas exibidas também são resetadas para evitar que resultados antigos permaneçam na tela.

---

## ⚡ Processamento em segundo plano

O cálculo das probabilidades pode envolver a análise de diversas combinações de cartas.

Para evitar que esse processamento bloqueie a interface gráfica, o programa utiliza `threading.Thread`.

O cálculo é executado em uma thread secundária e, após sua conclusão, os resultados são enviados novamente para a interface principal através do mecanismo `after()` do Tkinter.

Durante o cálculo, o botão **Calcular chances** é temporariamente desabilitado e os valores das probabilidades são substituídos por:

```text
...
```

Após o processamento, os valores são atualizados e o botão volta a ficar disponível.

---

## 🧰 Tecnologias utilizadas

O projeto foi desenvolvido utilizando:

| Tecnologia          | Utilização                             |
| ------------------- | -------------------------------------- |
| Python              | Linguagem principal                    |
| Tkinter             | Base da interface gráfica              |
| ttkbootstrap        | Estilização e tema da interface        |
| Pillow (PIL)        | Manipulação e carregamento das imagens |
| threading           | Execução dos cálculos em segundo plano |
| itertools           | Enumeração das combinações possíveis   |
| collections.Counter | Contagem de ranks e naipes             |
| typing              | Tipagem estática do código             |

---

## 📦 Dependências

As principais bibliotecas externas utilizadas pelo projeto são:

```text
Pillow
ttkbootstrap
```

As demais funcionalidades utilizadas no código fazem parte da biblioteca padrão do Python.

Para instalar as dependências, execute:

```bash
pip install -r requirements.txt
```

---

## 🚀 Instalação

### 1. Clone o projeto

```bash
git clone <url-do-repositorio>
cd POKER
```

### 2. Crie um ambiente virtual

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## ▶️ Como executar

Na raiz do projeto, execute:

```bash
python main.py
```

O ponto de entrada do programa é:

```python
if __name__ == '__main__':
    Game()
```

Isso cria uma instância da classe `Game` e inicia a aplicação gráfica.

---

## 🕹️ Como utilizar

### 1. Escolha suas cartas

Na seção **Sua Mão**, clique nos dois botões `+` e selecione as cartas que pertencem ao jogador.

### 2. Escolha as cartas da mesa

Na seção **Cartas da Mesa**, selecione as cartas comunitárias que já estão disponíveis.

É possível deixar espaços vazios caso a mão ainda não tenha chegado ao River.

### 3. Clique em "Calcular chances"

Depois de configurar as cartas, clique em:

```text
Calcular chances
```

O programa irá analisar as cartas restantes e calcular as probabilidades.

### 4. Analise os resultados

As probabilidades serão exibidas no painel:

```text
Straight Flush    XX.XX%
Four of a Kind    XX.XX%
Full House        XX.XX%
Flush             XX.XX%

Straight          XX.XX%
Three of a Kind   XX.XX%
Two Pair          XX.XX%
Pair              XX.XX%
```

---

## 📁 Estrutura do projeto

```text
POKER/
├── main.py
├── requirements.txt
├── README.md
├── imgs/
│   ├── clubs/
│   │   ├── A-clubs.png
│   │   ├── 2-clubs.png
│   │   └── ...
│   ├── diamonds/
│   │   ├── A-diamonds.png
│   │   ├── 2-diamonds.png
│   │   └── ...
│   ├── hearts/
│   │   ├── A-hearts.png
│   │   ├── 2-hearts.png
│   │   └── ...
│   ├── spades/
│   │   ├── A-spades.png
│   │   ├── 2-spades.png
│   │   └── ...
│   └── icon.ico
└── venv/
```

---

## 🏗️ Principais componentes do código

### `Card`

Representa uma carta individual do baralho.

Cada objeto possui:

* `rank`
* `suit`
* `image_url`

A classe também possui uma representação textual da carta através do método `__str__()`.

### `Game`

É a principal classe da aplicação.

Ela é responsável por:

* criar a janela;
* armazenar as cartas da mesa;
* armazenar as cartas do jogador;
* construir a interface;
* controlar a seleção de cartas;
* remover cartas;
* iniciar os cálculos;
* atualizar os resultados.

O baralho completo de 52 cartas também é definido dentro dessa classe.

### `hand_indicators()`

Analisa as cartas disponíveis e identifica quais categorias de poker já estão formadas.

Ela verifica:

* Par
* Dois pares
* Trinca
* Full House
* Flush
* Straight
* Quadra
* Straight Flush

### `rank_groups()`

Agrupa os ranks das cartas de acordo com a quantidade de ocorrências:

```text
singles
pairs
trips
pairs_or_better
trips_or_better
quads_or_better
```

Essa informação é utilizada principalmente no cálculo dos outs.

### `calculate_hand_probabilities()`

É a principal função matemática do projeto.

Ela recebe:

```python
player_cards
house
deck
```

e retorna um dicionário contendo a probabilidade de cada categoria.

---

## 📊 Exemplo de resultado

Após selecionar as cartas, o programa pode apresentar resultados semelhantes a:

```text
Straight Flush     1.23%
Four of a Kind     0.00%
Full House         8.70%
Flush              19.57%

Straight           34.78%
Three of a Kind    6.52%
Two Pair           41.30%
Pair               100.00%
```

Os valores são calculados de acordo com as cartas selecionadas e as possibilidades existentes no baralho restante.

---

## 📝 Observações

* O programa utiliza um baralho padrão de 52 cartas.
* Uma mesma carta não pode ser selecionada simultaneamente para a mão e para a mesa.
* As imagens das cartas precisam estar disponíveis no diretório `imgs/`.
* O caminho das imagens segue o formato `./imgs/{suit}/{rank}-{suit}.png`.
* O programa considera o Ás como valor alto e também como valor baixo em uma sequência `A-2-3-4-5`.
* As probabilidades são exibidas com duas casas decimais.
* Quando uma determinada combinação já está formada, sua probabilidade é apresentada como `100%`.
* Se todas as cartas comunitárias já estiverem preenchidas e uma combinação ainda não estiver formada, sua probabilidade futura é considerada `0%`.

---

## 💡 Sugestões para testes

Para testar o funcionamento do aplicativo, experimente diferentes cenários:

### Par

Selecione duas cartas do mesmo rank ou uma combinação que possa formar um par.

### Sequência

Utilize cartas conectadas, como:

```text
7 - 8 - 9 - 10
```

e observe a probabilidade de completar uma Straight.

### Flush

Selecione várias cartas do mesmo naipe e observe a evolução da probabilidade de Flush.

### Full House

Teste situações envolvendo pares e trincas para observar como o programa calcula os possíveis outs.

### Straight Flush

Combine cartas consecutivas do mesmo naipe para testar a detecção dessa categoria.

---

## 🎯 Objetivo do projeto

O objetivo do **Poker Calculator** é fornecer uma ferramenta visual e prática para analisar probabilidades de mãos de poker.

Além de facilitar a análise de diferentes cenários de jogo, o projeto demonstra conceitos importantes de programação, como:

* Programação orientada a objetos
* Interfaces gráficas
* Manipulação de imagens
* Estruturas de dados
* Contagem de elementos
* Combinações matemáticas
* Cálculo de probabilidades
* Programação concorrente com threads
* Atualização de interfaces gráficas

O projeto também foi estruturado de forma que sua lógica de cálculo possa ser posteriormente expandida para novas funcionalidades, regras ou métodos de simulação.