from configparser import ConfigParser
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
import joblib
import datetime as dt

def merge_format(input, output, shs, process):
    config_path = 'config.ini'
    config = ConfigParser()
    config.read(config_path)

    Month = config['Parameters']['Month']
    Year = config['Parameters']['Year']
    Month_Name = dt.datetime.strptime(str(Month), '%m').strftime('%B')

    pics = config[process]['PICfile']
    pics = pics.replace('MMMM', Month_Name).replace('MM', Month).replace('YYYY', Year)
    pics = pd.read_csv(pics, sep = '\t', header = None)
    pics.drop(columns = [1, 2, 3, 4], inplace = True)
    pics.columns = ['Invoice', 'Post Date', 'Code']
    pics['Post Date'] = pd.to_datetime(pics['Post Date'])

    pic_desc = ''
    pic_desc = pd.read_excel('')
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

    inputs = ''
    outputs = ''
    shs = ''
    pic_desc = ''
    pics = ''

    df = df.fillna('0').astype('str')
    return df

def predict(source, process):
    source.fillna('0', inplace = True)

    le_payer = LabelEncoder()
    le_coding_tool = LabelEncoder()
    le_shs_status = LabelEncoder()
    le_pic_desc = LabelEncoder()
    le_status = LabelEncoder()
    le_category = LabelEncoder()
    le_comment = LabelEncoder()

    le_payer.classes_ = np.load('../references/ML Training/classes/payer_classes.npy', allow_pickle = True)
    le_coding_tool.classes_ = np.load('../references/ML Training/classes/coding_tool_classes.npy', allow_pickle = True)
    le_shs_status.classes_ = np.load('../references/ML Training/classes/shs_status_classes.npy', allow_pickle = True)
    le_pic_desc.classes_ = np.load('../references/ML Training/classes/pic_desc_classes.npy', allow_pickle = True)
    le_status.classes_ = np.load('../references/ML Training/classes/status_classes.npy', allow_pickle = True)
    le_category.classes_ = np.load('../references/ML Training/classes/category_classes.npy', allow_pickle = True)
    le_comment.classes_ = np.load('../references/ML Training/classes/comment_classes.npy', allow_pickle = True)

    source = source.fillna('0')
    source['ACK'] = source['ACK'].astype('int64')
    source['Form Letter'] = source['Form Letter'].astype('int64')
    source['Proofs'] = source['Proofs'].astype('int64')
    new = source[['ACK', 'Form Letter', 'Proofs']]
    new['payer_n'] = le_payer.transform(source['PAYER'])
    new['coding_tool_n'] = le_coding_tool.transform(source['Coding Tool'])
    new['shs_status_n'] = le_shs_status.transform(source['RetrievalStatus'])
    new['pic_desc_n'] = le_pic_desc.transform(source['Name'])

    status = joblib.load(f'../references/ML Training/models/{process}_audit_status.joblib')
    category = joblib.load(f'../references/ML Training/models/{process}_audit_category.joblib')
    comments = joblib.load(f'../references/ML Training/models/{process}_audit_comment.joblib')

    new['status_n'] = status.predict(new)
    source['Status'] = le_status.inverse_transform(new['status_n'])
    new['category_n'] = category.predict(new)
    source['Category'] = le_category.inverse_transform(new['category_n'])
    new['comment_n'] = comments.predict(new)
    source['Comments'] = le_comment.inverse_transform(new['comment_n'])

    config_path = 'config.ini'
    config = ConfigParser()
    config.read(config_path)

    Month = config['Parameters']['Month']
    Year = config['Parameters']['Year']
    Month_Name = dt.datetime.strptime(str(Month), '%m').strftime('%B')

    save_path = config[process]['MonthlySummaryPath']
    file_name = f'{save_path}/{Year}/{Month} {Year} - {process} Monthly Summary.xlsx'

    source.to_excel(file_name)

    return source