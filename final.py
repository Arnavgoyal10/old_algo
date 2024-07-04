# import min1_agg.final1 as final1
# import min3_agg.final3 as final3
# import min5_agg.final5 as final5
# import threading


# def run_module(module):
#     module.main()

# def main():
#     modules = [final1, final3, final5]
#     threads = []
    
#     for module in modules:
#         thread = threading.Thread(target=run_module, args=(module,))
#         thread.start()
#         threads.append(thread)
    
#     for thread in threads:
#         thread.join()
    
# if __name__ == '__main__':
#     main()
    
    
    
    
import trial_hull.final_hull as final1
import trial_okx.final_okx as final2
import trial_okxfinal.final_okxfinal as final3
import trial_squee.final_squee as final4
import trial_super.final_super as final5
import threading


def run_module(module):
    module.main()

def main():
    modules = [final1, final2, final3, final4, final5]
    threads = []
    
    for module in modules:
        thread = threading.Thread(target=run_module, args=(module,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
if __name__ == '__main__':
    main()
    