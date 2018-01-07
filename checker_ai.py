#checkers_ai.py
"""All AI functions for checkers game end up here"""
import random
import time
import copy
import function_timer as ft

# Maximum moves to look ahead
MAX_RECURSION_DEPTH = 2
# Note, if we assume that each player has 8 moves availble
# on any given turn, eval_move will be run 8*8*8 = 512 times
# for a recursion depth of 3. For a recursion depth of 4,
# eval move is run 4096 times. since eval_move takes about 2 ms
# to run, a recursion depth of 4 means it will take 8 seconds
# to pick each move. Increase this number with caution!

def print_turn_eval(game, board):
    """Print basic info prior to evaluating which move to make."""
    moves_available = len(board.get_legal_moves())
    num_pieces_self = 0
    num_pieces_opp = 0
    num_kings_self = 0
    num_kings_opp = 0

    print('TURN # %d EVALUATION (%s):' % \
        ((len(game.move_history) + 1), game.players[board.turn].color))
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

def score_moves(game, board, echo):
    """
    Determine the available legal moves. Run eval_move on each.
    Return a dictionary of scored moves to be used by either
    a recursive instance of eval_move, or by pick_best_move.
    """
    legal_moves = board.get_legal_moves()
    scored_moves = dict()
    for possible_move in legal_moves:
        success_chance = eval_move(possible_move, game, board, echo=echo)
        if success_chance != 0 and success_chance is not None:
            if success_chance not in scored_moves:
                scored_moves[success_chance] = [possible_move]
            else:
                scored_moves[success_chance] = [possible_move] + scored_moves[success_chance]

    return scored_moves

def pick_best_move(game, board, echo=False):
    """
    Start with an array of available moves
    and pick the best one based on the probabilities
    found in eval_move
    """
    t_start = time.time()

    # No reason to evaluate if only one move available
    # but for now I want to see the score results,
    # even for a single move. Game should run faster
    # if the followin three lines are uncommented:
    # legal_moves = board.get_legal_moves()
    # if len(legal_moves) == 1:
    #     return legal_moves[0]

    if echo:
        print_turn_eval(game, board)

    scored_moves = score_moves(game, board, echo=echo)

    if echo:
        print('SUMMARY:')
        print('---------------')
        for score in sorted(scored_moves.keys()):
            moves_at_score = scored_moves[score]
            move_str = ''
            for move in moves_at_score:
                move_str = move_str + move.__str__()
            print('SCORE %.2f: %s' % (score, move_str))
        print('-------------\n')

    if scored_moves.keys():
        best_score = max(scored_moves.keys())
    else:
        print('NO MORE UNIQUE MOVES!')
        return None

    ft.log_function('pick_best_move', t_start)

    # if two or more moves have the same score, pick randomly betweent them.
    return random.choice(scored_moves[best_score])

def eval_move(move, game, board, recursion_depth=1, echo=False):
    """Function to evaluate the probability of a move
    leading to a successful outcome."""
    t_start = time.time()
    # make a copy of the existing board, and execute the move
    # under consideration
    result_board = copy.deepcopy(board)
    result_board.execute_move(move)

    # check if the resulting board has already been seen before
    # on this players turn. If it has, do a different move
    # this helps to avoid infinite loops that should be a draw
    result_int = result_board.int_rep()
    if result_int in game.board_history[result_board.turn]:
        if echo:
            print("eval_move: Already seen this configuration.")
        return None

    # number of moves to choose between
    move.moves_available = len(board.get_legal_moves())

    # how far are we into the game
    move.turn_num = len(game.move_history) + 1

    # count the number of pieces and kings on both sides
    move.num_pieces_self = 0
    move.num_pieces_opp = 0
    move.num_kings_self = 0
    move.num_kings_opp = 0
    for key in board.pieces.keys():
        piece = board.pieces[key]
        if piece.player.number == board.turn:
            move.num_pieces_self += 1
            if piece.is_king:
                move.num_kings_self += 1
        else:
            move.num_pieces_opp += 1
            if piece.is_king:
                move.num_kings_opp += 1
    if echo:
        print(move)

    # look at the legal moves for the next configuration
    result_legal_moves = result_board.get_legal_moves()

    if result_board.turn == board.turn:
        if not result_legal_moves:
            if echo:
                print('This move would lose the game.')
            return 0
        move.self_resulting_moves = len(result_legal_moves)
        move.opp_resulting_moves = 0
        if echo:
            print('Self Resulting Moves: %d' % move.self_resulting_moves)
    else:
        if not result_legal_moves:
            if echo:
                print('This would be a winning move!')
            return 1000
        move.opp_resulting_moves = len(result_legal_moves)
        move.self_resulting_moves = 0
        if echo:
            print('Opponent Resulting Moves: %d' % move.opp_resulting_moves)

    # test to see if this move forces a jump next turn
    move.forces_jump = result_legal_moves[0].is_jump()

    # check to see if a move will make a king
    move_piece = board.pieces[move.start_position] # current piece we are moving
    result_piece = result_board.pieces[move.end_position]
    move.makes_king = False
    if not move_piece.is_king: # if not already a king
        if result_piece.is_king:
            move.makes_king = True
        # for key in result_board.pieces.keys(): # for each piece on the resulting board
        #     result_piece = result_board.pieces[key]
        #     if result_piece.player.number == board.turn and result_piece.is_king:
        #         move.makes_king = True
        if echo and move.makes_king:
            print('This Move Makes a King')

    move.takes_king = False
    if move.is_jump():
        if board.pieces[move.mid_pos()].is_king:
            move.takes_king = True
            if echo:
                print('The Move Would Take a King')

    # will the move result in any threats?
    move.self_pieces_threatened = 0
    move.num_threats = 0
    move.king_threats = 0
    if result_legal_moves[0].is_jump():
        if echo:
            print('This Move Results in a Capture!')
        # see exactly how many pieces are threatened
        move.threatened_positions = []
        move.threatened_kings = []
        for jump_move in result_legal_moves:
            if jump_move.mid_pos() not in move.threatened_positions:
                move.threatened_positions.append(jump_move.mid_pos())
                move.self_pieces_threatened += 1
                if result_board.pieces[jump_move.mid_pos()].is_king:
                    move.threatened_kings.append(jump_move.mid_pos())
        move.num_threats = len(move.threatened_positions)
        if echo:
            print('Total threats: %d' % move.num_threats)
        move.king_threats = len(move.threatened_kings)
        if echo:
            print('The following pieces would be threatened:')
            for pos in move.threatened_positions:
                print('Piece at %s' % pos, end=' ')
                if result_board.pieces[pos].is_king:
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
    score = 5 # DEFAULT SCORE

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

    MAKE_KING = 1.5
    TAKE_KING = 1.5
    PCS_THREATENED = 0.25
    NUM_THREATS = 0.25
    OPP_MOVES = 0.5

    if move.makes_king:
        score = score * MAKE_KING

    if move.takes_king:
        score = score * TAKE_KING

    if move.self_pieces_threatened != 0:
        score = score * PCS_THREATENED \
            / move.self_pieces_threatened

    if move.num_threats != 0:
        score = score * NUM_THREATS \
            / move.num_threats

    if move.opp_resulting_moves != 0 and move.num_threats == 0:
        score = score / OPP_MOVES / move.opp_resulting_moves

    # if the evaluator of this move will get to go again:
    if move.self_resulting_moves != 0:
        if move.forces_jump:
            score = score * 10 * move.self_resulting_moves
        else:
            score = score * move.self_resulting_moves

    return score
