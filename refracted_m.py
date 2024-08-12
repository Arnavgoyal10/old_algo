import pandas as pd


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


ohlc = ["into", "inth", "intl", "intc"]

current_state = 0
# 0 == order not placed, 1 == order placed

signal = 0
# 0 == no signal, 1 == order_signal, 3 == exit_signal

market_direction = 0
# 1 == up, -1 == down, 0 == no direction

stoploss = 0
order_count = 0
buying_price = 0
exit_price = 0
exit_time = 0
order_flag_count = 0
entry_time = 0
entry_price = 0

"""""" """"""

stoploss_config = 10


"""""" """"""


def set_stoploss(df, market_direction, stoploss):
    temp = 0.0
    if market_direction == 1:
        temp = df["intl"].iloc[-1] - stoploss_config
        if temp > stoploss or stoploss == 0:
            stoploss = temp
    else:
        temp = df["inth"].iloc[-1] + stoploss_config
        if temp < stoploss or stoploss == 0:
            stoploss = temp
    return stoploss


def check_exit(df, market_direction, stoploss):
    exit_price = 0
    exit_time = df["time"].iloc[-1]
    inth_last = df["inth"].iloc[-1]
    intl_last = df["intl"].iloc[-1]

    if inth_last >= stoploss and intl_last <= stoploss:
        exit_price = stoploss
        return 3, exit_price, exit_time, stoploss

    stoploss = set_stoploss(df, market_direction, stoploss)
    return 0, exit_price, exit_time, stoploss


def check_trade(df, ret):

    # print(ret)

    buying_price = 0
    stoploss = 0

    if ret["prediction"].iloc[-1] == 1:
        print("order came in at", df["time"].iloc[-1])
        stoploss = set_stoploss(df, 1, stoploss)
        buying_price = df["inth"].iloc[-1]
        return 1, 1, buying_price, stoploss

    elif ret["prediction"].iloc[-1] == -1:
        print("order came in at", df["time"].iloc[-1])
        stoploss = set_stoploss(df, -1, stoploss)
        buying_price = df["intl"].iloc[-1]
        return 1, -1, buying_price, stoploss

    return 0, 0, 0, 0


def final(temp, trade_data, hyper_parameters, states, ret):
    global stoploss_config

    global current_state, signal, market_direction, stoploss, order_count, buying_price, exit_time
    global exit_price, order_flag_count, entry_time, entry_price

    (
        current_state,
        signal,
        market_direction,
        stoploss,
        order_count,
        buying_price,
        exit_time,
        exit_price,
        order_flag_count,
        entry_time,
        entry_price,
    ) = states

    stoploss_config = hyper_parameters

    agg_profit = 0
    if current_state == 1:
        signal, exit_price, exit_time, stoploss = check_exit(
            temp, market_direction, stoploss
        )
        if signal == 3:
            if market_direction == 1:
                profit = exit_price - entry_price
            else:
                profit = entry_price - exit_price
            # print("Order exited at: ", exit_time ,"at price: ", exit_price, "with profit: ", profit)
            trade_data = append_value(trade_data, "profit", profit, order_count)
            trade_data = append_value(trade_data, "exit_time", exit_time, order_count)
            trade_data = append_value(trade_data, "exit_price", exit_price, order_count)
            if profit > 120:
                agg_profit = 100
            elif profit < 10 and profit > 0:
                agg_profit = 0
            else:
                agg_profit = profit
            trade_data = append_value(trade_data, "agg_profit", agg_profit, order_count)
            if order_count == 0:
                percent = 100 * (1 + agg_profit / 100)
            else:
                percent = trade_data["percent"].iloc[order_count - 1] * (
                    1 + agg_profit / 100
                )
            trade_data = append_value(trade_data, "percent", percent, order_count)
            order_count = order_count + 1
            current_state = 0
            market_direction = 0
            signal = 0

    elif current_state == 0 and signal == 1:
        if order_flag_count < 2:
            if (
                temp["inth"].iloc[-1] >= buying_price
                and temp["intl"].iloc[-1] <= buying_price
            ):
                current_state = 1
                entry_time = temp["time"].iloc[-1]
                entry_price = buying_price
                stoploss = set_stoploss(temp, market_direction, stoploss)
                # print("Order placed at: ", entry_time ,"at price: ", entry_price, "with stoploss: ", stoploss)
                trade_data = append_value(
                    trade_data, "entry_time", entry_time, order_count
                )
                trade_data = append_value(
                    trade_data, "entry_price", entry_price, order_count
                )
                order_flag_count = 0

            else:
                order_flag_count = order_flag_count + 1
        else:
            order_flag_count = 0
            market_direction = 0
            signal = 0

    new_signal, new_market_direction, new_buying_price, new_stoploss = check_trade(
        temp, ret
    )
    # new_signal = 0, new_market_direction = 0, new_buying_price = 0, new_stoploss = 0
    # new_signal = 1, new_market_direction = market_direction, new_buying_price = buying_price, new_stoploss = stoploss

    if (
        market_direction == 0
        or (market_direction == 1 and new_market_direction == -1)
        or (market_direction == -1 and new_market_direction == 1)
    ):
        if current_state == 1:
            exit_price = temp["intc"].iloc[-1]
            if market_direction == 1:
                profit = exit_price - entry_price
            else:
                profit = entry_price - exit_price
            trade_data = append_value(trade_data, "profit", profit, order_count)
            trade_data = append_value(
                trade_data, "exit_time", temp["time"].iloc[-1], order_count
            )
            trade_data = append_value(trade_data, "exit_price", exit_price, order_count)
            if profit > 120:
                agg_profit = 100
            elif profit < 10 and profit > 0:
                agg_profit = 0
            else:
                agg_profit = profit
            trade_data = append_value(trade_data, "agg_profit", agg_profit, order_count)
            if order_count == 0:
                percent = 100 * (1 + agg_profit / 100)
            else:
                percent = trade_data["percent"].iloc[order_count - 1] * (
                    1 + agg_profit / 100
                )
            trade_data = append_value(trade_data, "percent", percent, order_count)
            order_count = order_count + 1
            order_flag_count = 0
            current_state = 0
        signal, market_direction, buying_price, stoploss = (
            new_signal,
            new_market_direction,
            new_buying_price,
            new_stoploss,
        )
        order_flag_count = 0

    states = (
        current_state,
        signal,
        market_direction,
        stoploss,
        order_count,
        buying_price,
        exit_time,
        exit_price,
        order_flag_count,
        entry_time,
        entry_price,
    )
    return trade_data, states
