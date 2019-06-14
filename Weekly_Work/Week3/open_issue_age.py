import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from issue import Issue
import utils

class OpenIssueAge(Issue):   
    
    def __init__(self, items, date_range=(None, None)):
        """
        Initilizes self.df, the dataframe with one issue per row.
        :param items: A list of dictionaries, each element a line from the
            JSON file
        :param date_range: A tuple which represents the start and end date of
            interest
        """

        super().__init__(items, date_range)
        self.df['open_issue_age'] = pd.np.nan

    def total_count(self):
        """
        Get a naive count of the number of issues in the Perceval data.
        """
        return len(self.df.index)
        
    def compute(self, plot_chart=False):
        """
        Count the average open issue age for all issues in the Perceval data.
       :param plot_chart: Plots a barchart of open issue age for each issue
            in the data
        """
        avg_open_issue_ages = None
        issue_status_series = datetime.datetime.now()   \
                             - df["created_date"][df["current_status"] == "open"]
        days = [x.days for x in issue_status_series]

        self.df.loc[df["current_status"] == "open", ['open_issue_age']] = days

        days = [day for day in days if not pd.isna(day)]
        avg_open_issue_ages = np.mean(days)

        if plot_chart:
            plt.figure(figsize=(10, 5))
            plt.ylim([0, max(days) + 100])
            plt.bar                  (
                x = range(1, len(days) +1),
                height=days, 
            )
            plt.style.use('seaborn')
        return avg_open_issue_ages
        
    def compute_time_series(self, period="month", plot_chart=False):
        """
        The metric value is computed for each fixed interval of time
        from the "since" date to the "until" date arguments, specified
        during object initiation.
        The fixed time interval can be either a month or a week.
        :param period: A string which can be either "month" or "week"
        :param plot_chart: Plots a barchart of the timeseries if True
        """
        dataframe = pd.DataFrame()
            
        df = self.df
        if period == "month": 
            timeseries_series =  df[['created_date', 'open_issue_age']] \
                .groupby([df['created_date'].dt.year.rename('year'),
                          df['created_date'].dt.month.rename('month')]) \
                .agg('mean')

            all_periods = pd.DataFrame(pd.date_range(self.since, self.until, freq='M'), columns=["Dates"])
            all_periods = pd.DataFrame(                        [all_periods['Dates'].dt.year.rename("year"),                        all_periods['Dates'].dt.month.rename("month")]).T

        elif period == "week":
            timeseries_series =  df[['created_date', 'open_issue_age']] \
                .groupby([df['created_date'].dt.year.rename('year'),
                          df['created_date'].dt.week.rename('week')]) \
                .agg('mean') 

            all_periods = pd.DataFrame(pd.date_range(self.since, self.until, freq='W'), columns=["Dates"])
            all_periods = pd.DataFrame(                        [all_periods['Dates'].dt.year.rename("year"),                        all_periods['Dates'].dt.week.rename("week")]).T


        timeseries_df = pd.DataFrame(timeseries_series)
        timeseries_df.reset_index(inplace=True)
        timeseries_df.columns = ["year", period, "open_issue_age"]
        merged_df = all_periods.merge(timeseries_df, how='outer').fillna(0)

        if plot_chart:
            plt.style.use('seaborn')
            merged_df.plot(y='open_issue_age', use_index=True, figsize=(10, 5))
            plt.fill_between(y1=merged_df['open_issue_age'], y2=0, x=merged_df.index)
            plt.title(repo_url)

        dataframe = merged_df
        return dataframe


if __name__ == "__main__":
    items = utils.read_JSON_file('./atom_issues.json')
    open_issue_age = OpenIssueAge(items)
    print(open_issue_age.compute(empty=True))