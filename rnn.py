import pandas as pd
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense
import seaborn as sns
from sklearn.metrics import confusion_matrix


ret = pd.read_excel('excel_files/nifty_full.xlsx')
df = pd.read_csv('trade_data_new_test.csv')



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
    global ret
    
    hyper_params = [10.02,14.72,48.73,27,33.43,9,14.87,31.35,15.1]
    ret = calculate_indicators(ret, hyper_params)
    
    ret['trade'] = 0
    ret['result'] = 0
    
    ret['time'] = pd.to_datetime(ret['time'])
    df['entry_time'] = pd.to_datetime(df['entry_time'])

    ret['trade'] = 0
    ret['result'] = 0

    for index, row in df.iterrows():
        entry_time = row['entry_time']
        profit = row['profit']
        
        match_index = ret[ret['time'] == entry_time].index
        
        if not match_index.empty:
            ret.at[match_index[0], 'trade'] = 1
            ret.at[match_index[0], 'result'] = 1 if profit > 0 else 0

    ret_dropped = ret.iloc[75:].reset_index(drop=True)
    ret_dropped['trade'] = ret_dropped['trade'].shift(-1)
    ret_dropped['result'] = ret_dropped['result'].shift(-1)
    ret_dropped = ret_dropped.iloc[:-1].reset_index(drop=True)
    # ret_dropped = ret_dropped.reset_index(drop=True)
    
    ret_dropped.drop(columns=['time'], inplace=True)
    
    df_y = ret_dropped[['trade', 'result']]
    df_x = ret_dropped.drop(columns=['trade', 'result'])
    
    x_train, x_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.2, random_state=0)
    
    print(x_train)
    
    sc = StandardScaler()

    x_train.reset_index(inplace=True, drop=True)

    x_train = sc.fit_transform(x_train)

    x_test = sc.transform(x_test)
    
    classifier = Sequential()

    classifier.add(Dense(units=11, kernel_initializer='uniform', activation='relu', input_dim=12))

    classifier.add(Dense(units=28, kernel_initializer='uniform', activation='relu'))

    classifier.add(Dense(units=2, kernel_initializer='uniform', activation='sigmoid'))

    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    classifier.fit(x_train, y_train, batch_size=29, epochs=191)
    
    from sklearn import metrics

    cutoff_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

    accuracy = []

    for cutoff in cutoff_values:
        y_pred = (classifier.predict(x_test) > cutoff)
        accuracy.append(metrics.accuracy_score(y_test, y_pred))

    print(accuracy)
    
    max_accuracy = max(accuracy)
    max_index = accuracy.index(max_accuracy)
    
    y_pred = classifier.predict(x_test)


    y_pred = (y_pred > max_index * 0.05)

    y_pred_trade = y_pred[:, 0]
    y_pred_result = y_pred[:, 1]

    y_test_trade = y_test.iloc[:, 0]
    y_test_result = y_test.iloc[:, 1]

    print("Accuracy for trade:", metrics.accuracy_score(y_test_trade, y_pred_trade))
    print("Accuracy for result:", metrics.accuracy_score(y_test_result, y_pred_result))

    cm_trade = confusion_matrix(y_test_trade, y_pred_trade)
    cm_result = confusion_matrix(y_test_result, y_pred_result)

    plt.figure(figsize=(10, 7))
    sns.heatmap(cm_trade, annot=True, fmt='d', cmap='Blues', xticklabels=['Class 0', 'Class 1'], yticklabels=['Class 0', 'Class 1'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix for Trade')
    plt.show()

    plt.figure(figsize=(10, 7))
    sns.heatmap(cm_result, annot=True, fmt='d', cmap='Blues', xticklabels=['Class 0', 'Class 1'], yticklabels=['Class 0', 'Class 1'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix for Result')
    plt.show()
    

if __name__ == "__main__":
    main()