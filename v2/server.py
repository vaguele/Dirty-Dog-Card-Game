from game import Game, DEFAULT_MAX_HANDS
import socket
import threading

HOST = 'localhost'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allow quick restart of the server on the same port
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}")

game = Game()
# Notes on cleanup:
# - The Deck instance and Player import that used to be here were removed because
#   the Game object is the authoritative owner of the deck and player objects.
#   Creating a separate Deck() or importing Player here was redundant and led
#   to duplicated state.
# - MIN_PLAYERS constant was removed since the Game instance exposes its
#   own `min_players` configuration and that single source of truth should be used.


def format_player_list():
    """Return a nicely formatted list of current players with score and READY status."""
    lines = ["Players in this game:"]
    for i, conn in enumerate(game.players.keys(), start=1):
        p = game.players[conn]
        status = "[READY]" if conn in game.ready_players else "[NOT READY]"
        lines.append(f"{i}) {p.name} {status}")
    return "\n".join(lines)

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
                # Send the joining player a formatted list of current players
                conn.send(format_player_list().encode())
                conn.send("\n\nGame starts when all players type <READY>".encode())
                # Instead of a join message, broadcast the updated player list
                broadcast(format_player_list().encode(), conn)

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
                    # Mark the player as ready first so the formatted list includes them
                    all_ready = game.mark_ready(conn)
                    # Broadcast only the updated formatted player list (no separate text)
                    broadcast(format_player_list().encode(), None)
                    if all_ready:
                        # Remind players of the max before starting
                        try:
                            broadcast(f"\nMax hand size for this match: {DEFAULT_MAX_HANDS}".encode(), None)
                        except Exception:
                            pass
                        broadcast("\nGAME STARTING!".encode(), None)
                        
                        game.start_game()
                        hands = game.build_hands()

                        # Reveal trump to all players before bidding
                        if game.trump:
                            broadcast(f"\nTRUMP is {game.trump}".encode(), None)
                        else:
                            broadcast("\nNO TRUMP this hand".encode(), None)

                        broadcast("\nPlace your bid using '<BID> #'".encode(), None)
                        game.BID_PHASE = True

                        for player_conn, hand_msg in hands.items():
                            player_conn.send(hand_msg.encode())

                        current_conn = game.get_current_player_conn()
                        current_conn.send("\nIt's your turn.".encode())
            
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
                    next_conn.send("\nYour turn to bid. Type: '<BID> #'".encode())
                
                else:
                    game.debug_state()

                    first_conn = game.get_current_player_conn()
                    broadcast("\nAll bids received.".encode(), None)
                    game.BID_PHASE = False
                    
                    hands = game.build_hands()

                    for player_conn, hand_msg in hands.items():
                        player_conn.send(hand_msg.encode())
                    first_conn.send("\nYour turn to play. Type: '<PLAY> card'".encode())

                    game.PLAY_PHASE = True
                    game.advance_turn()

            elif msg.startswith("PLAY ") and game.PLAY_PHASE == True:
                if not game.game_started:
                    conn.send("The game hasn't started yet.".encode())
                    continue

                if not game.is_player_turn(conn):
                    conn.send("It's not your turn.".encode())
                    continue

                card_played = msg[5:].strip()
                player = game.players[conn]

                # Validate card is in player hand
                matching_card = None
                for card in player.hand:
                    if str(card) == card_played:
                        matching_card = card
                        break

                if not matching_card:
                    conn.send("You don't have that card.".encode())
                    continue

                # Remove card from hand and broadcast play
                #
                #   
                #
                #
                # I NEED TO TRACK PLAYED CARDS SOMEHOW, TRUMPS, TRICKS,
                # store the actual Card object instead of string for resolution
                game.played_cards[conn] = matching_card
                player.hand.remove(matching_card)

                broadcast(f"{player.name} played {card_played}".encode(), conn)
                conn.send(str(player.hand).encode())

                # If this is the first card of the trick, set leading suit
                if len(game.played_cards) == 1:
                    game.leading_suit = matching_card.suit

                # Advance turn and notify next player
                game.advance_turn()
                if len(game.played_cards) < len(game.players):
                    next_conn = game.get_current_player_conn()
                    next_conn.send("\nYour turn to PLAY. Type: '<PLAY> card'".encode())
                else:
                    # All players have played: resolve trick
                    game.debug_state()
                    broadcast("\nEach player has played a card.".encode(), None)

                    # Determine winner by computing a strength score
                    strengths = []
                    for pconn, card in game.played_cards.items():
                        base = card.weight[card.value]
                        # Only trump or leading-suit cards can win. Dumped non-trump cards score 0.
                        if game.trump and card.suit == game.trump:
                            score = base + 100
                        elif card.suit == game.leading_suit:
                            score = base + 50
                        else:
                            score = 0
                        strengths.append((score, pconn, card))

                    # select the highest score (ties are unexpected per rules)
                    strengths.sort(reverse=True, key=lambda x: x[0])
                    winner_score, winner_conn, winning_card = strengths[0]
                    winner_name = game.players[winner_conn].name
                    broadcast(f"\n{winner_name} won the trick with {winning_card}".encode(), None)

                    # Award trick to player
                    game.players[winner_conn].tricks += 1

                    # Clear played cards for next trick and set next turn to winner
                    game.played_cards = {}
                    game.leading_suit = None
                    # set current turn index to winner
                    if winner_conn in game.turn_order:
                        game.current_turn_index = game.turn_order.index(winner_conn)
                    # advance to next (winner leads next)
                    game.advance_turn()

                    # Check end of round (all cards played)
                    remaining = any(p.hand for p in game.players.values())
                    if not remaining:
                        # End of hand — compute scoring per rules
                        for pconn, player in game.players.items():
                            if player.tricks == player.bid:
                                player.score += 5 + player.bid
                                pconn.send(f"You made your bid! Score +{5 + player.bid}. Total: {player.score}".encode())
                            else:
                                player.score -= max(player.bid, player.tricks)
                                pconn.send(f"You missed your bid. Tricks: {player.tricks}, Bid: {player.bid}. Total: {player.score}".encode())
                        broadcast("\nRound complete.".encode(), None)
                        # reset for next round
                        game.reset()
                    else:
                        # Notify next player to play
                        next_conn = game.get_current_player_conn()
                        next_conn.send("\nYour turn to PLAY. Type: '<PLAY> card'".encode())

            else:
                conn.send("Invalid command.".encode())

        except Exception as e:
            print(f"[ERROR] {addr} - {e}")
            break

    print(f"[DISCONNECT] {addr} disconnected.")
    if player_name:
        broadcast(f"{player_name} has left the game.".encode(), conn)
        # Broadcast updated player list after disconnect
        broadcast(format_player_list().encode(), None)
        handle_disconnect(conn)
    conn.close()

def broadcast(message, sender_conn):
    # Iterate over a snapshot of current clients to allow safe removal
    for client in list(game.players.keys()):
        if client != sender_conn:
            try:
                client.send(message)
            except Exception as e:
                print(f"[ERROR] Failed to send message to a client: {e}")
                try:
                    client.close()
                except:
                    pass
                # Clean up client from game state
                if client in game.players:
                    game.remove_player(client)

def handle_disconnect(conn):
    game.remove_player(conn)
    # Optional: Reset game state or broadcast status
    if game.game_started and len(game.players) < game.min_players:
        broadcast("A player left. Game cannot continue.".encode(), None)
        game.reset()

def start():
    try:
        while True:
            conn, address = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, address), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print('\n[SERVER] Shutting down...')
    finally:
        try:
            server.close()
        except:
            pass

start()