import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from os.path import exists

process = 'NonCodify'
print(exists(f'../ML Training/training data/{process}_training_data.csv'))
inputs = pd.read_csv(f'../ML Training/training data/{process}_training_data.csv')


features = ['PAYER', 'Process', 'SHS Status', 'PIC Desc', 'Form Letter', 'Records', 'ACK']
inputs.fillna('0', inplace = True)

le_payer = LabelEncoder()
le_coding_tool = LabelEncoder()
le_shs_status = LabelEncoder()
le_pic_desc = LabelEncoder()
le_category = LabelEncoder()
le_status = LabelEncoder()
le_comment = LabelEncoder()

def Category(training_data, process):

    training_data['Form Letter'] = training_data['Form Letter'].astype('int64')
    if process == 'Bundling':
        training_data['Proofs'] = training_data['Proofs'].astype('int64')
    elif process == 'medicalrecords':
        training_data['Records'] = training_data['Records'].astype('int64')
    training_data['ACK'] = training_data['ACK'].astype('int64')

    # converts the values into numbers
    training_data['payer_n'] = le_payer.fit_transform(training_data['PAYER'])
    if process == 'Bundling':
        training_data['coding_tool_n'] = le_coding_tool.fit_transform(training_data['Coding Tool'])
    elif process == 'medicalrecords':
        training_data['process_n'] = le_coding_tool.fit_transform(training_data['Process'])
    training_data['shs_status_n'] = le_shs_status.fit_transform(training_data['SHS Status'])
    training_data['pic_desc_n'] = le_pic_desc.fit_transform(training_data['PIC Desc'])

    training = training_data.copy()
    training['category_n'] = le_category.fit_transform(training_data['Category'])

    training_data = training_data.drop(
        columns = ['PAYER', 'Process', 'SHS Status', 'PIC Desc', 'Category', 'Status', 'Comment'], axis = 'columns')
    training = training.drop(columns = ['PAYER', 'Process', 'SHS Status', 'PIC Desc', 'Status', 'Comment'],
                             axis = 'columns')

    # sets the keys for the data you are feeding it

    model = DecisionTreeClassifier()

    X = training_data
    y = pd.DataFrame(training['category_n'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    print(accuracy)

    joblib.dump(model, f'../ML Training/models/{process}_audit_category.joblib')


def Status(training_data, process):
    training_data['Form Letter'] = training_data['Form Letter'].astype('int64')
    training_data['Proofs'] = training_data['Proofs'].astype('int64')
    training_data['ACK'] = training_data['ACK'].astype('int64')

    # converts the values into numbers
    training_data['payer_n'] = le_payer.fit_transform(training_data['PAYER'])
    if process == 'NonCodify':
        training_data['coding_tool_n'] = le_coding_tool.fit_transform(training_data['Coding Tool'])
    elif process == 'medicalrecords':
        training_data['process_n'] = le_coding_tool.fit_transform(training_data['Process'])
    training_data['shs_status_n'] = le_shs_status.fit_transform(training_data['SHS Status'])
    training_data['pic_desc_n'] = le_pic_desc.fit_transform(training_data['PIC Desc'])

    training = training_data.copy()
    test = pd.DataFrame()
    test['Status'] = training_data['Status'].unique()
    test['status_n'] = le_status.fit_transform(test['Status'])
    training['status_n'] = le_status.fit_transform(training['Status'])

    training_data = training_data.drop(columns = ['PAYER', 'Coding Tool', 'SHS Status', 'PIC Desc',
                                                  'Category', 'Status', 'Comment'], axis = 'columns')
    training = training.drop(columns = ['PAYER', 'Coding Tool', 'SHS Status', 'PIC Desc', 'Category', 'Comment'],
                             axis = 'columns')

    # sets the keys for the data you are feeding it
    model = DecisionTreeClassifier()

    X = training_data
    y = pd.DataFrame(training['status_n'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    status = le_status.inverse_transform(predictions)

    accuracy = accuracy_score(y_test, predictions)
    print(accuracy)

    joblib.dump(model, f'../ML Training/models/{process}_audit_status.joblib')


def Comment(training_data, process):

    training_data['Form Letter'] = training_data['Form Letter'].astype('int64')
    if process == 'Bundling':
        training_data['Proofs'] = training_data['Proofs'].astype('int64')
    elif process == 'medicalrecords':
        training_data['Records'] = training_data['Records'].astype('int64')
    training_data['ACK'] = training_data['ACK'].astype('int64')

    # converts the values into numbers
    # converts the values into numbers
    training_data['payer_n'] = le_payer.fit_transform(training_data['PAYER'])
    if process == 'Bundling':
        training_data['coding_tool_n'] = le_coding_tool.fit_transform(training_data['Coding Tool'])
    elif process == 'medicalrecords':
        training_data['process_n'] = le_coding_tool.fit_transform(training_data['Process'])
    training_data['shs_status_n'] = le_shs_status.fit_transform(training_data['SHS Status'])
    training_data['pic_desc_n'] = le_pic_desc.fit_transform(training_data['PIC Desc'])

    training = training_data.copy()
    training['comment_n'] = le_comment.fit_transform(training['Comment'])

    training_data = training_data.drop(columns = ['PAYER', 'Process', 'SHS Status', 'PIC Desc',
                                                  'Category', 'Status', 'Comment'], axis = 'columns')
    training = training.drop(columns = ['PAYER', 'Process', 'SHS Status', 'PIC Desc', 'Category', 'Status'], axis = 'columns')

    # sets the keys for the data you are feeding it
    model = DecisionTreeClassifier()

    X = training_data
    y = pd.DataFrame(training['comment_n'])


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    print(accuracy)

    joblib.dump(model, f'../ML Training/models/{process}_audit_comment.joblib')

Status(inputs, 'NonCodify')