import json
import datetime
import pandas as pd
from Metrics_Root_class import Metric

class Commit(Metric):
    """Class for Code_Changes for Git repositories.
    
    Objects are instantiated by specifying a file with the
    commits obtained by Perceval from a set of repositories.
        
    :param path: Path to file with one Perceval JSON document per line
    """
    
    def __init__(self, path, date_range=(None, None), source_code_exclude_list=None):
        """
        Initilizes self.df, the dataframe with one commit per row.
        The source_code_exclude_list parameter is a list which contains file extensions
        which are to be ignored. All possible file extensions are allowed. 
        For files without a standard ".xyz" extension, like LICENCE or AUTHORS, the "others" 
        extension is used. 
        
        :param since: Period start
        :param until: Period end
        :param source_code_exclude_list: Files extensions to exclude. For example, 
            source_code_exclude_list = ["py", "other", "gitignore"]
        """
        
        super().__init__(path, source_code_exclude_list)
        raw_data_list = self.raw_df.to_dict(orient='records')
        clean_data_list = list()

        self.since = date_range[0]
        self.until = date_range[1]

        for commit in raw_data_list:
            commit = self._clean_commit(commit)
            if super()._is_source_code(commit):
                clean_data_list.append(commit)

        self.df = pd.DataFrame(clean_data_list)


        if self.since:
            for df in self.clean_dict.values():
                df = df[df['created_date'] >= Metric._str_to_dt_other(self.since)]
        else: 
            self.since = Metric._get_date(self.df, "since")
            
        if self.until:
            for df in self.clean_dict.values():
                df = df[df['created_date'] < Metric._str_to_dt_other(self.until)]
        else: 
            self.until = Metric._get_date(self.df, "until")

    def _clean_commit(self, line):
        """
        what is the so called items present in the so called items
        """
        cdata = line['data']
        print(cdata)
        cleaned_line =  \
        {
            'repo': line['origin'],
            'hash': cdata['commit'],
            'author': cdata['Author'],
            'category': "commit",
            'created_date': Metric._str_to_dt_data(cdata['AuthorDate']),
            'commit': cdata['Commit'],
            'commit_date': Metric._str_to_dt_data(cdata['CommitDate']),
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
        
    
