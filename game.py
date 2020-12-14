import sys
import random

import cards
import player
import manager as mgr

HUMAN_ID = 3

def main(argv):
    # Create all players. Player 3 will be human
    players = []
    for i in range(1, 4):
        players.append(player.Player(i))
    
    print(players)

    #Initiate deck
    deck = cards.Deck()
    
    # Deal the cards
    handle_deal(players, deck)

    # Get the landlord
    landlord = handle_landlord(players, deck)

    # Game play
    game_play(players, landlord)

def handle_deal(players, deck):
    index = 0
    for i in range(51):
        card = deck.deal_card()
        players[index].add_card(card)
        index += 1
        index = index % 3
    
    for player in players:
        player.sort_cards()
        print(player.hand) #Todo delete it 
        

def handle_landlord(players, deck):
    '''
    Get the landlord in the players
    We first generate a random number in the players. Then loop through the players list.
    If we meet a computer (player 1 and 2), we calcuate the score of the cards and decide if 
    it is landlord
    If we meet human, we do this based on input
    If it is the last one in the round, then it has to be landlord.
    We need to add three cards to landlord
    return player id of the landlord
    '''
    cur = random.randint(0, 2)
    index = 0
    while index < 3:
        index += 1
        is_landlord = players[cur].landlord_choice(index)
        if is_landlord:
            players[cur].set_landlord(cur + 1)
            for i in range(3):  #landlord will get 3 extra cards
                card = deck.deal_card()
                players[cur].add_card(card)
                players[cur].hand.sort_cards()
            return cur
        else:
            print("Player {} is peasant.".format(cur + 1))
        cur += 1
        cur = cur % 3

def game_play(players, landlord):
    # Players is 0 indexed. player_id is 1 indexed
    '''
    Game process.
    players will take turns to play cards.
    There are two ways to play cards. One is positive play. You can play whatever valid ways you want
    The other one is negtive play. You have to play the way the previos player did.
    '''
    cur = landlord
    positive = True
    manager = mgr.Manager()
    prev_action = -1 # repesented by an index. See manager.card_style
    last_player = 0
    prev_cards = []
    while not game_over(players):
        
        player = players[cur]
        print("Player {} play game".format(player.id))

        if last_player == cur and not positive:
            positive = True

        if player.id == 3: #human
            valid = False
            while not valid:
                # handle input
                print(player.hand)

                cards = input("Please choose what card you want to play. \n Example: if you want to play 1st and 13rd card, type in: 1 13. 1-indexed \n")
                print(player.hand)
                card_list, valid = handle_input(cards, len(player.hand.hand))
                if valid and len(card_list) == 0 and positive:
                    print("Fisrt player must play cards.")
                    continue
                if valid and len(card_list) == 0: # Did not play card
                    break
                if manager.is_valid_play(card_list, player.hand.hand, positive, prev_action, prev_cards):
                    out_list = []
                    for index in card_list:
                        out_list.append(player.hand.hand[index])
                    print("Player {} plays {}".format(player.id, out_list))
                    prev_cards = player.card_play(card_list)
                    prev_action = manager.get_action(prev_cards)
                    valid = True
                    last_player = cur
                else:
                    valid = False
                    print("Wrong cards. Please choose again.")
            # Change positive if possible
            if positive:
                positive = False
        else: # Computer
            print("Prev_cards {} positive {} prev_action {}".format(prev_cards, positive, prev_action))
            card_list = manager.AI_play(player, player.id, positive, prev_action, prev_cards) # AI should play when it can play
            if not len(card_list) == 0:
                prev_cards = player.card_play(card_list)
                prev_action = manager.get_action(prev_cards)
                last_player = cur
                # Change positive if possible
                if positive:
                    positive = False
        cur +=1
        cur = cur % 3


def game_over(players):
    '''
    Check if the game is over
    When a player has no card in hand, it will win and game is over
    '''
    for player in players:
        if player.is_hand_empty():
            print("Game is over. {} wins.".format(player.id))
            return True
    return False

def handle_input(cards, hand_len):
    '''
    Turn the input string to a list of card
    return the list of card and if the input is valid
    '''
    if cards == None or len(cards) == 0:
        return [], True

    cards = cards.strip().split()
    result = []
    for card in cards:
        index = int(card) - 1
        if index < 0 or index > hand_len:
            return [], False
        result.append(index)

    return result, True
    

if __name__ == '__main__':
    main(sys.argv)