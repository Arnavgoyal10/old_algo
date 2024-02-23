import datetime
import time
import pandas as pd 
import files_interact
import login
import supertrend
import impulsemacd
import tsi
import threading



data_dict = files_interact.extract()       
client=login.login()



main_signal = False
bull_or_bear = None
feed_opened = False
current_atm = 0
order_placed = False
order_placed_token =0
order_number =0
alarm = False
order_waiting_impulse = False
order_waiting_tsi = False
threshold = 0
waiting_counter = 0





def on_tick_data(tick_data):
    
    if 'lp' not in tick_data:
        return

    ltp = tick_data["lp"]
    ltp = float(ltp)
    
    set_atm(ltp)
    if order_placed == False:
        process_ltp(ltp)
    else:
        if alarm == True:
            # ret = client.modify_order(exchange='NSE', tradingsymbol='CANBK-EQ', orderno=order_number,newquantity=1, 
            #                           newprice_type='SL-LMT', newprice=201.00, newtrigger_price= ltp-1)
            print("order modified")
    

    

        
def open_callback():
    global feed_opened
    print("connected")
    feed_opened = True

def event_handler_order_update(tick_data):
    print(f"order update {tick_data}")

client.start_websocket( order_update_callback=event_handler_order_update,
                        subscribe_callback=on_tick_data, 
                        socket_open_callback=open_callback)

def subsribe(exchange, index, side=None, current_atm=None):
    token_current =f"{exchange}|{files_interact.get_token(exchange, index, side, current_atm)}"
    client.subscribe(token_current)












