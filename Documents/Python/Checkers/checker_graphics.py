#checker_graphics.py
"""Graphics module for checkers game"""

from graphics import Point, Rectangle, Circle, Text, GraphWin
from checker_mechanics import is_king, get_piece, get_legal_moves, \
    get_turn, get_player_num
from checker_parameters import players, p1, p2

## Parameters
LIGHT_SQUARE_COLOR = "White"
DARK_SQUARE_COLOR = "Gray"
KING_COLOR = "Orange"
HIGHLIGHT_COLOR = "Orange"
PLAYER_1_COLOR = "Black"
PLAYER_2_COLOR = "Red"
BOARD_SIZE = 500
SQUARE_SIZE = BOARD_SIZE / 8
PIECE_SIZE = BOARD_SIZE / 20

def get_rc(mouse_x, mouse_y):
    """Given X and Y inputs from win.getMouse,
    return the corresponding row and column on the board"""
    col = mouse_x // SQUARE_SIZE + 1
    row = mouse_y // SQUARE_SIZE + 1
    return int(row), int(col)

def highlight_selection(row, col, window):
    """Given a row, column, and the graphics window,
    highlights the selected square."""
    selection = Rectangle(Point((col-1)*SQUARE_SIZE, (row-1)*SQUARE_SIZE), \
        Point(col*SQUARE_SIZE, row*SQUARE_SIZE))
    selection.setOutline(HIGHLIGHT_COLOR)
    selection.setWidth(5)
    selection.draw(window)

def get_graphics_move(window):
    """Returns the row and column from
    two consecutive clicks from the user"""
    first_click = window.getMouse()
    row_1, col_1 = get_rc(first_click.getX(), first_click.getY())
    highlight_selection(row_1, col_1, window)

    second_click = window.getMouse()
    row_2, col_2 = get_rc(second_click.getX(), second_click.getY())
    highlight_selection(row_2, col_2, window)
    return row_1, col_1, row_2, col_2

# needs update to remove player and board arguments.
# row and column should be sufficient
def draw_piece(row, col, player, board, window):
    """Draws a piece at a given row and column"""
    r_px = SQUARE_SIZE * (1/2 + row-1)
    c_px = SQUARE_SIZE * (1/2 + col-1)
    if player == 1:
        piece_color = PLAYER_1_COLOR
    elif player == 2:
        piece_color = PLAYER_2_COLOR
    piece = Circle(Point(c_px, r_px), PIECE_SIZE)
    piece.setFill(piece_color)
    if is_king(row, col, board):
        piece.setOutline(KING_COLOR)
        piece.setWidth(5)
    piece.draw(window)

def initialize_graphics_window():
    """Opens a new graphics window"""
    window = GraphWin("Checkers", BOARD_SIZE, \
        BOARD_SIZE+SQUARE_SIZE, autoflush=False)
    return window

def draw_background(window):
    """Draws the background"""
    for row in range(1, 9):
        for col in range(1, 9):
            rect = Rectangle(Point((col-1)*SQUARE_SIZE, (row-1)*SQUARE_SIZE),
                             Point(col*SQUARE_SIZE, row*SQUARE_SIZE))
            if (row % 2 == 0 and col % 2 == 0) \
                or (row % 2 != 0 and col % 2 != 0):
                rect.setFill(LIGHT_SQUARE_COLOR)
            else:
                rect.setFill(DARK_SQUARE_COLOR)
            rect.draw(window)

def draw_board(board, window):
    """Draws the boad and the pieces on it"""
    draw_background(window)
    for row in range(1, 9):
        for col in range(1, 9):
            player_num = get_player_num(row, col, board)
            if player_num:
                draw_piece(row, col, player_num, board, window)

    bottom = Rectangle(Point(0, 8*SQUARE_SIZE), \
        Point(9*SQUARE_SIZE, 9*SQUARE_SIZE))
    bottom.setFill("Green")
    bottom.draw(window)

    exit_button = Text(Point(7.5*SQUARE_SIZE, 8.5*SQUARE_SIZE), "EXIT")
    exit_button.setTextColor("Blue")
    exit_button.setStyle("bold")
    exit_button.draw(window)

    reset_button = Text(Point(0.5*SQUARE_SIZE, 8.5*SQUARE_SIZE), "RESET")
    reset_button.setTextColor("Blue")
    reset_button.setStyle("bold")
    reset_button.draw(window)
    num_moves = len(get_legal_moves(board))
    status_str = "%s's Turn. \n %d possible moves." \
        % (players[get_turn(board)][1], num_moves)
    status = Text(Point(0.5*BOARD_SIZE, 8.5*SQUARE_SIZE), status_str)
    status.setTextColor("Blue")
    status.setStyle("bold")
    status.draw(window)
