#checker_mechanics.py
from checker_parameters import *
import time

def capture(row, col, board):
    """capture (remove) a piece from play"""
    t_start = time.time()
    piece = get_piece(row, col, board)
    if piece == None:
        print("capture: not a valid piece.")
        return 0
    if piece == b_sq or piece == w_sq:
        print("capture: cannot capture an empty square.")
        return 0
    board = replace_piece(row, col, b_sq, board)
    log_function('capture', (time.time() - t_start))
    return board

def get_piece_index(r, c):
    ## Pieces only go in:
    # - odd rows and even columns
    # - even rows and odd columns
    t_start = time.time()
    if (r % 2 == 0 and c % 2 == 0) or (r % 2 != 0 and c % 2 != 0):
        log_function('get_piece_index', (time.time() - t_start))
        return None
    else:
        log_function('get_piece_index', (time.time() - t_start))
        index = int((r-1)*4 + c // 2 - r % 2 + 1)
        return index

def get_piece_rc(index):
    t_start = time.time()
    r = (index-1) // 4 + 1
    c = 2 * index - 8 * (r - 1)
    if r % 2 == 0:
        c -= 1 #I know there is a more concise way to do this...
    log_function('get_piece_rc', (time.time() - t_start))
    return r, c

def get_player_num(row, col, board):
    """
    Get the player number (1 or 2) based on the
    row, column, and board
    """
    piece = get_piece(row, col, board)
    if piece in [1, 3]:
        return 1
    elif piece in [2, 4]:
        return 2
    else:
        # print("get_player_num: attempted to access empty spot.")
        return None

def get_piece(row, col, board):
    """Returns which piece is at a given position by parsing global string board"""
    t_start = time.time()
    if type(row) != int or type(col) != int:
        raise LookupError('get_piece: invalid input!')
    if not is_in_bounds(row, col): #(r > 8) or (c > 8) or (r < 1) or (c < 1):
        raise LookupError("get_piece: no such position exists!")
    ind = get_piece_index(row, col) #(r-1)*4 + c // 2 - r % 2
    if ind == None:
        log_function('get_piece', (time.time() - t_start))
        return w_sq
    else:
        log_function('get_piece', (time.time() - t_start))
        #print('index: %d' % ind,end=': ')
        return int(board[ind])

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

def replace_piece(row, col, new_piece, board):
    """Updates the board variable
    row: row to update
    col: column to update
    new_piece: new piece to place at that position"""
    t_start = time.time()
    old_piece = get_piece(row, col, board) # check the piece we are replacing
    if old_piece == w_sq or old_piece == None:
        print("replace_piece: tried to replace a black square or invalid piece.")
        return board
    # get the index of the piece we are replacing
    ind = get_piece_index(row, col)
    new_board = board[:ind] + str(new_piece) + board[ind+1:]
    log_function('replace_piece', (time.time() - t_start))
    return new_board

def is_king(row, col, board):
    """Checks if a piece at a given row and col is a king"""
    return get_piece(row, col, board) > 2

def make_king(row, col, board):
    """Makes a piece into a king"""
    king = get_piece(row, col, board) + 2
    # print('making king at %d, %d.' % (r,c))
    board = replace_piece(row, col, king, board)
    return board

def is_in_bounds(*args):
    for a in args:
        if a > 8 or a < 1:
            return False
    return True

def get_legal_moves(board, echo=False):
    t_start = time.time()
    must_jump = False
    moves = []
    magnitudes = [2, 1] # start by checking jumps.
    current_player = [get_turn(board), (get_turn(board) + 2)]
    for m in magnitudes:
        pieces = 0
        if m == 1 and must_jump == True:
            break # if jump moves exist, ignore single space moves
        deltas = [[m,m],[m,-m],[-m,m],[-m,-m]]
        for b in range(len(board)):
            if int(board[b]) in current_player:
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
                            if echo: print('Must Jump!!')

    if echo: print(moves)
    log_function('get_legal_moves',(time.time() - t_start))# print(best_move)
    return moves

def is_legal_move(r1,c1,r2,c2,board,echo=True):
    t_start = time.time()
    if not is_in_bounds(r1,c1,r2,c2):
        if echo == True: print("move: out of bounds.")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    
    # check that position 2 is open
    d = str(get_piece(r2, c2, board)) # destination
    if d != b_sq:
        if echo: print("move: ending position is not open.")
        log_function('is_legal_move (false)',(time.time() - t_start))
        return False
    
    # check if the piece is a king (allowed to move backwards)
    p = get_piece(r1, c1, board) # piece to move
    if not is_king(r1, c1, board):
        if (p == int(p1) and r2 > r1) or (p == int(p2) and r2 < r1):
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
    if (p != turn) and (p != turn+2):
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
        p_mid = get_player_num(r_mid, c_mid, board)
        #if is_king(r_mid,c_mid,board):
            #p_mid -= 2
        if p_mid == None or p_mid == int(b_sq):
            if echo == True: print("Move: Cannot jump an empty or invalid square!")
            log_function('is_legal_move (false)',(time.time() - t_start))
            return False
        elif p_mid == turn:# p or p_mid == p + 2:
            if echo: print("Move: Cannot jump your own piece!")
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
    if (p == int(p1) and r2 == 1) or (p == int(p2) and r2 == 8):
        if not is_king(r2,c2,board):
            board = make_king(r2,c2,board)
    
    board = next_turn(board)
    log_function('move',(time.time() - t_start))# print(best_move)
    return board


