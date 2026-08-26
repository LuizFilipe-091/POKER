from typing import Any, Counter, List, Optional, cast
from PIL import Image, ImageTk
from ttkbootstrap import Label, Window, Separator, Frame, Button, Style, StringVar, Toplevel
from itertools import combinations


# --------------------------------------------------------------------------- #
#  Paleta e constantes visuais
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


def center_window(win, width: int, height: int) -> None:
    """
    Calcula o centro do monitor principal e posiciona a janela ali.
    Usa as dimensões de tela reportadas pelo Tk (winfo_screenwidth/height),
    que no monitor principal correspondem à resolução real de exibição.
    """
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    win.geometry(f'{width}x{height}+{x}+{y}')


def lock_size(win, width: int, height: int) -> None:
    """
    Bloqueia o redimensionamento da janela de forma robusta em qualquer
    sistema operacional / gerenciador de janelas.
    """
    win.resizable(False, False)
    win.minsize(width, height)
    win.maxsize(width, height)

    def _enforce_size(event=None):
        if win.winfo_width() != width or win.winfo_height() != height:
            win.geometry(f'{width}x{height}')

    win.bind('<Configure>', _enforce_size)

RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
}

class Card:

    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit
        self.image_url = f'./imgs/{suit}/{rank}-{suit}.png'

    def __str__(self):
        return self.rank + ' of ' + self.suit


