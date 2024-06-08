import os
import pandas as pd
import refracted_advance as refracted
import cProfile
import pstats
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi


ohlc=['into', 'inth', 'intl', 'intc']
     
file_path = 'excel_files/nifty_full_feb.xlsx'
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
    
    with cProfile.Profile() as pr:
        
        trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'agg_profit']
        trade_data = pd.DataFrame(columns=trade_columns)
        
        hyper_params = [16.041917247297274,15.320523103841708,41.04780663473374,18.482562040866295,31.478961215172188,9.382782998485993,12.711221098798884,18.64550035252773,14.408691653758103]
        parse  = [3.055179731108132,5.632012105972655]
        
        df = calculate_indicators(ret, hyper_params)
        temp = df.iloc[:200].copy()
        df = df[200:]
                                                       
        for i in range(0, len(df)):
            trade_data = refracted.final(temp, trade_data, parse)
            
            if len(trade_data) > 3 and (trade_data['profit'].tail(3) < 0).all():
                if trade_data['profit'].tail(3).sum() < -40:
                    break
            
            if (i%150 == 0):
                print(f'"working fine {i}"')
                print(temp["time"].iloc[-1])
                    
            next_row = df.iloc[[i]]
            temp = pd.concat([temp, next_row], ignore_index=True)
            temp = temp.tail(110)
    
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats("snakeviz/main.prof")
    
    df_comb_file = os.path.join(base_directory, 'trade_data_new_test2.csv')
    trade_data.to_csv(df_comb_file, index=True)


                                                                                                                 
if __name__ == "__main__":
    main()
    