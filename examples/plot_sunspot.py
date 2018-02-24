"""
Importing Sunspot Data
======================

This example aims to demonstrate how can the data be imported and plotted.
"""


import heliopy.data.sunspot as sunspot
import matplotlib.pyplot as plt

# Plotting Daily
data_daily = sunspot.daily()
print(data_daily.keys())
# You will get the keys,
# Let's assume we wish to plot the following,
# On x-axis, we plot Decimal Date, and on y-axis, we plot Daily Observations
x_daily = data_daily['DecD']
y_daily = data_daily['Daily']
plt.plot(x_daily, y_daily)
plt.show()  # Display the plot!

# Plotting Monthly
data_monthly = sunspot.monthly()
print(data_monthly.keys())
# You will get the keys,
# Let's assume we wish to plot the following,
# On x-axis, we plot Decimal Date, and on y-axis, we plot Monthly Observations
x_monthly = data_monthly['DecD']
y_monthly = data_monthly['Monthly']
plt.plot(x_monthly, y_monthly)
plt.show()  # Display the plot!

# Plotting Yearly
data_yearly = sunspot.yearly()
print(data_yearly.keys())
# You will get the keys,
# Let's assume we wish to plot the following,
# On x-axis, we plot Year, and on y-axis, we plot Yearly Mean
x_yearly = data_yearly['Y']
y_yearly = data_yearly['Y_Mean']
plt.plot(x_yearly, y_yearly)
plt.show()  # Display the plot!
