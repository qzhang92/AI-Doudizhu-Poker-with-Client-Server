import sys
import random
import player
import socket
import cards

START = 'start'
BUFF_SIZE = 512

def main(argv):
    # Parse command line args
    args = get_cmd_args(argv)
    cmd = args[0]
    server_addr = args[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_addr)

    msg = cmd

    # Send message and wait for response
    sock.send(msg.encode())
    response = sock.recv(BUFF_SIZE).decode()
    print(response)
    user = player.Player(3)

    handle_deal(user, sock)
    user.sort_cards()
    user.print_hand()

    handle_landlord(user, sock)

def handle_deal(user, sock):
    response = sock.recv(BUFF_SIZE).decode()
    while response != 'OK':
        suit = response[0]
        rank = response[1:]
        if rank != 'Joker':
            card = cards.Card(suit, rank)
            user.add_card(card)
        else:
            card = cards.Card('H', 'A', response)
            user.add_card(card)
        sock.send('OK'.encode())
        response = sock.recv(BUFF_SIZE).decode()

def handle_landlord(user, sock):
    response = sock.recv(BUFF_SIZE).decode()
    print(response[2:])
    index = int(response[0])
    is_landlord = user.landlord_choice(index)
    sock.send("{}".format(is_landlord).encode())
    if is_landlord:
        user.set_landlord(3)
        handle_deal(user, sock)
        user.sort_cards()
        user.print_hand()
        

def get_cmd_args(argv):
    '''
    Validates and returns command line arguments.
    For `start` returns ('start', (host, port), num_players, wallet_amt, ante, name)
    For `join` returns ('join', (host, port), name)
    '''
    cmd = argv[1]

    # Ensure valid command
    if not cmd == START:
        print('unknown command', cmd)
        help()
        sys.exit(1)
    
    # Extract host, port
    try:
        host = argv[2]
        port = int(argv[3])
        server_addr = (host, port)
    except IndexError:
        print("host and port of server are required")
        help()
        sys.exit(1)
    
    return (cmd, server_addr)

def help():
    '''
    Prints a usage help message.
    '''
    print('usage:')
    print('client.py start <host> <port> ')


if __name__ == '__main__':
    main(sys.argv)
