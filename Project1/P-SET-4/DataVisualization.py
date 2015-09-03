
# coding: utf-8
#    PROBLEM SET4 - 1
# In[ ]:

from pandas import *
from ggplot import *

def plot_weather_data(turnstile_weather):
    '''
    You are passed in a dataframe called turnstile_weather. 
    Use turnstile_weather along with ggplot to make a data visualization
    focused on the MTA and weather data we used in assignment #3.  
    You should feel free to implement something that we discussed in class 
    (e.g., scatterplots, line plots, or histograms) or attempt to implement
    something more advanced if you'd like.  

    Here are some suggestions for things to investigate and illustrate:
     * Ridership by time of day or day of week
     * How ridership varies based on Subway station (UNIT)
     * Which stations have more exits or entries at different times of day
       (You can use UNIT as a proxy for subway station.)

    If you'd like to learn more about ggplot and its capabilities, take
    a look at the documentation at:
    https://pypi.python.org/pypi/ggplot/
     
    You can check out:
    https://www.dropbox.com/s/meyki2wl9xfa7yk/turnstile_data_master_with_weather.csv
     
    To see all the columns and data points included in the turnstile_weather 
    dataframe. 
     
    However, due to the limitation of our Amazon EC2 server, we are giving you a random
    subset, about 1/3 of the actual data in the turnstile_weather dataframe.
    '''

    plot = ggplot(turnstile_weather, aes("Hour","ENTRIESn_hourly", color = 'UNIT')) + geom_point() +geom_line()
    return plot

#    PROBLEM SET4 - 2
# In[ ]:


def plot_weather_data(turnstile_weather):
    ''' 
    plot_weather_data is passed a dataframe called turnstile_weather. 
    Use turnstile_weather along with ggplot to make another data visualization
    focused on the MTA and weather data we used in Project 3.
    
    Make a type of visualization different than what you did in the previous exercise.
    Try to use the data in a different way (e.g., if you made a lineplot concerning 
    ridership and time of day in exercise #1, maybe look at weather and try to make a 
    histogram in this exercise). Or try to use multiple encodings in your graph if 
    you didn't in the previous exercise.
    
    You should feel free to implement something that we discussed in class 
    (e.g., scatterplots, line plots, or histograms) or attempt to implement
    something more advanced if you'd like.

    Here are some suggestions for things to investigate and illustrate:
     * Ridership by time-of-day or day-of-week
     * How ridership varies by subway station (UNIT)
     * Which stations have more exits or entries at different times of day
       (You can use UNIT as a proxy for subway station.)

    If you'd like to learn more about ggplot and its capabilities, take
    a look at the documentation at:
    https://pypi.python.org/pypi/ggplot/
     
    You can check out the link 
    https://www.dropbox.com/s/meyki2wl9xfa7yk/turnstile_data_master_with_weather.csv
    to see all the columns and data points included in the turnstile_weather 
    dataframe.
     
   However, due to the limitation of our Amazon EC2 server, we are giving you a random
    subset, about 1/3 of the actual data in the turnstile_weather dataframe.
    '''

    plot = ggplot(turnstile_weather, aes('UNIT', fill='rain'))+ geom_bar(binwidth=50)+           ggtitle("Ridership based on weather-Rain (Blue) / No Rain (Red)") +xlab("Stations") + ylab("Entries")
    return plot

	def plot_weather_data_mean_day_of_week(turnstile_weather):
    turnstile_weather = turnstile_weather[(turnstile_weather.rain == 1)]
    grouped_dataframe = turnstile_weather[['day_week','ENTRIESn_hourly']]
    grouped_dataframe = grouped_dataframe.groupby('day_week',as_index=False).mean()
    plot = ggplot(grouped_dataframe, aes(x='day_week', y='Mean ENTRIESn_hourly')) + \
            geom_bar(aes(x='day_week',weight='ENTRIESn_hourly'), fill='blue', stat="bar")+ \
            scale_x_continuous(name='Weekday',
                           breaks=[0, 1, 2, 3, 4, 5, 6],
                           labels=['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                                   'Thursday', 'Friday', 'Saturday'])+ \
            ggtitle('Average ENTRIESn_hourly by Weekday') + \
            xlab('Day of Week') + ylab('Mean Entries Hourly')
    
    return plot
	
def plot_weather_data_total_day_of_week(turnstile_weather):
    turnstile_weather = turnstile_weather[(turnstile_weather.rain == 1)]
    grouped_dataframe = turnstile_weather[['day_week','ENTRIESn_hourly']]
    grouped_dataframe = grouped_dataframe.groupby('day_week',as_index=False).sum()
    plot = ggplot(grouped_dataframe, aes(x='day_week', y='Mean ENTRIESn_hourly')) + \
            geom_bar(aes(x='day_week',weight='ENTRIESn_hourly'), fill='blue', stat="bar")+ \
            scale_x_continuous(name='Weekday',
                           breaks=[0, 1, 2, 3, 4, 5, 6],
                           labels=['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                                   'Thursday', 'Friday', 'Saturday'])+ \
            ggtitle('Average ENTRIESn_hourly by Weekday') + \
            xlab('Day of Week') + ylab('Mean Entries Hourly')
    
    return plot
