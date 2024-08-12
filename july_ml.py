import pandas as pd
import refracted_m as refracted
import threading

lock = threading.Lock()


def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame(
            [
                {
                    col: (value if col == column_name else None)
                    for col in dataframe.columns
                }
            ]
        )
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe


def main():
    ret = pd.read_csv("July/Nifty 50.csv")
    decision = pd.read_csv("testing_data_final2.csv")
    ret = ret[18:]
    states = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    trade_columns = [
        "entry_time",
        "entry_price",
        "exit_time",
        "exit_price",
        "profit",
        "agg_profit",
        "percent",
    ]
    trade_data = pd.DataFrame(columns=trade_columns)

    temp2 = decision.head(5).copy()
    df_decision = decision.iloc[5:].reset_index(drop=True)

    temp = ret.head(5).copy()
    ret = ret.iloc[5:].reset_index(drop=True)

    for j in range(0, len(df_decision)):
        with lock:
            trade_data, states = refracted.final(
                temp, trade_data, df_decision["stop_loss"].iloc[j], states, temp2
            )

        next_row = df_decision.iloc[[j]]
        temp2 = pd.concat([temp2, next_row.dropna(how="all")], ignore_index=True)
        temp2 = temp2.tail(5)

        next_row = ret.iloc[[j]]
        temp = pd.concat([temp, next_row.dropna(how="all")], ignore_index=True)
        temp = temp.tail(5)

    trade_data.to_csv("trade_data.csv", index=False)


if __name__ == "__main__":
    main()