def conditions():
    global main_signal, bull_or_bear, alarm, order_waiting_impulse, order_waiting_tsi, threshold, stoploss, waiting_counter
    
    while True:
        current_time = datetime.datetime.now()
        token = files_interact.get_token("NSE", "Nifty 50")
        lastBusDay = datetime.datetime.now()-datetime.timedelta(days=30)
        lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0)
        ret = client.get_time_price_series(exchange="NSE", token = str(int(token)), starttime=int(lastBusDay.timestamp()), interval="5")
        ret = pd.DataFrame.from_dict(ret)
        del ret["stat"]
        ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
        ret.sort_values(by='time', ascending=True, inplace=True)
        ret.reset_index(inplace=True) 
        del ret["index"] 
        print(ret)   
        ohlc=['into', 'inth', 'intl', 'intc']
        for col in ohlc:
            ret[col] = ret[col].astype(float)  
        df_impulse = ret[['time', 'inth', 'intl', 'intc']]
        df_impulse = impulsemacd.macd(df_impulse)
        df_tsi = ret[['intc']]
        df_tsi = tsi.tsi(df_tsi)
        
        
        if order_placed == True:
            if bull_or_bear == "up":
                if (df_tsi["tsi"].iloc[-1] < df_tsi["tsi"].iloc[-2]):
                    alarm = True
            else:
                if (df_tsi["tsi"].iloc[-1] > df_tsi["tsi"].iloc[-2]):
                    alarm = True
            if alarm == False:
                if ret["inth"].iloc[-2] > ret["inth"].iloc[-3]:
                    highest = ret["inth"].iloc[-2]
                else:
                    highest = ret["inth"].iloc[-3]
                if ret["intl"].iloc[-2] > ret["intl"].iloc[-3]:
                    lowest = ret["intl"].iloc[-2]
                else:
                    lowest = ret["intl"].iloc[-3]
                stoploss = (ret["intc"].iloc[-2] + ret["into"].iloc[-3] + highest + lowest) / 4
                # ret = client.modify_order(exchange='NSE', tradingsymbol='CANBK-EQ', orderno=order_number,
        #                                newquantity=1, newprice_type='SL-LMT', newprice=201.00, newtrigger_price= stoploss)
                print("order modified")

        
        
        
        
        elif (order_waiting_impulse == True or order_waiting_tsi == True):
            df_signal_super = supertrend.SuperTrend(ret, period= 17, multiplier=1.5, ohlc=ohlc)
            if (df_signal_super["STX"].iloc[-1] == df_signal_super["STX"].iloc[-2]):
                if ret["intc"].iloc[-1] > threshold:
                    main_signal = True
                    if ret["inth"].iloc[-2] > ret["inth"].iloc[-3]:
                        highest = ret["inth"].iloc[-2]
                    else:
                        highest = ret["inth"].iloc[-3]
                    if ret["intl"].iloc[-2] > ret["intl"].iloc[-3]:
                        lowest = ret["intl"].iloc[-2]
                    else:
                        lowest = ret["intl"].iloc[-3]
                    stoploss = (ret["intc"].iloc[-2] + ret["into"].iloc[-3] + highest + lowest) / 4
            elif (waiting_counter < 2):
                waiting_counter = waiting_counter + 1
            else:
                waiting_counter = 0
                order_waiting_impulse = False
                order_waiting_tsi = False
            
        
        
        
        else:
            df_ultimate_super = supertrend.SuperTrend(ret, period= 17, multiplier=3, ohlc=ohlc)
            df_signal_super = supertrend.SuperTrend(ret, period= 17, multiplier=1.5, ohlc=ohlc)
            
            if (df_ultimate_super["STX"].iloc[-1] != df_ultimate_super["STX"].iloc[-2]):
                if (df_signal_super["STX"].iloc[-1] != df_signal_super["STX"].iloc[-2]):
                    supertrend_signal = True
                elif (df_signal_super["STX"].iloc[-2] != df_signal_super["STX"].iloc[-3]):
                    supertrend_signal = True
            elif (df_signal_super["STX"].iloc[-1] != df_signal_super["STX"].iloc[-2]):
                if (df_signal_super["STX"].iloc[-1] == df_ultimate_super["STX"].iloc[-1]):
                    supertrend_signal = True
            
            if (supertrend_signal == True):
                bull_or_bear = df_ultimate_super["STX"].iloc[-1] 
                if (bull_or_bear == "up"):
                    temp1 = df_impulse["ImpulseMACD"].iloc[-1] - df_impulse["ImpulseMACDCDSignal"].iloc[-1]
                    temp2 = df_impulse["ImpulseMACD"].iloc[-2] - df_impulse["ImpulseMACDCDSignal"].iloc[-2]
                    if (temp2 < 0 and temp1 > 0):
                        order_waiting_impulse == True
                    elif ( temp1 > temp2):
                        if temp1 > 5:
                            super_impulse_signal = True                    
                else:
                    temp1 = df_impulse["ImpulseMACDCDSignal"].iloc[-1] - df_impulse["ImpulseMACD"].iloc[-1]
                    temp2 = df_impulse["ImpulseMACDCDSignal"].iloc[-2] - df_impulse["ImpulseMACD"].iloc[-2]
                    if (temp2 > 0 and temp1 < 0):
                        order_waiting_impulse == True
                    elif (temp1 > temp2):
                        if temp1 > 5:
                            super_impulse_signal = True
            
            if (super_impulse_signal == True or order_waiting_impulse == True):
                if (bull_or_bear == "up"):
                    temp1 = df_tsi["tsi"].iloc[-1] - df_tsi["signal"].iloc[-1]
                    temp2 = df_tsi["tsi"].iloc[-2] - df_tsi["signal"].iloc[-2]
                    if (temp2 < 0 and temp1 > 0):
                        order_waiting_tsi == True
                    elif (order_waiting_impulse == False and temp1 > temp2):
                        main_signal = True               
                else:
                    temp1 = df_tsi["signal"].iloc[-1] - df_tsi["tsi"].iloc[-1]
                    temp2 = df_tsi["signal"].iloc[-2] - df_tsi["tsi"].iloc[-2]
                    if (temp2 > 0 and temp1 < 0):
                        order_waiting_tsi == True
                    elif (order_waiting_impulse == False and temp1 > temp2):
                        main_signal = True
    
            if (order_waiting_impulse == True or order_waiting_tsi == True):
                threshold = ret["intc"].iloc[-1]
            
            
            if main_signal == True:
                current_time = datetime.datetime.now()
                comparison_time = current_time.replace(hour=9, minute=25, second=0, microsecond=0)
                if current_time < comparison_time:
                    if bull_or_bear == "up":
                        stoploss = ret["inth"].iloc[-1] + 10
                    else:
                        stoploss = ret["intl"].iloc[-1] - 10
                else:
                    if ret["inth"].iloc[-2] > ret["inth"].iloc[-3]:
                        highest = ret["inth"].iloc[-2]
                    else:
                        highest = ret["inth"].iloc[-3]
                    if ret["intl"].iloc[-2] > ret["intl"].iloc[-3]:
                        lowest = ret["intl"].iloc[-2]
                    else:
                        lowest = ret["intl"].iloc[-3]
                    stoploss = (ret["intc"].iloc[-2] + ret["into"].iloc[-3] + highest + lowest) / 4
                

            
        mins_to_wait = 5 - (current_time.minute % 5)
        seconds_to_wait = 60 - current_time.second
        if seconds_to_wait == 60:
            seconds_to_wait = 0
        if seconds_to_wait == 0 and mins_to_wait == 5:
            mins_to_wait = 0  
        if (mins_to_wait == 1 and seconds_to_wait != 60):
            mins_to_wait = 0
        
        total_seconds_to_wait = (mins_to_wait * 60) + seconds_to_wait + 2
        time.sleep(total_seconds_to_wait)
        
            
            

















