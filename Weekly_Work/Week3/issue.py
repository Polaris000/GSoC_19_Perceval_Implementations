import pandas as pd
from metric import Metric
import utils


class Issue(Metric):

    def __init__(self, items, date_range=(None, None)):
        """
        Initilizes self.df, the dataframe with one commit per row.

        :param items: A list of dictionaries, each element a
            line from the JSON file
        :param date_range: A tuple which represents the start and
            end date of interest
        """
        clean_items = list()
        (self.since, self.until) = date_range

        for line in items:    
            issue = self._flatten_data(line)
            if issue is not None:
                clean_items.append(issue)

        self.df = pd.DataFrame(clean_items)

    def _flatten_data(self, line):
        """
        This method is for cleaning a raw issue fetched by Perceval.
        Since all attributes of the data are not of our importance, it is
        better to just keep the ones which are required.

        :param line: a raw line fetched by Perceval, present in the JSON file
            It is a dictionary.

        :returns: A clean, flattened issue, which is a dictionary
        """
        creation_date = utils.str_to_dt_data(line['data']['created_at'])

        if self.since:
            if self.since > creation_date:
                return None

        else:
            self.since = utils.get_date(self.df, "since")            

        if self.until:
            if self.until < creation_date:
                return None

        else:
            self.until = utils.get_date(self.df, "until")

        if "pull_request" in line:
            return None

        cleaned_line = {
            'repo': line['origin'],
            'hash': line['data']['id'],
            'category': "issue",
            'author': line['data']['user']['login'],
            'created_date': line['data']['created_at'],
            'current_status': line['data']['state']
        }

        return cleaned_line
