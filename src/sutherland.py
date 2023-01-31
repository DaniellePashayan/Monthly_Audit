import pandas as pd
import datetime as dt
from configparser import ConfigParser


def sutherland_combine(process):
    config_path = 'config.ini'
    config = ConfigParser()
    config.read(config_path)

    Month = config['Parameters']['Month']
    Year = config['Parameters']['Year']
    Month_Name = dt.datetime.strptime(str(Month), '%m').strftime('%B')
    SHS_file = config[process]['SHSFullFile'].replace('MMMM', Month_Name).replace('YYYY', Year).replace('MM', Month)
    process_list = config[process]['SHSBotName'].split(',')

    print(f'Formatting Sutherland file for {process}')
    SHS_file = pd.read_excel(SHS_file, engine='openpyxl',
                             usecols=['INVNUM', 'Reason', 'BotName', 'RetrievalStatus', 'RetrievalDescription',
                                      'BOTRequestDate', 'LastModifiedDate'])
    SHS_file['BOTRequestDate'] = pd.to_datetime(SHS_file['BOTRequestDate'], format='%m/%d/%Y %I:%M:%S %p')
    SHS_file = SHS_file[SHS_file['BotName'].isin(process_list)]

    SHS_file.to_excel('Sutherland.xlsx', index=None)
    return SHS_file

