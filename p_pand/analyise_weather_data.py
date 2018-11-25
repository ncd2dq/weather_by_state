import pandas as pd 
import matplotlib.pyplot as plt 
from get_weather_data import get_df

df = get_df()

#
# Plot 1
# Precipitation by month of a given state
#
state = 'alabama'
state_df = df.loc[state]

# Deep means data is copied, not just references to data
new_df = state_df.copy(deep=True)

# Default is not in place
# Reset the index so you can use one of the indexes just as a standard column
# Really difficult to use an index as the x values in plotting without doing this 
# work around
new_df = new_df.reset_index()

# For multiple lines, just call .plot more than once
plt.plot(new_df.Month, new_df.Precipitation)
plt.plot(new_df.Month, new_df.Precipitation * 2)
plt.show()

# Simple bar chart
plt.bar(new_df.Month, new_df.Precipitation)
plt.show()