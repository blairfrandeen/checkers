"""
checker_classes.py

Contains all game mechanics for checkers.
"""
import math
import time
import pickle
import dbm
from itertools import count
class Game:
    """Represents a game of checkers."""

    # Players
    #  - Human, AI
    # Move History
    # - Board history can be derived from this
    # - Winner can be derived from move history
    #   but should also be explicit
    # Other Metrics
    # - Date & Time Played
    # - AI decision rationale

    ### SHIFT OVER FROM BOARD CLASS:
    # Get Legal Moves
    # All turn control
    # Execute Move
    # Is Legal Move / Is Valid Move?

    def __init__(self, winner=None, move_history=None, \
        board_history=None, player_1=None, player_2=None):
        self.winner = winner
        self.board_history = {1:[], 2:[]} if not board_history else board_history
        self.move_history = [] if not move_history else move_history
        self.player_1 = player_1
        self.player_2 = player_2
        self.players = {1: player_1, 2: player_2}

    def __str__(self):
        print('A game of checkers between %s (%s) and %s (%s)' %\
            (self.player_1.name, self.player_1.control,\
            self.player_2.name, self.player_2.control))
        if self.move_history:
            print('Move History: ')
            for move in self.move_history:
                print(move)
        return

    def end(self, winner=None):
        """Declare the end of the game."""
        total_turns = len(self.move_history)
        if not winner:
            print('Game has ended in a draw after %d turns.' %\
                total_turns)
        else:
            self.winner = winner
            print('Game over. %s has won in %d turns!' %\
                (self.players[winner].name, total_turns))

    def log(self, log_file):
        """
        Log the result of the game for later analysis.
        log file format is as follows:
        Keys are based on the GMT time at which the game was logged.
        Values are move_history.
        """
        game_id = time.strftime('%c', time.gmtime())
        print('Logging game ID %s...' % game_id)
        game_id = pickle.dumps(game_id)
        move_history = pickle.dumps(self.move_history)
        game_data = dbm.open(log_file, 'c')
        game_data[game_id] = move_history
        game_data.close()

