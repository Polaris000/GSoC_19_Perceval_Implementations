import pandas as pd


class Metric():
    """
    Create a dataframe from items, which is the data
    fetched by Perceval

    :param items: A list of dictionaries.
        Each element is a Perceval dictionary, obtained from a JSON
        file or from Perceval directly.
    """

    def __init__(self, items):
        flat_items = self._flatten_data(items)
        self.raw_df = pd.DataFrame(items_flattened)

    def _flatten_data(self, items):
        """
        Flattens the nested dictionaries in Perceval data to ease
        in converting the data to a DataFrame.

        :param items: A list of dictionaries.
        Each element is a Perceval dictionary, obtained from a JSON
        file or from Perceval directly.

        :returns: commit as a flattened dictionary.
        """
        data_rows = list()

        for data_line in items:
            row = dict()
            for key, val in data_line.items():
                if isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        row[key + "_" + sub_key] = sub_val
                else:
                    row[key] = val
            data_rows.append(row)
        return data_rows
