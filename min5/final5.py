import pandas as pd
import multiprocessing
import min5.hyperbanding as hyperbanding_5min
import min5.optimser as optimser


def working(symbol, count):
    hyperbanding_5min.final(symbol, count)
    
def optimising(symbol, count):
    optimser.main(symbol, count)
    
def worker(symbol, counter):
    print("Worker started ", counter)

    for i in range(0,6):
        working(symbol, i)
        optimising(symbol, i)
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
