import os
# from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import refracted_advance as refracted
import cProfile
import pstats
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi

# def trading_view():
#     tv = TvDatafeed(username='arnavgoyal63774', password='fAC@6kjug8tgqM-')
#     tv = TvDatafeed()

#     ret = tv.get_hist(symbol='BANKNIFTY',exchange='NSE',interval=Interval.in_1_minute,n_bars=20000)                                          
#     current_directory = os.getcwd()
#     df_comb_file = os.path.join(current_directory, 'bank_nifty_full1.csv')
#     ret.to_csv(df_comb_file, index=True)

ohlc=['into', 'inth', 'intl', 'intc']
     
file_path = 'excel_files/nifty_full.xlsx'
ret = pd.read_excel(file_path)
ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
for col in ohlc:
    ret[col] = ret[col].astype(float) 


base_directory = os.getcwd()  


def calculate_indicators(df, hyperparamas):
    
    (lookback_config, ema_length_config, conv_config, 
    length_config, lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    signal_config) = hyperparamas
    
    df = df.copy()
    
    df = velocity_indicator.calculate_float(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index2_float(df,conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA = lengthMA_config, lengthSignal = lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast = fast_config, slow = slow_config, signal = signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df
    

def main():
    

    # trading_view()
    
    with cProfile.Profile() as pr:
        
        trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit']
        trade_data = pd.DataFrame(columns=trade_columns)
        
        # hyper_params = [10.02,14.72,48.73,27,33.43,9,14.87,31.35,15.1]
        # parse = [2.87,2.12]
        hyper_params = [17,14,57,28,27,8,12,23,11]
        parse = [15,6]
        df = calculate_indicators(ret, hyper_params)
        temp = df.iloc[:200].copy()
        df = df[200:]
                                                       
        for i in range(0, len(df)):
            trade_data = refracted.final(temp, trade_data, parse)        
            
            if (i%150 == 0):
                print(f'"working fine {i}"')
                print(temp["time"].iloc[-1])
                    
            next_row = df.iloc[[i]]
            temp = pd.concat([temp, next_row], ignore_index=True)
            temp = temp.tail(110)
    
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats("profile1.prof")
    
    df_comb_file = os.path.join(base_directory, 'trade_data_new_test1.csv')
    trade_data.to_csv(df_comb_file, index=True)


                                                                                                                 
if __name__ == "__main__":
    main()
    