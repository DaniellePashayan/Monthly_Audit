import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

process = 'NonCodify'
inputs = pd.read_csv(f'../ML Training/training data/{process}_training_data.csv')
inputs.fillna('0', inplace = True)

le_payer = LabelEncoder()
le_coding_tool = LabelEncoder()
le_shs_status = LabelEncoder()
le_pic_desc = LabelEncoder()
le_status = LabelEncoder()

def Status(training_data, process):
    training_data['Form Letter'] = training_data['Form Letter'].astype('int64')
    training_data['Proofs'] = training_data['Proofs'].astype('int64')
    training_data['ACK'] = training_data['ACK'].astype('int64')

    df = training_data.copy()
    # converts the values into numbers
    training_data['payer_n'] = le_payer.fit_transform(training_data['PAYER'])
    if process == 'NonCodify':
        training_data['coding_tool_n'] = le_coding_tool.fit_transform(training_data['Coding Tool'])
    elif process == 'medicalrecords':
        training_data['process_n'] = le_coding_tool.fit_transform(training_data['Process'])
    training_data['shs_status_n'] = le_shs_status.fit_transform(training_data['SHS Status'])
    training_data['pic_desc_n'] = le_pic_desc.fit_transform(training_data['PIC Desc'])
    classes = le_pic_desc.classes_

    training = training_data.copy()
    training['status_n'] = le_status.fit_transform(training['Status'])
    np.save('status_classes.npy', le_status.classes_)
    np.save('payer_classes.npy', le_payer.classes_)
    np.save('coding_tool_classes.npy', le_coding_tool.classes_)
    np.save('shs_status_classes.npy', le_shs_status.classes_)
    np.save('pic_desc_classes.npy', le_pic_desc.classes_)


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
    # predictions = model.predict(X_test)
    # X_test['Status'] = le_status.inverse_transform(model.predict(X_test))
    df['Status2'] = le_status.inverse_transform(model.predict(X))
    # X['xyz'] = model.predict(X)
    status = le_status.inverse_transform(predictions)

    # accuracy = accuracy_score(y_test, predictions)
    print('f')

    # joblib.dump(model, f'../ML Training/models/{process}_audit_status.joblib')


Status(inputs, 'NonCodify')