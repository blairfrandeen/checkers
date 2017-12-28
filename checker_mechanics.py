#checker_mechanics.py
from checker_parameters import *
import time

def capture(r,c, board):
    """capture (remove) a piece from play"""
    t_start = time.time()
    piece = get_piece(r, c, board)
    if piece == None:
        print("capture: not a valid piece.")
        return 0
    if piece == b_sq or piece == w_sq:
        print("capture: cannot capture an empty square.")
        return 0
    board = replace_piece(r,c,b_sq,board)
    log_function('capture',(time.time() - t_start))
    return board

def get_piece_index(r, c):
    ## Pieces only go in:
    # - odd rows and even columns
    # - even rows and odd columns
    t_start = time.time()
    if (r % 2 == 0 and c % 2 == 0) or (r % 2 != 0 and c % 2 != 0):
        log_function('get_piece_index',(time.time() - t_start))
        return None
    else:
        log_function('get_piece_index',(time.time() - t_start))
        return (r-1)*4 + c // 2 - r % 2 + 1


def get_piece_rc(index):
    t_start = time.time()
    r = (index-1) // 4 + 1
    c = 2 * index - 8 * (r - 1)
    if r % 2 == 0:
        c -= 1 #I know there is a more concise way to do this...
    log_function('get_piece_rc',(time.time() - t_start))# print(best_move)
    return r,c

def get_piece(r, c, board):
    """Returns which piece is at a given position by parsing global string board"""
    t_start = time.time()
    if type(r) != int or type(c) != int:
        raise LookupError('get_piece: invalid input!')
    if not is_in_bounds(r,c): #(r > 8) or (c > 8) or (r < 1) or (c < 1):
        raise LookupError("get_piece: no such position exists!")
    ind = get_piece_index(r, c) #(r-1)*4 + c // 2 - r % 2
    if ind == None:
        log_function('get_piece',(time.time() - t_start))
        return w_sq
    else:
        log_function('get_piece',(time.time() - t_start))# print(best_move)
        #print('index: %d' % ind,end=': ')
        return board[(int(ind))]

def get_turn(board):
    """return who's turn it is (1 or 2)"""
    return int(board[0])

def next_turn(board):
    """update the board for the next player's turn"""
    if get_turn(board) == 1:
        next = 2
    elif get_turn(board) == 2:
        next = 1
    new_board = str(next) + board[1:]
    return new_board
    
def new_game():
    """Resets the board to new game."""
    board = ['1'] + [players[2][0]]*12 + [b_sq]* 8 + [players[1][0]]*12
    return ''.join(board)

def replace_piece(r, c, p, board):
    """Updates the board variable
    r: row to update
    c: column to update
    p: new piece to place at that position"""
    t_start = time.time()
    p_0 = get_piece(r,c,board) # check the piece we are replacing
    if p_0 == w_sq or p_0 == None:
        print("replace_piece: tried to replace a white square or invalid piece.")
        return board
    # get the index of the piece we are replacing
    ind = get_piece_index(r,c)
    new_board = board[:ind] + p + board[ind+1:]
    log_function('replace_piece',(time.time() - t_start))# print(best_move)
    return new_board

def is_king(r, c, board):
    return get_piece(r,c, board).isupper()

def make_king(r, c, board):
    king = get_piece(r,c,board).upper()
    # print('making king at %d, %d.' % (r,c))
    board = replace_piece(r,c,king,board)
    return board

def is_in_bounds(*args):
    for a in args:
        if a > 8 or a < 1:
            return False
    return True

