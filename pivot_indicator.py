
def pivot(df):
    p = (df["inth"] + df["intl"] + df["intc"])/3
    s1 = p - 0.382 * (df["inth"] - df["intl"])
    s2 = p - 0.618 * (df["inth"] - df["intl"])
    s3 = p - 1 * (df["inth"] - df["intl"])
    s4 = p + 0.382 * (df["inth"] - df["intl"])
    s5 = p + 0.618 * (df["inth"] - df["intl"])
    s6 = p + 1 * (df["inth"] - df["intl"])
        
    df = [s1, s2, s3, s4, s5, s6]

    return df