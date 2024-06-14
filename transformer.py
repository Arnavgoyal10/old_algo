import pandas as pd
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import matplotlib.pyplot as plt
import seaborn as sns
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi

    
# Load data
ret = pd.read_csv('nifty_data/nifty_feb.csv')
df = pd.read_csv('nifty_trades/nifty_profit.csv')



def calculate_indicators(df, hyperparamas):
    
    (lookback_config, ema_length_config, conv_config, 
    length_config, lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    signal_config) = hyperparamas
    
    df = df.copy()
    
    df = velocity_indicator.calculate_float(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index2_float(df,conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA = lengthMA_config, lengthSignal = lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast = fast_config, slow = slow_config, signal = signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df




class TradeDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx], dtype=torch.long) for key, val in self.encodings.items()}  # Convert to long
        item['labels'] = torch.tensor(self.labels[idx]).long()  # Use long for labels
        return item

    def __len__(self):
        return len(self.labels)

# Tokenize the data
def tokenize_data(df):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    encodings = tokenizer(list(df['text']), truncation=True, padding=True, max_length=512)
    return encodings

# Process and prepare the data
def prepare_data(df, ret):
    # Your existing logic to calculate indicators and process data
    
    # Assuming your calculate_indicators function and hyperparameters are defined
    hyper_params = [10.02,14.72,48.73,27,33.43,9,14.87,31.35,15.1]
    ret = calculate_indicators(ret, hyper_params)

    ret['trade'] = 0
    ret['result'] = 0

    ret['time'] = pd.to_datetime(ret['time'])
    df['entry_time'] = pd.to_datetime(df['entry_time'])

    for index, row in df.iterrows():
        entry_time = row['entry_time']
        profit = row['profit']
        
        match_index = ret[ret['time'] == entry_time].index
        
        if not match_index.empty:
            ret.at[match_index[0], 'trade'] = 1
            ret.at[match_index[0], 'result'] = 1 if profit > 0 else 0

    ret_dropped = ret.iloc[75:].reset_index(drop=True)
    # ret_dropped['trade'] = ret_dropped['trade'].shift(-1)
    # ret_dropped['result'] = ret_dropped['result'].shift(-1)
    # ret_dropped = ret_dropped.iloc[:-1].reset_index(drop=True)
    ret_dropped = ret_dropped.reset_index(drop=True)
    
    ret_dropped.drop(columns=['time'], inplace=True)
    
    df_y = ret_dropped[['trade', 'result']]
    df_x = ret_dropped.drop(columns=['trade', 'result'])

    # Assuming 'text' is the column with textual data
    df_x['text'] = df_x.apply(lambda row: ' '.join(map(str, row.values)), axis=1)

    return df_x, df_y

# Split and prepare datasets
df_x, df_y = prepare_data(df, ret)
x_train, x_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.2, random_state=0)

train_encodings = tokenize_data(x_train)
test_encodings = tokenize_data(x_test)

train_dataset = TradeDataset(train_encodings, y_train['trade'].values)
test_dataset = TradeDataset(test_encodings, y_test['trade'].values)

# Define the model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Define training arguments
training_args = TrainingArguments(
    output_dir='results',          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size for training
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='logs',            # directory for storing logs
    logging_steps=10,
)

# Define the Trainer
trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=test_dataset            # evaluation dataset
)

# Train the model
trainer.train()

# Evaluate the model
predictions, label_ids, metrics = trainer.predict(test_dataset)
preds = np.argmax(predictions, axis=1)

# Print accuracy
print(f"Accuracy: {accuracy_score(y_test['trade'].values, preds)}")

# Confusion matrix
cm = confusion_matrix(y_test['trade'].values, preds)
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Class 0', 'Class 1'], yticklabels=['Class 0', 'Class 1'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix for Trade')
plt.show()