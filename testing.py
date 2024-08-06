import pandas as pd

def main():
    print("starting")
    # ret1 = pd.read_csv(f'July/Nifty 50.csv')
    # ret2 = pd.read_csv('min5_prof/after/Nifty 50_after.csv')
    # df = pd.DataFrame()
    # for i in range(len(ret1)):
    #     for j in range(len(ret2)):
    #         df_temp = pd.concat([ret1['time'].iloc[i:i+1].reset_index(drop=True), ret2.iloc[j:j+1].reset_index(drop=True)], axis=1)
    #         df = pd.concat([df, df_temp], ignore_index=True)
            
    # df.to_csv('July/testing_data.csv', index=False)
    df = pd.read_csv('lstm/testing_data.csv')
    print(df)

    
if __name__ == '__main__':
    main()