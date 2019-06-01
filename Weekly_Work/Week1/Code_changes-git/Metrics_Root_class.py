#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import datetime
import matplotlib.pyplot as plt
import pandas as pd


# In[7]:


class Metric():
    
    def __init__(self, path, since=None, until=None, source_code_exclude_list=None):

        self.since = since
        self.until = until
        self.source_code_exclude_list = source_code_exclude_list
        self.repo_urls = set()
        
        clean_commit_list = list()
        clean_issue_list = list()
        clean_pr_list = list()
        
        with open(path, 'r') as raw_data:
            for line in raw_data:
                line = json.loads(line)
                self.repo_urls.add(line['origin'])
                clean_line = dict()
                if line['category'] == "commit":
                    clean_line = self._clean_commit(line)

                    if self._is_source_code(clean_line):
                        clean_commit_list.append(clean_line)
                    

                elif line['category'] == "issue":
                    if "pull_request" not in line['data']:
                        clean_line = self._clean_issue(line)
                        clean_issue_list.append(clean_line)
                    else: continue
                    

                elif line['category'] == "pull_request":
                    clean_line = self._clean_pr(line)
                    clean_pr_list.append(clean_line)
                        
                        
                self.clean_commit_df = pd.DataFrame(clean_commit_list)
                self.clean_issue_df = pd.DataFrame(clean_issue_list)
                self.clean_pr_df = pd.DataFrame(clean_pr_list)
                
            self.clean_dict = {
                'commit': self.clean_commit_df,
                'issue': self.clean_issue_df,
                'pull_request': self.clean_pr_df
            }
       
        if self.since:
            for df in self.clean_dict.values():
                df = df[df['created_date'] >= self._str_to_dt_other(self.since)]
        else: 
            self.since = self._get_date("since")
            
        if self.until:
            for df in self.clean_dict.values():
                df = df[df['created_date'] < self._str_to_dt_other(self.until)]
        else: 
            self.until = self._get_date("until")
        
    def _clean_commit(self, line):
        cdata = line['data']
        cleaned_line =  \
        {
            'repo': line['origin'],
            'hash': cdata['commit'],
            'author': cdata['Author'],
            'category': "commit",
            'created_date': self._str_to_dt_data(cdata['AuthorDate']),
            'commit': cdata['Commit'],
            'commit_date': self._str_to_dt_data(cdata['CommitDate']),
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
            
    def _clean_issue(self, line):
        repo_name = line['origin']
        line_data = line['data']
        cleaned_line =  \
        {
            'repo': repo_name,
            'hash': line_data['id'],
            'category': "issue",
            'author': line_data['user']['login'],
            'created_date': self._str_to_dt_data(line_data['created_at']),
            'current_status': line_data['state']   
        }
        return cleaned_line

            
    def _clean_pr(self, line):
        repo_name = line['origin']
        line_data = line['data']
        cleaned_line =  \
        {
            'repo': repo_name,
            'hash': line_data['id'],
            'category': "pull_request",
            'author': line_data['user']['login'],
            'created_date': self._str_to_dt_data(line_data['created_at']),
            'current_status': line_data['state']   
        }
        return cleaned_line

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
    
    def _get_extension(self, file):
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

    def _str_to_dt_data(self, date):
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
        

    def _str_to_dt_other(self, date):
        datetimeobj =  datetime.datetime.strptime(date, "%Y-%m-%d")
        return datetimeobj
    

    def _get_date(self, option="since"):
        """
        For certain metrics, computing a value for a repeated interval of time
        if important. For this, an initial and final date is necessary. This 
        can become a problem since `since` and `until` date parameters to __init__
        are optional. 
        Thus, if unspecified, since and until are set to the earliest and latest
        date of all data points respectively
        """
        if option == "since":
            return min([min(df['created_date']) for df in self.clean_dict.values() if not df.empty])

        if option == "until":
            return max([max(df['created_date']) for df in self.clean_dict.values() if not df.empty])