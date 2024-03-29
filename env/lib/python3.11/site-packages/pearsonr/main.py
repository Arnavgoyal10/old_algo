import math
import statistics
from typing import List, Optional, Tuple

from .beta import incompbeta


def sum_of_squares(data: List[float]) -> float:
    return sum(value * value for value in data)


def pearsonr(x_arr: List[float], y_arr: List[float]) -> Tuple[Optional[float], Optional[float]]:
    # pure python implementation of scipy.stats.pearsonr
    # https://github.com/scipy/scipy/blob/v1.0.0/scipy/stats/stats.py#L2933-L3015

    # x_arr and y_arr should have same length
    n = len(x_arr)
    mean_x = statistics.mean(x_arr)
    mean_y = statistics.mean(y_arr)
    delta_x_arr = [mean_x - x for x in x_arr]
    delta_y_arr = [mean_y - y for y in y_arr]

    r_num = sum(dx * dy for dx, dy in zip(delta_x_arr, delta_y_arr))
    r_den = math.sqrt(sum_of_squares(delta_x_arr) * sum_of_squares(delta_y_arr))

    if r_den == 0:
        return None, 1.0 if n > 2 else None

    r = r_num / r_den

    # presumably, if abs(r) > 1, then it is only some small artifact of floating point arithmetic
    r = max(min(r, 1.0), -1.0)
    df = n - 2

    if abs(r) == 1.0:
        prob = 0.0
    else:
        t_squared = r ** 2 * (df / ((1.0 - r) * (1.0 + r)))
        a, b, x = 0.5 * df, 0.5, df / (df + t_squared)
        prob = incompbeta(a, b, min(x, 1.0))

    return r, prob