class Game:

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

    def __init__(self) -> None:
        self.house: List[Card] = []
        self.player_cards: List[Card] = []
        self.select_cards: Optional[Toplevel] = None

        WIN_WIDTH, WIN_HEIGHT = 1040, 660
        self.window = Window(themename='darkly')
        self.window.title('Poker Calculator')
        icon_image = ImageTk.PhotoImage(Image.open("./imgs/icon.ico"))
        self.window.iconphoto(False, cast(Any, icon_image))

        lock_size(self.window, WIN_WIDTH, WIN_HEIGHT)
        center_window(self.window, WIN_WIDTH, WIN_HEIGHT)
        self.window.configure(background=COLORS['bg'])

        self.straight_flush = StringVar(value='—')
        self.four_of_a_kind = StringVar(value='—')
        self.full_house = StringVar(value='—')
        self.flush = StringVar(value='—')
        self.straight = StringVar(value='—')
        self.three_of_a_kind = StringVar(value='—')
        self.two_pair = StringVar(value='—')
        self.pair = StringVar(value='—')

        self.game()

    def game(self):

        def get_straight_flush_probability() -> float:
            return 0.0
        def get_four_of_a_kind_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]
            game_cards = self.house + self.player_cards
            player_ranks = list(map(lambda card: card.rank, game_cards))
            rank_counts = Counter(player_ranks)

            # JA TEM QUADRA?
            if any(count >= 4 for count in rank_counts.values()):
                return 100.0

            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # MESA JA COMPLETA E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            tripped_ranks = [rank for rank, count in rank_counts.items() if count == 3]

            # SO FALTA 1 CARTA: so completa quadra se voce ja tiver uma trinca
            # (falta so 1 pra virar 4) - com par so (2 cartas), 1 carta so vira
            # trinca, nao quadra.
            if missing_cards_count == 1:
                if not tripped_ranks:
                    return 0.0
                outs = sum(1 for card in remaining_cards if card.rank in tripped_ranks)
                return (outs / total_remaining * 100) if total_remaining else 0.0

            # FALTAM 2+ CARTAS: conferimos todas as combinacoes possiveis
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_ranks = player_ranks + [card.rank for card in extra_cards]
                counts = Counter(final_ranks)
                if any(count >= 4 for count in counts.values()):
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def get_full_house_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]
            game_cards = self.house + self.player_cards
            player_ranks = list(map(lambda card: card.rank, game_cards))
            rank_counts = Counter(player_ranks)
            counts_sorted = sorted(rank_counts.values(), reverse=True)

            # JA TEM FULL HOUSE? (trinca + outro par, ranks diferentes)
            if len(counts_sorted) > 1 and counts_sorted[0] >= 3 and counts_sorted[1] >= 2:
                return 100.0

            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # MESA JA COMPLETA E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            tripped_ranks = [rank for rank, count in rank_counts.items() if count >= 3]
            paired_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            single_ranks = [rank for rank, count in rank_counts.items() if count == 1]

            # SO FALTA 1 CARTA: so tem 2 jeitos de fechar o full house com 1 carta so
            if missing_cards_count == 1:
                if tripped_ranks:
                    # ja tem trinca -> falta so parear QUALQUER outra rank solta
                    outs = sum(1 for card in remaining_cards if card.rank in single_ranks)
                    return (outs / total_remaining * 100) if total_remaining else 0.0
                if len(paired_ranks) >= 2:
                    # ja tem 2 pares -> falta so virar trinca em UM dos dois
                    outs = sum(1 for card in remaining_cards if card.rank in paired_ranks)
                    return (outs / total_remaining * 100) if total_remaining else 0.0
                # so 1 par (ou nenhum) -> impossivel fechar full house com 1 carta so
                return 0.0

            # FALTAM 2+ CARTAS: conferimos todas as combinacoes possiveis
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_ranks = player_ranks + [card.rank for card in extra_cards]
                counts = sorted(Counter(final_ranks).values(), reverse=True)
                if len(counts) > 1 and counts[0] >= 3 and counts[1] >= 2:
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def get_flush_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]
            game_cards = self.house + self.player_cards
            suit_counts = Counter(card.suit for card in game_cards)

            # JA TEM FLUSH?
            if any(count >= 5 for count in suit_counts.values()):
                return 100.0

            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # MESA JA COMPLETA E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            # SO FALTA 1 CARTA: so completa o flush se algum naipe ja tiver
            # exatamente 4 cartas (falta so 1 pra fechar)
            if missing_cards_count == 1:
                needed_suits = [suit for suit, count in suit_counts.items() if count == 4]
                if not needed_suits:
                    return 0.0
                outs = sum(1 for card in remaining_cards if card.suit in needed_suits)
                return (outs / total_remaining * 100) if total_remaining else 0.0

            # FALTAM 2+ CARTAS: conferimos todas as combinacoes possiveis
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_suits = [card.suit for card in game_cards] + [card.suit for card in extra_cards]
                counts = Counter(final_suits)
                if any(count >= 5 for count in counts.values()):
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def get_straight_probability() -> float:
            def _has_straight(values) -> bool:
                unique_values = set(values)
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
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]
            game_cards = self.house + self.player_cards
            player_ranks = [RANK_VALUES[card.rank] for card in game_cards]

            # JA TEM STRAIGHT?
            if _has_straight(player_ranks):
                return 100.0

            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # MESA JA COMPLETA E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            # SO FALTA 1 CARTA: descobre exatamente quais valores completariam a
            # sequencia (pode ser 1 valor - sequencia de ponta - ou 2 valores -
            # sequencia aberta pelos dois lados) e conta quantas cartas restantes
            # tem esses valores.
            if missing_cards_count == 1:
                qualifying_values = {
                    value for value in range(2, 15)
                    if _has_straight(player_ranks + [value])
                }
                outs = sum(1 for card in remaining_cards if RANK_VALUES[card.rank] in qualifying_values)
                return (outs / total_remaining * 100) if total_remaining else 0.0

            # FALTAM 2+ CARTAS: a sequencia pode nascer de combinacoes diferentes
            # das cartas que ainda vao sair (nao da so pra contar "outs" fixos),
            # entao conferimos todas as combinacoes possiveis.
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_values = player_ranks + [RANK_VALUES[card.rank] for card in extra_cards]
                if _has_straight(final_values):
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def get_three_of_a_kind_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]
            game_cards = self.house + self.player_cards
            player_ranks = list(map(lambda card: card.rank, game_cards))
            rank_counts = Counter(player_ranks)

            # JA TEM TRINCA? (cobre tambem full house e quadra, que contem trinca dentro)
            if any(count >= 3 for count in rank_counts.values()):
                return 100.0

            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # MESA JA COMPLETA E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            paired_ranks = [rank for rank, count in rank_counts.items() if count == 2]

            # SO FALTA 1 CARTA: ela sozinha so completa uma trinca se voce ja tiver
            # um par de algum rank (falta so 1 pra virar trinca) - nao da pra
            # "nascer" uma trinca nova do zero com 1 carta so.
            if missing_cards_count == 1:
                if not paired_ranks:
                    return 0.0
                outs = sum(1 for card in remaining_cards if card.rank in paired_ranks)
                return (outs / total_remaining * 100) if total_remaining else 0.0

            # FALTAM 2+ CARTAS: alem de completar um par que voce ja tem, uma
            # trinca nova pode nascer inteiramente das cartas que ainda vao sair
            # (se sobrarem pelo menos 3 pra sair) - por isso conferimos todas as
            # combinacoes possiveis.
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_ranks = player_ranks + [card.rank for card in extra_cards]
                counts = Counter(final_ranks)
                if any(count >= 3 for count in counts.values()):
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def get_two_pair_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]
            game_cards = self.house + self.player_cards
            player_ranks = list(map(lambda card: card.rank, game_cards))

            rank_counts = Counter(player_ranks)
            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # JA TEM TWO PAIR? (cobre 2 pares distintos, e também full house/quadra+par,
            # que tecnicamente também contam como "ter dois pares")
            if sum(1 for count in rank_counts.values() if count >= 2) >= 2:
                return 100.0

            # MESA JA COMPLETA (river) E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            paired_ranks = [rank for rank, count in rank_counts.items() if count >= 2]
            leftover_ranks = [rank for rank, count in rank_counts.items() if count == 1]

            # SO FALTA 1 CARTA NA MESA (river por vir): ela sozinha NAO consegue
            # formar um par novo do nada (precisaria de 2 cartas pra isso) - só pode
            # completar o two pair se bater com uma rank que já sobrou.
            if missing_cards_count == 1:
                if not paired_ranks:
                    return 0.0  # sem nenhum par ainda, 1 carta só dá pra formar 1 par, nao 2

                leftover_outs = sum(1 for card in remaining_cards if card.rank in leftover_ranks)
                return (leftover_outs / total_remaining * 100) if total_remaining else 0.0

            # FALTAM 2+ CARTAS: além de poder parear com o que já sobrou, as
            # PRÓPRIAS cartas que ainda vão sair podem formar um par novo entre
            # elas (sem nenhuma relação com o que você já tem) - por isso, com 2+
            # cartas faltando, o cálculo direto não cobre tudo e a gente confere
            # todas as combinações possíveis das cartas que faltam.
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_ranks = player_ranks + [card.rank for card in extra_cards]
                counts = Counter(final_ranks)
                if sum(1 for count in counts.values() if count >= 2) >= 2:
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def get_pair_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards + self.house]
            game_cards = self.house + self.player_cards
            player_ranks = list(map(lambda card: card.rank, game_cards))

            # JA TEM PAR?
            if len(game_cards) != len(set(player_ranks)):
                return 100.0

            missing_cards_count = max(0, 5 - len(self.house))
            total_remaining = len(remaining_cards)

            # MESA JA COMPLETA (river) E AINDA NAO TEM -> nao tem mais carta pra sair
            if missing_cards_count == 0:
                return 0.0

            # SO FALTA 1 CARTA: ela sozinha só pode dar par se bater com uma rank
            # que já está na mão/mesa - não dá pra "nascer" um par novo com 1 carta só
            if missing_cards_count == 1:
                count_probability = sum(1 for card in remaining_cards if card.rank in player_ranks)
                return (count_probability / total_remaining * 100) if total_remaining else 0.0

            # FALTAM 2+ CARTAS: alem de poder bater com uma rank que voce ja tem,
            # DUAS cartas novas da mesa podem parear ENTRE ELAS, sem nenhuma
            # relacao com a sua mao - por isso, com 2+ faltando, conferimos todas
            # as combinacoes possiveis das cartas que ainda vao sair.
            hits = 0
            total = 0
            for extra_cards in combinations(remaining_cards, missing_cards_count):
                final_ranks = player_ranks + [card.rank for card in extra_cards]
                counts = Counter(final_ranks)
                if any(count >= 2 for count in counts.values()):
                    hits += 1
                total += 1

            return (hits / total * 100) if total else 0.0

        def generate_chances():
            if len(self.player_cards) > 0:
                self.straight_flush.set(f'{get_straight_flush_probability():.2f}%')
                self.four_of_a_kind.set(f'{get_four_of_a_kind_probability():.2f}%')
                self.full_house.set(f'{get_full_house_probability():.2f}%')
                self.flush.set(f'{get_flush_probability():.2f}%')
                self.straight.set(f'{get_straight_probability():.2f}%')
                self.three_of_a_kind.set(f'{get_three_of_a_kind_probability():.2f}%')
                self.two_pair.set(f'{get_two_pair_probability():.2f}%')
                self.pair.set(f'{get_pair_probability():.2f}%') 

        def close_select_cards():
            if self.select_cards:
                self.select_cards.destroy()
                self.select_cards = None

        def change_image(button: Button, card: Card, house: bool = False, index: int = 0):
            if house:
                image_url = card.image_url
                image = Image.open(image_url)
                resized_image = image.resize((120, 210))
                photo_image = ImageTk.PhotoImage(resized_image)
                button.configure(image=photo_image, style='Card.TButton')
                setattr(button, 'image', photo_image)
                if card not in self.house:
                    if len(self.house) == index:
                        self.house.append(card)
                    else:
                        temp_card = self.house[index]
                        self.house.remove(temp_card)
                        self.house.insert(index, card)
                close_select_cards()
                return

            image_url = card.image_url
            image = Image.open(image_url)
            resized_image = image.resize((100, 165))
            photo_image = ImageTk.PhotoImage(resized_image)
            button.configure(image=photo_image, style='Card.TButton')
            setattr(button, 'image', photo_image)
            if card not in self.player_cards:
                if len(self.player_cards) >= 2:
                    temp_card = self.player_cards[index]
                    self.player_cards.remove(temp_card)
                self.player_cards.insert(index, card)
            else:
                self.player_cards.remove(card)
                self.player_cards.insert(index, card)
            close_select_cards()

        def add_card(master_button: Button, house=False, index: int = 0):
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

                for i, card in enumerate(self.DECK):
                    if card in self.player_cards or card in self.house:
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
                        command=lambda b=master_button, c=card, h=house, idx=index: change_image(b, c, h, idx)
                    )
                    setattr(button, 'image', photo_image)
                    button.place(x=card_x, y=card_y)

                self.select_cards.mainloop()

        self.house = []
        self.player_cards = []

        WIN_WIDTH, WIN_HEIGHT = 1040, 660
        window = self.window

        # ------------------------------------------------------------------- #
        #  Estilos
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

        style.configure('Title.TLabel', background=COLORS['bg'], foreground=COLORS['text'], font=FONT_TITLE)
        style.configure('Gold.TSeparator', background=COLORS['gold'])
        style.configure('Section.TLabel', background=COLORS['felt'], foreground=COLORS['gold'], font=FONT_SECTION)
        style.configure('Stat.TLabel', background=COLORS['felt'], foreground=COLORS['text'], font=FONT_STAT)
        style.configure('StatValue.TLabel', background=COLORS['felt'], foreground=COLORS['accent'], font=('Segoe UI Semibold', 15))

        # ------------------------------------------------------------------- #
        #  Cabeçalho
        # ------------------------------------------------------------------- #
        title = Label(window, text='♠ Poker Calculator ♠', style='Title.TLabel')
        title.place(x=(WIN_WIDTH // 2) - 190, y=16)

        generate = Button(window, text='Calcular chances', style='Generate.TButton', command=generate_chances)
        generate.place(x=WIN_WIDTH - 215, y=20)

        bar = Separator(window, style='Gold.TSeparator', orient='horizontal')
        bar.place(x=20, y=70, width=WIN_WIDTH - 40)

        # ------------------------------------------------------------------- #
        #  Área comunitária (mesa)
        # ------------------------------------------------------------------- #
        house_frame = Frame(window, style='Felt.TFrame', width=WIN_WIDTH - 40, height=250)
        house_frame.place(x=20, y=92)

        house_label = Label(house_frame, text='Cartas da Mesa', style='Section.TLabel')
        house_label.place(x=24, y=12)

        card_positions_house = [55, 235, 415, 625, 805]

        button_house_1 = Button(house_frame, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_1, True, 0))
        button_house_1.place(x=card_positions_house[0], y=55, width=140, height=180)

        button_house_2 = Button(house_frame, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_2, True, 1))
        button_house_2.place(x=card_positions_house[1], y=55, width=140, height=180)

        button_house_3 = Button(house_frame, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_3, True, 2))
        button_house_3.place(x=card_positions_house[2], y=55, width=140, height=180)

        button_house_4 = Button(house_frame, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_4, True, 3))
        button_house_4.place(x=card_positions_house[3], y=55, width=140, height=180)

        button_house_5 = Button(house_frame, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_5, True, 4))
        button_house_5.place(x=card_positions_house[4], y=55, width=140, height=180)

        # ------------------------------------------------------------------- #
        #  Mão do jogador
        # ------------------------------------------------------------------- #
        player_frame = Frame(window, style='Felt.TFrame', width=330, height=270)
        player_frame.place(x=20, y=362)

        text_your_hand = Label(player_frame, text='Sua Mão', style='Section.TLabel')
        text_your_hand.place(x=110, y=12)

        button_player_1 = Button(player_frame, text='+', style='PlayerCard.TButton',
                                  command=lambda: add_card(button_player_1, False, 0))
        button_player_1.place(x=30, y=60, width=120, height=195)

        button_player_2 = Button(player_frame, text='+', style='PlayerCard.TButton',
                                  command=lambda: add_card(button_player_2, False, 1))
        button_player_2.place(x=175, y=60, width=120, height=195)

        # ------------------------------------------------------------------- #
        #  Painel de probabilidades
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