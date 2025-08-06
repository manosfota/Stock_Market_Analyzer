# -*- coding: utf-8 -*-
import pandas as pd 
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime


def search_info_stock():
  # Παράμετροι
  symbol=input("Give me the symbol of the equities: ")
  while True:
    start_date=input("Give me the start date (YYYY-MM-DD):")
    end_date=input("Give me the end date (YYYY-MM-DD):")
    try:
      start_dt=datetime.strptime(start_date, "%Y-%m-%d")
      end_dt=datetime.strptime(end_date, "%Y-%m-%d")
      if end_dt<=start_dt:
        print("⚠️ The end date must be after the start date!")
        continue
      break
    except ValueError:
      print("⚠️ Invalid Value! Please try again! ")
     
  # Retrieve stock data from Yahoo Finance
  data=yf.download(symbol, start=start_date, end=end_date)
  print(data)

  if data.empty:
    print(f"No Data found for this symbol {symbol}")
    return None, symbol

  while True:
    print("1- Show first 5 rows")
    print("2- Show last 5 rows")
    print("3- Show columns")
    print("4- Filter by close price > value")
    print("5- Show summary statistics")
    print("6- Export data to CSV")
    print("7- Exit menu")

    try:
      choise=int(input("Choose an option (1-7): "))
    except ValueError:
       print("⚠️ Invalid input. Please enter a number.")
       continue

    match choise:
      case 1:
        print(data.head())
      case 2:
        print(data.tail())
      case 3:
        print("\n Available columns:",list(data.columns))
        cols=input("Type the column name seperated by comma (e.g., Open,Close):  ")
        selected_cols=[col.strip() for col in cols.split(',')]
        valid_cols=[col for col in selected_cols if col in data.columns]
        invalid_cols=[col for col in selected_cols if col not in data.columns]
        if valid_cols:
          print(data[valid_cols])
        if invalid_cols:
          print(f"Invalid column(s): {', '.join(invalid_cols)}")
      case 4:
        try:
          price=float(input("Show rows where Close >"))
          print(data[data['Close']>price])
        except ValueError:
          print("Invalid Error")
      case 5: 
        print(data.describe())
      case 6:
        filename = input("Enter filename (e.g., stock_data.csv)")
        data.to_csv(filename)
        print(f"✅ Data exported to {filename}")
      case 7:
        print("🔚 Exiting for menu.")
        break
      case _:
        print("⚠️ Invalid option.")

  return data, symbol


def calcul_moving_average(data,symbol):
 
  # Calculate 20-day and 50-day moving averages
  data['MA20']=data['Close'].rolling(window=20).mean()
  data['MA50']=data['Close'].rolling(window=50).mean()
  data.dropna(inplace=True)

  index_ = ['Open','High','Low','Close','Volume']
  df=pd.DataFrame(data)
 
  df=data.reset_index()
  df.insert(loc=0, column='row_num', value=np.arange(len(df)))
  print("\n📊 Full Stock DataFrame with Moving Averages and Row Number:\n")
  print (df)
  print("\n")


  # Compute moving averages based on user-defined time frames
  avr=int(input("If you want to calculate the moving average for more or less days press 1: "))

  while(avr==1):
    days_avr=int(input("\nFor how many days would you like to calculate to moving average"))
    column_name=f"MA{days_avr}"
    data[column_name]=data['Close'].rolling(window=days_avr).mean()
    filtered_data=data[['Close',column_name]].dropna()   

    print(f"\n {days_avr}-Day Moving Average for equity {symbol}")
    print(filtered_data)

    # Plot the graph with titles and detailed annotations
    plt.figure(figsize=(12,6))
    plt.plot(filtered_data['Close'], label= 'Closing Price', color='blue')
    plt.plot(filtered_data[column_name],label=f'{days_avr}-Day MA',color='orange', linestyle='--')
    plt.title(f"{symbol} - Closing Price and {days_avr}-Day Moving Average")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid()
    plt.show()
    plt.tight_layout()
    con=con = int(input("ℹ️ Press 1 to calculate another moving average or 0 to continue: "))
    if con==0:
      break
 

def info_sell_buy(data, symbol):
  # Create lists to store trading signals
  buy_signals=[]
  sell_signals=[]
  position=False    

  for i in range(len(data)):
    if data['MA20'].iloc[i]>data['MA50'].iloc[i] and not position:
      buy_signals.append(data['Close'].iloc[i])
      sell_signals.append(None)
      position=True
    elif data['MA20'].iloc[i]<data['MA50'].iloc[i] and position:
      buy_signals.append(None)
      sell_signals.append(data['Close'].iloc[i])
      position=False
    else:
      buy_signals.append(None)
      sell_signals.append(None)

  # Add trading signals to the DataFrame
  data['Buy'] = buy_signals
  data['Sell'] = sell_signals

  # Visualize the updated data with plotted signals
  plt.figure(figsize=(12, 6))
  plt.plot(data['Close'], label=' Closing Price', color='blue')
  plt.plot(data['MA20'], label='20-day MA', color='green', linestyle='--')
  plt.plot(data['MA50'], label='50-day MA', color='red', linestyle='--')
  plt.scatter(data.index, data['Buy'], label=" Buy Signal", color='green', s=100)
  plt.scatter(data.index, data['Sell'],label=" Sell Signal", color='red', s=100)
  # Finalize graph with titles and additional details
  plt.title(f"{symbol} Stock Price with Moving Averages")
  plt.xlabel("Date")
  plt.ylabel("Price ($)")
  plt.legend()
  plt.grid()
  plt.show()
  plt.tight_layout()


def main():
  print("' Welcome to Stock Market 💻 Analyzer 📊' \n")
  data, symbol = search_info_stock()
  if data is not None:
    calcul_moving_average(data, symbol)
    info_sell_buy(data, symbol)
  else:
    print("❌ No valid data to proceed with analysis.")
  
if __name__=='__main__':
  main()

