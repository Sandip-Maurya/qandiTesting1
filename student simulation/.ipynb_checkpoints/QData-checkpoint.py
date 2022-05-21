import pandas as pd

class QData:
    def __init__(self):
        # Load question_data
        self.q_data_df = pd.read_csv('q_data.csv')
        self.topic_df = pd.read_csv('Topic_ID.csv')

    def get(self):
        return self.q_data_df , self.topic_df


        