import min1_agg.final1 as final1
import min3_agg.final3 as final3
import min5_agg.final5 as final5
import threading


def run_module(module):
    module.main()

def main():
    modules = [final1, final3, final5]
    threads = []
    
    for module in modules:
        thread = threading.Thread(target=run_module, args=(module,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
if __name__ == '__main__':
    main()
    