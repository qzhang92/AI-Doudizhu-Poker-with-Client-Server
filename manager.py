
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
        
    
    def get_action(self, card_list):
        '''
        return value -> key seen in init
        if value == -1:
            this is not a valid play
        '''
        size = len(card_list)
        if size == 1: #solo
            return 1
        elif size == 2:  # pair and rocket
            card0 = card_list[0]
            card1 = card_list[1]
            if card0.value > 150 and card1.value > 150: # Joker Joker
                return 12
            elif int(card0.value / 10) == int(card1.value / 10): #same rank
                return 2
            else:
                return -1 #invalid
        elif size == 3: # size == 3 is only possible with trio
            val = int(card_list[0].value / 10)
            for card in card_list:
                if not int(card.value / 10) == val:
                    return -1 # not Trio
            return 3
        else:
            card_dict = dict()
            for card in card_list:
                key = int(card.value / 10)
                if key in card_dict:
                    card_dict[key] += 1
                else:
                    card_dict[key] = 1
            if size == 4:
                if len(card_dict) == 1: #bomb
                    return 11
                elif len(card_dict) == 2: # 3 + 1 or 2 + 2
                    for key in card_dict:
                        if card_dict[key] != 2:
                            return 4 #Triosolo
                else: 
                    return -1
            elif size == 5:
                if len(card_dict) == 5: # 5 different cards. maybe chain
                    return -1#self.handle_chain(card_dict)
                elif len(card_dict) == 2: #only 3 + 2 is ok.
                    for key in card_dict:
                        if card_dict[key] == 3 or card_dict[key] == 2:
                            return 5
                        else:
                            return -1
                else: #len(card_dict) won't be 1, can be 3, 4, which are invalid
                    return -1
            else:
                return -1
            

    def evaluate_cards(self, cur_cards, prev_action):
        '''
        Bsed on the prev_action(that is also the current action), provide util score of the card
        '''
        card_dict = dict()
        for card in cur_cards:
            key = int(card.value / 10)
            if key in card_dict:
                card_dict[key] += 1
            else:
                card_dict[key] = 1
        if prev_action == 1:
            return int(cur_cards[0].value / 10)
        elif prev_action == 2:
            return int(cur_cards[0].value / 10)
        elif prev_action == 3:
            return int(cur_cards[0].value / 10)
        elif prev_action == 4:
            for key in card_dict:
                if card_dict[key] == 3:
                    return key
            return -1
        elif prev_action == 5:
            for key in card_dict:
                if card_dict[key] == 3:
                    return key
            return -1
        elif prev_action == 6:
            score = 0
            for key in card_dict:
                score += key
            return score
        elif prev_action == 7:
            score = 0
            for key in card_dict:
                score += key
            return score
        elif prev_action == 8:
            score = 0
            for key in card_dict:
                score += key
            return score
        elif prev_action == 9:
            score = 0
            for key in card_dict:
                if card_dict[key] == 3:
                    score += key
            return score
        elif prev_action == 10:
            score = 0
            for key in card_dict:
                if card_dict[key] == 3:
                    score += key
            return score
        elif prev_action == 11:
            return int(cur_cards[0].value / 10)
        elif prev_action == 12:
            return 200
        else:
            return -1


    def AI_play(self, player, id, positive, prev_action, prev_cards):
        '''
        AI is required here.
        Ai methods should be in manager.py or player.py?

        return a list of card index. Card is 1 indexed
        player.hand: Hand [H5 BJoker RJoker] -> [1, 2, 3] 
        play card BJoker RJoker -> return [2, 3]
        '''
        card = []
        if id == 1:
            card = self.greedy(player, id, positive, prev_action, prev_cards)
        else:
            card = self.a_search(player, id, positive, prev_action, prev_cards)
        if len(card) == 0:
            print("Player {} skip".format(id))
            return []
        print("Player {} plays {}".format(id, card))
        return self.card_to_index(player.hand.hand, card)

    

    


