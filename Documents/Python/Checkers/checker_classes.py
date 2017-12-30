class Board:
    """
    Represents the board and all the pieces on it
    attributes: int_rep and move
    """
    ### STRING CONVENTION
    EMPTY_SPACE = '0'
    P1_PIECE = '1'
    P2_PIECE = '2'
    P1_KING = '3'
    P2_KING = '4'

    def __init__(self, int_rep=None, move=None):
        self.players = [Player(1, 'Black', 'Black', 'Human'), \
                        Player(2, 'Red', 'Red', 'AI')]
        self.pieces = dict()

        if int_rep:
            self.convert_from_int(int_rep)
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

    def setup_new_game(self):
        """Set up the board for a new game."""
        for row in range(1, 9):
            for col in range(1, 9):
                position = Position(row, col)
                if position.is_valid():
                    if row in range(1, 4): # player 2
                        player = self.players[1]
                    elif row in range(6, 9): # player 1
                        player = self.players[0]
                    else:
                        continue
                    new_piece = Piece(player, position)
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
        if player_num == 1:
            player = self.players[0]
        elif player_num == 2:
            player = self.players[1]
        else:
            # print('Error: bad character string.')
            return None
        return player, is_king

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
    def __init__(self, number=1, name='Black', \
                color='Black', control='Human'):
        self.number = number
        self.name = name
        self.color = color
        self.control = control

    def __str__(self):
        return 'Player %d: %s\nPiece Color: %s. Controlled By: %s.' % \
        (self.number, self.name, self.color, self.control)

class Position:
    """Represents a position on the board
    attributes: row, col
    """
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col

    def __str__(self):
        return 'row, %d column, %d' % (self.row, self.col)

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return (self.row, self.col) == (other.row, other.col)

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

    def execute_move(self):
        """Move from one position to another"""
        pass

    def capture(self):
        """Capture the piece"""
        pass

class Move:
    """Represents a possible checkers move
    attributes: start_position, end_position"""
    def __init__(self, p1=Position(), p2=Position()):
        self.start_position = p1
        self.end_position = p2

    def __str__(self):
        return 'Start Position: %s \nEnd Position: %s' % \
            (self.start_position, self.end_position)

    def is_jump_move(self):
        if abs(self.start_position.row-self.end_position.row) > 1:
            return True
        else:
            return False

if __name__ == '__main__':
    pp1 = Position(1,2)
    pp2 = Position(2,3)
    m = Move(pp1,pp2)
    print(m)