def process_ltp(ltp):
    global order_placed
    
    if main_signal ==True:
        if (bull_or_bear == "up"):
            place_bull_order() 
        else:
            place_bear_order()
        order_placed = True
   
    else:
        print(f"ltp is: {ltp}, no order")




def place_bull_order():
    global order_placed_token, order_number
    trading_symbol = files_interact.get_trading_symbol("NFO", "NIFTY", "CE", current_atm)
    token = files_interact.get_token("NFO", "NIFTY", "CE", current_atm)
    
    # ret = client.place_order(buy_or_sell= "B", product_type= "I", exchange="NFO", 
    #                          tradingsymbol=trading_symbol, quantity=1,  discloseqty=0,price_type='LMT', price=1)
    
    order_placed_token = token
    ltp = client.get_quotes("NFO", str(token))['lp']
    print(f"buying {trading_symbol} at {ltp}")
    ltp = float(ltp)
    
    # if ret["stat"] == "ok":
    #     ret = client.place_order(buy_or_sell= "S", product_type= "I", exchange="NFO", 
    #                             tradingsymbol=trading_symbol, quantity=1,  discloseqty=0,price_type='M', price= stoploss)
    #     order_number = ret["norenordno"]
        


def place_bear_order():
    global order_placed_token, order_number
    trading_symbol = files_interact.get_trading_symbol("NFO", "NIFTY", "PE", current_atm)
    token = files_interact.get_token("NFO", "NIFTY", "PE", current_atm)
    
    # ret = client.place_order(buy_or_sell= "B", product_type= "I", exchange="NFO", 
    #                          tradingsymbol=trading_symbol, quantity=1,  discloseqty=0,price_type='M', price=1)

    order_placed_token = token
    ltp = client.get_quotes("NFO", str(token))['lp']
    print(f"buying {trading_symbol} at {ltp}")
    ltp = float(ltp)
    
    # if ret["stat"] == "ok":
    #     ret = client.place_order(buy_or_sell= "S", product_type= "I", exchange="NFO", 
    #                              tradingsymbol=trading_symbol, quantity=1,  discloseqty=0,price_type='LMT', price= stoploss)
    #     order_number = ret["norenordno"]
    








def set_atm(ltp):
    global current_atm
    strike_gap = 50
    remainder = ltp % strike_gap
    if remainder > strike_gap / 2:
        current_atm = ltp + strike_gap - remainder
    else:
        current_atm = ltp-remainder
 


def main():

    threading.Thread(target=conditions).start()
     
    while(feed_opened==False):
        pass
        
    subsribe("NSE", "Nifty 50")


if __name__ == "__main__":
    main()