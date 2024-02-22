import random

from cls_Tile import Tile
#create a deck and shuffle the order
def initialize_deck():
    deck = []
    for i in range(2):
        for s in range(1, 6): #5 colours
            for v in range(1, 16): # 15 numbers
                tile = Tile(s, v)
                tile.ID = (s-1)*15+v+(i*75)
                deck.append(tile)
    random.shuffle(deck)
    return deck

def return_deck(deck,tile):
    deck.append(tile)
    random.shuffle(deck)
    return deck

def next_turn(players,playing_area):
    current_turn = -1
    for player in players:
        if player.turn:
            current_turn = player.position
            players[current_turn].turn = False
            break
    if current_turn < len(players)-1:
        players[current_turn+1].turn = True
    else:
        players[0].turn = True
    players[0].tiles_in_current_turn = []
    playing_area.lock_tile()
    if players[0].turn:
        temp_dict = {}
        for pos,tile in playing_area.playing_area.items():
            temp_dict[pos] = tile
        players[0].before_tiles = temp_dict
        print('before_tiles',len(players[0].before_tiles))
    else:
        players[0].before_tiles = {}

def first_one_tile(players,deck):
    for player in players:
        player.first_one_tile = player.draw_first_tile(deck)

def find_first(players,deck):
    max = 1
    for player in players:
        if player.first_one_tile.value > max:
            max = player.first_one_tile.value
    for player in players:
        if player.first_one_tile.value == max:
            player.turn = True
        return_deck(deck,player.first_one_tile)
