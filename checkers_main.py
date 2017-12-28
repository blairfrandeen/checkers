#checkers_main.py
from checker_parameters import *
from checker_mechanics import *
from checker_graphics import *
import random
import dbm
import time

def print_board(board):
    """Print the current board configuration to the console"""
    print('|||  ',end='')
    for c in range(1,9):
        print('%d | ' % c, end='')
    print('')
    r = c = 1
    while r <= 8:
        print('%d |' % r, end='')
        while c <= 8:
            print('  %s ' % get_piece(r,c,board), end='')
            #print(r,c,get_piece(r,c))
            c += 1
        print('\n',end='')
        c = 1
        r += 1

def end_game(datafile,boards,winner):
    t_start = time.time()
    print("Game Over. %s Wins." % players[winner][1])
    db = dbm.open(datafile,'c')
    db_start_keys = len(db.keys())
    print('Logging Results. Total of %d configurations.' % len(boards))
    for b in boards:
        b = b.encode('utf-8')
        t, w1, w2 = 0, 0, 0
        if b in db.keys():
            t, w1, w2 = db[b].decode('utf-8').split(',')
            t, w1, w2 = int(t), int(w1), int(w2)
            # print('Found Key!')
        if winner == 1:
            w1 += 1
        elif winner == 2:
            w2 += 1
        t += 1
        ## data format = t,1,2
        ## times seen, player1 wins, player 2 wins
        db[b] = str(t) + ',' + str(w1) + ',' + str(w2)
    for key in db.keys():
        t, w1, w2 = db[key].decode('utf-8').split(',')
        # if int(t) > 10: print(key, db[key])
    db_end_keys = len(db.keys())
    # print('Total logs: %d' % len(db.keys()))
    print('New Configurations Found: %d' % (db_end_keys-db_start_keys))
    log_function('end_game',(time.time() - t_start))
    db.close()

def eval_move(m,current_board,board_history,datafile,echo=False):
    t_start = time.time()
    p = 0.5 # default probability of a win
    new_board = move(m[0],m[1],m[2],m[3],current_board)
    if new_board in board_history: # don't do any duplicate moves
        #print('Skipped repeated move!')
        log_function('eval_move(skip)',(time.time()-t_start))
        return 0
    new_board = new_board.encode('utf-8')
    db = dbm.open(datafile,'r')
    turn = get_turn(current_board) # whose turn is it?
    if new_board in db.keys():
        t, w1, w2 = db[new_board].decode('utf-8').split(',')
        t, w1, w2 = int(t), int(w1), int(w2)
        if turn == 1:
            p = (w1)/t * (1-C/t)
        elif turn == 2:
            p = (w2)/t * (1-C/t)
        ## If the move has led to a loss less than 3 times
        ## we'll assign it a 30% chance of working this time
        if p == 0 and t < 3:
            p = 1/3
        if echo == True:
            print('Player %d has seen this before:' % turn)
            print('%d Total, %d P1 wins, %d P2 wins.' % (t, w1, w2))
            print('Probability of a player %d win: %.2f' % (turn,p))
            print('')
    db.close()
    log_function('eval_move',(time.time() - t_start))
    return p

def get_possible_boards(moves,current_board):
    """return a list of possible board configurations in utf-8
    based on available moves and the current board configuration"""
    t_start = time.time()
    boards = []
    for m in moves:
        new_board = move(m[0],m[1],m[2],m[3],current_board)
        new_board = new_board.encode('utf-8')
        boards.append(new_board)
    log_function('get_possible_boards',(time.time() - t_start))
    return boards

def get_board_data(boards):
    """return a dictionary of possible board configurations (keys)
    and their associated data"""
    t_start = time.time()
    board_data = dict()
    #db = dbm.open(datafile,'r')
    for b in boards:
        if b in db.keys():
            board_data[b] = db[b]
        else:
            board_data[b] = '0,0,0'.encode('utf-8')
    #db.close()
    log_function('get_board_data',(time.time() - t_start))
    return board_data   
    
def pick_best_move(board,board_history,moves,echo=False):
    t_start = time.time()
    best_move = [] ## pick the first move by default
    # create lookup table with keys as probabilities of winning
    # values are possible moves
    p = dict() 
    # get_board_data(get_possible_boards(moves,board))
    
    for m in range(len(moves)):
        s = (eval_move(moves[m],board,board_history,\
                       datafile,echo=False))
        if s not in p:
            p[s] = [moves[m]]
        else:
            p[s] = p[s] + [moves[m]]
    best_p = max(p.keys())
    
    if len(p[best_p]) == 1:
        # if one move is distinctly better than others, play it
        best_move = p[best_p][0]
    else:
        # otherwise pick a random move
        best_move = random.choice(p[best_p])
    if echo == True:
        for key in p:
            print('Success Chance of %.2f: ' % key,end='')
            print(p[key])
        print('Picked move with %.2f chance of success.' % best_p)

    log_function('pick_best_move',(time.time() - t_start))
    return best_move

def play_game(p1='c',p2='c',graphics=False):
    """
    Play a game of checkers.
    p1 and p2 can be 'h' for human or 'c' for computer
    graphics can be True or False
    """
    game_start = time.time()
    # turn on graphics if there is human in the loop
    if p1 == 'h' or p2 == 'h':
        graphics = True
        
    board = new_game()
    if graphics == True:
        win = GraphWin("Checkers", board_size, board_size+square_size, autoflush=False)
        draw_board(board,win)
    board_history = [board]
    move_history = []
    while True:
        # check if the game has ended
        legal_moves = get_legal_moves(board,echo=False)
        turn = get_turn(board)
        if not legal_moves:
            end_game(datafile,board_history,get_turn(next_turn(board)))
            break
        if not get_legal_moves(next_turn(board),echo=False):
            end_game(datafile,board_history,turn)
            break
        
        # next player makes a move
        if (turn == 1 and p1 == 'h') or (turn == 2 and p2 == 'h'):
            r1,c1,r2,c2 = get_graphics_move(win)
            # check if human pressed 'reset' or 'quit'
            if r2 == 9 and c2 == 8:
                break
            if r2 == 9 and c2 == 1:
                board = new_game()
                draw_board(board,win)
                continue
        else:
            r1,c1,r2,c2 = pick_best_move(board,board_history,legal_moves,echo=False)

        if [r1,c1,r2,c2] in legal_moves:
            board = move(r1,c1,r2,c2,board)
            board_history.append(board)
            move_history.append([r1,c1,r2,c2])
        else:
            is_legal_move(r1,c1,r2,c2,board)
            
        if graphics == True:
            draw_board(board,win)
            if time_step != 0: update()
            time.sleep(time_step)


    if graphics == True: win.close()
    game_end = time.time()
    print('Total Game Time: %.2f seconds' % (game_end - game_start))
   
### MAIN
num_games = 1
for i in range(num_games):
    print('Game %d of %d...' % ((i+1),(num_games)))
    play_game()
    
report_game_metrics()

