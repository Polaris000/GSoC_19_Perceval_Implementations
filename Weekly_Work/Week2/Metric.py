import datetime
import pandas as pd
import utils


class Metric():
    
    def __init__(self, data_list):
        """
        Create a dataframe from data-list, which is the data 
        fetched by Perceval

        :param data_list: a list of dictionaries, where each line
            is a data line in the JSON file fetched by Perceval
        """
        self.raw_df = pd.DataFrame(data_list)

