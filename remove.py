import pandas as pd

# Read the CSV file
df = pd.read_csv('min1_prof/Nifty 50_agg.csv')
df1 = pd.read_csv('min1_prof/Nifty Bank_agg.csv')

# Filter out rows with net_profit less than 100
filtered_df = df[df['net_profit'] >= 250]
fil_df1 = df1[df1['net_profit'] >= 250]

# Sort the DataFrame by net_profit in descending order
sorted_df = filtered_df.sort_values(by='net_profit', ascending=False)
sorted_1 = fil_df1.sort_values(by='net_profit', ascending=False)
# Save the sorted and filtered data to a new CSV file
sorted_1.to_csv('min1_prof/bank_nifty_top.csv', index=False)
sorted_df.to_csv('min1_prof/Nifty_top50_agg.csv', index=False)