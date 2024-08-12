import os
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import threading
import pandas as pd
import refracted_advance as refracted
import warnings

warnings.simplefilter("ignore")

ohlc = ["into", "inth", "intl", "intc"]

lock = threading.Lock()


def calculate_indicators(df, hyperparamas):

    (
        lookback_config,
        ema_length_config,
        conv_config,
        length_config,
        lengthMA_config,
        lengthSignal_config,
        fast_config,
        slow_config,
        signal_config,
    ) = hyperparamas

    df = df.copy()

    df = velocity_indicator.calculate_float(
        df, lookback=lookback_config, ema_length=ema_length_config
    )
    df = squeeze.squeeze_index2_float(df, conv=conv_config, length=length_config)

    df_macd = impulsemacd.macd(
        df, lengthMA=lengthMA_config, lengthSignal=lengthSignal_config
    )
    df[["ImpulseMACD", "ImpulseMACDCDSignal"]] = df_macd[
        ["ImpulseMACD", "ImpulseMACDCDSignal"]
    ]

    df_tsi = tsi.tsi(df, fast=fast_config, slow=slow_config, signal=signal_config)
    df[["TSI", "TSIs"]] = df_tsi[["TSI", "TSIs"]]

    return df


# ret = pd.read_csv("min5_prof/after/Nifty 50_after.csv")
# ret1 = pd.read_csv("data_5min/Nifty 50.csv")

# os.makedirs("data", exist_ok=True)


def main():
    # ret1["time"] = pd.to_datetime(
    #     ret1["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False
    # )
    # for col in ohlc:
    #     ret1[col] = ret1[col].astype(float)

    # for i in range(len(ret)):
    #     trade_columns = [
    #         "entry_time",
    #         "entry_price",
    #         "exit_time",
    #         "exit_price",
    #         "profit",
    #         "agg_profit",
    #         "no_trade",
    #         "buy",
    #         "sell",
    #     ]
    #     trade_data = pd.DataFrame(columns=trade_columns)
    #     states = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    #     list1 = ret.iloc[i].to_list()
    #     configs = list1[:2]
    #     params = list1[2:-2]

    #     df = calculate_indicators(ret1.copy(), params).copy()
    #     temp = df.head(5)
    #     df = df.iloc[5:].reset_index(drop=True)

    #     for j in range(len(df)):
    #         trade_data, states = refracted.final(temp, trade_data, configs, states)

    #         next_row = df.iloc[[j]]
    #         temp = pd.concat([temp, next_row], ignore_index=True)
    #         temp = temp.tail(5)

    #     trade_data["stoploss"] = configs[0]
    #     trade_data["squee"] = configs[1]
    #     trade_data["lookback"] = params[0]
    #     trade_data["ema_length"] = params[1]
    #     trade_data["conv"] = params[2]
    #     trade_data["length"] = params[3]
    #     trade_data["lengthMA"] = params[4]
    #     trade_data["lengthSignal"] = params[5]
    #     trade_data["fast"] = params[6]
    #     trade_data["slow"] = params[7]
    #     trade_data["signal"] = params[8]

    #     for k in range(0, len(trade_data)):
    #         if trade_data["agg_profit"][k] is not None:
    #             if trade_data["agg_profit"][k] > 0:
    #                 trade_data["no_trade"][k] = 0
    #                 if trade_data["entry_price"][k] > trade_data["exit_price"][k]:
    #                     trade_data["buy"][k] = 0
    #                     trade_data["sell"][k] = 1
    #                 else:
    #                     trade_data["sell"][k] = 0
    #                     trade_data["buy"][k] = 1
    #             elif (
    #                 trade_data["agg_profit"][k] < 0 or trade_data["agg_profit"][k] == 0
    #             ):
    #                 trade_data["no_trade"][k] = 1
    #                 if trade_data["entry_price"][k] > trade_data["exit_price"][k]:
    #                     trade_data["buy"][k] = 0
    #                     trade_data["sell"][k] = 0
    #                 else:
    #                     trade_data["sell"][k] = 0
    #                     trade_data["buy"][k] = 0

    #     trade_data = trade_data.drop(
    #         columns=["entry_price", "exit_time", "exit_price", "agg_profit"]
    #     )

    #     trade_data.to_csv(f"data/trade_data_{i}.csv", index=False)
    #     print(f"Data {i} done")

    folder = "data"
    combined = pd.DataFrame()
    for files in os.listdir(folder):
        if files.endswith(".csv"):
            combined = pd.concat(
                [combined, pd.read_csv(f"{folder}/{files}")], ignore_index=True
            )
    combined["entry_time"] = pd.to_datetime(
        combined["entry_time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False
    )
    combined.sort_values("entry_time", ascending=True, inplace=True)
    combined = combined.dropna(subset=["profit"])
    combined.to_csv("comb.csv", index=False)
    print(combined.shape)


if __name__ == "__main__":
    main()
