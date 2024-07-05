import mate_1.trial_hull.final_hull as final1
import mate_1.trial_okx.final_okx as final2
import mate_1.trial_okxfinal.final_okxfinal as final3
import mate_1.trial_squee.final_squee as final4
import mate_1.trial_super.final_super as final5
import mate_3.trial_hull.final_hull as final6
import mate_3.trial_okx.final_okx as final7
import mate_3.trial_okxfinal.final_okxfinal as final8
import mate_3.trial_squee.final_squee as final9
import mate_3.trial_super.final_super as final10
import threading


def run_module(module):
    module.main()

def main():
    modules = [final1, final2, final3, final4, final5, final6, final7, final8, final9, final10]
    threads = []
    
    for module in modules:
        thread = threading.Thread(target=run_module, args=(module,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
if __name__ == '__main__':
    main()
    