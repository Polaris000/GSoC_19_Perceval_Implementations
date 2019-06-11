import pandas as pd


class MetricPure():
    """
    Create a list of dictionaries from data-list, which is the data
    fetched by Perceval

    :param data_list: A list of dictionaries.
        Each element is a Perceval dictionary, obtained from a JSON
        file or from Perceval directly.
    """

    def __init__(self, data_list):
        data_list_flattened = MetricPure._flatten_data(data_list)
        self.raw_list = data_list_flattened


    @staticmethod
    def _flatten_data(data_list):
        """
        Flattens the nested dictionaries in Perceval data to ease
        in converting the data to a DataFrame.

        :param data_list: A list of dictionaries.
        Each element is a Perceval dictionary, obtained from a JSON
        file or from Perceval directly.

        :returns: commit as a flattened dictionary.
        """
        data_rows = list()

        for data_line in data_list:
            row = dict()
            for key, val in data_line.items():
                if isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        row[key + "_" + sub_key] = sub_val
                else:
                    row[key] = val
            data_rows.append(row)
        return data_rows
