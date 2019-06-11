import math
import pandas as pd
from MetricPure import MetricPure
import utils


class CommitPure(MetricPure):
    """
    Initilizes self.clean_data_list, a list with commit dictionaries
    elements.

    :param data_list: A list of dictionaries.
        Each element is a Perceval dictionary, obtained from a JSON
        file or from Perceval directly.

    :param date_range: A tuple which represents the period of interest
        It is of the form (since, until), where since and until are strings.
        Either, or both can be None. If, for example, since is None, that 
        would mean that all commits from the first commit to the commit who last
        falls inside the until range will be included.

    :param src_code_obj: An object of SourceCode.
        It is used to determine what comprises source code.
    """

    def __init__(self, data_list, date_range=(None, None), src_code_obj=None):

        super().__init__(data_list)

        self.clean_data_list = list()
        (self.since, self.until) = date_range

        for commit in self.raw_list:
            commit = self._clean_commit(commit)
            if src_code_obj is None  \
                    or src_code_obj.is_source_code(commit):
                self.clean_data_list.append(commit)

        if self.since:
            self.clean_data_list = [commit for commit in self.clean_data_list 
                                        if e['created_date'] 
                                            >= utils.str_to_dt_data(self.since)]

        else:
            self.since = utils.get_date(self.clean_data_list, "since")

        if self.until:
            self.clean_data_list = [commit for commit in self.clean_data_list 
                                        if e['created_date'] 
                                            < utils.str_to_dt_data(self.until)]
        else:
            self.until = utils.get_date(self.clean_data_list, "until")


    def _clean_commit(self, line):
        """
        This method is for cleaning a raw commit fetched by Perceval.
        Since all attributes of the data are not of our importance, it is
        better to just keep the ones which are required.

        :param line: a raw line fetched by Perceval, present in the JSON file
            It is a dictionary.

        :returns: A cleaned commit, which is a dictionary
        """
        cleaned_line = {
            'repo': line['origin'],
            'hash': line['data_commit'],
            'author': line['data_Author'],
            'category': "commit",
            'created_date': utils.str_to_dt_data(line['data_AuthorDate']),
            'commit': line['data_Commit'],
            'commit_date': utils.str_to_dt_data(line['data_CommitDate']),
            'files_no': len(line['data_files']),
            'refs': line['data_refs'],
            'parents': line['data_parents'],
            'files': line['data_files']
        }

        actions = 0
        for file in line['data_files']:
            if 'action' in file:
                actions += 1
        cleaned_line['files_action'] = actions

        try:
            non_merge = math.isnan(line['data_Merge'])

        except (TypeError, KeyError):
            non_merge = False

        cleaned_line['merge'] = not non_merge
        return cleaned_line
