import pygame

from classes import *
# from cls_Tile import Tile
# from settings import *
from settings import (
    tile_width,
    tile_height,
    screen_width,
    screen_height,
    tile_interval_x,
    tile_interval_y,
    shelf_width,
    shelf_height,
    img_path,
)





def pre_main():
    global tile_width, tile_height, window_width, window_height, tile_background
    pygame.init()
    pygame.display.set_caption("rummikub")
    screen = pygame.display.set_mode((screen_width, screen_height))
    window_background = pygame.image.load(os.path.join(img_path,'pre_start.png'))
    window_background = pygame.transform.scale(window_background, (screen_width, screen_height))
    big_button_start = pygame.image.load(os.path.join(img_path,'big_button_start.png'))
    big_button_start = pygame.transform.scale(big_button_start, (180, 100))
    window_width, window_height = screen.get_size()
    running = True
    while running:
        screen.blit(window_background, (0, 0))
        screen.blit(big_button_start, ((screen_width - 180) / 2, screen_height - 200))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                main()
                running = False

        pygame.display.update()
    pygame.quit()


def main():
    global tile_width, tile_height, window_width, window_height, tile_background
    pygame.init()
    pygame.display.set_caption("rummikub")
    screen = pygame.display.set_mode((screen_width, screen_height))
    window_background = pygame.image.load(os.path.join(img_path,'background.png'))
    window_background = pygame.transform.scale(window_background, (screen_width, screen_height))
    tile_background = pygame.image.load(os.path.join(img_path,'tile.png'))
    tile_background = pygame.transform.scale(tile_background, (tile_width, tile_height))
    window_width, window_height = screen.get_size()
    shelf_background = pygame.image.load(os.path.join(img_path,'Tile_shelf_shadow.png'))
    shelf_background = pygame.transform.scale(shelf_background, (shelf_width, shelf_height))

    playing_area = PlayingArea(100, 30, 7)
    players = [Player("Player 1", position=0)]
    aiplayers = [AIPlayer("AIPlayer 1", position=1, difficulty='normal'),
                 AIPlayer("AIPlayer 2", position=2, difficulty='normal')]
    for aiplayer in aiplayers:
        players.append(aiplayer)

    deck = initialize_deck()
    show_first_tile = True
    first_one_tile(players, deck)

    timer_event_1 = pygame.USEREVENT + 1
    timer_event_3 = pygame.USEREVENT + 2
    timer_event_5 = pygame.USEREVENT + 3
    timer_event_6 = pygame.USEREVENT + 6

    pygame.time.set_timer(timer_event_1, 1000)
    pygame.time.set_timer(timer_event_5, 5000)
    pygame.time.set_timer(timer_event_3, 3000)
    pygame.time.set_timer(timer_event_6, 5000)

    TIMER_EVENT = pygame.USEREVENT + 4
    RESET_EVENT = pygame.USEREVENT + 5
    countdown_duration = 60 * 1000
    countdown_start_time = pygame.time.get_ticks()
    pygame.time.set_timer(TIMER_EVENT, 1000)
    resetting = False

    running = True
    while running:

        screen.blit(window_background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        players[0].render_shelf(screen, shelf_background)
        players[0].render_hand(screen)
        playing_area.render(screen, mouse_pos)
        players[0].render_dragging(screen)
        players[0].render_buttons(screen)
        if players[0].isSelect: players[0].render_select(screen)
        if players[0].show_alert_notrule:
            alert_rects = players[0].render_alert(screen, 'notrule_alert')
        if players[0].show_alert_innitial:
            alert_rects = players[0].render_alert(screen, 'innitial_alert')
        for player in players:
            player.render_profile(screen)
            if player.show_tiles:
                player.render_small_tiles(screen)
            if player.win:
                player.get_scores(players, screen)

        if show_first_tile:
            for player in players:
                screen.blit(player.first_one_tile.getImg(), (
                player.get_profile_pos()[0] + player.profile_width // 2 - tile_width // 2,
                player.get_profile_pos()[1] + player.profile_width // 2 - tile_height // 2))
        for player in players:
            if player.turn:
                player.render_time(countdown_duration, countdown_start_time, screen)
                break
        players[0].render_remaining(deck, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == timer_event_5:
                players[0].show_alert_notrule = False
                players[0].show_alert_innitial = False
            if event.type == timer_event_3:
                if players[0].play_for_me:
                    if players[0].turn:
                        players[0].play_tiles(playing_area, deck)
                        resetting = True
                        pygame.event.post(pygame.event.Event(RESET_EVENT))
                        if Rules.check_winner(players[0]):
                            players[0].win = True
                        next_turn(players, playing_area)
                        break

            if event.type == timer_event_3:
                for aiplayer in aiplayers:  # AI's turn
                    if aiplayer.turn:
                        aiplayer.make_decision(playing_area, deck)
                        resetting = True
                        pygame.event.post(pygame.event.Event(RESET_EVENT))
                        if Rules.check_winner(aiplayer):
                            aiplayer.win = True
                        next_turn(players, playing_area)
                        break

            if event.type == timer_event_6:
                show_first_tile = False
                pygame.time.set_timer(timer_event_6, 0)
                for _ in range(14):
                    for player in players:
                        player.draw_tile(deck)
                find_first(players, deck)

            elif event.type == TIMER_EVENT:
                if not resetting:
                    remaining_time = max(0, countdown_duration - (pygame.time.get_ticks() - countdown_start_time))
                    if remaining_time == 0:
                        pygame.time.set_timer(TIMER_EVENT, 0)
                        print(str(remaining_time))
                        players[0].cancel_play_tile(playing_area)
                        for _ in range(3):
                            players[0].draw_tile(deck)
                        next_turn(players, playing_area)
                        pygame.event.post(pygame.event.Event(RESET_EVENT))
                        resetting = True


            elif event.type == RESET_EVENT:
                resetting = False
                countdown_start_time = pygame.time.get_ticks()
                pygame.time.set_timer(TIMER_EVENT, 1000)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not players[0].play_for_me:
                    players[0].start_dragging(*event.pos, playing_area)
                    if players[0].turn:
                        playing_area.start_dragging(*event.pos)


            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                for button_name, rect in players[0].render_buttons(screen).items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        if button_name == 'set_button':
                            players[0].tiles = players[0].sort_by_same_number()
                        elif button_name == 'run_button':
                            players[0].tiles = players[0].sort_by_color_sequence()
                        elif button_name == 'plus_button':
                            players[0].isSelect = True
                            if players[0].select_tiles == []: players[0].select_draw_tile(deck)
                        elif button_name == 'cancel_button':
                            players[0].cancel_play_tile(playing_area)
                        elif button_name == 'done_button':
                            check_play = Rules.check_play(playing_area.playing_area)
                            if check_play == False:
                                players[0].show_alert_notrule = True
                            elif players[0].has_initial_meld == False:
                                check_meld = Rules.check_initial_meld(players[0])
                                if check_meld == False:
                                    players[0].show_alert_innitial = True
                                else:
                                    players[0].has_initial_meld = True
                                    resetting = True
                                    pygame.event.post(pygame.event.Event(RESET_EVENT))
                                    next_turn(players, playing_area)
                            else:
                                if Rules.check_winner(players[0]):
                                    players[0].win = True
                                resetting = True
                                pygame.event.post(pygame.event.Event(RESET_EVENT))
                                next_turn(players, playing_area)

                        elif button_name == 'temp_button':
                            resetting = True
                            pygame.event.post(pygame.event.Event(RESET_EVENT))
                            next_turn(players, playing_area)
                            for player in players:
                                if player.turn:
                                    print('now turn is player', player.position)
                        elif button_name == 'for_me_button':
                            players[0].play_for_me = not players[0].play_for_me

                if players[0].select_tiles:
                    for select_tile_index, select_tile_rect in players[0].render_select(screen).items():
                        pass
                        if select_tile_rect.collidepoint(mouse_x, mouse_y):
                            # if select_tile_index == 0:
                            players[0].cancel_play_tile(playing_area)
                            players[0].select_draw_tile([], False, select_tile_index)
                            players[0].select_draw_tile(deck, True, False)
                            players[0].isSelect = False
                            resetting = True
                            pygame.event.post(pygame.event.Event(RESET_EVENT))
                            next_turn(players, playing_area)
                if not players[0].play_for_me:
                    if not playing_area.stop_dragging(*event.pos, players):
                        players[0].stop_dragging(playing_area)
                for player in players:
                    rect = player.render_profile(screen)
                    if rect.collidepoint(mouse_x, mouse_y):
                        player.click_profile()
                        # print('hide & show')


            elif event.type == pygame.MOUSEMOTION:
                if playing_area.is_dragging and playing_area.dragging:
                    playing_area.check_insert_position(playing_area.dragging, event.pos)
                if players[0].dragging:
                    playing_area.check_insert_position(players[0].dragging, event.pos)

        pygame.display.update()
    pygame.quit()
