#!/usr/bin/env python
# coding: utf-8

# [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/chaoss/wg-gmd/master?filepath=implementations/Code_Changes-Git.ipynb)
# # Code_Changes-Git
# 
# This is the reference implementation for Code_Changes,
# a metric specified by the
# [GMD Working Group](https://github.com/chaoss/wg-gmd) of the
# [CHAOSS project](https://chaoss.community).
# This implementation is specific to Git repositories.
# 
# See [README.md](README.md) to find out how to run this notebook (and others in this directory).
# 
# The implementation is described in two parts (see below):
# 
# * Retrieving data from the data source
# * Class for computing Code_Changes
# 
# Some more auxiliary information in this notebook:
# 
# * Examples of the use of the implementation
# * Examples of how to check for specific peculiarities of git commits

# ## Retrieving data from the data source
# 
# From the command line run Perceval on the git repositories to analyze,
# to produce a file with JSON documents for all its commits,
# one per line (`git-commits.json`).
# 
# As an example we will use the Perceval, SortingHat, and a fork of SortingHat
# git repositories:
# change it to get data from your preferred repositories
# (for example, you can use `https://github.com/elastic/elasticsearch-docker`
# or `https://github.com/git/git`):
# 
# ```
# $ perceval git --json-line http://github.com/chaoss/grimoirelab-perceval > git-commits.json
# [2019-01-28 21:05:45,461] - Sir Perceval is on his quest.
# [2019-01-28 21:05:48,229] - Fetching commits: 'http://github.com/chaoss/grimoirelab-perceval' git repository from 1970-01-01 00:00:00+00:00 to 2100-01-01 00:00:00+00:00; all branches
# [2019-01-28 21:05:49,727] - Fetch process completed: 1320 commits fetched
# [2019-01-28 21:05:49,728] - Sir Perceval completed his quest.
# $ perceval git --json-line http://github.com/chaoss/grimoirelab-sortinghat >> git-commits.json
# ...
# [2019-01-28 21:07:27,169] - Fetch process completed: 635 commits fetched
# [2019-01-28 21:07:27,169] - Sir Perceval completed his quest.
# $ perceval git --json-line http://github.com/jgbarah-chaoss/grimoirelab-sortinghat >> git-commits.json
# ...
# [2019-01-28 23:58:47,068] - Fetch process completed: 567 commits fetched
# [2019-01-28 23:58:47,068] - Sir Perceval completed his quest.
# ```

# ## Class for computing Code_Changes-Git
# 
# This implementation uses data retrieved as described above.
# The implementation is encapsulated in the `Code_Changes` class,
# which gets all commits for a set of repositories.

# In[328]:


import json
import datetime

import pandas as pd

class Code_Changes:
    """Class for Code_Changes for Git repositories.
    
    Objects are instantiated by specifying a file with the
    commits obtained by Perceval from a set of repositories.
        
    :param path: Path to file with one Perceval JSON document per line
    """

    @staticmethod
    def _summary(repo, cdata):
        """Compute a summary of a commit, suitable as a row in a dataframe"""
        
        summary = {
            'repo': repo,
            'hash': cdata['commit'],
            'author': cdata['Author'],
            'author_date': datetime.datetime.strptime(cdata['AuthorDate'],
                                                      "%a %b %d %H:%M:%S %Y %z"),
            'commit': cdata['Commit'],
            'commit_date': datetime.datetime.strptime(cdata['CommitDate'],
                                                      "%a %b %d %H:%M:%S %Y %z"),
            'files_no': len(cdata['files']),
            'refs': cdata['refs'],
            'parents': cdata['parents'],
            'files': cdata['files']
        }
        
        actions = 0
        for file in cdata['files']:
            if 'action' in file:
                actions += 1
        summary['files_action'] = actions
        if 'Merge' in cdata:
            summary['merge'] = True
        else:
            summary['merge'] = False
        return summary;
    
    def __init__(self, path, since=None, until=None, source_code_exclude_list=None):
        """
        Initilizes self.df, the dataframe with one row per commit.
        """
        
        self.since = since
        self.until = until
        
        self.source_code_exclude_list = source_code_exclude_list
        commits = []
        with open(path) as commits_file:
            for line in commits_file:
                commit = json.loads(line)
                commit = self._summary(repo=commit['origin'],
                                             cdata=commit['data'])
                if self._is_source_code(commit):
                    commits.append(commit)
        self.df = pd.DataFrame(commits)
        self.df['author_date'] = pd.to_datetime(self.df['author_date'], utc=True)
        self.df['commit_date'] = pd.to_datetime(self.df['commit_date'], utc=True)
        
    def total_count(self):
        
        return len(self.df.index)
    
    def compute(self, empty=False, merge=False, date='author_date', master_only=False):
        """Count number of commits
        
        :param since: Period start
        :param until: Period end
        :param empty: Include empty commits
        :param merge: Include merge commits
        :param  date: Kind of date ('author_date' or 'commit_date')
        """
        
        if master_only:
            return self._count_master_only(empty)
        
        df = self.df
        if self.since:
            df = df[df[date] >= self.since]
        if self.until:
            df = df[df[date] < self.until]
        if not empty:
            df = df[df['files_action'] != 0]
        if not merge:
            df = df[df['merge'] == False]
        return df['hash'].nunique()
    
    def _count_master_only(self, empty):
        todo = set()
        for _, commit in self.df.iterrows():
            if 'HEAD -> refs/heads/master' in commit['refs']:
                todo.add(commit['hash'])

        master = set()
        while len(todo) > 0:
            current = todo.pop()
            master.add(current)
            
            if len(self.df[self.df['hash'] == current]['parents']) > 0:
                for parent in self.df[self.df['hash'] == current]['parents'].iloc[0]:
                    if parent not in master:
                        todo.add(parent)
        if empty:
            code_commits = 0
            for commit_id in master:
                commit = self.df[self.df['hash'] == commit_id]
                if len(commit['files']) > 0:
                    for file in commit['files'].iloc[0]:
                        if 'action' in file:
                            code_commits += 1
                            break
                        
        else:
            code_commits = len(master)
        
        return code_commits
    
    def compute_timeseries(self, period="month"):
        if period == "month":
        
            return self.df['author_date']                 .groupby([self.df.author_date.dt.year.rename('year'),
                          self.df.author_date.dt.month.rename('month')]) \
                .agg('count')
    
    def _is_source_code(self, commit):
        extension_set = set()
        for file in commit['files']:
            extension_set.add(self._get_extension(file))

        if self.source_code_exclude_list is None or len(extension_set.difference(self.source_code_exclude_list)) > 0:
            return True
        return False
    
    def _get_extension(self, file):
        file_name = file['file']
        if '.' in file_name:
            file_extension = file_name.split('.')[1]
        else:
            file_extension = "other"
        return file_extension


# Method `count()` implements `Count` aggregation for `Code_Changes`.
# It accepts parameters specified for the general metric:
#     
# * Period of time: `since` and `until`
# 
# It accepts parameters specified for the specific case of Git:
#     
# * Include merge commits: `merge`
# * Include empty commits: `empty`
# * Kind of date: `date`

# ## Examples of use of the implementation

# In[330]:

# print("Code changes count from 2018-01-01 to 2018-07-01:",
#       changes.compute(since="2018-01-01", until="2018-07-01"))
# print("Code changes count from 2018-01-01 to 2018-07-01 (no merge commits):",
#       changes.compute(since="2018-01-01", until="2018-07-01", merge=False))
# print("Code changes count from 2018-01-01 to 2018-07-01 (no empty commits):",
#       changes.compute(since="2018-01-01", until="2018-07-01", empty=False))

