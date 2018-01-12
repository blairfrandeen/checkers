"""
checker_classes.py

Contains all game mechanics for checkers.
"""
import time
import pickle
import dbm
import function_timer as ft

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
        """Return whose turn it will be next."""
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
        move_vectors = [\
            Position(1, 1), Position(1, -1), \
            Position(-1, 1), Position(-1, -1)]
        magnitudes = [2, 1]
        for multiplier in magnitudes:
            if multiplier == 1 and must_jump:
                break
            for key in self.pieces:
                piece_to_try = self.pieces[key]
                if piece_to_try.player.number != self.turn:
                    continue
                piece_moves = 0
                for vector in move_vectors:
                    position_to_try = \
                        piece_to_try.position + multiplier * vector
                    move_to_try = Move(piece_to_try.position, position_to_try)
                    if self.is_legal_move(move_to_try) and move_to_try.is_valid():
                        legal_moves.append(move_to_try)
                        piece_moves += 1
                        if multiplier == 2:
                            must_jump = True
                            if echo:
                                print('%s Must Jump!' % self.players[self.turn].name)
                    else:
                        del move_to_try
        del move_vectors
        return legal_moves

    def is_legal_move(self, move, echo=False):
        """Determine whether a move is legal."""
        # make sure we are selecting a valid piece
        if move.start_position in self.pieces.keys():
            piece = self.pieces[move.start_position]
        else:
            if echo:
                print("Please select a piece to move")
            return False

        # check that the end position is open
        if move.end_position in self.pieces.keys():
            if echo:
                print("Position is not open!!")
            return False

        # check if a backwards move is allowed
        if not piece.is_king:
            delta_row = (move.end_position - move.start_position).row
            if (delta_row > 0 and self.turn == 1) \
                or (delta_row < 0 and self.turn == 2):
                if echo:
                    print("Cannot move a non-king backwards!")
                return False

        # check that there is a piece to jump
        if move.is_jump():
            if move.mid_pos() in self.pieces.keys():
                if self.turn == self.pieces[move.mid_pos()].player.number:
                    if echo:
                        print("Jumping your own piece: Bad idea bro.")
                    return False
            else:
                if echo:
                    print("Cannot jump an empty square!")
                return False

        # check that the right player is moving
        if piece.player.number != self.turn:
            if echo:
                print("It's not your turn")
            return False
        return True

    def capture_piece(self, piece, echo=False):
        """Captures a piece and removes it from the board."""
        if echo:
            print("Capturing piece %s" % piece)
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

class Position:
    """Represents position on the board."""
    def __init__(self, row=0, column=0, player=None, is_king=False):
        self.player = player
        self.is_king = is_king
        if not self.player:
            self.is_king = False
        self.row = row
        self.column = column

    def __str__(self):
        if not self.is_valid():
            return 'Position (%d, %d): INVALID.' % (self.row, self.column)
        if self.player:
            player_str = 'Player %d' % self.player
        else:
            player_str = 'Empty'
        king_str = ' king' if self.is_king else ''
        posstr = 'Position (%d, %d): %s%s.' % (self.row, self.column, player_str, king_str)
        return posstr

    def __hash__(self):
        return hash((self.row, self.column))

    def __eq__(self, other):
        return (self.row == other.row) and (self.column == other.column)

    def __add__(self, other):
        return Position((self.row + other.row), (self.column + other.column))

    def __truediv__(self, divisor):
        return Position((int(self.row / divisor)), (int(self.column / divisor)))

    def __mul__(self, multiplier):
        return Position((self.row * multiplier), (self.column * multiplier))

    def __sub__(self, other):
        return Position((self.row - other.row), (self.column - other.column))

    def __rmul__(self, multiplier):
        return self.__mul__(multiplier)

    def make_king(self):
        """Make a king at a given position."""
        self.is_king = True

    def empty(self):
        """Remove a piece from the position."""
        self.player = None
        self.is_king = False

    def is_valid(self):
        """Return true if position is on the board and on a black square."""
        t_start = time.time()
        if (1 <= self.row <= 8) and (1 <= self.column <= 8):
            return (self.row % 2 != 0 and self.column % 2 == 0) or\
                    (self.row % 2 == 0 and self.column % 2 != 0)
        ft.log_function('position.is_valid', t_start)
        return False

class Move:
    """Represents a possible checkers move
    attributes: start_position, end_position"""
    def __init__(self, start_position, end_position):
        self.start_position = start_position
        self.end_position = end_position
        if self.start_position.row < self.end_position.row:
            self.direction = 2
        elif self.start_position.row > self.end_position.row:
            self.direction = 1

    def __str__(self):
        return '[ %d, %d --> %d, %d ]' % \
            (self.start_position.row, self.start_position.column,\
            self.end_position.row, self.end_position.column)
        
    def int_rep(self):
        positions = [self.start_position.row, self.start_position.column,
                      self.end_position.row, self.end_position.column]
        return int(''.join(str(p) for p in positions))

    def is_jump(self):
        """Determine if a move involves a jump."""
        if abs(self.start_position.row-self.end_position.row) > 1:
            return True
        return False

    def mid_pos(self):
        """Return the Position between the starting and ending positions."""
        if not self.is_jump():
            return None
        return (self.start_position + self.end_position) / 2
    
    def is_valid(self, echo=False):
        """Determine if a proposed move is valid."""
        t_start = time.time()
        delta = self.end_position - self.start_position
        if abs(delta.row) != abs(delta.column):
            if echo:
                print("Invalid Move: Must move on a diagonal!")
            return False
        if abs(delta.row) > 2:
            if echo:
                print("Invalid Move: may only go 1 or 2 spaces!")
            return False
        if not self.start_position.is_valid() or not self.end_position.is_valid():
            if echo:
                print("Invalid Move: Stay on the board!")
            return False
        ft.log_function('move.is_valid', t_start)
        return True

