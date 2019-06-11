import pandas as pd
import matplotlib.pyplot as plt
import utils
from SourceCode import SourceCode
from CommitPure import CommitPure


class Code_Changes_Git_Pure(CommitPure):
    """Class for Code_Changes for Git repositories.
    Objects are instantiated by specifying a file with the
    commits obtained by Perceval from a set of repositories.
    :param path: Path to file with one Perceval JSON document per line
    """

    def __init__(self, data_list, date_range=(None, None), src_code_obj=None):
        """
        Initilizes self.clean_data_list, a list of dictionaries where each element
            is fetched by Perceval
        :param data_list: A list of dictionaries, each element a line from the
            JSON file
        :param date_range: A tuple which represents the start and end date of
            interest
        :param src_code_obj: An object of SourceCode, to be used to determine
            what comprises source code.
        """

        super().__init__(data_list, date_range, src_code_obj)

    def total_count(self):
        """
        Get a naive count of the number of commits in the Perceval data.
        Note that some commits may be repeated and so total_count may
        overshoot.
        """
        return len(self.clean_data_list)

    def compute(self, incl_empty=True, incl_merge=True, master_only=False):
        """Count number of commits of different types, like including empty commits
        or counting only those commits made on the master branch.
        :param incl_empty: Include empty commits
        :param incl_merge: Include merge commits
        :param master_only: Include only commits made on master branch
        """
        clean_data_list = self.clean_data_list

        if master_only:
            count = self._count_master_only(incl_empty)

        else:
            if not incl_empty:
                clean_data_list = [commit for commit in clean_data_list if commit['files_action'] != 0]
            if not incl_merge:
                clean_data_list = [commit for commit in clean_data_list if not commit['merge']]
            count = len(set([x['hash'] for x in clean_data_list]))

        return count

    # compute_timeseries yet to be finished for non_pandas
    # please ignore this method.
    def compute_timeseries(self, period="month", plot_chart=False):
        """
        The metric value is computed for each fixed interval of time
        from the "since" date to the "until" date arguments, specified
        during object initiation.
        The fixed time interval can be either a month or a week.
        :param period: A string which can be either "month" or "week"
        :param plot_chart: Plots a barchart of the timeseries if True
        """

        df = self.df
        if period == "month":
            timeseries_series = df['created_date'] \
                .groupby([df['created_date'].dt.year.rename('year'),
                          df['created_date'].dt.month.rename('month')]) \
                .agg('count')

            all_periods = pd.DataFrame(
                            pd.date_range(self.since, self.until, freq='M'),
                            columns=["Dates"])
            all_periods = pd.DataFrame(
                [all_periods['Dates'].dt.year.rename("year"),
                 all_periods['Dates'].dt.month.rename("month")]).T

        elif period == "week":
            timeseries_series = df['created_date'] \
                .groupby([df['created_date'].dt.year.rename('year'),
                          df['created_date'].dt.week.rename('week')])   \
                .agg('count')

            all_periods = pd.DataFrame(
                            pd.date_range(self.since, self.until, freq='W'),
                            columns=["Dates"])
            all_periods = pd.DataFrame(
                [all_periods['Dates'].dt.year.rename("year"),
                 all_periods['Dates'].dt.week.rename("week")]).T

        timeseries_df = pd.DataFrame(timeseries_series)
        timeseries_df.reset_index(inplace=True)
        timeseries_df.columns = ["year", period, "count"]
        merged_df = all_periods.merge(timeseries_df, how='outer').fillna(0)

        if plot_chart:
            plt.style.use('seaborn')
            merged_df.plot(y='count', use_index=True)
            plt.fill_between(y1=merged_df['count'], y2=0, x=merged_df.index)
            plt.title("Commit Timeseries")
            plt.show()

        dataframe = merged_df
        return dataframe

    def _count_master_only(self, incl_empty=True):
        """
        Counts commits present only on the master branch.
        :param incl_empty: exclude empty commits on the master branch
        """

        todo = set()
        for commit in self.clean_data_list:
            if 'HEAD -> refs/heads/master' in commit['refs']:
                todo.add(commit['hash'])

        master = set()
        while len(todo) > 0:
            current = todo.pop()
            master.add(current)

            for parent in [commit['parents'] for commit in self.clean_data_list if commit['hash'] == current][0]:
                if parent not in master:
                    todo.add(parent)

        if not incl_empty:
            code_commits = 0
            count1 = 0
            count2 = 0
            for commit_id in master:
                commit = [commit for commit in self.clean_data_list if commit['hash'] == current][0]
                if commit['files_no'] > 0:
                    count1 += 1
                    for file in commit['files']:
                        if 'action' in file:
                            count2 += 1
                            code_commits += 1
                            break

        else:
            code_commits = len(master)

        return code_commits


if __name__ == "__main__":
    sourcecode = SourceCode(["tests/"], "folder_exclude")
    data_list = utils.read_JSON_file('git-commits.json')
    changes = Code_Changes_Git_Pure(data_list)
    print(changes.compute(incl_empty=False))