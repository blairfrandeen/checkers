#checkers_main.py
"""Main checkers program."""
import time

import checker_graphics
from checker_classes import Board, Position, Game, Player
from checker_ai import pick_best_move
import function_timer as ft

### CONSTANTS ###
LOG_FILE = 'game_history'

# Maximum moves that can be made with the same
# number of pieces on the board before a draw is triggered
MAX_DRAW_COUNT = 40

# Maxium difference between number of pieces each player
# has in order for a draw to be triggered
MAX_DRAW_PIECE_DIFF = 2

def play_game(player_1, player_2, graphics=True, echo=False):
    """Main loop for checkers game."""
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
            if echo:
                print('No More Legal Moves!')
            board.next_turn()
            game.end(board.turn)
            game.log(LOG_FILE)
            break

        # if other player has no pieces left, current player wins
        if board.players[board.get_next_turn()].num_pieces == 0:
            if echo:
                print('No More Pieces!')
            game.end(board.turn)
            game.log(LOG_FILE)
            break

        #### GET INPUT MOVE FROM HUMAN OR AI
        if game.players[board.turn].control == "AI":
            input_move = pick_best_move(game, board, echo)
        else:
            if echo:
                pick_best_move(game, board, echo=True)
            input_move = checker_graphics.get_graphics_move(GRAPHICS_WINDOW)

        ### IF NO MOVE GIVEN, DECLARE DRAW
        if not input_move:
            game.end(winner=None)
            game.log(LOG_FILE)
            break

        if board.draw_counter >= MAX_DRAW_COUNT:
            piece_diff = abs(board.players[1].num_pieces \
                - board.players[2].num_pieces)
            if piece_diff <= MAX_DRAW_PIECE_DIFF:
                print('DRAW COUNTER REACHED!')
                game.end(winner=None)
                game.log(LOG_FILE)
                break

        ### RESET AND QUIT BUTTONS
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
            board.execute_move(input_move)
            game.move_history.append(input_move)
            game.board_history[board.turn].append(board.int_rep())
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

    PLAYER_1 = Player(1, "Blair", "Black", "Human")
    PLAYER_2 = Player(2, "Kivo", "Red", "AI")

    for i in range(NUM_GAMES):
        print('Game %d of %d....' % (i+1, NUM_GAMES))
        play_game(PLAYER_1, PLAYER_2, graphics=True, echo=True)

    ft.report_game_metrics()
