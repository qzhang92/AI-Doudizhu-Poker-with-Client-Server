import sys
import random
import player
import socket
import manager
import cards

BUFF_SIZE = 512

def main(argv):
    # Parse command line arguments
    addr = get_cmd_args(argv)

    # Setup server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen()

    print('Server started, waiting for player.')

    players = []
    
    players.append(player.Player(1))
    players.append(player.Player(2))

    # Wait for `start` from a player and set-up game
    conn = wait_for_start(sock, players)

    print(players)

    #Initiate deck
    deck = cards.Deck()
    
    # Deal the cards
    handle_deal(players, deck, conn)
    # Get the landlord
    landlord = handle_landlord(players, deck, conn)

    # Game play
    game_play(players, landlord, conn)

def wait_for_start(sock, players):
    while True:
        # Get connection
        start = 'start'
        conn, addr = sock.accept()
        msg = conn.recv(BUFF_SIZE).decode()
        parts = msg.split()

        # Ensure start message
        if parts[0] != start:
            err = 'err start waiting for start but received: ' + msg
            conn.send(err.encode())
        else:
            conn.send("Player 3 joined. Game start.".encode())
            return conn

def handle_deal(players, deck, conn):
    index = 0
    for i in range(51):
        card = deck.deal_card()
        if index == 2:
            rec = ''
            msg = card.suit + card.rank
            while rec != 'OK':
                conn.send(msg.encode())
                rec = conn.recv(BUFF_SIZE).decode()
        else:
            players[index].add_card(card)
        index += 1
        index = index % 3
    conn.send("OK".encode())
    for player in players:
        player.sort_cards()
        player.print_hand() #Todo delete it 

def handle_landlord(players, deck, conn):
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
        if cur == 2: # client
            message = "{} Please choose if you would like to be landlord".format(index)   
            conn.send(message.encode())  
            response = conn.recv(BUFF_SIZE).decode()
            if response == 'True':
                print("Player {} is landlord.".format(cur + 1))
                for i in range(3):  #landlord will get 3 extra cards
                    card = deck.deal_card()
                    rec = ''
                    msg = card.suit + card.rank
                    print(msg)
                    while rec != 'OK':
                        conn.send(msg.encode())
                        rec = conn.recv(BUFF_SIZE).decode()
                conn.send("OK".encode())
                return cur
            else:
                print("Player {} is peasant.".format(cur + 1))
        else: # computer
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


def game_play(players, landlord, conn):
    # Players is 0 indexed. player_id is 1 indexed
    '''
    Game process.
    players will take turns to play cards.
    There are two ways to play cards. One is positive play. You can play whatever valid ways you want
    The other one is negtive play. You have to play the way the previos player did.
    '''
    cur = landlord
    positive = True
    
    prev_action = -1 # repesented by an index. See manager.card_style
    last_player = 0
    prev_cards = []

    while not game_over(players, conn):
        print("Player {} play game".format(cur + 1))

        if last_player == cur and not positive:
            positive = True
        if cur == 2:
            msg = "{}".format(positive)
            conn.send(msg.encode())
            response = conn.recv(BUFF_SIZE).decode()
            cards = response.strip().split()
            card_list = []
            for card in cards:
                '''
                This is wrong. We need to receive Suit + rank style responses. Then convert to card_list
                '''
                card_list.append(card)
            print(card_list)
        else:
            player = players[cur]
            print("Prev_cards {} positive {} prev_action {}".format(prev_cards, positive, prev_action))
            card_list = player.AI_play(player, player.id, positive, prev_action, prev_cards) # AI should play when it can play
            if not len(card_list) == 0:
                prev_cards = player.card_play(card_list)
                prev_action =player.get_action(prev_cards)
                last_player = cur
                msg = "Player {} plays {}".format(id, prev_cards)
                print(msg)
                conn.send(msg.encode())
                resp = conn.recv(BUFF_SIZE).decode()
            else:
                msg = "Player {} skipped".format(player.id)
                print(msg)
                conn.send(msg.encode())
                resp = conn.recv(BUFF_SIZE).decode()

        # Change positive if possible
        if positive:
            positive = False
        cur += 1
        cur = cur % 3

def game_over(players, conn):
    '''
    Check if the game is over
    When a player has no card in hand, it will win and game is over
    '''
    for player in players:
        if player.is_hand_empty():
            print("Game is over. {} wins.".format(player.id))
            return True
    resp = conn.recv(BUFF_SIZE).decode()
    if resp == 'OVER':
        print("Game is over, Player 3 wins")
        return True
    return False


def get_cmd_args(argv):
    '''
    Validates command line arguments and returns a tuple of (host, port) to
    start the server on.
    '''
    if len(argv) != 3:
        print('missing required arguments')
        help()
        sys.exit(1)

    host = argv[1]
    port = int(argv[2])
    return (host, port)

def help():
    '''
    Prints a usage help message.
    '''
    print('usage:')
    print('server.py <host> <port>')

if __name__ == '__main__':
    main(sys.argv)