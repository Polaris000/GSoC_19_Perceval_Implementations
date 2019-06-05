import json
import datetime
import matplotlib.pyplot as plt
import pandas as pd


class Metric():
    
    def __init__(self, path, source_code_exclude_list=None):

        self.source_code_exclude_list = source_code_exclude_list
        self.repo_urls = set()

        data_list = list()
        self.raw_df = pd.DataFrame()

        with open(path, 'r') as raw_data:
            for line in raw_data:
                line = json.loads(line)
                self.repo_urls.add(line['origin'])

                data_list.append(line)

            self.raw_df = pd.DataFrame(data_list)


    def _is_source_code(self, commit):
        """
        Given a commit structure, which is a dictionary returned by the _summary function, 
        and given a list of files to exclude using source_code_exclude_list while instantiating 
        an object, decide whether all the files in a commit are to be excluded or not
        
        :param commit: a commit structure, returned by the _summary method.
        """
        extension_set = set()
        for file in commit['files']:
            extension_set.add(self._get_extension(file))

        if self.source_code_exclude_list is None or len(extension_set.difference(self.source_code_exclude_list)) > 0:
            return True
        return False
    
    @staticmethod
    def _get_extension(file):
        """
        Given a file structure, which is a dictionary and an element of commit['files'], 
        return the extension of that file. 
        For files without a standard ".xyz" extension, like LICENCE or AUTHORS, the "others" 
        extension is used. 
        
        :param file: a file structure which is a dictionary, an element of commit["files"]
        """
            
        file_name = file['file']
        if '.' in file_name:
            file_extension = file_name.split('.')[1]
        else:
            file_extension = "other"
        return file_extension

    @staticmethod
    def _str_to_dt_data(date):
        """
        :param date: converts date (str) to a datetime object 
        Note: the string format for the date in the json file is either: 
         - %a %b %d %H:%M:%S %Y %z --> for commits
         - %Y-%m-%dT%H:%M:%SZ      --> for issues and pull requests
        """        
        try:
            datetimestr =  datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y %z").strftime("%Y-%m-%d")
        
        except ValueError as ve:
            datetimestr =  datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        
        finally:
            datetimeobj = datetime.datetime.strptime(datetimestr, "%Y-%m-%d")
            return datetimeobj
        
    @staticmethod
    def _str_to_dt_other(date):
        datetimeobj =  datetime.datetime.strptime(date, "%Y-%m-%d")
        return datetimeobj
    
    @staticmethod
    def _get_date(df, option="since"):
        """
        For certain metrics, computing a value for a repeated interval of time
        if important. For this, an initial and final date is necessary. This 
        can become a problem since `since` and `until` date parameters to __init__
        are optional. 
        Thus, if unspecified, since and until are set to the earliest and latest
        date of all data points respectively
        """
        if option == "since":
            return min(df['created_date'])

        if option == "until":
            return max(df['created_date'])