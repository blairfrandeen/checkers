#function_timer.py
# Report the amount of time a function, subroutine,
# or loop took to run.
# Usage Example:
#
# import time
# import function_timer as ft
#
# def some_fcn(args):
#     t_start = time.time()
#     #
#     # < FUNCITON CODE GOES HERE>
#     #
#     ft.log_function('some_fcn', t_start)
#     return Something
#
# At the end of the program, run report_game_metrics()
    

import time

function_calls = dict()
function_time_avg = dict()

def log_function(name, time_start):
    #global function_calls
    function_time = time.time() - time_start
    function_calls[name] = 1 + function_calls.get(name, 0)
    if name in function_time_avg.keys():
        t_avg = function_time_avg[name]
        t_avg = (t_avg*(function_calls[name]-1) + function_time) / function_calls[name]
    else: t_avg = function_time
    function_time_avg[name] = t_avg
    
def report_game_metrics():
    print('Game Metrics:')
    print('Function:\t\t\t Times Called\t Avg. Time(ms) \tTotal Time(s)')
    print('---------\t\t\t ------------\t --------------\t-------------')
    for k in function_calls:
        print("{:28s} \t {:7d} \t{:10.4f} \t\t{:6.2f}".format(\
                k, function_calls[k], function_time_avg[k]*1000, \
              (function_calls[k]*function_time_avg[k])))
        