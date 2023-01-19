from configparser import ConfigParser
import pandas as pd


def merge(input, output, shs):
    df = pd.merge(input, output, how='left', left_on=[''])