#%%[markdown]
import numpy as np
import pandas as pd
import os
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns


# %%
data = pd.read_csv("restaurant-1-orders.csv",  parse_dates=['Order Date'])

#%%
#I should say that I changed this part from mean to sum
data.isna().sum()
# %%
data.shape
data.info()
data.describe()
# %%
data["Total Price"] = data["Product Price"] * data["Quantity"]
data
# %%
item_freq = data.groupby('Item Name').agg({'Quantity': 'sum'})
item_freq = item_freq.sort_values(by=['Quantity'])
top_20 = item_freq.tail(20)
top_20.plot(kind="barh", figsize=(16,8))
plt.title('Top 20 sold items')
# %%
print('Number of unique item name: ', len(data['Item Name'].unique()))

# %%
item_freq = data.groupby('Item Name').agg({'Quantity': 'sum'})
item_freq = item_freq.sort_values(by=['Quantity'])
top_20 = item_freq.head(20)
top_20.plot(kind="barh", figsize=(16,8))
plt.title('Least 20 sold items')
# %%
data1 = data ["Total Price"].mean()
print(data1)

#%%
#I think we should delete this line coz we don't have na according to the previous code
data = data.dropna()
data = data.loc[data['Order Date'] >='2016-08-01']
# %%
#Investigating average order volume by periods
print("Daily:\n", data.groupby([pd.Grouper(key='Order Date', freq='D')])['Quantity'].sum().mean())
print("Weekly:\n", data.groupby([pd.Grouper(key='Order Date', freq='W-MON')])['Quantity'].sum().mean())
print("Monthly:\n", data.groupby([pd.Grouper(key='Order Date', freq='M')])['Quantity'].sum().mean())

# %%
#create relevant Database df1 for total and df2 for bombay aloo

### I am not sure what this part is ###
df = data[['Order Date', 'Quantity']]
df2 = data[data['Item Name'] == 'Bombay Aloo']
df2 = df2[['Order Date', 'Quantity']]
df = df.groupby([pd.Grouper(key='Order Date', freq='W-MON')])['Quantity'].sum().reset_index().sort_values('Order Date')
df2 = df2.groupby([pd.Grouper(key='Order Date', freq='W-MON')])['Quantity'].sum().reset_index().sort_values('Order Date')
#Add Seasonality features
df['Week'] = df['Order Date'].dt.isocalendar().week
df['Month'] = df['Order Date'].dt.month
df2['Week'] = df2['Order Date'].dt.isocalendar().week
df2['Month'] = df2['Order Date'].dt.month
#Add past volume features
for i in range (1,15):
    label = "Quantity_" + str(i)
    df[label] = df['Quantity'].shift(i)
    df2[label] = df2['Quantity'].shift(i)
    label = "Average_" + str(i)
    df[label] = df['Quantity'].rolling(i).mean()
    df2[label] = df2['Quantity'].rolling(i).mean()
df = df.dropna()
df2 = df2.dropna()
print(df)
#%%
print(df2)
# %%
## Orders by time of day
# We are going to calculate the average number of orders that are placed in each hour 
# of the day to give us an idea of ​​when the demand is greatest.
data['hour'] = data['Order Date'].dt.hour # Add column with the time of the order
data.sample(5)
#%%
data['date'] = data['Order Date'].dt.strftime('%y/%m/%d') # Add column with date
data.sample(5)

# The way we will calculate the average orders per hour is as follows:
#For a specified hour, we will calculate the number of orders that were taken at that hour considering 
# the average per day.
#%%
def avg_hour(hour):
    by_hour = data[data['hour'] == hour]
    avg = len(by_hour['Order Number'].unique()) / len(data['date'].unique())
    return avg

hours = pd.DataFrame(sorted(data['hour'].unique()))
hours.rename(columns={0:'hour'}, inplace=True)
hours['Average orders'] = hours['hour'].apply(avg_hour) 
hours.set_index('hour', inplace=True)
hours.head()
#%%
hours.plot.bar(figsize=(11,6), rot=0)
plt.xlabel('Hour')
plt.title('Average number of orders by hour of the day')
# As can be seen, the hours at which the greatest number of orders are made on average 
# are 5, 6, and 7:00 p.m., with a peak at 6:00 p.m.
#%%
## Orders by day of the week
# We are going to do the same analysis as before but this time considering the 
# different days of the week.
data['day'] = data['Order Date'].dt.day_name() # Column with the name of the day
data.sample(5)
#%%
def by_day(day):
    data_day = data[data['day'] == day]
    avg = len(data_day['Order Number'].unique()) / len(data_day['date'].unique())
    return(avg)

