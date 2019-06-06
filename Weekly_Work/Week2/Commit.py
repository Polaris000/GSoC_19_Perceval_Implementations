import json
import datetime
import pandas as pd
from Metric import Metric
import utils
from SourceCode import SourceCode


class Commit(Metric):

    def __init__(self, path, date_range=(None, None), source_code_exclude_list=None):
        """
        Initilizes self.df, the dataframe with one commit per row.
        The source_code_exclude_list parameter is a list which contains file extensions
        which are to be ignored. All possible file extensions are allowed. 
        For files without a standard ".xyz" extension, like LICENCE or AUTHORS, the "others" 
        extension is used. 
        
        :param path: Path to file with one Perceval JSON document per line
        :param date_range: A tuple which represents the start and end date of interest
        :param source_code_exclude_list: Files extensions to exclude. For example, 
            source_code_exclude_list = ["py", "other", "gitignore"]
        """
    
        
        data_list = utils.read_JSON_file(path)
        
        super().__init__(data_list)

        raw_data_list = self.raw_df.to_dict(orient='records')
        clean_data_list = list()
        self.repo_urls = set()

        self.source_code_exclude_list = source_code_exclude_list
        self.since = date_range[0]
        self.until = date_range[1]

        for commit in raw_data_list:
            self.repo_urls.add(commit['origin'])
            commit = self._clean_commit(commit)
            if SourceCode._is_source_code(commit, self.source_code_exclude_list):
                clean_data_list.append(commit)

        self.df = pd.DataFrame(clean_data_list)


        if self.since:
            for df in self.clean_dict.values():
                df = df[df['created_date'] >= utils.str_to_dt_other(self.since)]
        else: 
            self.since = utils.get_date(self.df, "since")
            
        if self.until:
            for df in self.clean_dict.values():
                df = df[df['created_date'] < utils.str_to_dt_other(self.until)]
        else: 
            self.until = utils.get_date(self.df, "until")

    def _clean_commit(self, line):
        """
        This method is for cleaning a raw commit fetched by Perceval. 
        Since all attributes of the data are not of our importance, it is 
        better to just keep the ones which are required.

        :param line: a raw line fetched by Perceval, present in the JSON file
            It is a dictionary.
        """
        cdata = line['data']
        print(cdata)
        cleaned_line =  \
        {
            'repo': line['origin'],
            'hash': cdata['commit'],
            'author': cdata['Author'],
            'category': "commit",
            'created_date': utils.str_to_dt_data(cdata['AuthorDate']),
            'commit': cdata['Commit'],
            'commit_date': utils.str_to_dt_data(cdata['CommitDate']),
            'files_no': len(cdata['files']),
            'refs': cdata['refs'],
            'parents': cdata['parents'],
            'files': cdata['files']
        }

        actions = 0
        for file in cdata['files']:
            if 'action' in file:
                actions += 1
        cleaned_line['files_action'] = actions
        if 'Merge' in cdata:
            cleaned_line['merge'] = True
        else:
            cleaned_line['merge'] = False

        return cleaned_line
        
    
