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

AI_MULTIPLIERS = {\
    'moves_available': 1,\
    'move_num': 1,\
    'num_pieces_self': 1,\
    'num_pieces_opp': 1,\
    'num_kings_self': 1,\
    'num_kings_opp': 1,\
    'makes_king': 1.5,\
    'takes_king': 1.5,\
    'num_resulting_moves': 0.5,\
    'self_pieces_threatened': 0.25,\
    'num_threats': 0.25}

def print_turn_eval(game, board):
    """Print basic info prior to evaluating which move to make."""
    moves_available = len(board.get_legal_moves())
    num_pieces_self = 0
    num_pieces_opp = 0
    num_kings_self = 0
    num_kings_opp = 0

    print('TURN # %d EVALUATION:' % (len(game.move_history) + 1))
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

    if echo:
        print_turn_eval(game, board)

    scored_moves = dict()
    for possible_move in legal_moves:
        success_chance = eval_move(possible_move, game, board, echo=False)
        if success_chance != 0 and success_chance is not None:
            if success_chance not in scored_moves:
                scored_moves[success_chance] = [possible_move]
            else:
                scored_moves[success_chance] = [possible_move] + scored_moves[success_chance]
    if echo:
        print('SUMMARY:')
        print('---------------')
    for score in sorted(scored_moves.keys()):
        moves_at_score = scored_moves[score]
        move_str = ''
        for move in moves_at_score:
            move_str = move_str + move.__str__()
        if echo:
            print('SCORE %.2f: %s' % (score, move_str))
        move_str = ''
    if echo:
        print('-------------\n')

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
    score_multipliers = dict()
    # make a copy of the existing board, and execute the move
    # under consideration
    result_board = copy.deepcopy(board)
    result_board.execute_move(possible_move)

    # check if the resulting board has already been seen before
    # on this players turn. If it has, do a different move
    # this helps to avoid infinite loops that should be a draw
    result_int = result_board.int_rep()
    if result_int in game.board_history[result_board.turn]:
        # print(game.board_history)
        # print("Already Been Here, Done That!")
        # print(result_int)
        return None
#465452383727610318580351000
#465452383727610318580351000
    # gather some basic information about the current configuration
    score_multipliers['moves_available'] = len(board.get_legal_moves())
    score_multipliers['move_num'] = len(game.move_history) + 1
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
    score_multipliers['num_pieces_self'] = num_pieces_self
    score_multipliers['num_pieces_opp'] = num_pieces_opp
    score_multipliers['num_kings_self'] = num_kings_self
    score_multipliers['num_kings_opp'] = num_kings_opp

    # look at the legal moves for the next configuration
    result_legal_moves = result_board.get_legal_moves()
    score_multipliers['num_resulting_moves'] = len(result_legal_moves)
    if echo: print('Opponent Moves Available: %d' % score_multipliers['num_resulting_moves'])

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
    score_multipliers['makes_king'] = makes_king
    score_multipliers['takes_king'] = takes_king

    # is the resulting move a winning move?
    if score_multipliers['num_resulting_moves'] == 0:
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
        if echo:
            print('Num_threats: %d' % num_threats)
        king_threats = len(threatened_kings)
        if echo:
            print('The following pieces are threatened:')
            for pos in threatened_positions:
                print('Piece at %s' % pos, end=' ')
                if result_board.pieces[pos].is_king:
                    print('(KING)')
                else:
                    print('\n', end='')

    score_multipliers['num_threats'] = num_threats
    score_multipliers['king_threats'] = king_threats
    score_multipliers['self_pieces_threatened'] = self_pieces_threatened

    del result_board
    score = calculate_success(score_multipliers, AI_MULTIPLIERS)
    if score != 0 and score is not None and echo:
        print('--- MOVE SCORE: %.2f' % score)
        print('')
    ft.log_function('eval_move', t_start)
    return score



def calculate_success(sm, AI_MULTIPLIERS):
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
    score = 5

    key = 'makes_king'
    if key in sm.keys():
        if sm[key]:
            score = score * AI_MULTIPLIERS[key]
    
    key = 'self_pieces_threatened'
    if key in sm.keys() and sm[key] != 0:
        score = score * AI_MULTIPLIERS[key] / sm[key]
    
    key = 'num_threats'
    if key in sm.keys() and sm[key] != 0:
        score = score * AI_MULTIPLIERS[key] / sm[key]

    key = 'num_resulting_moves'
    if key in sm.keys() and sm[key] != 0:
        if sm['num_threats'] == 0:
            score = score / AI_MULTIPLIERS[key] / sm[key]

    return score
