import datetime
import pandas as pd
import files_interact
import supertrend
import impulsemacd
import tsi
import threading
import os
import argparse
import hhll_indicator
import velocity_indicator
import hull_ma
import okx
import squeeze
import ranged
import okxfinal
import obv
import okxfinal
import okx
import strategy

# from tvDatafeed import TvDatafeed, Interval

# tv = TvDatafeed()

ohlc=['into', 'inth', 'intl', 'intc']
     

def main():
    # ret = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_5_minute,n_bars=3000)
    
    file_path = 'Book1.xlsx'
    ret = pd.read_excel(file_path)
    ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    for col in ohlc:
        ret[col] = ret[col].astype(float) 
         
    temp = pd.DataFrame()
    temp = ret.iloc[:80].copy()
    data_columns = ['time','reason', 'bull or bear']
    trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit']
    entry_frame_data = pd.DataFrame(columns=data_columns)
    trade_data = pd.DataFrame(columns=trade_columns)
    ret = ret[80:]
    

    for i in range(0, len(ret)):        
        
        entry_frame_data, trade_data = strategy.final(temp, entry_frame_data, trade_data)
            
        if (i%50 == 0):
            print("working fine")
            print(temp["time"].iloc[-1])
        next_row = ret.iloc[[i]]
        temp = pd.concat([temp, next_row], ignore_index=True)
    
    
    current_directory = os.getcwd()
    df_comb_file = os.path.join(current_directory, 'entries1.csv')
    entry_frame_data.to_csv(df_comb_file, index=True)
    trade_data1 = os.path.join(current_directory, 'trade_data1.csv')
    trade_data.to_csv(trade_data1, index=True)
    
if __name__ == "__main__":
    main()
    