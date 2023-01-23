import datetime as dt
import os
import re
from configparser import ConfigParser
from glob import glob
import pandas as pd
from progressbar import ProgressBar


def denied_cpt_list(x):
    x = x.tolist()
    x = ', '.join([str(y) for y in x])
    return x


def input_combine(process):

    config_path = 'config.ini'
    config = ConfigParser()
    config.read(config_path)

    Month = config['Parameters']['Month']
    Year = config['Parameters']['Year']
    Month_Name = dt.datetime.strptime(str(Month), '%m').strftime('%B')

    output_path = config[process]['InputFileOutputPath'].replace('MMMM', Month_Name)\
        .replace('MM', str(Month)).replace('YYYY', str(Year))
    file_name = config[process]['ETMOutputNamingConvention'].replace('MMMM', Month_Name)\
        .replace('MM', str(Month)).replace('YYYY', str(Year))

    output_file = output_path + file_name
    if os.path.exists(output_file):
        print(f'Reading existing input file for {process}')
        inputs = pd.read_excel(output_file, engine = 'openpyxl')
        return inputs
    else:
        if config[process]['BotType'] == 'Bundling':
            print(f'Combining inputs for {process}')
            input_paths = config[process]['InputFilePath'].split(',')
            df = []
            for path in input_paths:
                i = input_paths.index(path)
                folder_name = path + '**Inbound_' + str(Month) + '**' + str(Year) + '*' + '.xls'

                for file in glob(folder_name):
                    data = pd.read_excel(file, engine='xlrd', sheet_name='Sheet1')
                    file_date = re.search('([0-9]){8,8}(?=\D)', file).group()
                    file_date = dt.datetime.strptime(file_date, "%m%d%Y")
                    data['File Date'] = file_date
                    df.append(data)

            if len(df) > 0:
                df = pd.concat(df)

            df_denied = df.copy()
            df_denied = df_denied[df_denied['Txn Rej R C List'].str.contains("UNBUNDLED")]
            df_denied['Denied CPT List'] = df_denied.groupby(['INVNUM', 'File Date'])['CPT'].transform(
                lambda x: denied_cpt_list(x))
            df_new = pd.DataFrame(df_denied[['INVNUM', 'File Date', 'PAYER', 'CPT List', 'Denied CPT List']], columns =
            ['INVNUM', 'File Date', 'PAYER', 'CPT List', 'Denied CPT List'])
            df_new = df_new.drop_duplicates()
            df = ''
            data = ''
            df_denied = ''

            coding_tools = pd.read_csv('../References/Coding Tools.csv')
            df_new = df_new.merge(coding_tools, how='left', left_on=['PAYER'], right_on=['PAYER'])

            df_new.to_excel(output_file, index = None)
            return df_new
        if config[process]['BotType'] == 'MedicalRecords':

            input_paths = config[process]['InputFilePath'].split(',')
            processes = config[process]['InputProcesses'].split(',')

            df = []
            for path in input_paths:
                i = input_paths.index(path)
                print(f'Combining inputs for {processes[i]}')
                folder_name = path + '**Inbound_' + str(Month) + '**' + str(Year) + '*' + '.xls'

                for file in glob(folder_name):
                    data = pd.read_excel(file, engine='xlrd', sheet_name='Sheet1')
                    file_date = re.search('([0-9]){8,8}(?=\D)', file).group()
                    file_date = dt.datetime.strptime(file_date, "%m%d%Y")
                    data['File Date'] = file_date
                    data['Process'] = processes[i]
                    data = data[['INVNUM', 'File Date', 'PAYER', 'Process']]
                    df.append(data)
            if len(df) > 0:
                df = pd.concat(df)

            df = df.drop_duplicates()

            df.to_excel(output_file, index = None)
            return df

input_combine('Medical Records')