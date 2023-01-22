from configparser import ConfigParser
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
import joblib


def merge_format(input, output, shs, process):
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

    inputs = ''
    outputs = ''
    shs = ''
    pic_desc = ''
    pics = ''

    df = df.fillna('0').astype('str')
    return df

def preprocess(df):
    le_payer = LabelEncoder()
    le_coding_tool = LabelEncoder()
    le_shs_status = LabelEncoder()
    le_pic_desc = LabelEncoder()
    le_status = LabelEncoder()

    data = df[['ACK', 'Form Letter', 'Proofs']]
    data['ACK'] = data['ACK'].astype('int64')
    data['Form Letter'] = data['Form Letter'].astype('int64')
    data['Proofs'] = data['Proofs'].astype('int64')

    model = joblib.load(
        'C:/Users/dpashayan/PycharmProjects/Monthly_Audit/references/ML Training/models/noncodify_audit_status.joblib')

    le_status.classes_ = np.load(
        'C:/Users/dpashayan/PycharmProjects/Monthly_Audit/references/ML Training/status_classes.npy',
        allow_pickle = True)
    le_pic_desc.classes_ = np.load(
        'C:/Users/dpashayan/PycharmProjects/Monthly_Audit/references/ML Training/pic_desc_classes'
        '.npy', allow_pickle = True)
    le_coding_tool.classes_ = np.load(
        'C:/Users/dpashayan/PycharmProjects/Monthly_Audit/references/ML Training/coding_tool_classes.npy',
        allow_pickle = True)
    le_shs_status.classes_ = np.load(
        'C:/Users/dpashayan/PycharmProjects/Monthly_Audit/references/ML Training/shs_status_classes.npy',
        allow_pickle = True)
    le_payer.classes_ = np.load(
        'C:/Users/dpashayan/PycharmProjects/Monthly_Audit/references/ML Training/payer_classes.npy',
        allow_pickle = True)

    data['payer_n'] = le_payer.transform(df['PAYER'])
    data['coding_tool_n'] = le_coding_tool.transform(df['Coding Tool'])
    data['shs_status_n'] = le_shs_status.transform(df['RetrievalStatus'])
    data['pic_desc_n'] = le_pic_desc.transform(df['Name'])

    df['Status'] = le_status.inverse_transform(model.predict(data))
    return df
