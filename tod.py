import json
from pprint import pprint

with open("output2.txt", "r") as f:
    lines = f.readlines()

lines = [i for i in lines if i.startswith("Evaluated params")]

results = [i[i.find("Result: ") + len("Result: ") :].replace("\n", "") for i in lines]
results = [float(i) for i in results]
    
pprint(min(results))