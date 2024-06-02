import pandas as pd
from scipy.optimize import minimize

# Define the helper function
def helper(dataframe):
    # Example helper function: calculates net profit from the dataframe
    net_profit = dataframe['profit'].sum() - dataframe['cost'].sum()
    return net_profit

# Define the worker function
def worker(params):
    # params is a list of 11 parameters
    a, b, c, d, e, f, g, h, i, j, k = params
    
    # Example dataframe creation and mathematical calculations
    data = {
        'profit': [a, b, c, d, e, f, g, h, i, j, k],
        'cost': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    }
    df = pd.DataFrame(data)
    
    # Call the helper function with the dataframe
    net_profit = helper(df)
    return net_profit

# Define the wrapper function for optimization
def worker_wrapper(params):
    # We negate the output because scipy.optimize.minimize performs minimization
    return -worker(params)

# Example initial guess for the 11 parameters
initial_guess = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

# Define the bounds for each parameter within ±3 of the initial guess and positive
bounds = [(max(0, x - 3), x + 3) for x in initial_guess]

# Perform the optimization with increased maximum function evaluations
result = minimize(worker_wrapper, initial_guess, method="Nelder-Mead", bounds=bounds, options={'disp': True, 'fatol': 1e-04, 'maxfev': 4000})

# Output the result
optimized_parameters = result.x
maximum_net_profit = -result.fun

optimized_parameters, maximum_net_profit
print(optimized_parameters, maximum_net_profit)