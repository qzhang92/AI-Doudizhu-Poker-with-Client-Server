
import cards
import random
import sys

class Manager:
    '''
    Rules and regulations of the game
    '''
    def __init__(self):
        self.card_style = dict() # a hash of ways to win
        self.card_style['solo'] = 1
        self.card_style['pair'] = 2
        self.card_style['trio'] = 3
        self.card_style['triosolo'] = 4
        self.card_style['triopair'] = 5
        '''
        self.card_style['chain'] = 6
        self.card_style['pairchain'] = 7
        self.card_style['airplane'] = 8
        self.card_style['airplanewingsolo'] = 9
        self.card_style['airplanewingpair'] = 10
        '''
        self.card_style['bomb'] = 11
        self.card_style['rocket'] = 12
        
        self.p1 = 1
        self.p2 = 2
    
    def is_valid_play(self, card_list, hand, positive, prev_action, prev_cards):
        '''
        check if cards in card_list is good
        return bool
        '''
        cur_cards = []
        for index in card_list:
            cur_cards.append(hand[index])
        
        if positive:
            return not self.get_action(cur_cards) == -1
        if len(card_list) != len(prev_cards):
            return False
        if prev_action != self.get_action(cur_cards):
            return False
        num1 = self.evaluate_cards(cur_cards, prev_action)
        num2 = self.evaluate_cards(prev_cards, prev_action)
        return num1 > num2
        
    
    
