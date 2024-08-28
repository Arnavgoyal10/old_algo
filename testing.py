import pandas as pd
import os


def main():
    print("starting")
    # # ret1 = pd.read_csv(f'July/Nifty 50.csv')
    # # ret2 = pd.read_csv('min5_prof/after/Nifty 50_after.csv')
    # # df = pd.DataFrame()
    # # for i in range(len(ret1)):
    # #     for j in range(len(ret2)):
    # #         df_temp = pd.concat([ret1['time'].iloc[i:i+1].reset_index(drop=True), ret2.iloc[j:j+1].reset_index(drop=True)], axis=1)
    # #         df = pd.concat([df, df_temp], ignore_index=True)

    # # df.to_csv('July/testing_data.csv', index=False)
    # df = pd.read_csv('lstm/testing_data.csv')
    # print(df)

    folders = "filter"
    required_columns = [
        "stoploss",
        "squee",
        "lookback",
        "ema_length",
        "conv",
        "length",
        "lengthMA",
        "lengthSignal",
        "fast",
        "slow",
        "signal",
        "net_profit",
    ]

    for folder in os.listdir(folders):
        if folder == "all":
            continue
        folder_path = os.path.join(folders, folder)
        if os.path.isdir(folder_path):
            final = pd.DataFrame()
            for file in os.listdir(folder_path):
                if file.endswith(".csv"):
                    df = pd.read_csv(os.path.join(folder_path, file))

                    if list(df.columns) == required_columns:
                        final = pd.concat([final, df], ignore_index=True)

            if not final.empty:
                # final.to_csv(f"{folders}/{folder}_all.csv", index=False)
                # only keep rows which have net_profit > 250
                final = final[final["net_profit"] > 250]
                # sort in ascending order of net_profit
                final = final.sort_values(by="net_profit", ascending=False)
                final.to_csv(f"{folders}/all/{folder}_all.csv", index=False)
                print(final.shape)


if __name__ == "__main__":
    main()
