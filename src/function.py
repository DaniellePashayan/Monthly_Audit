from configparser import ConfigParser
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def merge(input, output, shs, process):
    config_path = 'config.ini'
    config = ConfigParser()
    config.read(config_path)

    pics = config[process]['PICfile']
    pics = pd.read_csv(pics, sep = '\t', header = None)
    pics.drop(columns = [1, 2, 3, 4], inplace = True)
    pics.columns = ['Invoice', 'Post Date', 'Code']
    pics['Post Date'] = pd.to_datetime(pics['Post Date'])

    pic_desc = pd.read_excel('references/Dictionary 6 - RPA Only Rejections.xlsx', engine = 'openpyxl')
    pics = pics.merge(pic_desc, how = 'left')
    pics = pics[pics['Bot Name'].str.contains('Bundling')]

    df = pd.merge(input, shs, how = 'left',
                  left_on = ['INVNUM', 'File Date', 'SHS Name'],
                  right_on = ['INVNUM', 'BOTRequestDate', 'BotName'])
    df = pd.merge(df, pics, how = 'left',
                  left_on = ['INVNUM', 'LastModifiedDate'],
                  right_on = ['Invoice', 'Post Date'])
    output['Process'] = output['Process'].str.strip()
    df = pd.merge(df, output, how = 'left',
                  left_on = ['INVNUM', 'File Date', 'Coding Tool'],
                  right_on = ['Invoice', 'File Date', 'Process'])
    df.drop(columns = ['SHS Name', 'Invoice_x', 'Name', 'Bot Type', 'Bot Name', 'Invoice_y', 'Process'], inplace = True)
    return df

def preprocess(data):
    le_payer = LabelEncoder()
    le_coding_tool = LabelEncoder()
    le_shs_status = LabelEncoder()
    le_pic_desc = LabelEncoder()
    le_category = LabelEncoder()
    le_status = LabelEncoder()
    le_comment = LabelEncoder()

    df = data[['ACK', 'Form Letter', 'Proofs']]
    df['ACK'] = df['ACK'].astype('int64')
    df['Form Letter'] = df['Form Letter'].astype('int64')
    df['Proofs'] = df['Proofs'].astype('int64')

    df['payer_n'] = le_payer.fit_transform(data['PAYER'])
    df['coding_tool_n'] = le_coding_tool.fit_transform(data['Coding Tool'])
    df['shs_status_n'] = le_shs_status.fit_transform(data['RetrievalStatus'])
    df['pic_desc_n'] = le_shs_status.fit_transform(data['Name'])
