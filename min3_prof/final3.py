import pandas as pd
import multiprocessing
import min3_prof.hyperbanding as hyperbanding_3min


def working(symbol, gamma):
    hyperbanding_3min.final(symbol, gamma)


def worker(symbol, counter, gamma):
    print("Worker started ", counter)
    # print("Working on ", symbol)
    working(symbol, gamma)
    print("Worker finished ", counter)


def main(gamma):
    file_path = "symbols_profit.csv"
    file = pd.read_csv(file_path)

    symbols = file["Symbol"].unique()
    processes = []

    for i, symbol in enumerate(symbols):
        p = multiprocessing.Process(target=worker, args=(symbol, i, gamma))
        processes.append(p)
        p.start()

        # if i >= 1:
        #     break

    for p in processes:
        p.join()

    print("All workers finished")


if __name__ == "__main__":
    main()
