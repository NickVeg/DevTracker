import pandas as pd
from clickhouse_driver import Client
import pytz

clickhouse_client = Client('localhost', port=9000)

class ClickhouseData:
    def __init__(self, author_name, date_range=None, projects=None):
        self.author_name = author_name
        self.date_range = date_range
        self.projects = projects
        self.df = self.create_working_dataframe(author_name)
        # filter dataframe with date_range and projects
        self.df = self.filter_dataframe(date_range=self.date_range, projects=self.projects)

    def create_working_dataframe(self, author_name):

        merged_df_list = []
        for author_name in self.author_name:
            # Query commit_all table for comments
            query1 = f"SELECT hex(sha1) as commit, comment FROM commit_all WHERE author = '{author_name}'"
            df1 = pd.DataFrame(clickhouse_client.execute(query1), columns=['commit', 'comment'])

            # Query b2cPtaPkgR_all table for the remaining fields
            query2 = f"SELECT hex(commit) as commit, author, language, project, time FROM b2cPtaPkgR_all WHERE author = '{author_name}'"
            df2 = pd.DataFrame(clickhouse_client.execute(query2), columns=['commit', 'author', 'language', 'project', 'time'])

            # Merge the two DataFrames on 'commit'
            merged_df = pd.merge(df1, df2, on='commit')

            merged_df_list.append(merged_df)

        # Concatenate all the dataframes into one
        final_df = pd.concat(merged_df_list)

        print(final_df.head())
        return final_df


    def get_commit_messages(self):
        """
        Returns a list of commit messages for the given author name.
        """
        # Select comments from DataFrame where author matches
        commit_messages = self.df[self.df['author'].isin(self.author_name)]['comment'].tolist()
        return commit_messages

    def get_projects_and_commits(self):
        """
        Returns a dictionary where the keys are project names and the values are the number of commits
        the given author has made to each project.
        """
        # Filter DataFrame where author matches and then count commits per project
        project_counts = self.df[self.df['author'].isin(self.author_name)]['project'].value_counts().to_dict()
    
        # Sort projects_and_commits by number of commits in descending order
        projects_and_commits = dict(sorted(project_counts.items(), key=lambda item: item[1], reverse=True))
    
        return projects_and_commits

    def get_language_use_over_time(self):
        """
        Returns a dictionary containing the number of commits per language per month
        for the given author name.
        """
        # Filter the DataFrame for the specific authors
        df_author = self.df[self.df['author'].isin(self.author_name)].copy()

        # Convert the 'time' column to datetime and extract the year and month
        df_author['year_month'] = pd.to_datetime(df_author['time'], unit='s').dt.to_period('M')

        # Convert the 'year_month' column to string to avoid JSON serialization error
        df_author['year_month'] = df_author['year_month'].astype(str)

        # Group by 'language' and 'year_month', and count the number of commits
        df_language_use = df_author.groupby(['language', 'year_month']).size().reset_index(name='count')

        # Convert the DataFrame to a nested dictionary
        language_use = {k: v.set_index('year_month')['count'].to_dict() 
                        for k, v in df_language_use.groupby('language')}
        
        return language_use

   
    def get_commit_heatmap(self):
        """
        Returns a dictionary containing the number of commits per day of the week
        for the given author name, taking into account the author's time zone.
        """
        # Convert the 'time' column to datetime
        self.df['time'] = pd.to_datetime(self.df['time'], unit='s')

        # Apply the time zone to the 'time' column
        #self.df['time'] = self.df.apply(lambda row: row['time'].tz_localize('UTC').tz_convert(f"Etc/GMT{int(row['taz'][:3])}"), axis=1)

        # Convert the 'time' column to 'UTC' timezone
        #self.df['time'] = self.df['time'].apply(lambda x: x.tz_convert('UTC'))

        # Convert the timezone-aware Timestamps to timezone-naive
        #self.df['time'] = self.df['time'].apply(lambda x: x.tz_localize(None))

        #self.df['time'] = self.df['time'].astype('datetime64[ns]')

        # Extract the day of the week from the 'time' column (Monday is 0, Sunday is 6)
        self.df['day_of_week'] = self.df['time'].dt.dayofweek

        # Group by 'day_of_week' and count the number of commits
        df_commit_heatmap = self.df.groupby('day_of_week').size().reset_index(name='count')

        # Map the day of the week number to actual day name
        day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        df_commit_heatmap['day_of_week'] = df_commit_heatmap['day_of_week'].map(day_map)
            
        # Convert the DataFrame to a dictionary
        commit_heatmap = df_commit_heatmap.set_index('day_of_week')['count'].to_dict()

        print(commit_heatmap)           
        return commit_heatmap

    
    def filter_dataframe(self, date_range=None, projects=None):
        df = self.df.copy()
        if date_range:
            start_date, end_date = date_range
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]

        if projects is not None:
            df = df[df['project'].isin(projects)]

        print(df.head())
        return df
