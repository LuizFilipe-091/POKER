from typing import List
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

    resizable(False, False) + minsize/maxsize já impedem o redimensionamento
    na maioria dos casos, mas alguns gerenciadores de janela no Linux ignoram
    esses avisos e permitem arrastar a borda mesmo assim. Por isso também
    "vigiamos" o evento <Configure> e forçamos o tamanho de volta sempre que
    ele muda, garantindo que o usuário não consiga alterar as dimensões por
    nenhum meio (arrastar borda, maximizar, atalho de teclado, etc.).
    """
    win.resizable(False, False)
    win.minsize(width, height)
    win.maxsize(width, height)

    def _enforce_size(event=None):
        if win.winfo_width() != width or win.winfo_height() != height:
            win.geometry(f'{width}x{height}')

    win.bind('<Configure>', _enforce_size)


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
        self.house: List[Card] or None = []  # type: ignore
        self.player_cards: List[Card] or None = []  # type: ignore
        self.select_cards: Toplevel or None = None  # type: ignore
        self.game()

    def game(self):

        def get_straight_flush_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            straight_flush_probability = 0

            return straight_flush_probability * 100

        def get_four_of_a_kind_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            four_of_a_kind_probability = 0

            return four_of_a_kind_probability * 100

        def get_full_house_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            full_house_probability = 0

            return full_house_probability * 100

        def get_flush_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            flush_probability = 0

            return flush_probability * 100

        def get_straight_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            straight_probability = 0

            return straight_probability * 100

        def get_three_of_a_kind_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            three_of_a_kind_probaility = 0

            return three_of_a_kind_probaility * 100

        def get_two_pair_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards and card not in self.house]

            two_pair_probability = 0

            return two_pair_probability * 100

        def get_pair_probability() -> float:
            remaining_cards = [card for card in self.DECK if card not in self.player_cards + self.house]
            game_cards = self.house + self.player_cards

            player_ranks = list(map(lambda card: card.rank, game_cards))

            if len(game_cards) != len(set(map(lambda card: card.rank, game_cards))):
                return 100.0

            count_probability = 0

            for rank_remaining in remaining_cards:
                if rank_remaining.rank in player_ranks:
                    count_probability += 1

            pair_probability = float(count_probability) / len(remaining_cards)

            return pair_probability * 100

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
            self.select_cards.destroy()
            self.select_cards = None

        def change_image(button: Button, card: Card, house: bool = False, index: int = 0):
            if house:
                image_url = card.image_url
                image = Image.open(image_url)
                resized_image = image.resize((120, 210))
                photo_image = ImageTk.PhotoImage(resized_image)
                button.configure(image=photo_image, style='Card.TButton')
                button.image = photo_image
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
            button.image = photo_image
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
                self.select_cards.iconphoto(False, ImageTk.PhotoImage(Image.open("./imgs/icon.ico")))

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

                x = 20
                y = y_start + 44

                for i, card in enumerate(self.DECK):
                    if card in self.player_cards or card in self.house:
                        continue

                    # Calcula a coluna (0 a 3) e a linha (0 a 12) de forma fixa
                    col = i // 13
                    row = i % 13

                    card_x = 20 + (col * 155)
                    card_y = (y_start + 44) + (row * 62)

                    image_url = card.image_url
                    image = Image.open(image_url)
                    resized_image = image.resize((100, 165))
                    photo_image = ImageTk.PhotoImage(resized_image)
                    button = Button(
                        self.select_cards, image=photo_image, style='Card.TButton',
                        command=lambda b=master_button, c=card, h=house, i=index: change_image(b, c, h, i)
                    )
                    button.image = photo_image
                    button.place(x=card_x, y=card_y)

                self.select_cards.mainloop()

        self.house = []
        self.player_cards = []

        # ------------------------------------------------------------------- #
        #  Janela principal
        # ------------------------------------------------------------------- #
        WIN_WIDTH, WIN_HEIGHT = 1040, 660

        window = Window(themename='darkly')
        window.title('Poker Calculator')
        window.iconphoto(False, ImageTk.PhotoImage(Image.open("./imgs/icon.ico")))

        lock_size(window, WIN_WIDTH, WIN_HEIGHT)
        center_window(window, WIN_WIDTH, WIN_HEIGHT)

        window.configure(background=COLORS['bg'])

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
        house = Frame(window, style='Felt.TFrame', width=WIN_WIDTH - 40, height=250)
        house.place(x=20, y=92)

        house_label = Label(house, text='Cartas da Mesa', style='Section.TLabel')
        house_label.place(x=24, y=12)

        card_positions_house = [55, 235, 415, 625, 805]

        button_house_1 = Button(house, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_1, True, 0))
        button_house_1.place(x=card_positions_house[0], y=55, width=140, height=180)

        button_house_2 = Button(house, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_2, True, 1))
        button_house_2.place(x=card_positions_house[1], y=55, width=140, height=180)

        button_house_3 = Button(house, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_3, True, 2))
        button_house_3.place(x=card_positions_house[2], y=55, width=140, height=180)

        button_house_4 = Button(house, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_4, True, 3))
        button_house_4.place(x=card_positions_house[3], y=55, width=140, height=180)

        button_house_5 = Button(house, text="+", style='Card.TButton',
                                 command=lambda: add_card(button_house_5, True, 4))
        button_house_5.place(x=card_positions_house[4], y=55, width=140, height=180)

        # ------------------------------------------------------------------- #
        #  Mão do jogador
        # ------------------------------------------------------------------- #
        player = Frame(window, style='Felt.TFrame', width=330, height=270)
        player.place(x=20, y=362)

        text_your_hand = Label(player, text='Sua Mão', style='Section.TLabel')
        text_your_hand.place(x=110, y=12)

        button_player_1 = Button(player, text='+', style='PlayerCard.TButton',
                                  command=lambda: add_card(button_player_1, False, 0))
        button_player_1.place(x=30, y=60, width=120, height=195)

        button_player_2 = Button(player, text='+', style='PlayerCard.TButton',
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
            var = StringVar(value='—')
            setattr(self, attr, var)

            name_label = Label(percentage, text=label_text, style='Stat.TLabel')
            name_label.place(x=24, y=start_y + i * row_height)

            value_label = Label(percentage, textvariable=var, style='StatValue.TLabel')
            value_label.place(x=190, y=start_y + i * row_height)

        divider = Separator(percentage, style='Gold.TSeparator', orient='vertical')
        divider.place(x=300, y=start_y - 6, height=row_height * len(stats_left) + 10)

        for i, (label_text, attr) in enumerate(stats_right):
            var = StringVar(value='—')
            setattr(self, attr, var)

            name_label = Label(percentage, text=label_text, style='Stat.TLabel')
            name_label.place(x=330, y=start_y + i * row_height)

            value_label = Label(percentage, textvariable=var, style='StatValue.TLabel')
            value_label.place(x=540, y=start_y + i * row_height)

        window.mainloop()


if __name__ == '__main__':
    Game()