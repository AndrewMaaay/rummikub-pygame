import pygame
import os
import random

from utils import *
from settings import (
    tile_width,
    tile_height,
    screen_width,
    screen_height,
    tile_interval_x,
    tile_interval_y,
    shelf_width,
    shelf_height,
    window_width,
    img_path,
)


# --------------------------------------------------------------

class Player:
    def __init__(self, name, position, hand_tiles_size = 42):
        self.name = name
        self.position = position
        self.shelf_pos, self.shelf_orientation = self.calculate_shelf_position()
        #initialize the hand tiles, key is x and y, and the value is instantiation of Tiles
        #if there are no tiles in this position, then value is None
        self.tiles = {self.get_tile_position(i): None for i in range(hand_tiles_size)}
        # 头像和回合部分
        self.profile_img_list=["player_0.png","player_1.png","player_2.png","player_3.png"]
        self.profile_width = 120
        # self.profile_x = 20
        self.profile_gap = 20
        self.profile_gap_name = 20
        # profile_pos_list=
        #initialize the position of dragged tile
        self.dragging = None  
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.isSelect = False
        self.show_alert_notrule = False
        self.show_alert_innitial = False
        self.select_tiles = []
        self.first_one_tile = None
        self.tiles_in_current_turn = []
        self.play_for_me = False        
        self.turn = False
        self.score = 0
        self.has_initial_meld = False  #initial_meild must place tiles that total at least 30 points
        self.before_tiles={}
        self.show_tiles = False
        self.ai_initial_sum = None
        self.win = False

        self.hand_tile_point = (self.shelf_pos[0] + 20, self.shelf_pos[1] + 5)

        
    def calculate_shelf_position(self):
        # Bottom position
        if self.position == 0:
            return ((screen_width // 2 - shelf_width // 2, screen_height - shelf_height - 10), 'horizontal')
        # Top position
        elif self.position == 1:
            return ((screen_width // 2 - shelf_width // 2, shelf_height -170), 'horizontal')
        # Left position
        elif self.position == 2:
            return ((shelf_width-710, screen_height//2  - 400), 'vertical')
        # Right position
        elif self.position == 3:
            return ((screen_width - shelf_width + 510, screen_height // 2 -400), 'vertical')

    def draw_tile(self, tile_deck):
        for position in self.tiles:
            if self.tiles[position] is None:  # find an empty space
                if tile_deck:
                    self.tiles[position] = tile_deck.pop() #draw a tile
                return
    
    def select_draw_tile(self, tile_deck = [], is_return = False, select_index = -1):
        if is_return:
            return_deck(tile_deck,self.select_tiles[0])
            self.select_tiles = []
        elif select_index >=0:
            for position in self.tiles:
                if self.tiles[position] is None:
                    self.tiles[position] = self.select_tiles[select_index]
                    self.select_tiles.pop(select_index)
                    break
        elif tile_deck!=[]:
            for i in range(2):
                self.select_tiles.append(tile_deck.pop())
        return 

    def draw_first_tile(self, tile_deck):
        return tile_deck.pop() #draw a tile

            
    def get_tile_position(self, index):
        if self.shelf_orientation == 'horizontal':
            col = index % ((shelf_width - 20) // (tile_width + tile_interval_x))
            row = index // ((shelf_width - 20) // (tile_width + tile_interval_x))
            x = self.shelf_pos[0] + 20 + col * (tile_width + tile_interval_x)
            y = self.shelf_pos[1] + row * (tile_height + tile_interval_y)
        elif self.shelf_orientation == 'vertical':
            col = index % ((shelf_height - 20) // (tile_height + tile_interval_y))
            row = index // ((shelf_height - 20) // (tile_height + tile_interval_y))
            x = self.shelf_pos[0] + col * (tile_height + tile_interval_y)
            y = self.shelf_pos[1] + 20 + row * (tile_width + tile_interval_x)
        return (x, y)
    

    def start_dragging(self, mouse_x, mouse_y, playing_area):
        for position, tile in self.tiles.items():
            if tile is not None:
                tile_rect = pygame.Rect(position[0], position[1], tile_width, tile_height)
                if tile_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = tile
                    self.dragging_original_position = position
                    self.drag_offset_x = position[0] - mouse_x
                    self.drag_offset_y = position[1] - mouse_y
                    self.tiles[position] = None
                    playing_area.is_dragging = True
                    playing_area.check_insert_position(tile, (mouse_x, mouse_y)) 
                    return
                
    def cancel_play_tile(self,playing_area):
        for back_tile in self.tiles_in_current_turn:
            for pos, playing_area_tile in playing_area.playing_area.items():
                if playing_area_tile!=None and back_tile.ID == playing_area_tile.ID and playing_area.playing_area[pos].unlock == True:
                    playing_area.playing_area[pos] = None
                    for pos2, hand_tile in self.tiles.items():
                        if hand_tile == None:
                            self.tiles[pos2] = back_tile
                            break
                    break
        if self.before_tiles !={}:
            playing_area.playing_area = self.before_tiles
        # self.before_tiles = {}
        self.tiles_in_current_turn = []

    def stop_dragging(self, playing_area):
        if self.dragging:
            final_position = pygame.mouse.get_pos()
            tile_placed = False
            place_pos = None
            positions = sorted(playing_area.playing_area.keys(), key=lambda x: (x[1], x[0]))

            if self.turn:
                for i, (area_position, tile) in enumerate(playing_area.playing_area.items()):
                    area_rect = pygame.Rect(area_position[0], area_position[1], tile_width, tile_height)
                    if area_rect.collidepoint(final_position):
                        if playing_area.playing_area[area_position] is not None:
                            dragging = self.dragging
                            shift_direction = playing_area.shift_tiles_backward(area_position, playing_area.playing_area, dragging)
                            if shift_direction == 0:
                                place_pos = area_position
                            else:
                                place_pos = positions[i-1]
                            # playing_area.playing_area[area_position] = self.dragging
                        else:
                            playing_area.playing_area[area_position] = self.dragging
                            place_pos = area_position
                        self.tiles_in_current_turn.append(self.dragging)
                        print('ddsxd',len(self.tiles_in_current_turn))
                        place_pos = area_position
                        tile_placed = True
                        break

            if not tile_placed:
                for pos in self.tiles:
                    tile_rect = pygame.Rect(pos[0], pos[1], tile_width, tile_height)
                    if tile_rect.collidepoint(final_position):
                        if self.tiles[pos] is not None:
                            self.tiles[self.dragging_original_position], self.tiles[pos] = \
                                self.tiles[pos], self.dragging
                        else:
                            self.tiles[pos] = self.dragging

                        tile_placed = True
                        break

            if not tile_placed:
                self.tiles[self.dragging_original_position] = self.dragging

            self.dragging = None
            playing_area.insert_position = None
            
            if place_pos:
                playing_area.put_down_tiles(place_pos)

    def play_tiles(self, playing_area, deck):
        valid_plays = Rules.is_valid_play(self.tiles)
        
        if self.ai_initial_sum == None:
            sum = 0
            for valid in valid_plays:
                for tile in valid:
                    sum+=tile.value
            if sum>=30:
                self.has_initial_meld = True
                self.ai_initial_sum = True
            else:self.ai_initial_sum = False
        
        if not valid_plays or (self.ai_initial_sum == False and self.has_initial_meld == False):
            self.draw_tile(deck)
            self.ai_initial_sum = None
            return

        #         selected_play = random.choice(valid_plays)
        selected_play = valid_plays.pop()

        space_found = False
        positions = list(playing_area.playing_area.keys())
        for start_pos in playing_area.playing_area.keys():
            current_pos = start_pos
            space_needed = len(selected_play)
            space_available = 0

            while space_available < space_needed and playing_area.playing_area.get(current_pos) is None:
                space_available += 1
                # current_pos = (current_pos[0] + tile_width + tile_interval_x, current_pos[1])
                current_pos = positions[positions.index(current_pos) + 1]

            if space_available == space_needed:
                # start_pos =(start_pos[0] + tile_width + tile_interval_x,start_pos[1])
                start_pos = positions[positions.index(start_pos) + 1]
                current_pos = start_pos
                
                for tile in selected_play:
                    playing_area.playing_area[current_pos] = tile
                    
                    playing_area.put_down_tiles(current_pos)
                    
                    # current_pos = (current_pos[0] + tile_width + tile_interval_x, current_pos[1])
                    current_pos = positions[positions.index(current_pos) + 1]
                space_found = True
                for tile in selected_play:
                    for k,v in self.tiles.items():
                        if v != tile :
                            self.tiles[k] = v
                        else:
                            self.tiles[k] = None
                break
        if space_found and valid_plays:
            self.play_tiles(playing_area,deck)
            
        if not space_found:
            self.draw_tile(deck)

    def get_scores(self,players,screen):
        for player in players:
            player.turn = False
        print_scores_width=500
        print_scores_height=400
        print_scores_blackground = pygame.image.load(os.path.join(img_path,'score_board.png'))
        print_scores_blackground = pygame.transform.scale(print_scores_blackground, (500, 400))
        print_scores_surface = pygame.Surface((print_scores_width, print_scores_height), pygame.SRCALPHA)
        print_scores_surface.fill((0, 0, 0, 0))
        print_scores_rect = pygame.Rect((screen_width // 2)-(print_scores_width//2), 0, 500, 400)
        #load the tile background image
        # print_scores_surface.blit(print_scores_blackground, center=((screen_width // 2)-(print_scores_width//2) , 0))
        screen.blit(print_scores_blackground, print_scores_rect)
        print("111")
        #define font and colour 
        font = pygame.font.Font(None, 40)
        # font.set_bold(True)
        
        
        #player_text = Rules.calculate_score.get(sorted_players_scores[player], (0, 0, 0)) 
        score_dict = Rules.calculate_score(players)
        print('222111',len(score_dict))
        y=150
        for k,v in score_dict.items():
            text = font.render(k.name + '                '+str(v), True, (0,0,0))
            text_rect = text.get_rect(center=(screen_width // 2, y))
            screen.blit(text, text_rect)
            print('111222',len(score_dict))
            y+=40
        screen.blit(print_scores_surface,(0,0))

    def render_hand(self, screen):
        for position, tile in self.tiles.items():
            if tile is not None:
                tile_image = tile.getImg()
                if tile_image is not None:
                    if self.shelf_orientation == 'horizontal':
                        screen.blit(tile_image, position)
                    elif self.shelf_orientation == 'vertical':
                        rotated_tile = pygame.transform.rotate(tile_image, 90)
                        adjusted_position = (position[0], position[1] + tile_width // 2 - tile_height // 2)
                        screen.blit(rotated_tile, adjusted_position)



    def render_shelf(self, screen, shelf_background):
        if self.shelf_orientation == 'horizontal':
            screen.blit(shelf_background, self.shelf_pos)
        elif self.shelf_orientation == 'vertical':
            rotated_shelf = pygame.transform.rotate(shelf_background, 90)  # Rotate 90 degrees for vertical
            screen.blit(rotated_shelf, self.shelf_pos)

    def render_dragging(self, screen):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.dragging.getImg(), (mouse_x + self.drag_offset_x, mouse_y + self.drag_offset_y))
            
    def render_buttons(self, screen):
        button_width, button_height = 100, 70
        button_gap = 10
        
        done_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap) - 20)
        cancel_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*2 - 20)
        plus_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*3 - 20)
        run_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*4 - 20)
        set_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*5 - 20)
        for_me_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*6 - 20)
        for_me_button2_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*6 - 20)
        temp_button_pos = (screen_width - button_width - 20,screen_height - (button_height+button_gap)*7 - 20)
        
        done_button_img = pygame.image.load(os.path.join(img_path,'button_Y.png'))
        cancel_button_img = pygame.image.load(os.path.join(img_path,'button_x.png'))
        set_button_img = pygame.image.load(os.path.join(img_path,'button_777.png'))
        run_button_img = pygame.image.load(os.path.join(img_path,'button_579.png'))
        plus_button_img = pygame.image.load(os.path.join(img_path,'button_plus.png'))
        temp_button_img = pygame.image.load(os.path.join(img_path,'button_temp.jpg'))
        for_me_button_img = pygame.image.load(os.path.join(img_path,'button_for_me.png'))
        for_me_button2_img = pygame.image.load(os.path.join(img_path,'for_me_circle.png'))
        
        done_button_img = pygame.transform.scale(done_button_img, (button_width,button_height))
        cancel_button_img = pygame.transform.scale(cancel_button_img, (button_width,button_height))
        set_button_img = pygame.transform.scale(set_button_img, (button_width,button_height))
        run_button_img = pygame.transform.scale(run_button_img, (button_width,button_height))
        plus_button_img = pygame.transform.scale(plus_button_img, (button_width,button_height))
        temp_button_img = pygame.transform.scale(temp_button_img, (button_width,button_height))
        for_me_button_img = pygame.transform.scale(for_me_button_img, (button_width,button_height))
        for_me_button2_img = pygame.transform.scale(for_me_button2_img, (button_width,button_height))

        done_button_rect = pygame.Rect(done_button_pos[0], done_button_pos[1], button_width, button_height)
        cancel_button_rect = pygame.Rect(cancel_button_pos[0], cancel_button_pos[1], button_width, button_height)
        set_button_rect = pygame.Rect(set_button_pos[0], set_button_pos[1], button_width, button_height)
        run_button_rect = pygame.Rect(run_button_pos[0], run_button_pos[1], button_width, button_height)
        plus_button_rect = pygame.Rect(plus_button_pos[0], plus_button_pos[1], button_width, button_height)
        # temp_button_rect = pygame.Rect(temp_button_pos[0], temp_button_pos[1], button_width, button_height)
        for_me_button_rect = pygame.Rect(for_me_button_pos[0], for_me_button_pos[1], button_width, button_height)
        for_me_button2_rect = pygame.Rect(for_me_button2_pos[0], for_me_button2_pos[1], button_width, button_height)


        if self.turn and len(self.tiles_in_current_turn)>0 and self.isSelect == False:screen.blit(done_button_img, done_button_rect)
        if self.turn and len(self.tiles_in_current_turn)>0 and self.isSelect == False:screen.blit(cancel_button_img, cancel_button_rect)
        screen.blit(set_button_img, set_button_rect)
        screen.blit(run_button_img, run_button_rect)
        if self.turn:screen.blit(plus_button_img, plus_button_rect)
        # screen.blit(temp_button_img, temp_button_rect)
        screen.blit(for_me_button_img, for_me_button_rect)
        if self.play_for_me:
            screen.blit(for_me_button2_img, for_me_button2_rect)
        
        button_dict = {
            'set_button': set_button_rect,
            'run_button': run_button_rect,
            # 'temp_button':temp_button_rect,
            'for_me_button':for_me_button_rect
        }
        if self.turn:
            button_dict['plus_button'] = plus_button_rect
            if len(self.tiles_in_current_turn)>0 and self.isSelect == False:
                button_dict['done_button'] = done_button_rect
                button_dict['cancel_button'] = cancel_button_rect
            
        return button_dict

    def render_select(self,screen):
        select_area_width, select_area_height = 150, 150
        button_width, button_height = 100, 70
        button_gap = 10
        
        select_area_pos = (screen_width - button_width - select_area_width- button_gap-20,screen_height - (button_height+button_gap)*3 - 20)
        select_area_img = pygame.image.load(os.path.join(img_path,'select_area.png'))
        select_area_img = pygame.transform.scale(select_area_img, (select_area_width,select_area_height))
        select_area_rect = pygame.Rect(select_area_pos[0], select_area_pos[1], select_area_width, select_area_height)
        screen.blit(select_area_img, select_area_rect)
        select_tile_rects = []
        for i in range(len(self.select_tiles)):
            select_tile_x = select_area_pos[0]+13+((tile_width+10)*i)
            select_tile_y = select_area_pos[1]+60
            select_tile = self.select_tiles[i].getImg()
            screen.blit(select_tile,(select_tile_x,select_tile_y))
            select_tile_rects.append(pygame.Rect(select_tile_x, select_tile_y, tile_width, tile_height))
        if len(self.select_tiles) == 2: 
            return {
                0 : select_tile_rects[0],
                1 : select_tile_rects[1]
            }
        
    def render_remaining(self, deck, screen):
        font = pygame.font.Font(None, 40)
        array_length_text = font.render("Tiles: {}".format(len(deck)), True, (255, 0, 0))
        screen.blit(array_length_text, (screen_width - 150, screen_height - 50))

    def render_time(self, countdown_duration, countdown_start_time, screen):
        profile_pos = self.get_profile_pos()
        remaining_time = max(0, countdown_duration - (pygame.time.get_ticks() - countdown_start_time) + 1000)
        font = pygame.font.Font(None, 60)
        timer_text = font.render(f"{remaining_time // 1000}s", True, (255, 0, 0))
        text_rect = timer_text.get_rect(topleft=(profile_pos[0]+30, profile_pos[1]+35))
        screen.blit(timer_text, text_rect)
        
    def render_profile(self,screen):
        # profile_img_width = 120
        profile_pos = self.get_profile_pos()
        turn_on_img = pygame.image.load(os.path.join(img_path,'player_on.png'))
        turn_on_img = pygame.transform.scale(turn_on_img,(self.profile_width,self.profile_width))
        profile_img = pygame.image.load(os.path.join(img_path,self.profile_img_list[self.position]))
        profile_img = pygame.transform.scale(profile_img,(self.profile_width,self.profile_width))
        profile_rect = pygame.Rect(profile_pos[0],profile_pos[1],self.profile_width,self.profile_width)
        screen.blit(profile_img,profile_rect)
        if self.turn:
            screen.blit(turn_on_img,profile_rect)
        # if self.position == 0:
        return profile_rect

    def get_profile_pos(self):
        if self.position == 0:
            return (self.profile_gap , screen_height - self.profile_width - 20)
        else:return (self.profile_gap , self.profile_gap + (self.profile_width+self.profile_gap_name)*(self.position - 1))

    def click_profile(self):
        if self.show_tiles:
            self.show_tiles = False
        else:
            self.show_tiles = True

    def render_small_tiles(self,screen):
        if self.position !=0:
            j = 1/2
            small_tiles_list = list(self.tiles.values())
            small_tiles_list = [item for item in small_tiles_list if item is not None]
            small_shelf_pos = (self.get_small_tile_pos(0,j)[0]-5,self.get_small_tile_pos(0,j)[1]-5)
            small_shelf_img = pygame.image.load(os.path.join(img_path,'small_shelf.png'))
            small_shelf_img = pygame.transform.scale(small_shelf_img, ((tile_width+tile_interval_x)*j*len(small_tiles_list)+10,tile_height*j+10))
            small_shelf_rect = pygame.Rect(small_shelf_pos[0], small_shelf_pos[1], (tile_width+tile_interval_x)*j*len(small_tiles_list)+10, tile_height*j+10)
            screen.blit(small_shelf_img, small_shelf_rect)
            for i,tile in enumerate(small_tiles_list):
                tile_image = tile.getImg()
                if tile_image is not None:
                    tile_image = pygame.transform.scale(tile_image, (tile_width*j, tile_height*j))
                    screen.blit(tile_image,self.get_small_tile_pos(i,j))
            
        else:pass

    def get_small_tile_pos(self,index,j):
        position = self.get_profile_pos()
        return (position[0]+self.profile_gap+self.profile_width+(tile_width+tile_interval_x)*j*index+10,position[1]+5)
    def render_alert(self, screen, alert_type='notrule_alert'):
        alert_width, alert_height = 1000, 100

        alert_pos = (screen_width / 4, screen_height / 3)

        if alert_type == 'innitial_alert':
            alert_img = pygame.image.load(os.path.join(img_path,'alert_initial_move.png'))
        else:
            alert_img = pygame.image.load(os.path.join(img_path,'alert_not_rule_l.png'))

        alert_img = pygame.transform.scale(alert_img, (alert_width, alert_height))

        alert_rect = pygame.Rect(alert_pos[0], alert_pos[1], alert_width, alert_height)

        screen.blit(alert_img, alert_rect)

        return {alert_type: alert_rect}
            
        
    def sort_by_color_sequence(self):
        num_tiles_in_row = 21
        hand_tiles_start_x, hand_tiles_start_y = self.shelf_pos 
        sorted_tiles = []
        
        sequences, tiles_list = Rules.is_valid_run(self.tiles, 'both')
        
        
        for sequence in sequences:
            sorted_tiles.extend(sequence)
            sorted_tiles.append(None)  


        remaining_tiles = sorted(tiles_list, key=lambda tile: (tile.suit, tile.value))
        for i in range(0, len(remaining_tiles), num_tiles_in_row):
            sorted_tiles.extend(remaining_tiles[i:i + num_tiles_in_row])
        
        sorted_hand_tiles = {}
        for i in range(2):
            for j in range(num_tiles_in_row):
                if (num_tiles_in_row*i+j) < len(sorted_tiles):
                    sorted_hand_tiles[(hand_tiles_start_x + j * (tile_width + tile_interval_x),
                            hand_tiles_start_y + i * (tile_height + tile_interval_y))] = sorted_tiles[num_tiles_in_row*i+j]
                else:
                    sorted_hand_tiles[(hand_tiles_start_x + j * (tile_width + tile_interval_x), hand_tiles_start_y + i * (tile_height + tile_interval_y))] = None


        return sorted_hand_tiles
    def sort_by_same_number(self):
        num_tiles_in_row = 21
        hand_tiles_start_x, hand_tiles_start_y = self.shelf_pos 
        sorted_tiles = []

        sequences, tiles_list = Rules.is_valid_group(self.tiles, 'both')

        for sequence in sequences:
            sorted_tiles.extend(sequence)
            sorted_tiles.append(None)  

        remaining_tiles = sorted(tiles_list, key=lambda tile: (tile.suit, tile.value))
        for i in range(0, len(remaining_tiles), num_tiles_in_row):
            sorted_tiles.extend(remaining_tiles[i:i + num_tiles_in_row])
            # if i + num_tiles_in_row < len(remaining_tiles):
            #     sorted_tiles.append(None) 

        sorted_hand_tiles = {}
        for i in range(2):
            for j in range(num_tiles_in_row):
                if (num_tiles_in_row*i+j) < len(sorted_tiles):
                    sorted_hand_tiles[(hand_tiles_start_x + j * (tile_width + tile_interval_x),
                            hand_tiles_start_y + i * (tile_height + tile_interval_y))] = sorted_tiles[num_tiles_in_row*i+j]
                else:
                    sorted_hand_tiles[(hand_tiles_start_x + j * (tile_width + tile_interval_x), hand_tiles_start_y + i * (tile_height + tile_interval_y))] = None

        return sorted_hand_tiles

# --------------------------------------------------------------

class AIPlayer(Player):
    def __init__(self, name, position, difficulty):
        super().__init__(name, position)
        self.difficulty = difficulty

    def make_decision(self, playing_area, deck):
        if self.difficulty == 'easy':
            self.make_decision_easy(playing_area, deck)
            
        elif self.difficulty == 'normal':
            self.make_decision_normal(playing_area, deck)
            
    def make_decision_easy(self, playing_area, deck):

        action = random.choice(["play", "draw"])
        if action == "play":
            self.play_tiles(playing_area, deck)
        else:
            self.draw_tile(deck)

    def make_decision_normal(self,playing_area, deck):
        is_valid = Rules.is_valid_play(self.tiles)
        if is_valid:
            self.play_tiles(playing_area, deck)
        else:
            self.draw_tile(deck)

# --------------------------------------------------------------

class PlayingArea:
    def __init__(self, start_x, start_y, rows):
        self.start_x = start_x
        self.start_y = start_y
        self.rows = rows
        self.end_x = window_width - start_x
        self.end_y = start_y + (tile_height + tile_interval_y) * rows 
        self.playing_area = self.initialize_playing_area()
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.dragging = None  
        self.is_dragging = False 
        self.insert_position = None

    def initialize_playing_area(self):
        area = {}
        for i in range(self.rows):
            for j in range((self.end_x - self.start_x) // (tile_width + tile_interval_x)):
                area[(self.start_x + (tile_width + tile_interval_x) * j,
                      self.start_y + (tile_height + tile_interval_y) * i)] = None
        return area
    
    def start_dragging(self, mouse_x, mouse_y):
        for position, tile in self.playing_area.items():
            if tile is not None:
                tile_rect = pygame.Rect(position[0], position[1], tile_width, tile_height)
                if tile_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = tile
                    self.dragging_original_position = position
                    self.drag_offset_x = position[0] - mouse_x
                    self.drag_offset_y = position[1] - mouse_y
                    self.playing_area[position] = None
                    self.is_dragging = True
                    self.insert_position = None 
                    return position
        return None

    def stop_dragging(self, mouse_x, mouse_y, players):
        self.is_dragging = False
        place_pos = None
        positions = sorted(self.playing_area.keys(), key=lambda x: (x[1], x[0]))
        if self.dragging:
            inserted = False
            for i, (position, tile) in enumerate(self.playing_area.items()):
                tile_rect = pygame.Rect(position[0], position[1], tile_width, tile_height)
                if tile_rect.collidepoint(mouse_x, mouse_y):
                    if self.playing_area[position] is not None:
                        # if self.is_last_position_full():
                        #     break
                        shift_direction = self.shift_tiles_backward(position, self.playing_area, self.dragging)
                        if shift_direction == 0:
                            place_pos = position
                        else:
                            place_pos = positions[i-1]
                        # self.playing_area[position] = self.dragging
                        inserted = True
                        
                    elif self.playing_area[position] is None:
                        self.playing_area[position] = self.dragging
                        inserted = True
                        place_pos = position
                    break
            print('unlock',self.dragging.unlock)
            if self.dragging.unlock:
                for player in players:
                    if player.turn:
                        for position in player.tiles:
                            tile_rect = pygame.Rect(position[0], position[1], tile_width, tile_height)
                            if tile_rect.collidepoint(mouse_x, mouse_y):
                                if player.tiles[position] is not None:
                                    self.shift_tiles_backward(position, player.tiles, self.dragging)
                                    # players[0].tiles[position] = self.dragging
                                    inserted = True
                                elif player.tiles[position] is None:
                                    player.tiles[position] = self.dragging
                                    inserted = True
                                player.tiles_in_current_turn = [tile for tile in player.tiles_in_current_turn if tile.ID != self.dragging.ID]
                                print('hdehdhe',len(player.tiles_in_current_turn))
                                break
            if not inserted:
                self.playing_area[self.dragging_original_position] = self.dragging

            self.dragging = None
            self.insert_position = None
            if place_pos:
                self.put_down_tiles(place_pos)



    def is_last_position_full(self):
        positions = sorted(self.playing_area.keys(), key=lambda x: (x[1], x[0]))
        return self.playing_area[positions[-1]] is not None
            
    def check_nearby_tile(self, mouse_pos):
        for position in self.playing_area:
            rect = pygame.Rect(position[0], position[1], tile_width, tile_height)
            if rect.collidepoint(mouse_pos):
                return position
        return None
    
    def check_insert_position(self, dragging_tile, mouse_pos):
        for position, tile in self.playing_area.items():
            if tile and tile != dragging_tile:
                tile_rect = pygame.Rect(position[0], position[1], tile_width, tile_height)
                if tile_rect.collidepoint(mouse_pos):
                    self.insert_position = position
                    return
        self.insert_position = None

    def lock_tile(self):
        # result = {}
        for pos , tile in self.playing_area.items():
        #     print('before',tile.unlock)
            if tile is not None:
                tile.unlock = False
                # print('after',tile.unlock)
        #     result[pos] = tile
        # return result
        
        
        
    def shift_tiles_backward(self, start_position, tiles, dragging = None):
        positions = sorted(tiles.keys(), key=lambda x: (x[1], x[0]))
        start_index = None
        buffer_index = None
        shift_direction = 0 

        for i, position in enumerate(positions):
            if position == start_position:
                start_index = i

            if start_index is not None and tiles[position] == None and tiles[positions[i - 1]] == None:
                buffer_index = i
                break

        if start_index is not None and buffer_index is None:
            for i in range(start_index, 0, -1):
                if start_index is not None and tiles[positions[i]] == None and tiles[positions[i - 1]] == None:
                    buffer_index = i
                    shift_direction = 1
                    break
            
        
        if shift_direction == 0:
            if start_index is not None:
                for i in range(buffer_index, start_index, -1):
                    tiles[positions[i]] = tiles[positions[i - 1]]
            if dragging:
                tiles[start_position] = dragging
            else:
                tiles[start_position] = None

        else:
            if dragging is not None:
                for i in range(buffer_index, start_index - 1):
                    tiles[positions[i]] = tiles[positions[i + 1]]
            else:
                for i in range(buffer_index, start_index - 1):
                    tiles[positions[i]] = tiles[positions[i + 1]]

            if dragging:
                tiles[positions[start_index-1]] = dragging
            else:
                tiles[positions[start_index-1]] = None

        return shift_direction
 
    def put_down_tiles(self, place_pos):
        tiles = self.playing_area
        shift_direction = 0
        def is_group(tile1, tile2, tile3, placed_tile=None):
            if tile1 is None:
                tile1 = tile2
                tile2 = tile3
                tile3 = None

            if tile3 is None:
                if (tile1.suit == tile2.suit and tile1.value == tile2.value - 2) or (tile1.suit != tile2.suit and tile1.value == tile2.value):
                    return True
                else:
                    return False
            else:
                if tile1.suit == tile2.suit and tile1.value == tile2.value - 2:
                    if tile3 is None:
                        return True
                    elif tile2.suit == tile3.suit and tile2.value == tile3.value - 2:
                        return True
                    else:
                        return False
                elif tile1.suit != tile2.suit and tile1.value == tile2.value:
                    if tile3 is None:
                        return True
                    elif tile2.suit != tile3.suit and tile2.value == tile3.value:
                        suits = []
                        positions = list(tiles.keys())
                        for i, pos in enumerate(positions):
                            if tiles[pos] == placed_tile:
                                j = i - 1
                                while j >= 0 and tiles[positions[j]] is not None:
                                    suits.append(tiles[positions[j]].suit)
                                    j -= 1

                                k = i + 1
                                while k < len(positions) and tiles[positions[k]] is not None:
                                    suits.append(tiles[positions[k]].suit)
                                    k += 1
                                break
                        return placed_tile.suit not in suits
                    else:
                        return False
                else:
                    return False
            
        positions = list(tiles.keys())
        for i, pos in enumerate(positions):
            if pos == place_pos:
                tile_left, tile_left_left, tile_right, tile_right_right = None, None, None, None
                if i == 0:
                    pass
                elif i == 1:
                    tile_left = tiles[positions[i - 1]]
                else:
                    tile_left = tiles[positions[i - 1]]
                    tile_left_left = tiles[positions[i - 2]]

                if i == len(positions) - 1:
                    pass
                elif i == len(positions) - 2:
                    tile_right = tiles[positions[i + 1]]
                else:
                    tile_right = tiles[positions[i + 1]]
                    tile_right_right = tiles[positions[i + 2]]

                if tile_right is None:
                    if tile_left is None:
                        return
                    elif is_group(tile_left_left, tile_left, tiles[pos], tiles[pos]):
                        return
                    else:
                        self.shift_tiles_backward(pos, tiles)
                        return
                elif is_group(tiles[pos], tile_right, tile_right_right, tiles[pos]):
                    if tile_left is None:
                        return
                    elif is_group(tile_left_left, tile_left, tiles[pos], tiles[pos]):
                        if not is_group(tile_left, tiles[pos], tile_right, tiles[pos]):
                            self.shift_tiles_backward(positions[i + 1], tiles)
                        return
                    else:
                        self.shift_tiles_backward(pos, tiles)
                        return
                else:
                    shift_direction = self.shift_tiles_backward(positions[i + 1], tiles)
                    if shift_direction == 1:
                        i = i - 1
                    if tiles[positions[i - 1]] is None:
                        return
                    elif is_group(tiles[positions[i - 2]], tiles[positions[i - 1]], tiles[positions[i]], tiles[positions[i]]):
                        return
                    else:
                        self.shift_tiles_backward(positions[i], tiles)
                        return
                    
    def render(self, screen, mouse_pos):
        for position, tile in self.playing_area.items():
            rect = pygame.Rect(position[0], position[1], tile_width, tile_height)

            if position == self.insert_position:
                pygame.draw.rect(screen, (255, 0, 0), (rect.left, rect.top, rect.width / 2, rect.height))

                if tile is not None:
                    tile_image = tile.getImg()
                    screen.blit(tile_image, (rect.left + rect.width / 2, rect.top))
                else:
                    pygame.draw.rect(screen, (255, 0, 0), (rect.left, rect.top, rect.width / 2, rect.height))
                    if tile is not None:
                        tile_image = tile.getImg()
                        tile_half_image = pygame.Surface((tile_width // 2, tile_height), pygame.SRCALPHA)
                        tile_half_image.blit(tile_image, (0, 0))
                        screen.blit(tile_half_image, (rect.left + rect.width / 2, rect.top))

            elif self.is_dragging and rect.collidepoint(mouse_pos) and tile is None:
                pygame.draw.rect(screen, (255, 0, 0), rect)

            elif tile is not None:
                tile_image = tile.getImg()
                if tile_image is not None:
                    screen.blit(tile_image, position)

        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.dragging.getImg(), (mouse_x + self.drag_offset_x, mouse_y + self.drag_offset_y))

# --------------------------------------------------------------

class Rules:
    @staticmethod
    def is_valid_run(tiles, return_type = 'sequences'):
        tiles_list = [tile for tile in tiles.values() if tile is not None]
        sequences = []

        for color in set(tile.suit for tile in tiles_list):
            color_tiles = [tile for tile in tiles_list if tile.suit == color]
            odd_tiles = [tile for tile in color_tiles if tile.value % 2 != 0]
            even_tiles = [tile for tile in color_tiles if tile.value % 2 == 0]

            for parity_tiles in [odd_tiles, even_tiles]:
                parity_tiles.sort(key=lambda tile: tile.value)
                sequence = []

                for i, tile in enumerate(parity_tiles):
                    if sequence:
                        if tile.value == sequence[-1].value + 2:
                            sequence.append(tile)
                    else:
                        sequence = [tile]
                if len(sequence) >= 3:
                    sequences.append(sequence)
        for sequence in sequences:
            for tile in sequence:
                tiles_list.remove(tile)
                
        if return_type == 'both':
            return sequences, tiles_list
        elif return_type == 'sequences':
            return sequences
        elif return_type == 'tiles_list':
            return tiles_list
        
    
    @staticmethod
    def is_valid_group(tiles, return_type = 'sequences'):
        tiles_list = [tile for tile in tiles.values() if tile is not None]
        sequences = []

        for number in set(tile.value for tile in tiles_list):
            number_tiles_origin = [tile for tile in tiles_list if tile.value == number]
            number_tiles = []
            for tile in number_tiles_origin:
                if not any(t.suit == tile.suit for t in number_tiles):
                    number_tiles.append(tile)

            if len(number_tiles) >= 3:
                sequences.append(number_tiles)
                for tile in number_tiles:
                    tiles_list.remove(tile)
        
        if return_type == 'both':
            return sequences, tiles_list
        elif return_type == 'sequences':
            return sequences
        elif return_type == 'tiles_list':
            return tiles_list
    
    @staticmethod
    def is_valid_play(tiles):
        valid_plays = []
        
        valid_runs = Rules.is_valid_run(tiles)
        valid_plays.extend(valid_runs)

        valid_groups = Rules.is_valid_group(tiles)
        valid_plays.extend(valid_groups)

        return valid_plays
    
    
    @staticmethod   
    def check_play(input_tiles):
        print('check_play')
        instance_count = 0 
        judge_list = [] 

        for key, tile in sorted(input_tiles.items(), key=lambda x: (x[0][1], x[0][0])):
            if tile is not None:
                instance_count += 1
            else:
                if instance_count >=3:
                    judge_list.append(1) 
                    instance_count = 0  
                elif instance_count>0 and instance_count<3:
                    judge_list.append(2)  
                    instance_count = 0   
        return all(x == 1 for x in judge_list)

    @staticmethod 
    def check_winner(player):
        if len([tile for tile in player.tiles.values() if tile is not None]) == 0: 
                return True
        return False 
    



    @staticmethod
    def calculate_score(players):
        players_scores = {}
        total_score = 0
        winner = None
        for player in players:
            if not Rules.check_winner(player):
                player_score = -sum(tile.value for tile in player.tiles.values() if tile is not None)
                players_scores[player] = player_score
                total_score += abs(player_score)
            else:
                winner = player
        players_scores[winner] = total_score



        sorted_players_scores = {}

        while players_scores:
            max_player = max(players_scores, key=players_scores.get)
            sorted_players_scores[max_player] = players_scores[max_player]
            del players_scores[max_player]

        return sorted_players_scores
    @staticmethod
    def check_initial_meld(player):
        hand_value=sum(tile.value for tile in player.tiles_in_current_turn)
        if hand_value >= 30:
            return True
        else:
            return False
 