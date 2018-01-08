#checkers_main.py
"""Main checkers program."""
import time
import pickle
import dbm
import checker_graphics
from checker_classes import Configuration, Position
from checker_ai import pick_best_move
import function_timer as ft

PLAYER_1 = {'color': 'Black', 'name': 'Blair', 'control': 'Beard'}
PLAYER_2 = {'color': 'Red', 'name': 'Kivo', 'control': 'AI'}
PLAYERS = {1: PLAYER_1, 2: PLAYER_2}

### CONSTANTS ###
LOG_FILE = 'game_history_new'

# Maximum moves that can be made with the same
# number of pieces on the board before a draw is triggered
MAX_DRAW_COUNT = 40

# Maxium difference between number of pieces each player
# has in order for a draw to be triggered
MAX_DRAW_PIECE_DIFF = 2

def end_game(config, winner=None):
    """Ends the game and declares the winner."""
    if not winner:
        print('Game has ended in a draw after %d turns.' % config.num_moves)
    else:
        print('Game Over. %s has won in %d turns!' %\
            (PLAYERS[winner]['name'], config.num_moves))
    log_game(config)

def log_game(config):
    """
    Log the result of the game for later analysis.
    log file format is as follows:
    Keys are based on the GMT time at which the game was logged.
    Values are move_history.
    """
    t_start = time.time()
    game_id = time.strftime('%c', time.gmtime())
    print('Logging game ID %s...' % game_id)
    game_id = pickle.dumps(game_id)
    move_history = pickle.dumps(config.history)
    game_data = dbm.open(LOG_FILE, 'c')
    game_data[game_id] = move_history
    game_data.close()
    ft.log_function('log_game', t_start)

def check_end_condition(config, echo=False):
    """Check to see if any of the end game conditions have been met."""
    # legal_moves = board.legal_moves
    # if no legal moves available, other player wins.
    if not config.legal_moves:
        if echo:
            print('No More Legal Moves!')
        end_game(config, config.next_turn())
        return True

    # if other player has no pieces left, current player wins
    if config.pieces_remaining[config.next_turn()] == 0:
        if echo:
            print('No More Pieces!')
        end_game(config, config.turn)
        return True

    if config.draw_counter >= MAX_DRAW_COUNT:
        piece_diff = abs(config.pieces_remaining[1] - config.pieces_remaining[2])
        if piece_diff <= MAX_DRAW_PIECE_DIFF:
            print('Draw Counter Reached!')
            end_game(config, winner=None)
        return True

    return False

def play_game(players, graphics=True, echo=False):
    """Main loop for checkers game."""
    # game = Game(player_1=player_1, player_2=player_2)
    # game.start_time = time.time()

    if graphics:
        GRAPHICS_WINDOW = checker_graphics.initialize_graphics_window()

    board = Configuration(PLAYERS)
    board.new_game()
    while True:
        if graphics:
            checker_graphics.draw_board(board, GRAPHICS_WINDOW)

        if check_end_condition(board):
            break

        #### GET INPUT MOVE FROM HUMAN OR AI
        if players[board.turn]['control'] == "AI":
            input_move = pick_best_move(board, echo)
        else:
            if echo:
                pick_best_move(board, echo=True)
            input_move = checker_graphics.get_graphics_move(GRAPHICS_WINDOW)

        ## IF NO MOVE GIVEN, DECLARE DRAW
        if not input_move:
            end_game(board, winner=None)
            break

        ### RESET AND QUIT BUTTONS
        if graphics:
            if input_move.end_position == Position(9, 8):
                print("Thanks for playing!")
                GRAPHICS_WINDOW.close()
                break
            if input_move.end_position == Position(9, 1):
                print("Starting Over...")
                board.new_game()
                continue

        if board.is_legal_move(input_move, echo=True):
            board.execute_move(input_move)

        if graphics:
            checker_graphics.draw_board(board, GRAPHICS_WINDOW)
            if checker_graphics.TIME_STEP != 0:
                checker_graphics.draw_board(board, GRAPHICS_WINDOW)
                GRAPHICS_WINDOW.update()
                # GRAPHICS_WINDOW.getMouse()
                time.sleep(checker_graphics.TIME_STEP)
    if graphics:
        GRAPHICS_WINDOW.close()



if __name__ == '__main__':
    NUM_GAMES = 1
    for i in range(NUM_GAMES):
        print('Game %d of %d....' % (i+1, NUM_GAMES))
        play_game(PLAYERS, graphics=True, echo=True)

    ft.report_game_metrics()
