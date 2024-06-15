import min1_agg.final1 as final1
import min1_peak.final2 as final2
import min3_agg.final3 as final3
import min3_peak.final4 as final4
import min5_agg.final5 as final5
import min5_peak.final6 as final6
import threading


def run_module(module):
    module.main()

def main():
    modules = [final1, final2, final3, final4, final5, final6]
    threads = []
    
    for module in modules:
        thread = threading.Thread(target=run_module, args=(module,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
if __name__ == '__main__':
    main()
    