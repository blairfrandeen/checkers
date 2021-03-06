#checkers_ai.py
"""All AI functions for checkers game end up here"""
import random
import time
import copy
import function_timer as ft

# Maximum moves to look ahead (NOT IMPLEMENTED)
MAX_RECURSION_DEPTH = 2
# Note, if we assume that each player has 8 moves availble
# on any given turn, eval_move will be run 8*8*8 = 512 times
# for a recursion depth of 3. For a recursion depth of 4,
# eval move is run 4096 times. since eval_move takes about 2 ms
# to run, a recursion depth of 4 means it will take 8 seconds
# to pick each move. Increase this number with caution!

# If true, AI will not make a move that results in a config that
# has already been seen. May lead to draws or AI losses which are
# unnecessary, since not all possible threads will be played out.
IGNORE_REPEAT_CONFIGS = True

def print_turn_eval(config):
    """Print basic info prior to evaluating which move to make."""
    print('TURN # %d EVALUATION (%s):' % \
        ((config.num_moves + 1), config.players[config.turn]['color']))
    print('------------------------')
    print('Total Moves Available: %d' % len(config.legal_moves))
    print('Self Pieces:     %d (%d kings)' % \
        (config.pieces_remaining[config.turn], config.kings_remaining[config.turn]))
    print('Opponent Pieces: %d (%d kings)' % \
        (config.pieces_remaining[config.next_turn()], config.kings_remaining[config.next_turn()]))
    print('------------------------')

def rank_moves(config, echo):
    """
    Determine the available legal moves. Run eval_move on each.
    Return a dictionary of scored moves to be used by either
    a recursive instance of eval_move, or by pick_best_move.
    """
    ranked_moves = dict()
    for possible_move in config.legal_moves:
        success_chance = eval_move(possible_move, config, echo=echo)
        if success_chance != 0 and success_chance is not None:
            if success_chance not in ranked_moves:
                ranked_moves[success_chance] = [possible_move]
            else:
                ranked_moves[success_chance] = [possible_move] + ranked_moves[success_chance]

    if echo:
        print('SUMMARY:')
        print('---------------')
        for score in sorted(ranked_moves.keys()):
            moves_at_score = ranked_moves[score]
            move_str = ''
            for move in moves_at_score:
                move_str = move_str + move.__str__()
            print('SCORE %.2f: %s' % (score, move_str))
        print('-------------\n')

    return ranked_moves

def pick_best_move(config, echo=False):
    """
    Start with an array of available moves
    and pick the best one based on the probabilities
    found in eval_move
    """
    t_start = time.time()

    # No reason to evaluate if only one move available
    # but for now I want to see the score results,
    # even for a single move. Game should run faster
    # if the followin twolines are uncommented:
    # if len(config.legal_moves) == 1:
    #     return legal_moves[0]

    if echo:
        print_turn_eval(config)

    ranked_moves = rank_moves(config, echo=echo)

    if ranked_moves.keys():
        best_score = max(ranked_moves.keys())
    else:
        print('NO MORE UNIQUE MOVES!')
        return None

    ft.log_function('pick_best_move', t_start)

    # if two or more moves have the same score, pick randomly betweent them.
    return random.choice(ranked_moves[best_score])

