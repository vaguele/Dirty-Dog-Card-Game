from player import Player
from deck import Deck
from game import Game
import socket
import threading

HOST = 'localhost'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}")

deck = Deck()
game = Game()
MIN_PLAYERS = 2

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("Welcome! Please type 'JOIN <name>' to enter the game.".encode())

    player_name = None

    while True:
        try:
            # decode converts first 1024 bytes to string
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break
            
            # JOIN command
            if msg.startswith("JOIN ") and game.game_started == False:
                player_name = msg[5:].strip()

                name_taken = False
                for p in game.players.values():
                    if p.name == player_name:
                        conn.send("That name is already taken. Choose another.".encode())
                        name_taken = True
                        break

                if name_taken:
                    continue

                game.add_player(conn, player_name)
                print(f"[JOIN] {player_name} joined from {addr}")
                conn.send(f"Hello, {player_name}! You joined the game.".encode())
                conn.send("Game starts when all players type <READY>".encode())
                conn.send(f"\nWaiting for other players...".encode())
                broadcast(f"{player_name} has joined the game.".encode(), conn)

            # SAY command
            elif msg.startswith("SAY "):
                if player_name:
                    chat_msg = msg[4:].strip()
                    print(f"[{player_name}] says: {chat_msg}")
                    broadcast(f"{player_name}: {chat_msg}".encode(), conn)
                else:
                    conn.send("You must JOIN before sending messages.".encode())


            # READY command
            elif msg.startswith("READY") and game.game_started == False:
                if player_name:
                    print(f"[{player_name}] is ready to play")
                    broadcast(f"{player_name} is ready to play".encode(), conn)
                    if game.mark_ready(conn):
                        broadcast("GAME STARTING!".encode(), None)
                        
                        game.start_game()
                        hands = game.build_hands()

                        broadcast("Place your bid using '<BID> #'".encode(), None)
                        game.BID_PHASE = True

                        for player_conn, hand_msg in hands.items():
                            player_conn.send(hand_msg.encode())

                        #game.debug_state()

                        current_conn = game.get_current_player_conn()
                        current_conn.send("\nIt's your turn.".encode())
            

            #MAKE SURE TO REMEMBER BID RESTRICTIONS FOR CERTAIN PLAYERS (last bid cannot equal number of cards)
            elif msg.startswith("BID ") and game.BID_PHASE == True:
                if not game.game_started:
                    conn.send("The game hasn't started yet.".encode())
                    continue

                if not game.is_player_turn(conn):
                    conn.send("It's not your turn.".encode())
                    continue

                if not game.last_conn:
                    game.last_conn = game.get_last_player_conn()
                
                game.BID_PHASE = True
                player = game.players[conn]
                bid = msg[4:].strip()

                if not bid.isdigit():
                    conn.send("Please enter a valid digit".encode())
                    continue
            
                elif int(bid) + game.bid_count == game.cards_per_player and conn == game.last_conn:
                    conn.send("Number of bids cannot equal number of cards in hand".encode())
                    continue

                broadcast(f"{player.name} has bid {bid} card(s)".encode(), conn)
                conn.send(f"Your bid of {bid} is accepted.".encode())
                game.place_bid(conn, int(bid))
                

                game.advance_turn()
                if len(game.bids) < len(game.players):
                    next_conn = game.get_current_player_conn()
                    next_conn.send("Your turn to bid. Type: '<BID> #'".encode())
                
                else:
                    game.debug_state()
                    hands = game.build_hands()

                    for player_conn, hand_msg in hands.items():
                        player_conn.send(hand_msg.encode())

                    first_conn = game.get_current_player_conn()
                    broadcast("All bids received.".encode(), None)
                    game.BID_PHASE = False
                    
                    first_conn.send("Your turn to play. Type: '<PLAY> card'".encode())
                    game.advance_turn()

                    next_conn = game.get_current_player_conn()
                    if next_conn != game.last_conn:
                        next_conn.send("Your turn to bid. Type: '<BID> #'".encode())
                    else:
                        next_conn.send("Your turn to bid. Type: '<BID> #'".encode())


            elif msg.startswith("PLAY ") and game.PLAY_PHASE == True:
                if not game.game_started:
                    conn.send("The game hasn't started yet.".encode())
                    continue

                if not game.is_player_turn(conn):
                    conn.send("It's not your turn.".encode())
                    continue

                card_played = msg[5:].strip()
                player = game.players[conn]

                # Validate card
                matching_card = None
                for card in player.hand:
                    if str(card) == card_played:
                        matching_card = card
                        break
                
                if not matching_card:
                    conn.send("You don't have that card.".encode())
                    continue

                # Remove card from hand and broadcast play



                # I NEED TO TRACK PLAYED CARDS SOMEHOW, TRUMPS, TRICKS,
                player.hand.remove(matching_card)
                broadcast(f"{player.name} played {card_played}".encode(), conn)
                
                conn.send(str(player.hand).encode())

                # Advance turn and notify next player
                game.advance_turn()
                next_conn = game.get_current_player_conn()
                next_conn.send("It's your turn.".encode())

            else:
                conn.send("Invalid command.".encode())

        except Exception as e:
            print(f"[ERROR] {addr} - {e}")
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    if player_name:
        broadcast(f"{player_name} has left the game.".encode(), conn)
        handle_disconnect(conn)
    conn.close()

def broadcast(message, sender_conn):
    for client in game.players:
        if client != sender_conn:
            try:
                client.send(message)
            except:
                print("[ERROR] Failed to send message to a client.")

def handle_disconnect(conn):
    game.remove_player(conn)
    # Optional: Reset game state or broadcast status
    if game.game_started and len(game.players) < game.min_players:
        broadcast("A player left. Game cannot continue.".encode(), None)
        game.reset()


def start():
    while True:
        conn, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, address))
        thread.start()

start()