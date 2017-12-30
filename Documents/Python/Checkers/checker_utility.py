#checker_utility.py
import dbm
import sys
import random
import checker_graphics

def convert_database(old_database_file, new_database_file):
    old_data = dbm.open(old_database_file, 'r')
    new_data = dbm.open(new_database_file, 'c')
    for key in old_data.keys():
        b = key.decode('utf-8')
        b_int_str = convert_old_board(b)
        b_int_comp = convert_board_to_int(b_int_str)
        if b_int_str == convert_int_to_board(b_int_comp, 33):
            new_data[str(b_int_comp).encode('utf-8')] = old_data[b]
        else:
            print(b)
            print(b_int_str)
            print(b_int_comp)
            print(convert_int_to_board(b_int_comp,33))
            print("FATAL ERROR OMG!")
            break
    old_data.close()
    new_data.close()

def convert_old_board(board,echo=False):
    if echo: 
        print('Original String:')
        board_size(board)
    t = ({ord('0'): '0',\
          ord('b'): '1',\
          ord('r'): '2',\
          ord('B'): '3',\
          ord('R'): '4'})
    board = board.translate(t)
    return board

def make_random_board(board_chars, board_length):
    """Generate a random board based on a character set
    and length of the board.
    Adds condition that there may not be more than 12
    pieces for any player at any time.
    attributes: board chars, board_length"""
    random_board = ''
    p1_chars = ['1','3']
    p2_chars = ['2','4']
    max_pieces = 12
    p1_pieces = 0
    p2_pieces = 0
    while len(random_board) < board_length:
        random_char = random.choice(board_chars)
        if random_char in p1_chars:
            if p1_pieces == max_pieces:
                continue
            p1_pieces += 1
        if random_char in p2_chars:
            if p2_pieces == max_pieces:
                continue
            p2_pieces += 1
        random_board = random_board + random_char
    return random_board

def compress_board(board):
    """
    Compress a board to a shorter integer using 0 thru 7
    Starts with a board using integers 0 thru 4
    Integers repeated three times are replaced
    With a 5 followed by the integer, e.g. 111 = 51
    Integers repeated four times are replaced
    with a 6 followed by the integer, e.g. 1111 = 61
    5 times is 7, e.g. 11111 = 71
    """
    compressed_str = ''
    # FORMAT: { Number of Repeats: Multiplier }
    trans_table = { 3: '5', 4: '6', 5: '7' }
    index = 0
    board_string_length = len(board)
    while index < board_string_length:
        # the character we are adding
        char = board[index]
        num_repeats = 0
        for i in range(index, min(index+4, board_string_length)):
            if board[i] == char:
                num_repeats += 1
            else:
                break
        if num_repeats in trans_table.keys():
            char = char + trans_table[num_repeats]
        compressed_str = compressed_str + char
        index = index + num_repeats
    return compressed_str
        

def test_conversion(board_length,echo=False):
    """
    Tests convert_board_to_int and
    convert_int_to board to ensure that what goes
    in to the integer representation of the board
    comes out the same way.
    """
    # Start by generating a random board
    board_chars = ['0','1','2','3','4']
    test_board = make_random_board(board_chars,board_length)
    test_board_to_int = convert_board_to_int(test_board)
    test_int_to_board = convert_int_to_board(test_board_to_int, board_length)
    if echo:   
        print('Randomly Generated Board: %s' % test_board)
        print('Converted to Integer:     %d' % test_board_to_int)
        print('Converted back to board:  %s' % test_int_to_board)
    if test_board != test_int_to_board:
        if echo:
            print('ERROR! CONVERSION FAILED')
        return False
    return True


def convert_board_to_int(board, echo=False):
    """
    Convert a board from a string to a shorter integer
    number which is slightly smaller for storage purposes.
    CONVENTION:
    0 = empty
    1 = player 1
    2 = player 2
    3 = player 1 king
    4 = player 2 king
    """
    if echo: 
        print('Translated to Integer String:')
        board_size(board)
    integer_sum = 0
    while len(board) > 0:
        # pick the last number in the board string
        last_character = int(board[-1])
        # shift the current integer sum left 3 places
        integer_sum = integer_sum << 3
        # add the last character to the integer sum
        integer_sum += last_character
        # remove the last character in the board string
        board = board[:-1]
        ### EXAMPLE: ###
        ### Board String = '123', integer sum = 0
        ### shift integer sum left 3 places (nothing happens)
        ### add 3 to integer sum
        ### integer sum = 3 or 011 in binary
        ### Board string becomes '12'
        ### shift integer sum left 3 place and add 2:
        ### integer sum is now 011 010
        ### Board string becomes '1'
        ### shift integer sum left 3 places and add 1:
        ### integer sum is now 011 010 001
        ### at the end of the loop, integer sum is now 209 in binary

    if echo:
        print('Translated to Smaller Int:')          
        board_size(integer_sum)
    return integer_sum

def convert_int_to_board(board_int, board_len):
    """
    Converts an integer to a board string
    """
    board_string = ''
    for i in range(board_len):
        board_string = board_string + str(board_int & 7 )
        board_int = board_int >> 3

        ### EXAMPLE:
        ### Start with board int 209
        ### Perform bitwise and with 209 and 7
        ### Since 7 is the largest number we can have in
        ### our board string(0-7)
        ### 209 & 7 in binary:
        ### 011 010 001
        ### 000 000 111
        ### => Add '1' to board string
        ### shift right by 3, board_int becomes:
        ### 011 010 &
        ### 000 111
        ### => Add '2' to board string
        ### shift right by 3, board int becomes:
        ### 011 &
        ### 111
        ### => Add '3' to board_string
    return board_string

def board_size(board):
    size = sys.getsizeof(board)
    print('Board Rep: %s Size: %d\n' % (board, size))

def find_reverse_boards():
    #check to see how many inverse pairs we have in the board file
    count = 0
    t = ({ord('r'): 'b',\
          ord('b'): 'r',\
          ord('R'): 'B',\
          ord('B'): 'R'})

    db = dbm.open('checkers_data','r')
    for key in db.keys():
        b = key.decode('utf-8')
        b = b[1:] # remove the turn character
        if b == b[::-1].translate(t):
            count += 1
            
    db.close()
    print('found %d reverse boards.' % count)

def test_multiple_conversions(max_len, num_tests):
    """
    Tests the board conversion algorithm forwards
    and backwards
    max_len: maximum board string length
    num_tests: number of tests to execute for each length
    """
    for str_length in range(max_len):
        print('Testing board length %d...' % str_length, end='')
        for test in range(num_tests):
            if not test_conversion(str_length):
                print('FAILURE FOR BOARD LENGTH %d !!!' % len)
                return 0
        print('... %d tests passed successfully.' % num_tests)

def examine_board():
    while True:
        command = input('Enter board integer: ')
        if command == 'quit':
            break
        board_config = convert_int_to_board(int(command),33)
        window = checker_graphics.initialize_graphics_window()
        checker_graphics.draw_board(board_config, window)
    window.close()

# test_chars = ['0','1','2','3','4']
# random_test = make_random_board(test_chars, 32)
# random_test = '11111111111100000000222222222222'
# print('Random Test:\t%s' % random_test)
# random_compressed = compress_board(random_test)
# print('Compressed:\t%s' % random_compressed)
# random_8bit = convert_board_to_int(random_compressed)
# print('8 Bit Conv.:\t%d' % random_8bit)
# print('sys.maxsize:\t%d' % sys.maxsize)
test_conversion(32,echo=True)
