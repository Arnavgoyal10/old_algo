import min1_prof.final1 as final1_prof
import min3_prof.final3 as final3_prof
import min5_prof.final5 as final5_prof
import threading


def run_module(module):
    module.main()

def main():
    modules = [final1_prof, final3_prof, final5_prof]
    threads = []
    
    for module in modules:
        thread = threading.Thread(target=run_module, args=(module,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
if __name__ == '__main__':
    main()
    