import pandas as pd
from glob import glob
import datetime as dt
import numpy as np
import re
import os
from configparser import ConfigParser
from progressbar import ProgressBar


def populate_file_type(file_name):
    if 'FORMLETTER' in file_name.upper():
        return 'Form Letter'
    elif 'ACK' in file_name.upper():
        return 'ACK'
    else:
        return 'Proof'


def get_invoice(file_name):
    if re.search('(?<!\d)([4-9])\d{7,7}(?!\d)|(?<!\d)([0-1])\d{8,8}(?!\d)', file_name) is None:
        invoice = ''
    else:
        invoice = re.search('(?<!\d)([4-9])\d{7,7}(?!\d)|(?<!\d)([0-1])\d{8,8}(?!\d)',file_name).group()
    return invoice


def get_date(file_name):
    if re.search('(?<=[\\\])([0-9]){2,}[_][0-9]{2,}[_][0-9]{2,}(?=[\\\])', file_name) is None:
        date = re.search('(?<=["/"])([0-9]){2,}[_][0-9]{2,}[_][0-9]{2,}(?=[\\\])', file_name).group()
    else:
        date = re.search('(?<=[\\\])([0-9]){2,}[_][0-9]{2,}[_][0-9]{2,}(?=[\\\])', file_name).group()
        date = dt.datetime.strptime(date, '%m_%d_%y')
    return date


def output_combine(process):
    config_path = 'config.ini'
    config = ConfigParser()
    config.read(config_path)

    Month = config['Parameters']['Month']
    Year = config['Parameters']['Year']
    Month_Name = dt.datetime.strptime(str(Month), '%m').strftime('%B')

    folders = config[process]['OutputFilePath'].split(',')
    bot_type = config[process]['BotType']
    output = config[process]['OutputFileOutputPath']\
        .replace('MMMM', Month_Name).replace('MM', str(Month)).replace('YYYY', str(Year))
    file_name = config[process]['OutputFileNamingConvention']\
        .replace('MMMM', Month_Name).replace('MM', str(Month)).replace('YYYY', str(Year))
    output = output + file_name
    all_files = []

    if os.path.exists(output):
        print(f'Reading existing output file for {process}')
        outputs = pd.read_excel(output, engine='openpyxl')
        return outputs
    else:
        for folder in folders:
            index = folders.index(folder)
            curr_process = config[process]['SHSBotName'].strip().split(",")[index]
            print(f'Combining outputs for {curr_process}')
            folder = folder.replace('MM', Month).replace('YYYY', Year)
            file_criteria = folder + '*/*/*'
            files = [[get_invoice(file), get_date(file), os.path.split(file)[1], populate_file_type(file), curr_process]
                     for file in glob(file_criteria)]
            process_df = pd.DataFrame(files, columns=['Invoice', 'File Date', 'File Name', 'File Type', 'Process'])
            all_files.append(process_df)

        df = pd.concat(all_files)

        df_pivot = df.copy()
        df_pivot.drop(columns=['File Name'], inplace=True)
        file_types = df_pivot['File Type'].unique()

        df_pivot['Count'] = 1
        df_pivot = df_pivot.pivot_table(index=['Invoice', 'File Date', 'Process'], columns=['File Type'],
                                        aggfunc=np.count_nonzero).reset_index()

        if 'ACK' in file_types:
            df_pivot.columns = ['Invoice', 'File Date', 'Process', 'ACK', 'Form Letter', 'Records']
        else:
            df_pivot['ACK'] = 0
            df_pivot.columns = ['Invoice', 'File Date', 'Process', 'ACK', 'Form Letter', 'Records']
        df_pivot.to_excel(output, index=None)
        return df_pivot

output_combine('Medical Records')