days = pd.DataFrame(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
days.rename(columns={0: 'day'}, inplace=True)
days['avg_orders'] = days['day'].apply(by_day)
days

# %%
plt.bar(days['day'], days['avg_orders'])
plt.xlabel('Day of week')
plt.ylabel('Average number of orders')
plt.title('Average orders by day of week')
plt.xticks(rotation=90)
# The graph shows that the day with the highest average number of orders is Saturday. 
# Interestingly, more averages are performed on Friday than on Sundays.

#%%
#We will visualize sales over time considering monthly time periods
print('First Sale: ', data['Order Date'].min())
print('Last Sale: ', data['Order Date'].max())
# %%
#We will then consider the dates between January 2016 and December 2019.
import datetime

months = []

for year in range(2016, 2020):
    for month in range(1, 13):
        d = datetime.date(year, month, 1)
        months.append(d)

monthly = pd.DataFrame(months)
monthly.rename(columns={0: 'month'}, inplace=True)
monthly.head()

#Now we will assign each month its total sales.

# %%
def sales_month(date):
    year_month = date.strftime('%y/%m')
    data1 = data[data['date'].str[:5] == year_month].copy()
    total = (data1['Quantity'] * data1['Product Price']).sum()
    return(total)

monthly['total'] = monthly['month'].apply(sales_month)
monthly.head()
# %%
#################### can we have the dates 90 degree ###
plt.plot(monthly['month'], monthly['total'])
plt.xlabel('Date')
plt.ylabel('Total sales (USD)')
plt.title('Total monthly sales')
# You can see that monthly sales had been growing up to a point in the middle of 
# 2019, where they suffered a big drop. Let's identify this point.
# %%
monthly[monthly['month'] >= datetime.date(2019, 1, 1)]
#The month in which sales fell was August 2019.
# %%
## Order price distribution
###################### I belive we should werk in this 

# We are going to visualize the distribution of the cost of the orders to the restaurant.
order_total = data[['Order Number', 'Quantity', 'Product Price']].copy()

############ I belive we to answer the question of average restaurant prices we should not do math? ###
order_total['total'] = order_total['Quantity'] * order_total['Product Price']


############# very intereting!! Can we invistigate the very high prices?!
# Add the order price
order_totals = order_total.groupby('Order Number').agg({'total': 'sum'})
plt.boxplot(order_totals['total'])
plt.title('Order price distribution')


#%%
p_95 = order_totals['total'].describe(percentiles=[0.95])['95%']
print('95% of the orders are less than or equal to {percentile} USD'.format(percentile=p_95))
# 95% of the orders are less than or equal to 62.2 USD
# Let's consider the distribution for the total price of orders less than 63 USD.

#%%
plt.boxplot(order_totals[order_totals['total'] < 63]['total'])
plt.title('Order total USD')
plt.ylabel('USD')

#%%
sns.distplot(order_totals[order_totals['total'] < 63], bins=20)
plt.title('Order price distribution')

#%%

# restaurant prices and restaurant quantity of each item
item_freq2 = data.groupby('Item Name').agg({'Quantity': 'sum', 'Product Price':'mean'})
item_freq2.mean()
item_freq2.max()
item_freq2.min()

# plot
sns.scatterplot(item_freq2, x= 'Product Price', y='Quantity')
plt.title('Item price VS item quantity')
plt.show()

# delete outliers of quantity and price
items = item_freq2[(item_freq2['Product Price'] <= 14.) & (item_freq2['Quantity'] <= 7000.)]

sns.scatterplot(items, x= 'Product Price', y='Quantity')
plt.title('Item price VS item quantity')
plt.show()

# is theer carrolation between the product price and number of total orders of each item?
#  Pearson correlation coefficient 
from scipy.stats import pearsonr
corr, _ = pearsonr(items['Product Price'], items['Quantity'])
print('Pearsons correlation: %.3f' % corr)
print('''The two varibles have low carrolation of .4 that means people decition of bying an item is not heavely based on the price.
      However, the test shows a negative result therefore we could say that the generally when the price of an item goes up, probably
      the number of orders will go down''')

# Another test for no-liner relationship or not Normal Distribution varibles
# Spearman correlation coefficient
from scipy.stats import spearmanr
corr, _ = spearmanr(items['Product Price'], items['Quantity'])
print('Spearmans correlation: %.3f' % corr)
print('There is .5 carrolation between the two samples however, it is not strong and we stick with our previous clime')