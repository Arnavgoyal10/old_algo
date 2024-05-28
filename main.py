import os
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import refracted

def trading_view():
    tv = TvDatafeed(username='arnavgoyal63774', password='fAC@6kjug8tgqM-')
    tv = TvDatafeed()

    ret = tv.get_hist(symbol='BANKNIFTY',exchange='NSE',interval=Interval.in_1_minute,n_bars=20000)                                          
    current_directory = os.getcwd()
    df_comb_file = os.path.join(current_directory, 'bank_nifty_full1.csv')
    ret.to_csv(df_comb_file, index=True)



ohlc=['into', 'inth', 'intl', 'intc']
     
file_path = 'nifty_full.xlsx'
ret = pd.read_excel(file_path)
ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
for col in ohlc:
    ret[col] = ret[col].astype(float) 


base_directory = os.getcwd()  


def main():
    # trading_view()
    
    global ret

    trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit']
    trade_data = pd.DataFrame(columns=trade_columns)
    
    hyper_params = [10,6,16,16,44,24,30,9,16,20,10]
    temp = pd.DataFrame()
    temp = ret.iloc[:200].copy()
    ret = ret[200:]
                                                       
    for i in range(0, len(ret)):
                                                            
        trade_data = refracted.final(temp, trade_data, hyper_params)        
        
        if (i%150 == 0):
            print(f'"working fine {i}"')
            print(temp["time"].iloc[-1])
                
        next_row = ret.iloc[[i]]
        temp = pd.concat([temp, next_row], ignore_index=True)
        temp = temp.iloc[-110:].reset_index(drop=True)
    
    df_comb_file = os.path.join(base_directory, 'trade_data_new.csv')
    trade_data.to_csv(df_comb_file, index=True)


                                                                                                                 
if __name__ == "__main__":
    main()
    