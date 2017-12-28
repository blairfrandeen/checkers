#checker_parameters.py

# Some Globals
p1 = 'b' # Player 1 symbol
p1_name = "Black"
p2 = 'r' # Player 2 symbol
p2_name = "Red"
players = {1:[p1,p1_name],2:[p2,p2_name]}
b_sq = '0' # Empty black squares
w_sq = '-' # Empty white squares
C = 0.5 # Confidence parameter
datafile = 'checkers_data'

# Graphics Options
show_graphics = True
light_square_color = "White"
dark_square_color = "Gray"
king_color = "Orange"
p1_color = "Black"
p2_color = "Red"
board_size = 500
square_size = board_size / 8
piece_size = board_size / 20
time_step = 0

# Metrics
function_calls = dict()
function_time_avg = dict()

def log_function(name,time):
    function_calls[name] = 1 + function_calls.get(name,0)
    if name in function_time_avg.keys():
        t_avg = function_time_avg[name]
        t_avg = (t_avg*(function_calls[name]-1) + time) / function_calls[name]
    else: t_avg = time
    function_time_avg[name] = t_avg
    
def report_game_metrics():
    print('Game Metrics:')
    print('Function:\t\t\t Times Called\t\t Avg. Time(ms) \t\tTotal Time(s)')
    print('---------\t\t\t ------------\t\t --------------\t\t-------------')
    for k in function_calls:
        print('%s \t\t\t %d \t\t %.3f \t\t %.2f' \
              % (k, function_calls[k], function_time_avg[k]*1000, \
              (function_calls[k]*function_time_avg[k])))
        