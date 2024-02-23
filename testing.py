import datetime
import pandas as pd 
import files_interact
import login
import supertrend
import impulsemacd
import tsi
import threading
import os
import argparse

data_dict = files_interact.extract()      
client=login.login()

def strat():
    print("print")

def program(count):
        for outer in range(count, count+1):
            outer /= 10
            for inner in range(8, int(outer * 10) + 1):
                inner /= 10
                df = strat(outer, inner)
                current_directory = os.getcwd()
                filename = f'df_ultimate_super_outer_{outer}_inner_{inner}.csv'
                file = os.path.join(current_directory, filename)
                df.to_csv(file, index=False)   
                if inner >= 2.5:
                    break
            print(f"Outer loop: {outer}, Inner loop: {inner} processing done")


def main():
    print("ok")
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--int-value', type=int, help='An integer value')
    # args = parser.parse_args()
    # print('Received integer:', args.int_value)
    # program(args.int_value)


    
    
if __name__ == "__main__":
    main()