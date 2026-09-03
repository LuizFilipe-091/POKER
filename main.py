from typing import Any, Dict, List, Optional, cast
from collections import Counter
from PIL import Image, ImageTk
from ttkbootstrap import Label, Window, Separator, Frame, Button, Style, StringVar, Toplevel
from itertools import combinations
import threading


# --------------------------------------------------------------------------- #
# Paleta e constantes visuais
# --------------------------------------------------------------------------- #
COLORS = {
    'bg':          '#0e1116',   # fundo geral (quase preto, elegante)
    'felt':        '#12271d',   # verde "mesa de baralho" para as áreas de cartas
    'felt_border': '#1f4a34',
    'card_slot':   '#1a2a22',   # cor do slot vazio de carta
    'gold':        '#d4af37',   # detalhes dourados (título, separadores)
    'accent':      '#35d43a',   # verde de destaque (mantido do original)
    'accent_soft': '#2e8b3e',
    'text':        '#f5f5f5',
    'text_muted':  '#a9b4ad',
    'button_bg':   '#1c1f26',
    'button_hover':'#262b34',
}

FONT_TITLE = ('Segoe UI Semibold', 26)
FONT_SECTION = ('Segoe UI', 16)
FONT_STAT = ('Segoe UI', 15)
FONT_CARD_PLUS = ('Segoe UI', 34)


# =============================================================================
# FUNÇÃO: center_window
# =============================================================================
# O QUE FAZ: Centraliza uma janela Tkinter/ttkbootstrap na tela do usuário.
# PARAMÊTROS:
#   - win: Janela (Window ou Toplevel) que será centralizada.
#   - width (int): Largura desejada da janela em pixels.
#   - height (int): Altura desejada da janela em pixels.
# RETORNO:
#   - None (modifica diretamente a posição da janela).
# =============================================================================
def center_window(win, width: int, height: int) -> None:
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    win.geometry(f'{width}x{height}+{x}+{y}')


# =============================================================================
# FUNÇÃO: lock_size
# =============================================================================
# O QUE FAZ: Trava o redimensionamento de uma janela, impedindo o usuário de
#            alterar seu tamanho e reescrevendo a geometria caso ocorra resize.
# PARAMÊTROS:
#   - win: Janela (Window ou Toplevel) a ter o tamanho travado.
#   - width (int): Largura fixa em pixels.
#   - height (int): Altura fixa em pixels.
# RETORNO:
#   - None.
# =============================================================================
def lock_size(win, width: int, height: int) -> None:
    win.resizable(False, False)
    win.minsize(width, height)
    win.maxsize(width, height)

    def _enforce_size(event=None):
        if win.winfo_width() != width or win.winfo_height() != height:
            win.geometry(f'{width}x{height}')

    win.bind('<Configure>', _enforce_size)


# Mapeamento numérico dos valores dos valores das cartas para validação de sequências
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
}

# Categorias de mãos de poker avaliadas
CATEGORIES = (
    'pair', 'two_pair', 'three_of_a_kind', 'full_house',
    'flush', 'straight', 'four_of_a_kind', 'straight_flush',
)


# =============================================================================
# FUNÇÃO AUXILIAR: _has_straight
# =============================================================================
# O QUE FAZ: Verifica se uma lista de valores numéricos de cartas contém uma
#            sequência (Straight) de pelo menos 5 cartas consecutivas.
#            Trata o Ás (14) tanto como valor alto quanto como valor 1 (A-2-3-4-5).
# PARAMÊTROS:
#   - values (List[int] ou Iterable[int]): Lista com os valores numéricos dos ranks.
# RETORNO:
#   - bool: True se houver sequência de 5 cartas; False caso contrário.
# =============================================================================
def _has_straight(values) -> bool:
    unique_values = set(values)
    # Ás também pode atuar como carta de valor 1 em A-2-3-4-5 (Wheel)
    if 14 in unique_values:
        unique_values.add(1)

    sorted_values = sorted(unique_values)
    run_length = 1
    for i in range(1, len(sorted_values)):
        if sorted_values[i] == sorted_values[i - 1] + 1:
            run_length += 1
            if run_length >= 5:
                return True
        else:
            run_length = 1
    return False