def get_legal_moves(board,echo=False):
    t_start = time.time()
    must_jump = False
    moves = []
    magnitudes = [2,1] # start by checking jumps.
    turn = get_turn(board)
    for m in magnitudes:
        pieces = 0
        if m == 1 and must_jump == True:
            break # if jump moves exist, ignore single space moves
        deltas = [[m,m],[m,-m],[-m,m],[-m,-m]]
        for b in range(len(board)):
            if board[b].lower() == players[turn][0]:
                mv = 0 # moves a given piece has
                r,c = get_piece_rc(b) # location of that piece
                pieces += 1 # total pieces the player has
                for d in deltas:
                    r_d = r + d[0] # possible new row
                    c_d = c + d[1] # possible new column
                    if is_legal_move(r,c,r_d,c_d,board,echo=False):
                        moves.append([r,c,r_d,c_d])
                        mv += 1
                        if m == 2:
                            must_jump = True
                            if echo == True: print('Must Jump!!')

    if echo == True: print(moves)
    log_function('get_legal_moves',(time.time() - t_start))# print(best_move)
    return moves

def is_legal_move(r1,c1,r2,c2,board,echo=True):
    t_start = time.time()
    if not is_in_bounds(r1,c1,r2,c2):
        if echo == True: print("move: out of bounds.")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    
    # check that position 2 is open
    d = get_piece(r2,c2, board) # destination
    if d != b_sq:
        if echo == True: print("move: ending position is not open.")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    
    # check if the piece is a king (allowed to move backwards)
    p = get_piece(r1,c1, board) # piece to move
    if not is_king(r1,c1, board):
        if (p.lower() == p1 and r2 > r1) or (p.lower() == p2 and r2 < r1):
            if echo == True: print("move: Cannot move a non-king backwards!")
            log_function('is_legal_move (false)',(time.time() - t_start))
            return False
        
    # check that there is a piece at position 1:
    if p == None:
        if echo == True: print("move: no piece at that starting position.")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    
    # check that the right player is moving:
    turn = get_turn(board)
    if p.lower() != players[turn][0]:
        if echo == True: print("It's %s's turn, not yours!" % players[turn][1])
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    
    # check that the piece moves on a diagonal
    if abs(r2-r1) != abs(c2-c1):
        if echo == True: print("move: pieces must move on a diagonal!")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    # check if the piece tries to move too far
    if abs(r2-r1) > 2:
        if echo == True: print("move: cannot move more than two spaces.")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    elif abs(r2-r1) == 2:
        # check if there is a piece to jump here
        r_mid = int((r1 + r2) / 2)
        c_mid = int((c1 + c2) / 2)
        p_mid = get_piece(r_mid, c_mid, board).lower()
        if p_mid == None or p_mid == w_sq or p_mid == b_sq:
            if echo == True: print("Move: Cannot jump an empty or invalid square!")
            log_function('is_legal_move (false)',(time.time() - t_start))
            return False
        elif p_mid == p.lower():
            if echo == True: print("Move: Cannot jump your own piece!")
            log_function('is_legal_move (false)',(time.time() - t_start))
            return False

    log_function('is_legal_move (true)',(time.time() - t_start))
    return True

def move(r1, c1, r2, c2, board):
    """Move a piece from position 1 to position 2"""
    t_start = time.time()
    p = get_piece(r1,c1, board) # piece to move

    if not is_legal_move(r1,c1,r2,c2,board,echo=False):
        print("Invalid Move!")
        return board
    if abs(r2-r1) == 2:
        # check if there is a piece to jump here
        r_mid = int((r1 + r2) / 2)
        c_mid = int((c1 + c2) / 2)
        # capture the piece
        board = capture(r_mid, c_mid, board)
        board = next_turn(board)
            
    # go ahead and move the piece
    board = replace_piece(r1,c1,b_sq,board) # empty square where the piece was
    board = replace_piece(r2,c2,p,board) # moved piece
    # check to see if we made a king
    # if player 1 makes it to row 1
    # or if player 2 makes it to row 8
    if (p == p1 and r2 == 1) or (p == p2 and r2 == 8):
        if not is_king(r2,c2,board):
            board = make_king(r2,c2,board)
    
    board = next_turn(board)
    log_function('move',(time.time() - t_start))# print(best_move)
    return board