class Configuration:
    """Replace board class."""
    def __init__(self, players):
        self.history = []
        self.turn = 1
        self.num_moves = 0
        self.draw_counter = 0
        self.positions = dict()
        self.pieces_remaining = {1: 12, 2: 12}
        self.kings_remaining = {1: 0, 2: 0}
        self.legal_moves = []
        self.players = players

    def __str__(self):
        config_str = ''
        return config_str

    def new_game(self):
        """Set up pieces in configuration for new game."""
        for row in range(1, 9):
            for col in range(1, 9):
                pos = Position(row, col)
                if pos.is_valid():
                    if row in range(1, 4):
                        pos.player = 2
                    elif row in range(6, 9):
                        pos.player = 1
                    self.positions[pos] = pos
        self.get_legal_moves()

    def end_turn(self):
        """End the current turn."""
        self.turn = 1 if self.turn == 2 else 2
        self.get_legal_moves()

    def next_turn(self):
        """Return what the next turn will be"""
        return 1 if self.turn == 2 else 2

    def is_legal_move(self, move, echo=False):
        """Determine whether a move is legal."""
        t_start = time.time()
        # make sure the end position is valid
        if not move.end_position in self.positions.keys():
            if echo:
                print('Please select a valid destination!')
            return False

        # check that the end position is open
        if self.positions[move.end_position].player:
            if echo:
                print("Position is not open!!")
            return False

        # check if a backwards move is allowed
        if not self.positions[move.start_position].is_king:
            if move.direction != self.turn:
                if echo:
                    print("Cannot move an non-king backwards!")
                return False

        # check that there is a piece to jump
        if move.is_jump():
            if self.positions[move.mid_pos()].player:
                if self.turn == self.positions[move.mid_pos()].player:
                    if echo:
                        print("Jumping your own piece: Bad idea bro.")
                    return False
            else:
                if echo:
                    print("Cannot jump an empty square!")
                return False

        # make sure we are selecting a valid piece
        if not move.start_position in self.positions.keys():
            if echo:
                print('Please select a valid piece to move!')
            return False

        # make sure the right player is moving.
        if self.positions[move.start_position].player != self.turn:
            if echo:
                print('Please wait your turn.')
                return False
        
        ft.log_function('is_legal_move', t_start)
        return True

    def get_legal_moves(self, echo=False):
        """Generate an array of all possible legal moves."""
        t_start = time.time()
        self.legal_moves = []
        must_jump = False
        move_vectors = [\
            Position(1, 1), Position(1, -1), \
            Position(-1, 1), Position(-1, -1)]
        if self.turn == 1:
            move_vectors.reverse()
        magnitudes = [2, 1]
        for multiplier in magnitudes:
            if multiplier == 1 and must_jump:
                break
            for position in self.positions.values():
                if position.player != self.turn:
                    continue
                directions = move_vectors[:2] if not position.is_king \
                    else move_vectors
                for vector in directions:
                    position_to_try = position + multiplier * vector
                    move_to_try = Move(position, position_to_try)
                    if self.is_legal_move(move_to_try) and move_to_try.is_valid():
                        self.legal_moves.append(move_to_try)
                        if multiplier == 2:
                            must_jump = True
                            if echo:
                                print('Player %d Must Jump!' % self.turn)
        ft.log_function('get_legal_moves', t_start)

    def execute_move(self, move):
        """Move a piece from one position to another."""
        if not self.legal_moves:
            self.get_legal_moves()
        # make sure move is a jump move, if one is available
        if not move.is_jump() and self.legal_moves[0].is_jump():
            print("Thou Shalt Jump!")
            return
        # make sure the move is valid
        if self.is_legal_move(move, echo=True) and move.is_valid():
            # execute the move
            self.positions[move.end_position].player = self.positions[move.start_position].player
            self.positions[move.end_position].is_king = self.positions[move.start_position].is_king
            self.positions[move.start_position].empty()

            # did we make a king?
            if not self.positions[move.end_position].is_king:
                if (move.end_position.row == 1 and self.turn == 1) or \
                    (move.end_position.row == 8 and self.turn == 2):
                    self.positions[move.end_position].make_king()
                    self.kings_remaining[self.turn] += 1

            # did a piece get jumped?
            if move.is_jump():
                self.capture_piece(move.mid_pos())
                self.get_legal_moves()
            else:
                self.end_turn()
            # cleanup tasks
            self.history.append(move.int_rep())
            self.num_moves += 1
            self.draw_counter += 1

    def capture_piece(self, position):
        """Capture a piece. Update piece counts. Reset draw counter."""
        if self.positions[position].is_king:
            self.kings_remaining[self.next_turn()] -= 1
        self.positions[position].empty()
        self.draw_counter = 0
        self.pieces_remaining[self.next_turn()] -= 1

if __name__ == '__main__':
    pass
