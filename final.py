import os
import pandas as pd
import multiprocessing
import min1_agg.hyperbanding as hyperbanding_1min
import min1_peak.hyperbanding_peak as hyperbanding_peak_1min
import min3_agg.hyperbanding as hyperbanding_3min
import min3_peak.hyperbanding_peak as hyperbanding_peak_3min
import min5_agg.hyperbanding as hyperbanding_5min
import min5_peak.hyperbanding_peak as hyperbanding_peak_5min
import threading



def working(symbol):
    # Define the tasks
    tasks = [
        hyperbanding_1min.final,
        hyperbanding_peak_1min.final,
        hyperbanding_3min.final,
        hyperbanding_peak_3min.final,
        hyperbanding_5min.final,
        hyperbanding_peak_5min.final
    ]

    threads = []
    
    # Create a thread for each task
    for task in tasks:
        t = threading.Thread(target=task, args=(symbol,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

def worker(symbol, counter):
    print("Worker started ", counter)
    # print("Working on ", symbol)
    working(symbol)
    print("Worker finished ", counter) 

def main():
    file_path = 'combined_df.csv'
    file = pd.read_csv(file_path)
    # csv_files = [f for f in os.listdir(file_path) if f.endswith('.csv')]

    symbols  = file['Symbol'].unique()
    processes = []
    
    for i, symbol in enumerate(symbols):
        # symbol = os.path.splitext(csv_file)[0]  # Remove the .csv extension
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
