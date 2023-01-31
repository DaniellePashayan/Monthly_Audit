import os
from inputs import input_combine
from outputs import output_combine
from sutherland import sutherland_combine
from function import merge_format, predict
import pandas as pd


def connection_status():
    try:
        os.scandir('M:/')
        return True
    except FileNotFoundError:
        return False

"""
1. Inputs
2. Outputs
3. Sutherland File Parse
4. Merge
5. Populate 
"""


def run(process):
    if connection_status():
        inputs = input_combine(process)
        outputs = output_combine(process)
        shs = sutherland_combine(process)
        formatted = merge_format(inputs, outputs, shs, process)
        final = predict(formatted, process)
        print('done')

    else:
        print('Not connected to the MDrive')


if __name__ == '__main__':
    run('Medical Records')