from NorenRestApiPy.NorenApi import  NorenApi
from threading import Timer
import pandas as pd
import time
import concurrent.futures

api = None

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        global api
        api = self
