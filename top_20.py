import os
import pandas as pd

data_folder = "data_trial"
all_data = []

def main():
    
    for i in range(208):  # Assuming files go from netprofit_0.csv to netprofit_50.csv
        file_path = os.path.join(data_folder, f"netprofit_{i}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    top_20_net_profit = combined_df.nlargest(20, 'net_profit')
    output_path = "top_20_net_profit1.csv"
    top_20_net_profit.to_csv(output_path, index=False)
    print(f"Top 20 net profit saved to {output_path}")
    
if __name__ == "__main__":
    main()