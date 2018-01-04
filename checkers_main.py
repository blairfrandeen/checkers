#checkers_main.py
"""Main checkers program."""
import time
import copy

import checker_graphics
from checker_classes import Board, Position, Game, Player, Move, Piece
import checker_classes
from checker_ai import pick_best_move
import function_timer as ft

### CONSTANTS ###
LOG_FILE = 'game_history'

## Here is a change for you!

def play_game(graphics=True):
    """Main loop for checkers game."""
    player_1 = Player(1, "Blair", "Black", "AI")
    player_2 = Player(2, "Kivo", "Red", "AI")
    game = Game(player_1=player_1, player_2=player_2)
    game.start_time = time.time()

    if graphics:
        GRAPHICS_WINDOW = checker_graphics.initialize_graphics_window()

    board = Board(players={1: game.player_1, 2: game.player_2})
    while True:
        if graphics:
            checker_graphics.draw_board(board, GRAPHICS_WINDOW)

        legal_moves = board.get_legal_moves()
        # if no legal moves available, other player wins.
        if not legal_moves:
            board.next_turn()
            game.end(board.turn)
            game.log(LOG_FILE)
            break
        board_next_turn = copy.copy(board)
        board_next_turn.next_turn()
        legal_moves_next_turn = board_next_turn.get_legal_moves()
        # if no legal moves exist for the next player
        # on the next turn, current player wins
        if not legal_moves_next_turn:
            game.end(board.turn)
            game.log(LOG_FILE)
            break

        # get input move from human or AI
        if game.players[board.turn].control == "AI":
            input_move = pick_best_move(game, board)
        else:
            pick_best_move(game, board)
            input_move = checker_graphics.get_graphics_move(GRAPHICS_WINDOW)

        if graphics:
            if input_move.end_position == Position(9, 8):
                print("Thanks for playing!")
                GRAPHICS_WINDOW.close()
                break
            if input_move.end_position == Position(9, 1):
                print("Starting Over...")
                game = Game(player_1=player_1, player_2=player_2)
                board = Board()
                continue

        if board.is_legal_move(input_move, echo=True):
            #print('SELECTED MOVE:', end='')
            # print(input_move)
            board.execute_move(input_move)
            game.move_history.append(input_move)
            game.board_history[board.turn].append(board.int_rep())
        if graphics:
            checker_graphics.draw_board(board, GRAPHICS_WINDOW)
            if checker_graphics.TIME_STEP != 0:
                checker_graphics.draw_board(board, GRAPHICS_WINDOW)
                GRAPHICS_WINDOW.update()
                time.sleep(checker_graphics.TIME_STEP)
### MAIN
NUM_GAMES = 1

for i in range(NUM_GAMES):
    print('Game %d of %d....' % (i+1, NUM_GAMES))
    play_game() 

ft.report_game_metrics()
# print('Graphics Objects: %d' % len(Move.instances))
