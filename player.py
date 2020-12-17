import cards
import manager

LANDLORD_UTIL = 40

class Player:
    '''
    Represents the three player. The default role is peasant. 
    Player 3 is human
    Player 1 is search_AI
    Player 2 reinforcement_AI

    Search_AI:
    1. DFS
    2. A* search
    '''
    def __init__(self, id):
        '''
        id is 1 indexed
        '''
        self.id = id
        self.role = 'Peasant'
        self.hand = cards.Hand()
        self.manager = manager.Manager()

    def set_landlord(self, id):
        if self.id != id:
            raise ValueError("Wrong user!")
        self.role = "Landlord"
        msg = "Player {} is landlord".format(id)
        print(msg)

    def add_card(self, card):
        self.hand.add_card(card)

    def sort_cards(self):
        self.hand.sort_cards()
    
    def landlord_choice(self, index):
        if index == 3:   #If this is the last player in the round
            return True
        if self.id == 3:
            while True:
                is_landlord = input("Do you wnat to become the landlord? (Y/N)")
                if is_landlord == 'Y':
                    return True
                elif is_landlord == 'N':
                    return False
        else:
            return self.landlord_util() >= LANDLORD_UTIL

    def landlord_util(self):
        '''
        Calculate the utility of the current cards
        '''
        score = 0
        card_list = self.hand.hand
        length = len(card_list)
        #if card_list[length - 1].value == 170 and card_list[length - 2].value == 160:
        #    score += 16
        legal_actions = self.manager.legal_actions(card_list)
        if len(legal_actions[12]) > 0: # Rocket
            score += 16
        if len(legal_actions[11]) > 0: # Boomb
            score += 8 * len(legal_actions[11])
        i = 0
        val = 0
        while i < length:
            val += int(card_list[i].value / 10)
            i += 1
        score += int(val / 5)
        return score

    def card_play(self, card_list):
        '''
        play the card in the list
        return a list of cards
        '''
        card_list.sort(reverse = True)
        result = []
        for card_index in card_list:
            card = self.hand.remove_card(card_index + 1)
            result.append(card)
        return result

    def is_hand_empty(self):
        '''
        return if the hand is empty
        '''
        return len(self.hand.hand) == 0

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
        
       
        

