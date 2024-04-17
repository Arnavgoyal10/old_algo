import os
from tvDatafeed import TvDatafeed, Interval

# tv = TvDatafeed(username='arnavgoyal63774', password='fAC@6kjug8tgqM-')
tv = TvDatafeed()


def main():
    
    ret = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_5_minute,n_bars=6000)                                          
    current_directory = os.getcwd()
    df_comb_file = os.path.join(current_directory, 'nifty_full1.csv')
    ret.to_csv(df_comb_file, index=True)
                                                                                    
                                                                                                                     
if __name__ == "__main__":
    main()
    