def eval_move(move, config, echo=False):
    """Function to evaluate the probability of a move
    leading to a successful outcome."""
    t_start = time.time()
    if echo:
        print(move)

    # make a copy of the existing board, and execute the move
    # under consideration
    result_config = copy.deepcopy(config)
    result_config.execute_move(move)

    # check if the resulting board has already been seen before
    # on this players turn. If it has, do a different move
    # this helps to avoid infinite loops that should be a draw
    # if IGNORE_REPEAT_CONFIGS:
    #     result_int = config.
    #     if result_int in config.history:
    #         # if echo:
    #         print("eval_move: Already seen this configuration.")
    #         return None

    # number of moves to choose between
    move.num_options = len(config.legal_moves)

    # how far are we into the game
    move.turn_num = config.num_moves

    # how many options result from this move
    move.num_result_options = len(result_config.legal_moves)

    # NOTE: if move.is_jump(), current player goes again.

    # check if this is a winning or losing move.
    if move.is_jump(): # if evaluator will move again
        if move.num_result_options == 0:
            if echo:
                print('This move would lose the game.')
            return 0
        if echo:
            print('Self Resulting Moves: %d' % move.num_result_options)
    else:
        if move.num_result_options == 0:
            if echo:
                print('This would be a winning move!')
            return 1
        if echo:
            print('Opponent Resulting Moves: %d' % move.num_result_options)

    # test to see if this move forces a jump next turn
    move.forces_jump = result_config.legal_moves[0].is_jump()

    # check to see if a move will make a king
    move.makes_king = False
    if not config.positions[move.start_position].is_king: # if not already a king
        if result_config.positions[move.end_position].is_king:
            move.makes_king = True
        if echo and move.makes_king:
            print('This Move Makes a King')

    move.takes_king = False
    if move.is_jump():
        if config.positions[move.mid_pos()].is_king:
            move.takes_king = True
            if echo:
                print('The Move Would Take a King')

    # will the move result in any threats?
    move.self_pieces_threatened = 0
    move.num_threats = 0
    move.king_threats = 0
    if result_config.legal_moves[0].is_jump():
        if echo:
            print('This Move Results in a Capture!')
        # see exactly how many pieces are threatened
        move.threatened_positions = []
        move.threatened_kings = []
        for jump_move in result_config.legal_moves:
            if jump_move.mid_pos() not in move.threatened_positions:
                move.threatened_positions.append(jump_move.mid_pos())
                move.self_pieces_threatened += 1
                if result_config.positions[jump_move.mid_pos()].is_king:
                    move.threatened_kings.append(jump_move.mid_pos())
        move.num_threats = len(move.threatened_positions)
        if echo:
            print('Total threats: %d' % move.num_threats)
        move.king_threats = len(move.threatened_kings)
        if echo:
            print('The following pieces would be threatened:')
            for pos in move.threatened_positions:
                print('Piece at %s' % pos, end=' ')
                if result_config.positions[pos].is_king:
                    print('(KING)')
                else:
                    print('\n', end='')

    score = calculate_score(move)
    if score != 0 and score is not None and echo:
        print('--- MOVE SCORE: %.2f' % score)
        print('')
    ft.log_function('eval_move', t_start)
    return score

def calculate_score(move):
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
    score = 0.5 # DEFAULT SCORE 50% CHANCE OF SUCCESS

    # AI_MULTIPLIERS = {\
    #     'moves_available': 1,\
    #     'move_num': 1,\
    #     'num_pieces_self': 1,\
    #     'num_pieces_opp': 1,\
    #     'num_kings_self': 1,\
    #     'num_kings_opp': 1,\
    #     'makes_king': 1.5,\
    #     'takes_king': 1.5,\
    #     'num_resulting_moves': 0.5,\
    #     'self_pieces_threatened': 0.25,\
    #     'num_threats': 0.25}

    ### INCREASE SCORE FOR DECREASED OPP MOVES
    MAKE_KING = 0.1
    TAKE_KING = 0.15
    MULT_JUMP = 0.2
    PCS_THREATENED = 0.1
    NUM_THREATS = 0.25
    NUM_RES_OPT = 0.05

    if move.makes_king:
        score = score + MAKE_KING

    if move.takes_king:
        score = score + TAKE_KING

    if move.self_pieces_threatened != 0:
        score = score - PCS_THREATENED * move.self_pieces_threatened

    if move.num_threats != 0:
        score = score * NUM_THREATS / move.num_threats

    # increase score for more options if current player goes again
    if move.is_jump:
        score = score + move.num_result_options * NUM_RES_OPT
    else:
        # decrease score for more options if opponent plays next
        score = score - move.num_result_options * NUM_RES_OPT
    if move.is_jump() and move.forces_jump:
        score = score + MULT_JUMP

    return score

def alter_score(score, factor):
    # score must always be between zero and 1
    # alteration factors shall be between -1 and 1
    pass
