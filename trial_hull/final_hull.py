import pandas as pd
import multiprocessing
import trial_hull.hyperbanding as hyperbanding_1min

def working(symbol):
    hyperbanding_1min.final(symbol)

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
        
        if i >= 1:
            break
        
    for p in processes:
        p.join()
    
    print("All workers finished")

if __name__ == "__main__":
    main()
