
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

    def legal_actions(self, hand): # hand is array
        '''
        List legal actions
        hand: current hand of the game
        https://github.com/thuxugang/doudizhu/blob/master/myclass.py

        Airplane and chain may be removed. They are super hard
        legal actions is called every time you are on your turn
        The moves are based on 1-index card index. Because cards.Hand.remove(self, card_id)
        There is a hand of cards. We evaluate every card by all ways of card play 1- 5 11 12
        On way 1: we find all possible combinations of solo
        Same applies to other ways 
        return result : a dict, where key is 1 - 5 and 11 and 12 
                        value is a list of card_list on possible action under key
        '''
        result = dict()
        card_dict = dict()
        for card in hand:
            key = int(card.value / 10)
            if key in card_dict:
                card_dict[key] += 1
            else:
                card_dict[key] = 1
        for i in range(1, 13):
            result[i] = []
        # 1
        for card in hand:
            action = [card]
            result[1].append(action)
        # 2
        for key in card_dict:
            if card_dict[key] >= 2:
                card = self.get_card_from_hand(hand, key, 2)
                action = [hand[card[0]], hand[card[1]]]
                result[2].append(action) 
        
        # 3
        for key in card_dict:
            if card_dict[key] >= 3:
                card = self.get_card_from_hand(hand, key, 3)
                action = [hand[card[0]], hand[card[1]], hand[card[2]]]
                result[3].append(action)
        
        # 4
        for key in card_dict:
            if card_dict[key] >= 3:
                card = self.get_card_from_hand(hand, key, 3)
                action = [hand[card[0]], hand[card[1]], hand[card[2]]]
                for i in range(len(hand)):
                    if not int(hand[i].value / 10) == key:
                        action.append(hand[i])
                        cards = action.copy()
                        result[4].append(cards)
                        action.remove(hand[i])
        # 5
        for key in card_dict:
            if card_dict[key] >= 3:
                card = self.get_card_from_hand(hand, key, 3)
                action = [hand[card[0]], hand[card[1]], hand[card[2]]]
                for cards in result[2]:
                    if not int(cards[0].value / 10) == int(action[0].value / 10):
                        array = action.copy()
                        array.append(cards[0])
                        array.append(cards[1])
                        result[5].append(array)
        # 11
        for key in card_dict:
            if card_dict[key]== 4:
                card = self.get_card_from_hand(hand, key, 4)
                action = []
                for index in card:
                    action.append(hand[index])
                result[11].append(action)
        # 12
        b_joker = False
        r_joker = False
        for key in card_dict:
            if key == 16:
                b_joker = True
            if key == 17:
                r_joker = True
        if b_joker and r_joker:
            array =[self.get_card_from_hand(hand, 16, 1)[0], self.get_card_from_hand(hand, 17, 1)[0]]
            action = []
            for index in array:
                action.append(hand[index])
            result[12].append(action)

        #print("Leagal actions are {} end".format(result))
        return result

    
    def get_card_from_hand(self, hand, key, num):
        result = []
        for i in range(len(hand)):
            card = hand[i]
            val = int(card.value / 10)
            if val == key:
                result.append(i)
                num -= 1
                if num == 0:
                    return result
        return []


        
    def greedy(self, player, id, positive, prev_action, prev_cards):
        #This is a greedy search algorithm.
        #We find the cards with least utility under negative play
        #return a list of card index. Card is 1 indexed
        cur_card_list = player.hand.hand
        legal_actions = self.legal_actions(cur_card_list)
        if not positive:
            if len(legal_actions[prev_action]) == 0 and len(legal_actions[11]) == 0 and len(legal_actions[11]) == 0:
                return [] # In this neg round, we do not have a card to play
            elif len(legal_actions[prev_action]) > 0:
                same_style_actions = legal_actions[prev_action]
                prev_util = self.util_greedy(prev_cards)
                result = []
                util_g = sys.maxsize
                for card_list in same_style_actions:
                    # card list is a [card]
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = self.util_greedy(card_list)  # Todo
                    if cur_util > prev_util and util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
                return result # Greedy will play card when it can play
            elif prev_action != 11 and len(legal_actions[11]) > 0: # handle bomb
                same_style_actions = legal_actions[11]
                result = []
                util_g = sys.maxsize
                for card_list in same_style_actions:
                    # card list is a [int]
                    # cur_card = self.index_to_card(cur_card_list, card_list)
                    cur_util = self.util_greedy(card_list)
                    if util_g > cur_util: # No prev_util with boomb
                        result = card_list.copy()
                        util_g = cur_util
                return result
            elif len(legal_actions[12]) > 0: # rocket There is only one rocket possible in the game
                return legal_actions[12][0]
            
            return []
        else: # positive play play with least utility
            result = []
            util_g = sys.maxsize
            if len(legal_actions[12]) > 0:
                same_style_actions = legal_actions[12]
                card_list = legal_actions[12][0] # [int]
                # cur_card = self.index_to_card(cur_card_list, card_list)
                cur_util = self.util_greedy(card_list)
                util_g = (12 * self.util_greedy(card_list)) / 2
                result = card_list
            if len(legal_actions[11]) > 0:
                same_style_actions = legal_actions[11]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = (11 * self.util_greedy(card_list)) / 4  # Todo
                    if util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
            if len(legal_actions[5]) > 0:
                same_style_actions = legal_actions[5]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int((2 * self.util_greedy(card_list)) / 5)  # Todo
                    if util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
            if len(legal_actions[4]) > 0:
                same_style_actions = legal_actions[4]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int(self.util_greedy(card_list) / 4)  # Todo
                    if util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
            if len(legal_actions[3]) > 0:
                same_style_actions = legal_actions[3]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int(5 * self.util_greedy(card_list) / 3)  # Todo
                    if util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
            if len(legal_actions[2]) > 0:
                same_style_actions = legal_actions[2]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int(3 * self.util_greedy(card_list) / 2)  # Todo
                    if util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
            if len(legal_actions[1]) > 0:
                same_style_actions = legal_actions[1]
                for card_list in same_style_actions:
                    cur_util = 4 * self.util_greedy(card_list)  # Todo
                    if util_g > cur_util:
                        result = card_list.copy()
                        util_g = cur_util
            return result
        
    def a_search(self, player, id, positive, prev_action, prev_cards):
        '''
        This is a greedy search algorithm.
        We find the cards with least utility under negative play
        return a list of card index. Card is 1 indexed
        '''
        cur_card_list = player.hand.hand
        legal_actions = self.legal_actions(cur_card_list)
        if not positive:
            
            if len(legal_actions[prev_action]) == 0 and len(legal_actions[11]) == 0 and len(legal_actions[11]) == 0:
                return [] # In this neg round, we do not have a card to play
            elif len(legal_actions[prev_action]) > 0:
                same_style_actions = legal_actions[prev_action]
                prev_util = self.util_greedy(prev_cards)
                result = []
                util_a = sys.maxsize
                for card_list in same_style_actions:
                    # card list is a [card]
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    util_g = self.util_greedy(card_list) 
                    cur_util = self.util_greedy(card_list) + self.util_h(cur_card_list, card_list)  # Todo
                    if util_g > prev_util and util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
                return result # Greedy will play card when it can play
            elif prev_action != 11 and len(legal_actions[11]) > 0: # handle bomb
                same_style_actions = legal_actions[11]
                result = []
                util_a = sys.maxsize
                for card_list in same_style_actions:
                    # card list is a [int]
                    # cur_card = self.index_to_card(cur_card_list, card_list)
                    cur_util = self.util_greedy(card_list) + self.util_h(cur_card_list, card_list)
                    if util_a > cur_util: # No prev_util with boomb
                        result = card_list.copy()
                        util_a = cur_util
                return result
            elif len(legal_actions[12]) > 0: # rocket There is only one rocket possible in the game
                return legal_actions[12][0]
            
            return []
        else: # positive play play with least utility
            result = []
            util_a = sys.maxsize
            if len(legal_actions[12]) > 0:
                same_style_actions = legal_actions[12]
                card_list = legal_actions[12][0] # [int]
                # cur_card = self.index_to_card(cur_card_list, card_list)
                cur_util = self.util_greedy(card_list)
                util_a = (12 * cur_util) / 2 + self.util_h(cur_card_list, card_list)
                result = card_list.copy()
            if len(legal_actions[11]) > 0:
                same_style_actions = legal_actions[11]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = (11 * self.util_greedy(card_list)) / 4  + self.util_h(cur_card_list, card_list) # Todo
                    if util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
            if len(legal_actions[5]) > 0:
                same_style_actions = legal_actions[5]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int((2 * self.util_greedy(card_list)) / 5) + self.util_h(cur_card_list, card_list)  # Todo
                    if util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
            if len(legal_actions[4]) > 0:
                same_style_actions = legal_actions[4]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int(self.util_greedy(card_list) / 4) + self.util_h(cur_card_list, card_list)  # Todo
                    if util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
            if len(legal_actions[3]) > 0:
                same_style_actions = legal_actions[3]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int(5 * self.util_greedy(card_list) / 3) + self.util_h(cur_card_list, card_list)  # Todo
                    if util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
            if len(legal_actions[2]) > 0:
                same_style_actions = legal_actions[2]
                for card_list in same_style_actions:
                    #cur_card = self.index_to_card(cur_card_list, card_list) # Todo
                    cur_util = int(3 * self.util_greedy(card_list) / 2) + self.util_h(cur_card_list, card_list)  # Todo
                    if util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
            if len(legal_actions[1]) > 0:
                same_style_actions = legal_actions[1]
                for card_list in same_style_actions:
                    cur_util = 4 * self.util_greedy(card_list) + self.util_h(cur_card_list, card_list)  # Todo
                    if util_a > cur_util:
                        result = card_list.copy()
                        util_a = cur_util
            return result

    def index_to_card(self, hand, card_list):
        result = []
        for index in card_list:
            result.append(hand[index])
        return result

    def card_to_index(self, hand, cards):
        result = []
        j = 0
        for i in range(len(hand)):
            if hand[i] == cards[j]:
                result.append(i)
                j += 1
                if j == len(cards):
                    return result
        return result

    def util_greedy(self, cards):
        result = 0
        for card in cards:
            result += int(card.value / 10)
        return result

    def util_h(self, hand, card_list):
        cards = []
        for card in hand:
            if card not in card_list:
                cards.append(card)
        if len(cards) == 0:
            return 0
        result = 0
        return result - self.util_greedy(cards)

    


