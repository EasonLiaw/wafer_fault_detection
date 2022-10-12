'''
Author: Liaw Yi Xian
Last Modified: 11th October 2022
'''

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from Application_Logger.logger import App_Logger
import joblib
import numpy as np

class pred_Preprocessor:


    def __init__(self, file_object):
        '''
            Method Name: __init__
            Description: This method initializes instance of Preprocessor class
            Output: None
        '''
        self.file_object = file_object
        self.log_writer = App_Logger()


    def extract_compiled_data(self, path):
        '''
            Method Name: extract_compiled_data
            Description: This method extracts data from a csv file and converts it into a pandas dataframe.
            Output: A pandas dataframe
            On Failure: Logging error and raise exception
        '''
        self.log_writer.log(
            self.file_object, "Start reading compiled data from database")
        self.path = path
        try:
            data = pd.read_csv(path)
        except Exception as e:
            self.log_writer.log(
                self.file_object, f"Fail to read compiled data from database with the following error: {e}")
            raise Exception(
                f"Fail to read compiled data from database with the following error: {e}")
        self.log_writer.log(
            self.file_object, "Finish reading compiled data from database")
        return data


    def remove_duplicated_rows(self, data):
        '''
            Method Name: remove_duplicated_rows
            Description: This method removes duplicated rows from a pandas dataframe.
            Output: A pandas DataFrame after removing duplicated rows. In addition, duplicated records that are removed will be stored in a separate csv file labeled "Duplicated_Records_Removed.csv"
            On Failure: Logging error and raise exception
        '''
        self.log_writer.log(
            self.file_object, "Start handling duplicated rows in the dataset")
        self.data = data
        if len(self.data[self.data.duplicated()]) == 0:
            self.log_writer.log(
                self.file_object, "No duplicated rows found in the dataset")
        else:
            try:
                self.data[self.data.duplicated()].to_csv('Intermediate_Pred_Results/Duplicated_Records_Removed.csv', index=False)
                self.data = self.data.drop_duplicates(ignore_index=True)
            except Exception as e:
                self.log_writer.log(
                    self.file_object, f"Fail to remove duplicated rows with the following error: {e}")
                raise Exception(
                    f"Fail to remove duplicated rows with the following error: {e}")
        self.log_writer.log(
            self.file_object, "Finish handling duplicated rows in the dataset")
        return self.data

    
    def data_preprocessing(self, data_path, train_path, col_remove):
        '''
            Method Name: data_preprocessing
            Description: This method performs all the data preprocessing tasks for the data.
            Output: A pandas dataframe, where all the data preprocessing tasks are performed.
            On Failure: Logging error and raise exception
        '''
        self.log_writer.log(self.file_object, 'Start of data preprocessing')
        self.train_path = train_path
        self.data_path = data_path
        data = self.extract_compiled_data(self.data_path)
        index = data[col_remove]
        data = self.remove_duplicated_rows(data)
        data.drop(col_remove,axis=1,inplace=True)
        self.log_writer.log(
            self.file_object, "Start adding missing indicator to features with missing values")
        missingindicatorobject = joblib.load(
            self.train_path + 'AddMissingIndicator.pkl')
        data = missingindicatorobject.transform(data)
        self.log_writer.log(
            self.file_object, "Finish adding missing indicator to features with missing values")
        self.log_writer.log(
            self.file_object, "Start adding zero indicator to features")
        zeroindicatorobject = joblib.load(self.train_path + 'ZeroIndicator.pkl')
        for col in zeroindicatorobject:
            data[col+"_zero"] = np.where(data[col]==0, 1, 0)
        self.log_writer.log(
            self.file_object, "Finish adding zero indicator to features")
        self.log_writer.log(
            self.file_object, "Start removing features with constant variance")
        dropconstantfeatureobject = joblib.load(
            self.train_path + 'Dropconstantfeatures.pkl')
        data = dropconstantfeatureobject.transform(data)
        self.log_writer.log(
            self.file_object, "Finish removing features with constant variance")
        data = pd.concat([index,data],axis=1)
        data.to_csv(
            'Intermediate_Pred_Results/Prediction_Processed_Data.csv', index=False)
        self.log_writer.log(self.file_object, 'End of data preprocessing')