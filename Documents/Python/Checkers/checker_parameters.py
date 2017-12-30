#checker_parameters.py
"""Parameters"""

# Some Globals
p1 = '1' # Player 1 symbol
p1_name = "Black"
p2 = '2' # Player 2 symbol
p2_name = "Red"
players = {1:[p1,p1_name],2:[p2,p2_name]}
b_sq = '0' # Empty black squares
w_sq = '-' # REMOVE
datafile = 'new_checkers_data'
BOARD_STRING_LENGTH = 33

# Graphics Options

"""Options for graphics module"""
light_square_color = "White"
dark_square_color = "Gray"
king_color = "Orange"
highlight_color = "Orange"
p1_color = "Black"
p2_color = "Red"
board_size = 500
square_size = board_size / 8
piece_size = board_size / 20
time_step = 0.25

# Metrics
function_calls = dict()
function_time_avg = dict()

def log_function(name, time):
    #global function_calls
    function_calls[name] = 1 + function_calls.get(name, 0)
    if name in function_time_avg.keys():
        t_avg = function_time_avg[name]
        t_avg = (t_avg*(function_calls[name]-1) + time) / function_calls[name]
    else: t_avg = time
    function_time_avg[name] = t_avg
    
def report_game_metrics():
    print('Game Metrics:')
    print('Function:\t\t\t Times Called\t Avg. Time(ms) \tTotal Time(s)')
    print('---------\t\t\t ------------\t --------------\t-------------')
    for k in function_calls:
        print("{:28s} \t {:7d} \t{:10.4f} \t\t{:6.2f}".format(\
                k, function_calls[k], function_time_avg[k]*1000, \
              (function_calls[k]*function_time_avg[k])))
        