class Board:
    """
    Represents the board and all the pieces on it

    attributes: int_rep and move
    """
    ### STRING CONVENTION
    EMPTY_SPACE = '0'
    # P1_PIECE = '1'
    # P2_PIECE = '2'
    # P1_KING = '3'
    # P2_KING = '4'

    def __init__(self, int_rep=None, move=None, \
        players=None):
        self.players = players
        if not players:
            self.players = {1: Player(1), \
                        2: Player(2)}
        self.pieces = dict()
        self.turn = 1
        self.draw_counter = 0
        self.opponent = 2

        if int_rep:
            self.convert_from_int(int_rep)
            if move:
                self.execute_move(move)
        else:
            self.setup_new_game()

    def __str__(self):
        """
        Converts a board configuration to a data
        string for storage.
        CONVENTION:
        0 = empty
        1 = player 1
        2 = player 2
        3 = player 1 king
        4 = player 2 king
        """
        data_string = ''
        for row in range(1, 9):
            for col in range(1, 9):
                position = Position(row, col)
                if position in self.pieces:
                    piece = self.pieces[position]
                    char = self.piece_to_str(piece)
                elif position.is_valid():
                    char = self.EMPTY_SPACE
                else:
                    char = ''
                data_string = data_string + char
        return data_string

    def next_turn(self):
        """Switch turn from 1 to 2 or 2 to 1."""
        if self.turn == 1:
            self.turn = 2
            self.opponent = 1
        else:
            self.turn = 1
            self.opponent = 2

    def get_next_turn(self):
        return 2 if self.turn == 1 else 1

    def execute_move(self, move):
        """Executes a move by changing the position of a piece."""
        legal_moves = self.get_legal_moves()
        if not move.is_jump() and legal_moves[0].is_jump():
            print("Thou Shalt Jump!")
            return None
        if move.is_valid() and self.is_legal_move(move):
            piece = self.pieces[move.start_position]
            del self.pieces[move.start_position]
            # print('Moving %s' % piece)
            piece.position = move.end_position
            self.draw_counter += 1
            # print('Moved to %s' % piece.position)
            # check to see if we made a king
            if (move.end_position.row == 1 and self.turn == 1)\
                or (move.end_position.row == 8 and self.turn == 2):
                piece.make_king()
            self.pieces[move.end_position] = piece
            # capture a piece if a jump was made
            # if no jump let the next player go
            if move.is_jump():
                self.capture_piece(self.pieces[move.mid_pos()])
            else:
                self.next_turn()

    def get_legal_moves(self, echo=False):
        """Return an array of all possible legal moves."""
        if self.players[self.turn].num_pieces == 0:
            return None
        legal_moves = []
        must_jump = False
        POSSIBLE_MOVE_VECTORS = [\
            Position(1, 1), Position(1, -1),\
            Position(-1, 1), Position (-1, -1)]
        magnitudes = [2, 1]
        for multiplier in magnitudes:
            if multiplier == 1 and must_jump:
                break
            for key in self.pieces:
                piece_to_try = self.pieces[key]
                if piece_to_try.player.number != self.turn:
                    continue
                piece_moves = 0
                for vector in POSSIBLE_MOVE_VECTORS:
                    position_to_try = \
                        piece_to_try.position + multiplier * vector
                    move_to_try = Move(piece_to_try.position, position_to_try)
                    if self.is_legal_move(move_to_try) and move_to_try.is_valid():
                        legal_moves.append(move_to_try)
                        piece_moves += 1
                        if multiplier == 2:
                            must_jump = True
                            if echo: print('%s Must Jump!' % self.players[self.turn].name)
                    else:
                        del move_to_try
        del POSSIBLE_MOVE_VECTORS
        return legal_moves

    def is_legal_move(self, move, echo=False):
        """Determine whether a move is legal."""
        # make sure we are selecting a valid piece
        if move.start_position in self.pieces.keys():
            piece = self.pieces[move.start_position]
        else:
            if echo: print("Please select a piece to move")
            return False

        # check that the end position is open
        if move.end_position in self.pieces.keys():
            if echo: print("Position is not open!!")
            return False
        
        # check if a backwards move is allowed
        if not piece.is_king:
            delta_row = (move.end_position - move.start_position).row
            if (delta_row > 0 and self.turn == 1) \
                or (delta_row < 0 and self.turn == 2):
                if echo: print("Cannot move a non-king backwards!")
                return False
        
        # check that there is a piece to jump
        if move.is_jump():
            if move.mid_pos() in self.pieces.keys():
                if self.turn == self.pieces[move.mid_pos()].player.number:
                    if echo: print("Jumping your own piece: Bad idea bro.")
                    return False
            else:
                if echo: print("Cannot jump an empty square!")
                return False

        # check that the right player is moving
        if piece.player.number != self.turn:
            if echo: print("It's not your turn")
            return False
        return True

    def capture_piece(self, piece, echo=False):
        """Captures a piece and removes it from the board."""
        if echo: print("Capturing piece %s" % piece)
        self.players[piece.player.number].num_pieces -= 1
        self.draw_counter = 0
        del self.pieces[piece.position]

    def setup_new_game(self):
        """Set up the board for a new game."""
        self.players[1].num_pieces = 0
        self.players[2].num_pieces = 0
        for row in range(1, 9):
            for col in range(1, 9):
                position = Position(row, col)
                if position.is_valid():
                    if row in range(1, 4): # player 2
                        player = self.players[2]
                    elif row in range(6, 9): # player 1
                        player = self.players[1]
                    else:
                        continue
                    new_piece = Piece(player, position)
                    #self.players[player].num_pieces += 1
                    self.players[player.number].num_pieces += 1
                    self.pieces[position] = new_piece

    def piece_from_char(self, char):
        """
        Look at a character from a board string 
        to determine the player number and king status for a piece.
        """
        player_num = int(char)
        if player_num == 3 or player_num == 4:
            is_king = True
            player_num -= 2
        else:
            is_king = False

        player = self.players[player_num]

        return player, is_king
    
    def print_legal_moves(self):
        """Print a list of legal moves to the console."""
        legal_moves = self.get_legal_moves()
        print('Legal Moves Available:')
        for move in legal_moves:
            print(move)
        
    def piece_to_str(self, piece):
        """Generate a string character based on a pieces attributes."""
        player_num = piece.player.number
        if piece.is_king:
            player_num += 2
        return str(player_num)

    def convert_from_int(self, int_rep):
        """Convert an integer to an arragnemnt of pieces on the board."""
        index = 0
        for row in range(1, 9):
            for col in range(1, 9):
                position = Position(row, col)
                if position.is_valid():
                    index += 1
                    char = str(int_rep & 7)
                    int_rep = int_rep >> 3
                    if char != self.EMPTY_SPACE:
                        player, is_king = self.piece_from_char(char)
                        piece = Piece(player, position, is_king)
                        self.pieces[position] = piece
                        self.players[int(char)].num_pieces += 1

    def int_rep(self):
        """Create an integer representation of the board setup."""
        integer_sum = 0
        data_string = self.__str__()
        data_string_length = len(data_string)
        while data_string_length > 0:
            # pick the last number in the board string
            last_character = int(data_string[-1])
            # shift the current integer sum left 3 places
            integer_sum = integer_sum << 3
            # add the last character to the integer sum
            integer_sum += last_character
            # remove the last character in the board string
            data_string = data_string[:-1]
            data_string_length -= 1
        return integer_sum

