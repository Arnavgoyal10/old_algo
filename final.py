import os
import multiprocessing
import hyperbanding_agg
import hyperbanding_profit


def working(symbol):
    hyperbanding_profit.final(symbol)
    hyperbanding_agg.final(symbol)

def worker(symbol, counter):
    print("Worker started ", counter)
    working(symbol)
    print("Worker finished ", counter) 

def main():
    file_path = 'symbols'
    csv_files = [f for f in os.listdir(file_path) if f.endswith('.csv')]
    
    processes = []
    
    for i, csv_file in enumerate(csv_files):
        symbol = os.path.splitext(csv_file)[0]  # Remove the .csv extension
        p = multiprocessing.Process(target=worker, args=(symbol, i))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print("All workers finished")

if __name__ == "__main__":
    main()
