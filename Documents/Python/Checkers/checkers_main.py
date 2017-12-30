#checkers_main.py
"""Main checkers program."""
import dbm
import time
from checker_parameters import players, time_step, datafile, log_function,\
    report_game_metrics
from checker_mechanics import new_game, get_legal_moves, \
    get_turn, next_turn, move, is_legal_move
from graphics import update
from checker_ai import pick_best_move, report_repeated_boards
from checker_utility import convert_board_to_int
import checker_graphics

def end_game(data_file, boards, winner):
    """Ends the game and records the result."""
    t_start = time.time()
    print("Game Over. %s Wins." % players[winner][1])
    data = dbm.open(data_file, 'c')
    db_start_keys = len(data.keys())
    print('Logging Results. Total of %d configurations.' % len(boards))
    for board_config in boards:
        board_config = str(convert_board_to_int(board_config))
        t, w1, w2 = 0, 0, 0
        if board_config in data.keys():
            t, w1, w2 = data[b].decode('utf-8').split(',')
            t, w1, w2 = int(t), int(w1), int(w2)
            # print('Found Key!')
        if winner == 1:
            w1 += 1
        elif winner == 2:
            w2 += 1
        t += 1
        ## data format = t,1,2
        ## times seen, player1 wins, player 2 wins
        data[board_config] = str(t) + ',' + str(w1) + ',' + str(w2)
    #for key in data.keys():
    #    t, w1, w2 = data[key].decode('utf-8').split(',')
        # if int(t) > 1000: print(key, data[key])
    db_end_keys = len(data.keys())
    data.close()
    print('Total logs: %d' % db_end_keys)
    print('New Configurations Found: %d' % (db_end_keys - db_start_keys))
    log_function('end_game', (time.time() - t_start))

def end_turn(current_turn):
    if current_turn == 1:
        return 2
    else:
        return 1

def play_game(player_1='c', player_2='c', graphics=False):
    """
    Play a game of checkers.
    p1 and p2 can be 'h' for human or 'c' for computer
    graphics can be True or False
    """
    game_start = time.time()
    # turn on graphics if there is human in the loop
    if player_1 == 'h' or player_2 == 'h':
        graphics = True

    board = new_game()
    player_turn = 1

    if graphics:
        window = checker_graphics.initialize_graphics_window()
        checker_graphics.draw_board(board, window)

    board_history = [board]
    move_history = []

    while True:
        # print(board)
        # check if the game has ended
        # print('%s\'s turn.' % players[player_turn][1])
        legal_moves = get_legal_moves(board, echo=False)

        # Check if this player will get another turn due to a jump
        # If the first legal move has magnitude 2, this is true

        turn = get_turn(board)
        if not legal_moves:
            end_game(datafile, board_history, get_turn(next_turn(board)))
            break
        if not get_legal_moves(next_turn(board), echo=False):
            end_game(datafile, board_history, turn)
            break
        r1, c1, r2, c2 = legal_moves[0]
        if abs(r1-r2) == 1:
            # if the first legal move is a single space
            # the other player will go next turn.
            player_turn = end_turn(player_turn)
        # next player makes a move
        if (turn == 1 and player_1 == 'h') or (turn == 2 and player_2 == 'h'):
            r1, c1, r2, c2 = checker_graphics.get_graphics_move(window)
            # check if human pressed 'reset' or 'quit'
            if r2 == 9 and c2 == 8:
                break
            if r2 == 9 and c2 == 1:
                board = new_game()
                checker_graphics.draw_board(board, window)
                continue
        else:
            r1, c1, r2, c2 = \
                pick_best_move(board, board_history, legal_moves, echo=False)

        if [r1, c1, r2, c2] in legal_moves:
            board = move(r1, c1, r2, c2, board)
            board_history.append(board)
            move_history.append([r1, c1, r2, c2])
        else:
            is_legal_move(r1, c1, r2, c2, board,echo=True)

        if graphics:
            checker_graphics.draw_board(board, window)
            if time_step != 0:
                update()
            time.sleep(time_step)

    if graphics:
        window.close()
    print('Total Game Time: %.2f seconds' % (time.time() - game_start))

### MAIN
NUM_GAMES = 1

for game_number in range(NUM_GAMES):
    print('Game %d of %d...' % ((game_number+1), (NUM_GAMES)))
    play_game('h','c',graphics=False)

report_game_metrics()
report_repeated_boards()
