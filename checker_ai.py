#checkers_ai.py
"""All AI functions for checkers game end up here"""
import random
import dbm
import time
import copy
import function_timer as ft
from graphics import *

MAXIMUM_DB_SEARCH_TURN = 6 # May increase as more data is collected
REP_BOARD_DICT = dict()

def pick_best_move(game, board, echo=False):
    """
    Start with an array of available moves
    and pick the best one based on the probabilities
    found in eval_move
    """
    t_start = time.time()
    legal_moves = board.get_legal_moves()
    # No reason to evaluate if only one move available
    # but for now I want to see the results
    # if len(legal_moves) == 1:
    #     return legal_moves[0]
    moves_available = len(board.get_legal_moves())
    num_pieces_self = 0
    num_pieces_opp = 0
    num_kings_self = 0
    num_kings_opp = 0

    #### MOVE THE FOLLOWING TO SEPARATE FUNCTION:
    print('MOVE # %d EVALUATION:' % (len(game.move_history) + 1))
    print('------------------------')
    for key in board.pieces.keys():
        piece = board.pieces[key]
        if piece.player.number == board.turn:
            num_pieces_self += 1
            if piece.is_king:
                num_kings_self += 1
        else:
            num_pieces_opp += 1
            if piece.is_king:
                num_kings_opp += 1
    print('Total Moves Available: %d' % moves_available)
    print('Self Pieces:     %d (%d kings)' % (num_pieces_self, num_kings_self))
    print('Opponent Pieces: %d (%d kings)' % (num_pieces_opp, num_kings_opp))
    print('------------------------')

    scored_moves = dict()
    for possible_move in legal_moves:
        success_chance = eval_move(possible_move, game, board, echo=True)
        if success_chance:
            if success_chance not in scored_moves:
                scored_moves[success_chance] = [possible_move]
            else:
                scored_moves[success_chance] = [possible_move] + scored_moves[success_chance]
        # if success_chance == 0:
        #     legal_moves.remove(possible_move)
        #     continue

    print('SUMMARY:')
    print('---------------')
    for score in sorted(scored_moves.keys()):
        moves_at_score = scored_moves[score]
        move_str = ''
        for move in moves_at_score:
            move_str = move_str + move.__str__()
        print('SCORE %.2f: %s' % (score, move_str))
        move_str = ''
    print('-------------\n')

    ### CHOOSE SOMETHING ELSE
    if scored_moves.keys():
        best_score = max(scored_moves.keys())
    else:
        print('NO MORE UNIQUE MOVES!')
    ft.log_function('pick_best_move', t_start)
    # del scored_moves
    return random.choice(scored_moves[best_score])

def log_repeated_boards(turn, found_board):
    """
    Logs the average number of times a familiar configuration has been seen
    Based on the current turn.
    Hypothesis is that more familiar configurations have been seen
    earlier in the game.
    
    turn: How many turns into the game a search was made
    found_board: Boolean whether or not a board was found
    """
    ### DATA FORMAT: { KEY: [TOTAL, FOUND] }
    rep_board_data = dbm.open('repdata','c')
    turn_data = [0, 0]
    turn = str(turn).encode('utf-8')
    if turn in rep_board_data.keys():
        turn_data = pickle.loads(rep_board_data[turn])
    total_times_searched = turn_data[0]
    total_times_found = turn_data[1]
    total_times_searched += 1
    if found_board:
        total_times_found += 1
    rep_board_data[turn] = pickle.dumps([total_times_searched, total_times_found])
    rep_board_data.close()

def report_repeated_boards():
    rep_board_data = dbm.open('repdata', 'r')
    formatted_board_data = dict()
    for key in rep_board_data.keys():
        formatted_board_data[int(key)] =  pickle.loads(rep_board_data[key])
    print('Turn\tSuccessful Searches\tTotal Searches\tSuccess Chance')
    print('----\t-------------------\t--------------\t--------------')
    for turn_key in sorted(formatted_board_data.keys()):
        total_searches, successful_searches = formatted_board_data[turn_key]
        success_chance = successful_searches / total_searches
        if turn_key < MAXIMUM_DB_SEARCH_TURN * 2:
            print('{:3d} \t\t{:5d} \t\t\t{:5d} \t\t{:.3f}'.format\
                (turn_key, successful_searches, \
                total_searches, success_chance))
    rep_board_data.close()

