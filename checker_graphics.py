#checker_graphics.py
"""Graphics module for checkers game"""

from graphics import Point, Rectangle, Circle, Text, GraphWin
from checker_classes import *

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
TIME_STEP = 0.25 # time step for animating automated games

def get_rc(mouse_x, mouse_y):
    """Return the position that was clicked on."""
    col = mouse_x // SQUARE_SIZE + 1
    row = mouse_y // SQUARE_SIZE + 1
    return Position(int(row), int(col))

def highlight_selection(position, graph_win):
    """Given a row, column, and the graphics window,
    highlights the selected square."""
    row, col = position.row, position.col
    selection = Rectangle(Point((col-1)*SQUARE_SIZE, (row-1)*SQUARE_SIZE), \
        Point(col*SQUARE_SIZE, row*SQUARE_SIZE))
    selection.setOutline(HIGHLIGHT_COLOR)
    selection.setWidth(5)
    selection.draw(graph_win)

def get_graphics_move(graph_win):
    """Returns the row and column from
    two consecutive clicks from the user"""
    first_click = graph_win.getMouse()
    start_position = get_rc(first_click.getX(), first_click.getY())
    highlight_selection(start_position, graph_win)

    second_click = graph_win.getMouse()
    end_position = get_rc(second_click.getX(), second_click.getY())
    highlight_selection(end_position, graph_win)
    graphics_move = Move(start_position, end_position)
    return graphics_move

# needs update to remove player and board arguments.
# row and column should be sufficient
def draw_piece(piece, graph_win):
    """Draws a piece at a given row and column"""
    r_px = SQUARE_SIZE * (1/2 + piece.position.row-1)
    c_px = SQUARE_SIZE * (1/2 + piece.position.col-1)
    # if piece.player.number == 1:
    #     piece_color = PLAYER_1_COLOR
    # elif piece.player.number == 2:
    #     piece_color = PLAYER_2_COLOR
    p_graphic = Circle(Point(c_px, r_px), PIECE_SIZE)
    p_graphic.setFill(piece.player.color)
    if piece.is_king:
        p_graphic.setOutline(KING_COLOR)
        p_graphic.setWidth(5)
    p_graphic.draw(graph_win)

def initialize_graphics_window():
    """Opens a new graphics window"""
    window = GraphWin("Checkers", BOARD_SIZE, \
        BOARD_SIZE+SQUARE_SIZE, autoflush=False)
    return window

def draw_background(graph_win):
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
            rect.draw(graph_win)

def draw_status(current_board, graph_win):
    bottom = Rectangle(Point(0, 8*SQUARE_SIZE), \
        Point(9*SQUARE_SIZE, 9*SQUARE_SIZE))
    bottom.setFill("Green")
    bottom.draw(graph_win)

    ## Make an exit button on the lower right
    exit_button = Text(Point(7.5*SQUARE_SIZE, 8.5*SQUARE_SIZE), "EXIT")
    exit_button.setTextColor("Blue")
    exit_button.setStyle("bold")
    exit_button.draw(graph_win)

    ## Make a reset button on the lower left
    reset_button = Text(Point(0.5*SQUARE_SIZE, 8.5*SQUARE_SIZE), "RESET")
    reset_button.setTextColor("Blue")
    reset_button.setStyle("bold")
    reset_button.draw(graph_win)

    legal_moves = current_board.get_legal_moves()
    num_moves = len(legal_moves)
    turn = current_board.players[current_board.turn].name
    num_pieces_p1 = current_board.players[1].num_pieces
    name_1 = current_board.players[1].name
    num_pieces_p2 = current_board.players[2].num_pieces
    name_2 = current_board.players[2].name
    status_str = "%s's Turn. \n %d possible moves.\n\
        %s: %d \t %s: %d" \
        % (turn, num_moves, name_1, num_pieces_p1, name_2, num_pieces_p2)
    status = Text(Point(0.5*BOARD_SIZE, 8.5*SQUARE_SIZE), status_str)
    status.setTextColor("Blue")
    status.setStyle("bold")
    status.draw(graph_win)

def draw_board(current_board, graph_win):
    """Draws the boad and the pieces on it"""
    draw_background(graph_win)
    for key in current_board.pieces.keys():
        draw_piece(current_board.pieces[key], graph_win)
    draw_status(current_board, graph_win)

if __name__ == '__main__':
    win = initialize_graphics_window()
    board = Board()
    draw_board(board, win)
    draw_status(board, win)
    move = get_graphics_move(win)
    print(move)
    win.getMouse()
    win.close