class Player:
    """
    Represents one of two players in the game
    attributes: number, name, color, and who controls it.
    """
    def __init__(self, number=1, name='New Player', \
                color='Green', control='Human', num_pieces=0):
        self.number = number
        self.name = name
        self.color = color
        self.control = control
        self.num_pieces = num_pieces

    def __str__(self):
        return 'Player %d: %s\nPiece Color: %s. Controlled By: %s.' % \
        (self.number, self.name, self.color, self.control)

    def __eq__(self, num):
        return self.number == num

class Position:
    """Represents a position on the board
    attributes: row, col
    """
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def __str__(self):
        return '%d, %d' % (self.row, self.col)

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return (self.row, self.col) == (other.row, other.col)

    def __add__(self, other):
        return Position((self.row + other.row), (self.col + other.col))

    def __sub__(self, other):
        return Position((self.row - other.row), (self.col - other.col))

    def __mul__(self, multiplier):
        return Position((self.row * multiplier), (self.col*multiplier))
        
    def __rmul__(self, multiplier):
        return self.__mul__(multiplier)

    def __truediv__(self, divisor):
        return Position((int(self.row / divisor)), (int(self.col / divisor)))

    def mid_position(self, other):
        return ((self + other) / 2)

    def is_valid(self):
        if (1 <= self.row <= 8) and (1 <= self.col <= 8):
            return (self.row % 2 != 0 and self.col % 2 == 0) or\
                    (self.row % 2 == 0 and self.col % 2 != 0)
        else:
            return False

class Piece():
    """
    Represents a piece on the board
    attributes: player, is_king, position
    """
    def __init__(self, player=Player(), position=Position(), is_king=False):
        self.player = player
        self.position = position
        self.is_king = is_king

    def __str__(self):
        if self.is_king:
            description = 'king'
        else:
            description = 'piece'
        return '%s %s at %s' % (self.player.name, description, self.position)

    def __bool__(self):
        return hasattr(self, 'player')

    def make_king(self):
        """Makes a piece into a king"""
        self.is_king = True

class Move:
    """Represents a possible checkers move
    attributes: start_position, end_position"""
    def __init__(self, start_position, end_position):
        self.start_position = start_position
        self.end_position = end_position

    def __str__(self):
        return '[ %s --> %s ]' % \
            (self.start_position, self.end_position)

    def is_jump(self):
        """Determine if a move involves a jump."""
        if abs(self.start_position.row-self.end_position.row) > 1:
            return True
        else:
            return False

    def mid_pos(self):
        """Return the Position between the starting and ending positions."""
        if not self.is_jump():
            return None
        return (self.start_position + self.end_position) / 2

    def is_valid(self, echo=False):
        """Determine if a proposed move is valid."""
        delta = self.end_position - self.start_position
        if abs(delta.row) != abs(delta.col):
            if echo: print("Invalid Move: Must move on a diagonal!")
            return False
        if abs(delta.row) > 2:
            if echo: print("Invalid Move: may only go 1 or 2 spaces!")
            return False
        if not self.start_position.is_valid() or not self.end_position.is_valid():
            if echo: print("Invalid Move: Stay on the board!")
            return False
        del delta
        return True

if __name__ == '__main__':
    import copy
    b = Board()
    print(b)
    b.print_legal_moves()
    test = copy.copy(b)
    test.next_turn()
    test.print_legal_moves()
    b.print_legal_moves()
    # pp1 = Position(3,2)
    # pp2 = Position(4,3)
    # m = Move(pp1,pp2)
    # b.execute_move(m)
    # m2 = Move(Position(6,1),Position(5,2))
    # rep = b.int_rep()
    # print(b)
    # print(rep)
    # c = Board(rep,m2)
    # print(c)

