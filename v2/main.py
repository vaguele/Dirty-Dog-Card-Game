import random
from deck import Deck
from player import Player
from datetime import datetime
# Press Control + Command + Space to open the emoji panel

def play_round(deck, players, cards_per_player):

    def commentary():
        pass
    
    deck.deal(players, cards_per_player)
    for player in players:
        print(f"\n{player.name}'s hand: {player.hand}")

    trump = deck.reveal_trump()
    if trump:
        print(f"\nTrump suit: {trump}")
    else:
        print(f"\nNO TRUMP")

    for player in players:
        player.place_bid()

    for trick in range(cards_per_player):
        leading_suit = players[0].play_lead_card(trump)
        for player in players[1:]:
            player.play_card(leading_suit, trump)
                
        print(f"\n--{max(players).name} takes the trick--")  
        max(players).tricks += 1

        new_lead = players.index(max(players))
        for _ in range(new_lead):
            players.append(players.pop(0))
    
    for player in players:
        if player.bid == player.tricks:
            player.score += player.bid + 5
        else:
            player.score -= max(player.bid, player.tricks)
        print(f"{player.name}'s current score is {player.score}")
        player.round_reset()
    deck.refresh()

def play_game(deck, players, max_cards, cards_per_player):
    round = 1
    while cards_per_player != max_cards:
        print(f"\nROUND: {round}")
        play_round(deck, players, cards_per_player)
        cards_per_player += 1
        round += 1

    for _ in range(3):
        print(f"\nROUND: {round}")
        play_round(deck, players, cards_per_player)
        round += 1

    while cards_per_player != 0:
        print(f"\nROUND: {round}")
        play_round(deck, players, cards_per_player)
        cards_per_player -= 1
        round += 1

def tie_breaker():
    pass

def game_results(players):
    players.sort(key=lambda player: player.score, reverse = True)

    print("🏆 Final Leaderboard 🏆")

    filename = datetime.now().strftime("leaderboard_%Y-%m-%d_%H-%M-%S.txt")
    with open(filename, "w") as file:
        for i in range(len(players)):
            if i == 0:
                print(f"🥇 {players[i].name}: {players[i].score}")
                file.write(f"🥇 {players[i].name}: {players[i].score}\n")
            elif i == 1:
                print(f"🥈 {players[i].name}: {players[i].score}")
                file.write(f"🥈 {players[i].name}: {players[i].score}\n")
            elif i == 2:
                print(f"🥉 {players[i].name}: {players[i].score}")
                file.write(f"🥉 {players[i].name}: {players[i].score}\n")
            else:
                print(f"{i+1}. {players[i].name}: {players[i].score}")
                file.write(f"{i+1}. {players[i].name}: {players[i].score}\n")

def main():
    players = []
    
    while True:
        try:
            num_players = int(input("Please enter the number of players: "))
            if num_players < 2:
                raise ValueError("Too few players. Minimum is 2.")
            if num_players > 51:
                raise ValueError("Too many players. Max is 51.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")


    for _ in range(num_players):
        players.append(Player(input("Enter Name: ")))
    
    random.shuffle(players)
    print(f"\nHere is the game's order: {players}")

    deck = Deck()
    # max_cards = len(deck.cards) -1 // num_players
    max_cards = 3
    cards_per_player = 1

    play_game(deck, players, max_cards, cards_per_player)
    game_results(players)

    while True:
        try:
            restart = input("\nWould you like to play again? (Y/N): ").upper()
            if restart not in ["Y", "N"]:
                raise ValueError
            break
        except ValueError:
            print("Invalid Input. Please enter Y or N")

    while restart == "Y":
        for player in players:
            player.game_reset()

        play_game(deck, players, max_cards, cards_per_player)
        game_results(players)

        while True:
            try:
                restart = input("\nWould you like to play again? (Y/N): ").upper()
                if restart not in ["Y", "N"]:
                    raise ValueError
                break
            except ValueError:
                print("Invalid Input. Please enter Y or N")

if __name__ == "__main__":
    main()