# =============================================================================
# FUNÇÃO: hand_indicators
# =============================================================================
# O QUE FAZ: Avalia um conjunto de cartas (ex: 5 a 7 cartas) e determina quais
#            categorias de mãos de poker já estão FORMADAS.
# PARAMÊTROS:
#   - cards (List[Card]): Lista de objetos do tipo Card a serem analisados.
# RETORNO:
#   - Dict[str, bool]: Dicionário mapeando cada categoria ('pair', 'flush', etc.)
#                      para True (já possui) ou False (não possui).
# =============================================================================
def hand_indicators(cards: List['Card']) -> Dict[str, bool]:
    ranks = [RANK_VALUES[card.rank] for card in cards]
    suits = [card.suit for card in cards]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    counts_sorted = sorted(rank_counts.values(), reverse=True)

    max_count = counts_sorted[0] if counts_sorted else 0
    ranks_with_pair_or_better = sum(1 for count in rank_counts.values() if count >= 2)

    flush_suit = next((suit for suit, count in suit_counts.items() if count >= 5), None)
    is_flush = flush_suit is not None

    is_straight_flush = False
    if is_flush:
        suited_values = [RANK_VALUES[card.rank] for card in cards if card.suit == flush_suit]
        is_straight_flush = _has_straight(suited_values)

    is_full_house = len(counts_sorted) > 1 and counts_sorted[0] >= 3 and counts_sorted[1] >= 2

    return {
        'pair': max_count >= 2,
        'two_pair': ranks_with_pair_or_better >= 2,
        'three_of_a_kind': max_count >= 3,
        'full_house': is_full_house,
        'flush': is_flush,
        'straight': _has_straight(ranks),
        'four_of_a_kind': max_count >= 4,
        'straight_flush': is_straight_flush,
    }


# =============================================================================
# FUNÇÃO: rank_groups
# =============================================================================
# O QUE FAZ: Agrupa os ranks das cartas em jogo pela frequência (quantas cópias saíram).
# PARAMÊTROS:
#   - game_cards (List[Card]): Cartas presentes na mesa e na mão.
# RETORNO:
#   - Dict[str, List[str]]: Dicionário com listas de ranks classificados por:
#     'singles', 'pairs', 'trips', 'pairs_or_better', 'trips_or_better', 'quads_or_better'.
# =============================================================================
def rank_groups(game_cards: List['Card']) -> Dict[str, List[str]]:
    rank_counts = Counter(card.rank for card in game_cards)
    return {
        'singles': [rank for rank, count in rank_counts.items() if count == 1],
        'pairs': [rank for rank, count in rank_counts.items() if count == 2],
        'trips': [rank for rank, count in rank_counts.items() if count == 3],
        'pairs_or_better': [rank for rank, count in rank_counts.items() if count >= 2],
        'trips_or_better': [rank for rank, count in rank_counts.items() if count >= 3],
        'quads_or_better': [rank for rank, count in rank_counts.items() if count >= 4],
    }


