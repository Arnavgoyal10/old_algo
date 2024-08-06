import os
import pandas as pd
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi

# def stage1():
    
#     folder_path = 'data'

#     csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    
#     combined_df = pd.DataFrame()

#     for file in csv_files:
#         file_path = os.path.join(folder_path, file)
#         df = pd.read_csv(file_path)
#         combined_df = pd.concat([combined_df, df])

#     combined_df["entry_time"] = pd.to_datetime(combined_df["entry_time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)

#     combined_df = combined_df.sort_values(by='entry_time')

#     combined_df.to_csv('combined_model_data.csv', index=False)

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
    
    ret = pd.read_csv('lstm/testing_data.csv')
    data = pd.read_csv('data_5min/Nifty 50.csv')
    # ret = ret.dropna(subset=['no_trade']) 
    # ret = ret.reset_index(drop=True)
    # ret.to_csv('combined_model_data.csv', index=False)
    
    # Convert columns to datetime
    ret['time'] = pd.to_datetime(ret['time'], format="%Y-%m-%d %H:%M:%S")
    data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%d %H:%M:%S")

    for i in range(len(ret)):
        entry_time = ret['time'][i]

        temp = data.index[data['time'] == entry_time].tolist()
        if not temp:
            continue
        temp = temp[0]

        if temp < 120:
            temp_data = data.iloc[:temp + 1]
        else:
            temp_data = data.iloc[(temp - 120):temp + 1]

        temp_data = temp_data.reset_index(drop=True)
        params = ret.iloc[i, 3:].to_list()
        temp_data = calculate_indicators(temp_data, params)

        temp_data = temp_data.tail(18).reset_index(drop=True)
        temp_data = temp_data.drop(columns=['Unnamed: 0'])
        temp_data.to_csv(f'long_data/ret_{i}.csv', index=False)
        print(f"File {i} done")
                
        

    
if __name__ == "__main__":
    main()
