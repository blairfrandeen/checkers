#checker_graphics.py

# To do:
# - don't re-draw the squares every time
from graphics import *
from checker_parameters import *
from checker_mechanics import *

def get_rc(x,y):
    c = x // square_size + 1
    r = y // square_size + 1
    return int(r), int(c)

def highlight_selection(r,c,win):
    selection = Rectangle(Point((c-1)*square_size,(r-1)*square_size),
                             Point(c*square_size,r*square_size))
    selection.setOutline(king_color)
    selection.setWidth(5)
    selection.draw(win)
    
def get_graphics_move(win):
    p1 = win.getMouse()
    x1, y1 = p1.getX(), p1.getY()
    #print(x1,y1)
    r1, c1 = get_rc(x1,y1)
    #print(r1,c1)
    highlight_selection(r1,c1,win)
    
    p2 = win.getMouse()
    x2, y2 = p2.getX(), p2.getY()
    #print(x2,y2)
    r2, c2 = get_rc(x2,y2)
    highlight_selection(r2,c2,win)
    #print(r2,c2)
    return r1,c1,r2,c2

def draw_piece(r,c,p,board,win):
    r_px = square_size * (1/2 + r-1)
    c_px = square_size * (1/2 + c-1)
    if p == 1:
        color = p1_color
    elif p == 2:
        color = p2_color
    piece = Circle(Point(c_px,r_px),piece_size)
    piece.setFill(color)
    if is_king(r,c,board):
        piece.setOutline(king_color)
        piece.setWidth(5)
    piece.draw(win)

def draw_background(win):
    for r in range(1,9):
        for c in range(1,9):
            rect = Rectangle(Point((c-1)*square_size,(r-1)*square_size),
                             Point(c*square_size,r*square_size))
            if (r % 2 == 0 and c % 2 == 0) or (r % 2 != 0 and c % 2 != 0):
                rect.setFill(light_square_color)
            else:
                rect.setFill(dark_square_color)
            rect.draw(win)
    
def draw_board(board,win):    
    for r in range(1,9):
        for c in range(1,9):
            rect = Rectangle(Point((c-1)*square_size,(r-1)*square_size),
                             Point(c*square_size,r*square_size))
            if (r % 2 == 0 and c % 2 == 0) or (r % 2 != 0 and c % 2 != 0):
                rect.setFill(light_square_color)
            else:
                rect.setFill(dark_square_color)
            rect.draw(win)
            if get_piece(r,c,board).lower() == p1.lower():
                draw_piece(r,c,1,board,win)
            elif get_piece(r,c,board).lower() == p2.lower():
                draw_piece(r,c,2,board,win)
    bottom = Rectangle(Point(0,8*square_size),Point(9*square_size,9*square_size))
    bottom.setFill("Green")
    bottom.draw(win)
    exit = Text(Point(7.5*square_size,8.5*square_size), "EXIT")
    exit.setTextColor("Blue")
    exit.setStyle("bold")
    exit.draw(win)
    reset = Text(Point(0.5*square_size,8.5*square_size), "RESET")
    reset.setTextColor("Blue")
    reset.setStyle("bold")
    reset.draw(win)
    num_moves = len(get_legal_moves(board))
    status_str = "%s's Turn. \n %d possible moves." % (players[get_turn(board)][1], num_moves)
    status = Text(Point(0.5*board_size,8.5*square_size), status_str)
    status.setTextColor("Blue")
    status.setStyle("bold")
    status.draw(win)