# =============================================================================
# FUNÇÃO: calculate_hand_probabilities
# =============================================================================
# O QUE FAZ: Calcula a probabilidade percentual (0.0% a 100.0%) de completar
#            cada uma das 8 categorias de poker considerando a mão atual e o baralho.
# PARAMÊTROS:
#   - player_cards (List[Card]): Cartas na mão do jogador.
#   - house (List[Card]): Cartas comunitárias já expostas na mesa.
#   - deck (List[Card]): Lista completa do baralho (52 cartas).
# RETORNO:
#   - Dict[str, float]: Dicionário vinculando o nome de cada categoria ao valor %.
# =============================================================================
def calculate_hand_probabilities(player_cards: List['Card'], house: List['Card'], deck: List['Card']) -> Dict[str, float]:
    remaining_cards = [card for card in deck if card not in player_cards and card not in house]
    game_cards = house + player_cards
    missing_cards_count = max(0, 5 - len(house))
    total_remaining = len(remaining_cards)

    already_have = hand_indicators(game_cards)
    result = {category: 100.0 for category in CATEGORIES if already_have[category]}
    pending = [category for category in CATEGORIES if category not in result]

    if not pending:
        return result

    if missing_cards_count == 0:
        for category in pending:
            result[category] = 0.0
        return result

    # Caso onde falta apenas 1 carta na mesa (calcula via Outs exatos)
    if missing_cards_count == 1:
        groups = rank_groups(game_cards)
        suit_counts = Counter(card.suit for card in game_cards)
        player_values = [RANK_VALUES[card.rank] for card in game_cards]

        for category in pending:
            if category == 'pair':
                outs = sum(1 for card in remaining_cards if card.rank in groups['singles'])

            elif category == 'two_pair':
                if not groups['pairs_or_better']:
                    outs = 0
                else:
                    outs = sum(1 for card in remaining_cards if card.rank in groups['singles'])

            elif category == 'three_of_a_kind':
                if not groups['pairs']:
                    outs = 0
                else:
                    outs = sum(1 for card in remaining_cards if card.rank in groups['pairs'])

            elif category == 'full_house':
                if groups['trips_or_better']:
                    outs = sum(1 for card in remaining_cards if card.rank in groups['singles'])
                elif len(groups['pairs']) >= 2:
                    outs = sum(1 for card in remaining_cards if card.rank in groups['pairs'])
                else:
                    outs = 0

            elif category == 'four_of_a_kind':
                if not groups['trips']:
                    outs = 0
                else:
                    outs = sum(1 for card in remaining_cards if card.rank in groups['trips'])

            elif category == 'flush':
                needed_suits = [suit for suit, count in suit_counts.items() if count == 4]
                if not needed_suits:
                    outs = 0
                else:
                    outs = sum(1 for card in remaining_cards if card.suit in needed_suits)

            elif category == 'straight':
                qualifying_values = {
                    value for value in range(2, 15)
                    if _has_straight(player_values + [value])
                }
                outs = sum(1 for card in remaining_cards if RANK_VALUES[card.rank] in qualifying_values)

            else:  # straight_flush
                outs = sum(
                    1 for card in remaining_cards
                    if hand_indicators(game_cards + [card])['straight_flush']
                )

            result[category] = (outs / total_remaining * 100) if total_remaining else 0.0

        return result

    # Faltam 2+ cartas: combinação/enumeração completa do baralho
    hits = {category: 0 for category in pending}
    total = 0
    for extra_cards in combinations(remaining_cards, missing_cards_count):
        final_hand = game_cards + list(extra_cards)
        indicators = hand_indicators(final_hand)
        for category in pending:
            if indicators[category]:
                hits[category] += 1
        total += 1

    for category in pending:
        result[category] = (hits[category] / total * 100) if total else 0.0

    return result


# =============================================================================
# CLASSE: Card
# =============================================================================
# O QUE FAZ: Representa uma carta individual do baralho contendo rank, naipe e imagem.
# =============================================================================
class Card:

    # MÉTODO: __init__
    # O QUE FAZ: Construtor da classe Card.
    # PARAMÊTROS:
    #   - rank (str): Valor da carta ('A', '2', ..., 'K').
    #   - suit (str): Naipe ('clubs', 'diamonds', 'hearts', 'spades').
    # RETORNO: None.
    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit
        self.image_url = f'./imgs/{suit}/{rank}-{suit}.png'

    # MÉTODO: __str__
    # O QUE FAZ: Retorna representação em texto amigável da carta.
    # PARAMÊTROS: Nenhum.
    # RETORNO: str (Ex: "A of spades").
    def __str__(self):
        return self.rank + ' of ' + self.suit


