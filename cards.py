'''
The `cards` module contains classes related to a deck of cards and how they are used.
It contains classes for a card (Card) and deck of cards (Deck). It does not
contain a class for a hand of cards because that is dependent on the game being 
played and managed by the player of a game.
'''

import random
from functools import total_ordering

# Char representations of suits
# Hearts, Diamonds, Clubs, Spades
SUITS = set(['H', 'D', 'C', 'S'])

# Char representations of rank including numbers and Jack, Queen, King, Ace
RANKS = set(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'])

# Char representations of Jokers
JOKERS = set(['BJoker', 'RJoker'])

INITIAL_CARD_NUM = 17

EXTRA_CARD_NUM = 3



class Deck:
    '''
    Represents a standard 54 card deck of playing cards. It has the standard suits and ranks.
    Besides that, it includes Jokers, both black and red.
    '''

    def __init__(self):
        '''
        Creates the inital deck.
        '''
        self.deck = []
        self.create()
        self.shuffle()

    def create(self):
        '''
        Builds a 52 card deck from scratch.
        '''
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append(Card(suit, rank))
        for joker in JOKERS: 
            self.deck.append(Card('H', 'A',joker))

    def shuffle(self):
        '''
        Suffles the deck.
        '''
        random.shuffle(self.deck)

    def deal_card(self):
        '''
        Removes and returns a card from the top of the deck.
        '''
        if len(self.deck) <= 0:
            raise ValueError('Deck is empty')

        return self.deck.pop()

    # Not used
    def add_card_to_bottom(self, card):
        '''
        Adds the given card to the bottom of the deck. The card can not be
        a duplicate of a card already in the deck.

        card: Card - A Card object
        '''
        if not isinstance(card, Card):
            raise TypeError('card must be of type `Card`')
        if card in self.deck:
            raise ValueError('cannot add duplicate card to the deck')

        self.deck.insert(0, card)

    def _print_deck(self):
        '''
        Prints each card of a deck. Should only be needed for debugging.
        '''
        for card in self.deck:
            print(card)


class Card:
    '''
    Represents a standard playing card with a suit and rank.
    '''

    def __init__(self, suit, rank, joker = None):
        '''
        Creates a Card.

        suit: str - A char representing a suit ('H', 'D', 'C', 'S')
        rank: str - A char representing a rank
            ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
        '''
        if suit not in SUITS:
            raise ValueError('invalid suit')
        if rank not in RANKS:
            raise ValueError('invalid rank')
        
        if joker != None:
            self.__init_joker__(joker)
            return

        self.suit = suit
        self.rank = rank

        #Note all values rank * 10 + suit
        if self.rank == 'A':
            self.value = 140
        if self.rank == 'K':
            self.value = 130
        if self.rank == 'Q':
            self.value = 120
        if self.rank == 'J':
            self.value = 110
        if self.rank == '10':
            self.value = 100
        if self.rank == '9':
            self.value = 90
        if self.rank == '8':
            self.value = 80
        if self.rank == '7':
            self.value = 70
        if self.rank == '6':
            self.value = 60
        if self.rank == '5':
            self.value = 50
        if self.rank == '4':
            self.value = 40
        if self.rank == '3':
            self.value = 30
        if self.rank == '2':
            self.value = 150

        # Assign UTF suit also
        if suit == 'H':
            self.utf_suit = '♥'    # U+2665
            self.value += 1
        elif suit == 'D':
            self.utf_suit = '♦'    # U+2666
            self.value += 2
        elif suit == 'C':
            self.utf_suit = '♣'    # U+2663
            self.value += 3
        else:
            # Must be spade, from check above
            self.utf_suit = '♠'    # U+2660
            self.value += 4
    
    def __init_joker__(self, joker):
        '''
        Creates a Joker Card.
        '''
        if joker not in JOKERS:
            raise ValueError('invalid card')
        
        self.suit = joker[0]
        self.rank = joker[1:]
        if self.suit == 'B':
            self.value = 160
        else:
            self.value = 170

        self.utf_suit = self.suit

    def __eq__(self, other):
        return (self.value == other.value)

    def __ne__(self, other):
        return not (self.value == other.value)

    def __lt__(self, other):
        return (self.value < other.value)


    '''
    def compare(card_1, card_2):
        return card_1.value - card_2.value
    '''

    def __str__(self):
        '''
        Prints the card so it looks like a playing card.
        '''
        edge = '+-----+'  # top and bottom, so no newline automatically
        middle = '|  ' + self.utf_suit + '  |\n'

        # Account for different length ranks ('2' vs '10')
        if self.rank == '10':
            rank_top =    '|10   |\n'
            rank_bottom = '|   10|\n'
        elif self.rank == 'Joker':
            rank_top =    '|Joker|\n'
            rank_bottom = '|Joker|\n'
        else:
            rank_top =    '|' + self.rank + '    |\n'
            rank_bottom = '|    ' + self.rank + '|\n'

        return edge + '\n' + rank_top + middle + rank_bottom + edge

    def __repr__(self):
        '''
        Simple representation of a card for TCP messaging.
        '''
        return self.suit + self.rank


class Hand:
    '''
    Hand represents a hand of cards that a poker player might have.
    '''

    def __init__(self):
        '''
        Creates an empty hand.

        num_cards: int - the number of cards a hand should contain
        '''
        #self.max_len = INITIAL_CARD_NUM
        self.hand = []

    def add_card(self, card):
        '''
        Adds a card to the hand. If the hand is full, raises a HandFullError. If
        the given card is not a Card object, raises a TypeError.

        card: Card - the card to add to the hand
        '''
        if not isinstance(card, Card):
            raise TypeError('card must be of type Card')

        self.hand.append(card)

    def remove_card(self, card_id):
        '''
        Removes the card with the given index from the hand. The index is
        1-indexed for user friendliness. IDs are printed for the user next
        to each card when displayed. The card is returned after removal.

        card_id: int - the 1-indexed position of the card to remove
        '''
        if not 0 < card_id <= len(self.hand):
            raise ValueError('card_id must be a valid index (1 to len)')

        card = self.hand[card_id - 1]
        self.hand.remove(card)
        return card

    def swap_cards(self, card_id_1, card_id_2):
        '''
        Swaps two cards in a hand as one would do with a real hand of cards.

        card_id_1: int - the 1-indexed position of the first card to swap
        card_id_2: int - the 1-indexed position of the second card to swap
        '''
        if not 0 < card_id_1 <= len(self.hand):
            raise ValueError('card_id_1 must be a valid index (1 to len)')
        if not 0 < card_id_2 <= len(self.hand):
            raise ValueError('card_id_2 must be a valid index (1 to len)')

        i = card_id_1 - 1
        j = card_id_2 - 1
        self.hand[i], self.hand[j] = self.hand[j], self.hand[i]

    def print_hand(self):
        '''
        Displays each card in the hand along with its ID number.
        '''
        for i, card in enumerate(self.hand):
            print(i+1)
            print(card)

    def sort_cards(self):
        self.hand.sort()

    def __repr__(self):
        '''
        Provides a simple representation of the hand.
        '''
        # Get the representation of each card in the hand
        hand_repr = map(lambda card: card.__repr__(), self.hand)

        # Return them as comma seperated values
        return "Hand(" + ', '.join(hand_repr) + ")"



