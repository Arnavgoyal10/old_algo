import min3.final3 as final3
import min5.final5 as final5
# import min3_prof.final3 as final3_prof
# import min5_prof.final5 as final5_prof
import threading


def run_module(module):
    module.main()

def main():
    modules = [final3, final5]
    
    threads = []
    
    for module in modules:
        thread = threading.Thread(target=run_module, args=(module,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
if __name__ == '__main__':
    main()
    