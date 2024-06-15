import pandas as pd
import multiprocessing
import min5_agg.hyperbanding as hyperbanding_5min



def working(symbol):
    hyperbanding_5min.final(symbol)

def worker(symbol, counter):
    print("Worker started ", counter)
    # print("Working on ", symbol)
    working(symbol)
    print("Worker finished ", counter) 

def main():
    file_path = 'combined_df.csv'
    file = pd.read_csv(file_path)

    symbols  = file['Symbol'].unique()
    processes = []
    
    for i, symbol in enumerate(symbols):
        p = multiprocessing.Process(target=worker, args=(symbol, i))
        processes.append(p)
        p.start()
        
    
    for p in processes:
        p.join()
    
    print("All workers finished")

if __name__ == "__main__":
    main()
