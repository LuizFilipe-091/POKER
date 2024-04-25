from typing import List
from PIL import Image, ImageTk
from tkinter import Tk, Label
from time import sleep


class Card:

    def __init__(self, rank, suit) -> None:
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
        self.house: List[Card] or None = None # type: ignore
        self.player_cards: List[Card] or None = None # type: ignore
        self.new_game()

    def new_game(self):
        # TODO
        pass


if __name__ == '__main__':
    Game()