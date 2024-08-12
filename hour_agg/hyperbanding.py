import os
import pandas as pd
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import refracted_agg as refracted
import csv
from datetime import datetime
import threading
import ray
from ray import tune, train
from ray.tune.search.bayesopt import BayesOptSearch
from ray.tune.search import ConcurrencyLimiter
import warnings

warnings.filterwarnings("ignore")

lock = threading.Lock()


def calculate_indicators(df, hyperparameters):
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
    ) = hyperparameters

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


def worker(params, ret):
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
    states = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    hyperparameters = [
        params["lookback"],
        params["ema_length"],
        params["conv"],
        params["length"],
        params["lengthMA"],
        params["lengthSignal"],
        params["fast"],
        params["slow"],
        params["signal"],
    ]

    df = calculate_indicators(ret, hyperparameters)
    temp = df.head(5).copy()
    df = df.iloc[5:].reset_index(drop=True)

    for j in range(0, len(df)):
        with lock:
            trade_data, states = refracted.final(
                temp, trade_data, [params["stoploss"], params["squee"]], states
            )

        next_row = df.iloc[[j]]
        temp = pd.concat(
            [temp, next_row.dropna(how="all")], ignore_index=True
        )  # Handle concatenation properly
        temp = temp.tail(5)

    if trade_data["percent"].iloc[-1].isna():
        net_profit = trade_data["percent"].iloc[-2]
    else:
        net_profit = trade_data["percent"].iloc[-1]
    return net_profit  # BayesianOptimization minimizes the objective function


def final(name):
    print("Script started at:", datetime.now())
    print("Current working directory:", os.getcwd())

    ray.init(include_dashboard=False, num_gpus=0, num_cpus=26)

    ohlc = ["into", "inth", "intl", "intc"]

    file_path = f"four_hour/{name}.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    print(f"Loading data from {file_path}")
    ret = pd.read_csv(file_path)
    ret["time"] = pd.to_datetime(
        ret["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False
    )
    for col in ohlc:
        ret[col] = ret[col].astype(float)

    top_results = []

    def optimize_function(config):

        params = config
        result = worker(params, ret)
        params["net_profit"] = result
        top_results.append(params)
        columns = [
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

        output_dir = "/home/arnav.goyal_ug2023/old_algo/hour_agg/out"
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        output_file = os.path.join(output_dir, f"{name.replace(' ', '')}_agg.csv")
        print(f"Writing results to {output_file}")

        exists = os.path.isfile(output_file)

        with open(output_file, "a") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            if not exists:
                writer.writeheader()
            writer.writerows(top_results)

        train.report({"net_profit": result, **params})
        return {"net_profit": result}

    pbounds = {
        "stoploss": tune.uniform(0, 50),
        "squee": tune.uniform(0, 10),
        "lookback": tune.uniform(5, 30),
        "ema_length": tune.uniform(6, 35),
        "conv": tune.uniform(28, 75),
        "length": tune.uniform(2, 40),
        "lengthMA": tune.uniform(14, 52),
        "lengthSignal": tune.uniform(2, 28),
        "fast": tune.uniform(2, 27),
        "slow": tune.uniform(8, 42),
        "signal": tune.uniform(2, 30),
    }

    algo = BayesOptSearch(utility_kwargs={"kind": "ucb", "kappa": 2.5, "xi": 0.0})
    algo = ConcurrencyLimiter(algo, max_concurrent=40)

    tuner = tune.Tuner(
        optimize_function,
        param_space=pbounds,
        tune_config=tune.TuneConfig(
            num_samples=1900, metric="net_profit", mode="max", search_alg=algo
        ),
    )

    results = tuner.fit()

    output_best_file = os.path.join("hour_agg", f"{name}_runs.csv")
    res_df = results.get_dataframe(filter_metric="net_profit", filter_mode="max")
    res_df.to_csv(output_best_file)

    best_config = results.get_best_result(metric="net_profit", mode="max").config

    output_best_file = os.path.join("hour_agg", f"{name}_best_params.csv")
    with open(output_best_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(best_config.keys()))
        writer.writeheader()
        writer.writerow(best_config)

    print("Best hyperparameters found were: ", best_config)
    print("Script ended at:", datetime.now())
