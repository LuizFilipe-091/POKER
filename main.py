from typing import List
from PIL import Image, ImageTk
from ttkbootstrap import Label, Window, Separator, Frame, Button, Style, StringVar, Toplevel
from itertools import combinations


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

    def __init__(self) -> None:
        self.house: List[Card] or None = [] # type: ignore
        self.player_cards: List[Card] or None = [] # type: ignore
        self.select_cards: Toplevel or None = None #type: ignore
        self.game()

    def game(self):
        
        def generate_chances():
            if len(self.player_cards) > 0:
                self.straight_flush.set(f'Straight Flush: {get_straight_flush_probability():.2f}%')
                self.four_of_a_kind.set(f'Four of a Kind: {get_four_of_a_kind_probability():.2f}%')
                self.full_house.set(f'Full House: {get_full_house_probability():.2f}%')
                self.flush.set(f'Flush: {get_flush_probability():.2f}%')
                self.straight.set(f'Straight: {get_straight_probability():.2f}%')
                self.three_of_a_kind.set(f'Three of a Kind: {get_three_of_a_kind_probability():.2f}%')
                self.two_pair.set(f'Two Pair: {get_two_pair_probability():.2f}%')
                self.pair.set(f'Pair: {get_pair_probability():.2f}%')
            return

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

            cleaned_ranks = []

            for rank in player_ranks:
                if rank not in cleaned_ranks:
                    cleaned_ranks.append(rank)
                else:
                    return 100.00
            
            # PROBABILIDADE DAS PRÓXIMAS CARTAS SEREM PARES

            pair_probability = 0.00

            return pair_probability * 100


        def close_select_cards():
            self.select_cards.destroy()
            self.select_cards = None

        def change_image(button:Button, card:Card, house:bool=False, index:int=0):
            if house:
                image_url = card.image_url
                image = Image.open(image_url)
                resized_image = image.resize((120, 210))
                photo_image = ImageTk.PhotoImage(resized_image)
                button.configure(image=photo_image)
                button.image = photo_image
                if card not in self.house:
                    if len(self.house) >= 5:
                        temp_card = self.house[index]
                        self.house.remove(temp_card)
                    self.house.insert(index,card)
                else:
                    self.house.remove(card)
                    self.house.insert(index,card)
                return
            image_url = card.image_url
            image = Image.open(image_url)
            resized_image = image.resize((100, 165))
            photo_image = ImageTk.PhotoImage(resized_image)
            button.configure(image=photo_image)
            button.image = photo_image
            if card not in self.player_cards:
                if len(self.player_cards) >= 2:
                    temp_card = self.player_cards[index]
                    self.player_cards.remove(temp_card)
                self.player_cards.insert(index,card)
            else:
                self.player_cards.remove(card)
                self.player_cards.insert(index,card)

        def add_card(master_button:Button, house=False, index:int=0):
            if master_button['text'] == '+' and not self.select_cards:
                self.select_cards = Toplevel(title='Cards')
                self.select_cards.protocol("WM_DELETE_WINDOW", close_select_cards)
                self.select_cards.iconphoto(False, ImageTk.PhotoImage(Image.open("./imgs/icon.ico")))
                self.select_cards.resizable(False, False)
                self.select_cards.geometry('600x900')
                self.select_cards.place_window_center()

                x = y = 10

                for i, card in enumerate(self.DECK):

                    if i % 13 == 0 and i != 0:
                        x += 150
                        y = 10

                    image_url = card.image_url
                    image = Image.open(image_url)
                    resized_image = image.resize((100, 165))
                    photo_image = ImageTk.PhotoImage(resized_image)
                    button = Button(self.select_cards, image=photo_image, style='1.TButton', command=lambda b=master_button, c=card, h=house, i=index: change_image(b, c, h, i))
                    button.image = photo_image
                    button.place(x=x, y=y)

                    y += 60

                self.select_cards.mainloop()

        self.house = []
        self.player_cards = []

        window = Window(themename='darkly')
        window.title('Poker')
        window.iconphoto(False, ImageTk.PhotoImage(Image.open("./imgs/icon.ico")))
        window.geometry('1000x600')
        window.place_window_center()
        window.resizable(False, False)

        style = Style()
        style.configure('1.TButton', font=('Helvetica', 140), background='#808080', foreground='#35d43a', borderwidth=0)
        style.map('1.TButton', background=[('active', '#808080')], foreground=[('active', '#35d43a')])
        style.configure('2.TButton', font=('Helvetica', 110), background='#808080', foreground='#35d43a', borderwidth=0)
        style.map('2.TButton', background=[('active', '#808080')], foreground=[('active', '#35d43a')])
        style.configure('3.TButton', font=('Helvetica', 22), background='#4c7d2c', foreground='#ffffff', borderwidth=0)
        style.map('3.TButton', background=[('active', '#4c7d2c')], foreground=[('active', '#ffffff')])

        title = Label(window, bootstyle='light', font=('Helvetica', 24),text='Poker Calculator')
        title.place(x=370, y=10)

        generate = Button(window,style='3.TButton', text='Generate', command=generate_chances)
        generate.place(x=850, y=10)

        bar = Separator(window, bootstyle='light', orient='horizontal')
        bar.place(x=0, y=60, width=1000)

        house = Frame(window, bootstyle='secondary', width=980, height=240)
        house.place(x=10, y=80)

        button_house_1 = Button(house, text="+", style='1.TButton', command=lambda: add_card(button_house_1, True, 0))
        button_house_1.place(x=20, y=10)

        button_house_2 = Button(house, text="+", style='1.TButton', command=lambda: add_card(button_house_2, True, 1))
        button_house_2.place(x=220, y=10)

        button_house_3 = Button(house, text="+", style='1.TButton', command=lambda: add_card(button_house_3, True, 2))
        button_house_3.place(x=420, y=10)

        button_house_4 = Button(house, text="+", style='1.TButton', command=lambda: add_card(button_house_4, True, 3))
        button_house_4.place(x=620, y=10)

        button_house_5 = Button(house, text="+", style='1.TButton', command=lambda: add_card(button_house_5, True, 4))
        button_house_5.place(x=820, y=10)
            
        player = Frame(window, bootstyle='secondary', width=315, height=250)
        player.place(x=10, y=340)

        text_your_hand = Label(player, bootstyle='inverse-secondary', font=('Helvetica', 24), text='Your Hand')
        text_your_hand.place(x=80, y=5)

        button_player_1 = Button(player, text='+', style='2.TButton', command=lambda: add_card(button_player_1, False, 0))
        button_player_1.place(x=20, y=60)

        button_player_2 = Button(player, text='+', style='2.TButton', command=lambda: add_card(button_player_2, False, 1))
        button_player_2.place(x=180, y=60)

        percentage = Frame(window, bootstyle='secondary', width=590, height=250)
        percentage.place(x=400, y=340)

        self.straight_flush = StringVar()
        self.straight_flush.set('Straight Flush:')

        straight_flush = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.straight_flush)
        straight_flush.place(x=5, y=10)

        self.four_of_a_kind = StringVar()
        self.four_of_a_kind.set('Four of a Kind:')

        four_of_a_kind = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.four_of_a_kind)
        four_of_a_kind.place(x=5, y=70)

        self.full_house = StringVar()
        self.full_house.set('Full House:')

        full_house = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.full_house)
        full_house.place(x=5, y=130)

        self.flush = StringVar()
        self.flush.set('Flush:')

        flush = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.flush)
        flush.place(x=5, y=190)

        self.straight = StringVar()
        self.straight.set('Straight:')

        straight = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.straight)
        straight.place(x=280, y=10)

        self.three_of_a_kind = StringVar()
        self.three_of_a_kind.set('Three of a Kind:')

        three_of_a_kind = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.three_of_a_kind)
        three_of_a_kind.place(x=280, y=70)

        self.two_pair = StringVar()
        self.two_pair.set('Two Pair: ')

        two_pair = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.two_pair)
        two_pair.place(x=280, y=130)

        self.pair = StringVar()
        self.pair.set('Pair:')

        pair = Label(percentage, bootstyle='inverse-secondary', font=('Helvetica', 20), textvariable=self.pair)
        pair.place(x=280, y=190)

        window.mainloop()

if __name__ == '__main__':
    Game()