# =============================================================================
# CLASSE: Game
# =============================================================================
# O QUE FAZ: Gerencia a interface gráfica (GUI), captura interações do usuário
#            e orquestra os cálculos de probabilidade.
# =============================================================================
class Game:

    # Baralho padrão de 52 cartas
    DECK: List[Card] = [
        Card('A', 'clubs'), Card('2', 'clubs'), Card('3', 'clubs'), Card('4', 'clubs'), Card('5', 'clubs'),
        Card('6', 'clubs'), Card('7', 'clubs'), Card('8', 'clubs'), Card('9', 'clubs'), Card('10', 'clubs'),
        Card('J', 'clubs'), Card('Q', 'clubs'), Card('K', 'clubs'),
        Card('A', 'diamonds'), Card('2', 'diamonds'), Card('3', 'diamonds'), Card('4', 'diamonds'), Card('5', 'diamonds'),
        Card('6', 'diamonds'), Card('7', 'diamonds'), Card('8', 'diamonds'), Card('9', 'diamonds'), Card('10', 'diamonds'),
        Card('J', 'diamonds'), Card('Q', 'diamonds'), Card('K', 'diamonds'),
        Card('A', 'hearts'), Card('2', 'hearts'), Card('3', 'hearts'), Card('4', 'hearts'), Card('5', 'hearts'),
        Card('6', 'hearts'), Card('7', 'hearts'), Card('8', 'hearts'), Card('9', 'hearts'), Card('10', 'hearts'),
        Card('J', 'hearts'), Card('Q', 'hearts'), Card('K', 'hearts'),
        Card('A', 'spades'), Card('2', 'spades'), Card('3', 'spades'), Card('4', 'spades'), Card('5', 'spades'),
        Card('6', 'spades'), Card('7', 'spades'), Card('8', 'spades'), Card('9', 'spades'), Card('10', 'spades'),
        Card('J', 'spades'), Card('Q', 'spades'), Card('K', 'spades')
    ]

    SUIT_SYMBOLS = {
        'clubs': ('♣', COLORS['text']),
        'diamonds': ('♦', '#e05656'),
        'hearts': ('♥', '#e05656'),
        'spades': ('♠', COLORS['text']),
    }

    # MÉTODO: __init__
    # O QUE FAZ: Inicializa a janela principal, variáveis reativas (StringVar) e inicia a GUI.
    # PARAMÊTROS: Nenhum.
    # RETORNO: None.
    def __init__(self) -> None:
        self.house: List[Optional[Card]] = [None] * 5
        self.player_cards: List[Optional[Card]] = [None, None]
        self.select_cards: Optional[Toplevel] = None

        WIN_WIDTH, WIN_HEIGHT = 1040, 660
        self.window = Window(themename='darkly')
        self.window.title('Poker Calculator')
        icon_image = ImageTk.PhotoImage(Image.open("./imgs/icon.ico"))
        self.window.iconphoto(False, cast(Any, icon_image))

        lock_size(self.window, WIN_WIDTH, WIN_HEIGHT)
        center_window(self.window, WIN_WIDTH, WIN_HEIGHT)
        self.window.configure(background=COLORS['bg'])

        # Variáveis ligadas à interface gráfica para exibição dos resultados
        self.straight_flush = StringVar(value='—')
        self.four_of_a_kind = StringVar(value='—')
        self.full_house = StringVar(value='—')
        self.flush = StringVar(value='—')
        self.straight = StringVar(value='—')
        self.three_of_a_kind = StringVar(value='—')
        self.two_pair = StringVar(value='—')
        self.pair = StringVar(value='—')

        self.game()

    # MÉTODO: game
    # O QUE FAZ: Monta toda a estrutura de componentes visuais, layout da tela
    #            e funções internas de manipulação de eventos.
    # PARAMÊTROS: Nenhum.
    # RETORNO: None.
    def game(self):

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: generate_chances
        # O QUE FAZ: Inicia o cálculo de probabilidades em segundo plano (Thread)
        #            para não travar a interface do usuário.
        # PARAMÊTROS: Nenhum.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def generate_chances():
            player_cards_snapshot = [card for card in self.player_cards if card is not None]
            house_snapshot = [card for card in self.house if card is not None]

            if not player_cards_snapshot:
                return

            status_vars = (
                self.straight_flush, self.four_of_a_kind, self.full_house, self.flush,
                self.straight, self.three_of_a_kind, self.two_pair, self.pair,
            )
            for status_var in status_vars:
                status_var.set('...')
            generate.configure(state='disabled')

            # SUB-FUNÇÃO INTERNA: apply_result
            # O QUE FAZ: Atualiza as StringVars da UI com as porcentagens calculadas.
            # PARAMÊTROS: result (Dict[str, float]) - dicionário com as probabilidades.
            # RETORNO: None.
            def apply_result(result: Dict[str, float]):
                self.straight_flush.set(f"{result['straight_flush']:.2f}%")
                self.four_of_a_kind.set(f"{result['four_of_a_kind']:.2f}%")
                self.full_house.set(f"{result['full_house']:.2f}%")
                self.flush.set(f"{result['flush']:.2f}%")
                self.straight.set(f"{result['straight']:.2f}%")
                self.three_of_a_kind.set(f"{result['three_of_a_kind']:.2f}%")
                self.two_pair.set(f"{result['two_pair']:.2f}%")
                self.pair.set(f"{result['pair']:.2f}%")
                generate.configure(state='normal')

            # SUB-FUNÇÃO INTERNA: worker
            # O QUE FAZ: Executado na Thread secundária para processar as probabilidades.
            # PARAMÊTROS: Nenhum.
            # RETORNO: None.
            def worker():
                result = calculate_hand_probabilities(player_cards_snapshot, house_snapshot, self.DECK)
                self.window.after(0, lambda: apply_result(result))

            threading.Thread(target=worker, daemon=True).start()

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: reset_stats
        # O QUE FAZ: Reseta o texto exibido dos valores de porcentagem para "—".
        # PARAMÊTROS: Nenhum.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def reset_stats():
            for status_var in (
                self.straight_flush, self.four_of_a_kind, self.full_house, self.flush,
                self.straight, self.three_of_a_kind, self.two_pair, self.pair,
            ):
                status_var.set('—')

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: close_select_cards
        # O QUE FAZ: Destrói o pop-up de seleção de cartas se estiver aberto.
        # PARAMÊTROS: Nenhum.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def close_select_cards():
            if self.select_cards:
                self.select_cards.destroy()
                self.select_cards = None

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: show_delete_badge
        # O QUE FAZ: Exibe o botão de exclusão ('✕') sobre o slot da carta.
        # PARAMÊTROS:
        #   - house (bool): True se for carta da mesa, False se for da mão do jogador.
        #   - index (int): Posição (índice) do slot.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def show_delete_badge(house: bool, index: int):
            badge = house_delete_buttons[index] if house else player_delete_buttons[index]
            x, y = (house_delete_positions if house else player_delete_positions)[index]
            badge.place(x=x, y=y, width=DELETE_BADGE_SIZE, height=DELETE_BADGE_SIZE)
            badge.lift()

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: hide_delete_badge
        # O QUE FAZ: Oculta o botão de exclusão ('✕') do slot da carta.
        # PARAMÊTROS:
        #   - house (bool): True se for carta da mesa, False se for do jogador.
        #   - index (int): Posição (índice) do slot.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def hide_delete_badge(house: bool, index: int):
            badge = house_delete_buttons[index] if house else player_delete_buttons[index]
            badge.place_forget()

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: remove_card
        # O QUE FAZ: Remove a carta selecionada de um slot (mesa ou jogador),
        #            restaurando o botão para o estado padrão de adição ('+').
        # PARAMÊTROS:
        #   - house (bool): True se for carta da mesa, False se for do jogador.
        #   - index (int): Posição do slot a ser limpo.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def remove_card(house: bool, index: int):
            if house:
                self.house[index] = None
                card_button = house_card_buttons[index]
                card_button.configure(image='', text='+', style='Card.TButton')
            else:
                self.player_cards[index] = None
                card_button = player_card_buttons[index]
                card_button.configure(image='', text='+', style='PlayerCard.TButton')
            setattr(card_button, 'image', None)
            hide_delete_badge(house, index)
            reset_stats()

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: change_image
        # O QUE FAZ: Define a imagem da carta escolhida no slot correspondente
        #            e atualiza a lista de cartas em jogo (`self.house` / `self.player_cards`).
        # PARAMÊTROS:
        #   - card (Card): Objeto da carta selecionada.
        #   - house (bool): True se a carta vai para a mesa, False se vai para a mão.
        #   - index (int): Posição no slot.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def change_image(card: Card, house: bool, index: int):
            if house:
                image = Image.open(card.image_url)
                resized_image = image.resize((120, 210))
                photo_image = ImageTk.PhotoImage(resized_image)
                card_button = house_card_buttons[index]
                card_button.configure(image=photo_image, style='Card.TButton')
                setattr(card_button, 'image', photo_image)
                self.house[index] = card
            else:
                image = Image.open(card.image_url)
                resized_image = image.resize((100, 165))
                photo_image = ImageTk.PhotoImage(resized_image)
                card_button = player_card_buttons[index]
                card_button.configure(image=photo_image, style='PlayerCard.TButton')
                setattr(card_button, 'image', photo_image)
                self.player_cards[index] = card

            show_delete_badge(house, index)
            reset_stats()
            close_select_cards()

        # ---------------------------------------------------------------------
        # SUB-FUNÇÃO: add_card
        # O QUE FAZ: Abre a janela modal pop-up exibindo o baralho disponível para
        #            o usuário selecionar uma carta para o slot desejado.
        # PARAMÊTROS:
        #   - house (bool): True se a carta é para a mesa, False se é para a mão.
        #   - index (int): Posição do slot selecionado.
        # RETORNO: None.
        # ---------------------------------------------------------------------
        def add_card(house: bool, index: int):
            if not self.select_cards:
                popup_width, popup_height = 660, 900

                self.select_cards = Toplevel(title='Escolha uma carta')
                self.select_cards.protocol("WM_DELETE_WINDOW", close_select_cards)
                select_icon = ImageTk.PhotoImage(Image.open("./imgs/icon.ico"))
                self.select_cards.iconphoto(False, cast(Any, select_icon))

                lock_size(self.select_cards, popup_width, popup_height)
                center_window(self.select_cards, popup_width, popup_height)
                self.select_cards.configure(background=COLORS['bg'])

                header = Label(
                    self.select_cards, text='Selecione uma carta', font=('Segoe UI Semibold', 18),
                    foreground=COLORS['gold'], background=COLORS['bg']
                )
                header.place(x=20, y=14)

                suits_order = ['clubs', 'diamonds', 'hearts', 'spades']
                x = 20
                y_start = 60

                for col, suit in enumerate(suits_order):
                    symbol, color = self.SUIT_SYMBOLS[suit]
                    suit_label = Label(
                        self.select_cards, text=symbol, font=('Segoe UI', 20, 'bold'),
                        foreground=color, background=COLORS['bg']
                    )
                    suit_label.place(x=x + 40, y=y_start)
                    x += 155

                y_start_cards = y_start + 44
                used_cards = set(self.player_cards) | set(self.house)

                for i, card in enumerate(self.DECK):
                    if card in used_cards:
                        continue

                    col = i // 13
                    row = i % 13
                    card_x = 20 + (col * 155)
                    card_y = y_start_cards + (row * 62)

                    image_url = card.image_url
                    image = Image.open(image_url)
                    resized_image = image.resize((100, 165))
                    photo_image = ImageTk.PhotoImage(resized_image)
                    button = Button(
                        self.select_cards, image=photo_image, style='Card.TButton',
                        command=lambda c=card, h=house, idx=index: change_image(c, h, idx)
                    )
                    setattr(button, 'image', photo_image)
                    button.place(x=card_x, y=card_y)

                self.select_cards.mainloop()

        self.house = [None] * 5
        self.player_cards = [None, None]

        WIN_WIDTH, WIN_HEIGHT = 1040, 660
        window = self.window

        DELETE_BADGE_SIZE = 24

        # ------------------------------------------------------------------- #
        # Configurações de Estilo da Interface (ttkbootstrap)
        # ------------------------------------------------------------------- #
        style = Style()
        style.configure('TFrame', background=COLORS['bg'])
        style.configure(
            'Felt.TFrame', background=COLORS['felt'],
            bordercolor=COLORS['felt_border'], relief='flat'
        )
        style.configure(
            'Card.TButton', font=FONT_CARD_PLUS,
            background=COLORS['card_slot'], foreground=COLORS['accent'],
            borderwidth=0, relief='flat', focusthickness=0
        )
        style.map(
            'Card.TButton',
            background=[('active', COLORS['button_hover']), ('!disabled', COLORS['card_slot'])],
            foreground=[('active', COLORS['accent'])]
        )
        style.configure(
            'PlayerCard.TButton', font=('Segoe UI', 26),
            background=COLORS['card_slot'], foreground=COLORS['accent'],
            borderwidth=0, relief='flat'
        )
        style.map(
            'PlayerCard.TButton',
            background=[('active', COLORS['button_hover'])],
            foreground=[('active', COLORS['accent'])]
        )
        style.configure(
            'Generate.TButton', font=('Segoe UI Semibold', 14),
            background=COLORS['accent_soft'], foreground='#ffffff',
            borderwidth=0, padding=(18, 10)
        )
        style.map(
            'Generate.TButton',
            background=[('active', COLORS['accent'])],
            foreground=[('active', '#ffffff')]
        )
        style.configure(
            'Delete.TButton', font=('Segoe UI', 12, 'bold'),
            background='#7a2323', foreground='#f5f5f5',
            borderwidth=0, relief='flat', padding=0
        )
        style.map(
            'Delete.TButton',
            background=[('active', '#c0392b')],
            foreground=[('active', '#ffffff')]
        )

        style.configure('Title.TLabel', background=COLORS['bg'], foreground=COLORS['text'], font=FONT_TITLE)
        style.configure('Gold.TSeparator', background=COLORS['gold'])
        style.configure('Section.TLabel', background=COLORS['felt'], foreground=COLORS['gold'], font=FONT_SECTION)
        style.configure('Stat.TLabel', background=COLORS['felt'], foreground=COLORS['text'], font=FONT_STAT)
        style.configure('StatValue.TLabel', background=COLORS['felt'], foreground=COLORS['accent'], font=('Segoe UI Semibold', 15))

        # ------------------------------------------------------------------- #
        # Montagem do Cabeçalho
        # ------------------------------------------------------------------- #
        title = Label(window, text='♠ Poker Calculator ♠', style='Title.TLabel')
        title.place(x=(WIN_WIDTH // 2) - 190, y=16)

        generate = Button(window, text='Calcular chances', style='Generate.TButton', command=generate_chances)
        generate.place(x=WIN_WIDTH - 215, y=20)

        bar = Separator(window, style='Gold.TSeparator', orient='horizontal')
        bar.place(x=20, y=70, width=WIN_WIDTH - 40)

        # ------------------------------------------------------------------- #
        # Área comunitária (Mesa)
        # ------------------------------------------------------------------- #
        house_frame = Frame(window, style='Felt.TFrame', width=WIN_WIDTH - 40, height=250)
        house_frame.place(x=20, y=92)

        house_label = Label(house_frame, text='Cartas da Mesa', style='Section.TLabel')
        house_label.place(x=24, y=12)

        card_positions_house = [55, 235, 415, 625, 805]
        CARD_WIDTH_HOUSE, CARD_HEIGHT_HOUSE, CARD_Y_HOUSE = 140, 180, 55

        house_card_buttons: List[Button] = []
        house_delete_buttons: List[Button] = []
        house_delete_positions: List[tuple] = []

        for i, pos_x in enumerate(card_positions_house):
            card_button = Button(
                house_frame, text="+", style='Card.TButton',
                command=lambda idx=i: add_card(True, idx)
            )
            card_button.place(x=pos_x, y=CARD_Y_HOUSE, width=CARD_WIDTH_HOUSE, height=CARD_HEIGHT_HOUSE)
            house_card_buttons.append(card_button)

            delete_x = pos_x + CARD_WIDTH_HOUSE - DELETE_BADGE_SIZE + 6
            delete_y = CARD_Y_HOUSE - (DELETE_BADGE_SIZE // 2) - 2
            house_delete_positions.append((delete_x, delete_y))

            delete_button = Button(
                house_frame, text='✕', style='Delete.TButton',
                command=lambda idx=i: remove_card(True, idx)
            )
            house_delete_buttons.append(delete_button)

        # ------------------------------------------------------------------- #
        # Mão do jogador
        # ------------------------------------------------------------------- #
        player_frame = Frame(window, style='Felt.TFrame', width=330, height=270)
        player_frame.place(x=20, y=362)

        text_your_hand = Label(player_frame, text='Sua Mão', style='Section.TLabel')
        text_your_hand.place(x=110, y=12)

        card_positions_player = [30, 175]
        CARD_WIDTH_PLAYER, CARD_HEIGHT_PLAYER, CARD_Y_PLAYER = 120, 195, 60

        player_card_buttons: List[Button] = []
        player_delete_buttons: List[Button] = []
        player_delete_positions: List[tuple] = []

        for i, pos_x in enumerate(card_positions_player):
            card_button = Button(
                player_frame, text='+', style='PlayerCard.TButton',
                command=lambda idx=i: add_card(False, idx)
            )
            card_button.place(x=pos_x, y=CARD_Y_PLAYER, width=CARD_WIDTH_PLAYER, height=CARD_HEIGHT_PLAYER)
            player_card_buttons.append(card_button)

            delete_x = pos_x + CARD_WIDTH_PLAYER - DELETE_BADGE_SIZE + 6
            delete_y = CARD_Y_PLAYER - (DELETE_BADGE_SIZE // 2) - 2
            player_delete_positions.append((delete_x, delete_y))

            delete_button = Button(
                player_frame, text='✕', style='Delete.TButton',
                command=lambda idx=i: remove_card(False, idx)
            )
            player_delete_buttons.append(delete_button)

        # ------------------------------------------------------------------- #
        # Painel de Probabilidades
        # ------------------------------------------------------------------- #
        percentage = Frame(window, style='Felt.TFrame', width=WIN_WIDTH - 400, height=270)
        percentage.place(x=370, y=362)

        panel_title = Label(percentage, text='Probabilidades', style='Section.TLabel')
        panel_title.place(x=24, y=12)

        stats_left = [
            ('Straight Flush', 'straight_flush'),
            ('Four of a Kind', 'four_of_a_kind'),
            ('Full House', 'full_house'),
            ('Flush', 'flush'),
        ]
        stats_right = [
            ('Straight', 'straight'),
            ('Three of a Kind', 'three_of_a_kind'),
            ('Two Pair', 'two_pair'),
            ('Pair', 'pair'),
        ]

        row_height = 44
        start_y = 58

        for i, (label_text, attr) in enumerate(stats_left):
            var = getattr(self, attr)
            name_label = Label(percentage, text=label_text, style='Stat.TLabel')
            name_label.place(x=24, y=start_y + i * row_height)

            value_label = Label(percentage, textvariable=var, style='StatValue.TLabel')
            value_label.place(x=190, y=start_y + i * row_height)

        divider = Separator(percentage, style='Gold.TSeparator', orient='vertical')
        divider.place(x=300, y=start_y - 6, height=row_height * len(stats_left) + 10)

        for i, (label_text, attr) in enumerate(stats_right):
            var = getattr(self, attr)
            name_label = Label(percentage, text=label_text, style='Stat.TLabel')
            name_label.place(x=330, y=start_y + i * row_height)

            value_label = Label(percentage, textvariable=var, style='StatValue.TLabel')
            value_label.place(x=540, y=start_y + i * row_height)

        window.mainloop()


if __name__ == '__main__':
    Game()