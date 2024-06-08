# from tvDatafeed import TvDatafeed, Interval
# import os
# import pandas as pd
# import time

# def trading_view(symbol):
#     tv = TvDatafeed()
#     ret = tv.get_hist(symbol=symbol, exchange='NSE', interval=Interval.in_5_minute, n_bars=40000)
#     current_directory = os.getcwd()
#     df_comb_file = os.path.join(current_directory, f'past/{symbol}.csv')
#     ret.to_csv(df_comb_file, index=True)

# def main():

#     file_path = 'combined_df.csv'
#     combined_df = pd.read_csv(file_path)

#     # Read the last processed symbol from a log file, if it exists
#     log_file = 'progress_log.txt'
#     start_from = 0

#     if os.path.exists(log_file):
#         with open(log_file, 'r') as f:
#             last_symbol = f.readline().strip()
#             if last_symbol in combined_df['Symbol'].values:
#                 start_from = combined_df.index[combined_df['Symbol'] == last_symbol].tolist()[0] + 1

#     error_symbols = []

#     for i in range(start_from, len(combined_df)):
#         symbol = combined_df['Symbol'][i]
#         try:
#             time.sleep(2)
#             trading_view(symbol)
#             print(f"Done with {symbol}")
#             # Log progress
#             with open(log_file, 'w') as f:
#                 f.write(symbol)
#         except Exception as e:
#             print(f"Error processing {symbol}: {e}")
#             print("Retrying in 10 seconds...")
#             error_symbols.append(symbol)
#             time.sleep(10)
#             # Restart the loop from the same symbol
#             continue

#     # Write error symbols to a file
#     with open('error_symbols.txt', 'w') as error_file:
#         for error_symbol in error_symbols:
#             error_file.write(f"{error_symbol}\n")

# if __name__ == "__main__":
#     main()
