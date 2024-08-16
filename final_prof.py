import min5_prof.final5 as final5_prof
import hour_prof.final3 as finalh_prof
import min3_prof.final3 as final3_prof
import threading


def run_module(module, gamma):
    module.main(gamma)


def main():
    modules = [finalh_prof, final3_prof, final5_prof]
    gamma = [1.1, 1.9, 2.8, 4]

    print("TEST")

    threads = []

    for module in modules:
        for g in gamma:
            thread = threading.Thread(target=run_module, args=(module, g))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