def eval_move(possible_move, game, board, echo=False):
    """Function to evaluate the probability of a move
    leading to a successful outcome."""
    t_start = time.time()
    # make a copy of the existing board, and execute the move
    # under consideration
    result_board = copy.deepcopy(board)
    result_board.execute_move(possible_move)

    # check if the resulting board has already been seen before
    # on this players turn. If it has, do a different move
    # this helps to avoid infinite loops that should be a draw
    result_int = result_board.int_rep()
    if result_int in game.board_history[board.turn]:
        if echo: print("Already Been Here, Done That!")
        return None

    # gather some basic information about the current configuration
    moves_available = len(board.get_legal_moves())
    move_num = len(game.move_history) + 1
    num_pieces_self = 0
    num_pieces_opp = 0
    num_kings_self = 0
    num_kings_opp = 0
    for key in board.pieces.keys():
        piece = board.pieces[key]
        if piece.player.number == board.turn:
            num_pieces_self += 1
            if piece.is_king:
                num_kings_self += 1
        else:
            num_pieces_opp += 1
            if piece.is_king:
                num_kings_opp += 1
    if echo:
        print(possible_move)   

    # look at the legal moves for the next configuration
    result_legal_moves = result_board.get_legal_moves()
    num_resulting_moves = len(result_legal_moves)
    if echo: print('Opponent Moves Available: %d' % num_resulting_moves)
   
    # check to see if a move will make a king
    makes_king = False
    takes_king = False ## NEED TO IMPLEMENT
    for key in result_board.pieces.keys():
        result_piece = result_board.pieces[key]
        move_piece = board.pieces[possible_move.start_position]
        # if our turn AND result becomes king 
        # AND not already king
        if result_piece.player.number == board.turn \
            and result_piece.is_king\
            and not move_piece.is_king: ## TO DO: ADD NOT ALREADY KING HERE!!
            makes_king = True
    if echo and makes_king:
        print('This Move Makes a King')
    
    # is the resulting move a winning move?
    if num_resulting_moves == 0:
        if echo: print('This is a winning move!')
        return 1

    # will the move result in getting jumped?
    self_pieces_threatened = 0
    num_threats = 0
    king_threats = 0
    if result_legal_moves[0].is_jump():
        if echo: print('This Move Results in a Capture!')
        # see exactly how many pieces are threatened
        threatened_positions = []
        threatened_kings = []
        for jump_move in result_legal_moves:
            if jump_move.mid_pos() not in threatened_positions:
                threatened_positions.append(jump_move.mid_pos())
                self_pieces_threatened += 1
                if result_board.pieces[jump_move.mid_pos()].is_king:
                    threatened_kings.append(jump_move.mid_pos())
        num_threats = len(threatened_positions)
        print('Num_threats: %d' % num_threats)
        king_threats = len(threatened_kings)
        if echo:
            print('The following pieces are threatened:')
            for pos in threatened_positions:
                print('Piece at %s' % pos, end=' ')
                if result_board.pieces[pos].is_king:
                    print('(KING)')
                else:
                    print('\n',end='')
    
    del result_board
    score = calculate_success(moves_available, move_num, num_pieces_self, num_pieces_opp, \
        num_kings_self, num_kings_opp, makes_king, takes_king, num_resulting_moves, \
        self_pieces_threatened, num_threats)
    print('MOVE SCORE: %.2f' % score)
    ft.log_function('eval_move', t_start)
    return score

def calculate_success(moves_available, move_num, num_pieces_self, num_pieces_opp, \
    num_kings_self, num_kings_opp, makes_king, takes_king, num_resulting_moves, \
    self_pieces_threatened, num_threats):
    """
    Calculate the chance of this being a "good move" based on the following criteria:

    :moves_available: number of moves to choose between\n
    :move_num: how many moves we are into the game\n
    :num_pieces_self: how many pieces pieces we have left\n
    :num_pieces_opp: how many pieces the opponent has left\n
    :num_kings_self: how many kings we have\n
    :num_kings_opp: how many kings the opponent has\n
    :makes_king: whether this move will make us a king piece\n
    :takes_king: whether this move will capture a king\n
    :num_resulting_moves: how many moves the opponent can choose between after this one\n
    :self_pieces_threatened: how many pieces of ours will be under threat\n
    :num_threats: total number of jump moves opponent can make\n\n

    Returns: Calculated chance of success
    """
    score = 1

    # Fewer moves available should lead to a higher score
    # Score ~ 1/moves_available
    # Maybe??

    # taking and making kings generates a higher score
    if takes_king:
        score += 1
    if makes_king:
        score += 1

    # being threatened reduces score:
    score -= self_pieces_threatened * num_threats

    # giving the opponent fewer options generates a higher score
    # as long as no pieces are threatened
    if self_pieces_threatened == 0:
        score = score / num_resulting_moves
        pass 

    ### IGNORED FOR NOW:
    # move_num
    # num_pieces_self
    # num_pieces_opp
    # num_kings_self
    # num_kings_opp

    return score