# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime


def search_info_stock():
    # Παράμετροι
    symbol = input("Give me the symbol of the equities: ").upper()

    while True:
        start_date = input("Give me the start date (YYYY-MM-DD): ")
        end_date = input("Give me the end date (YYYY-MM-DD): ")
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if end_dt <= start_dt:
                print("⚠️ The end date must be after the start date!")
                continue
            break
        except ValueError:
            print("⚠️ Invalid date format! Please try again.")

    # Retrieve stock data
    data = yf.download(symbol, start=start_date, end=end_date)

    if data.empty:
        print(f"❌ No data found for {symbol} in this date range.")
        return None, symbol

    # Υπολογισμός Moving Averages (20 & 50)
    if len(data) < 50:
        print("⚠️ Not enough data for 50-day moving average. Some calculations may be skipped.")
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()

    while True:
        print("\n📌 Menu Options:")
        print("1- Show first 5 rows")
        print("2- Show last 5 rows")
        print("3- Show columns")
        print("4- Filter by Close price > value")
        print("5- Show summary statistics")
        print("6- Export data to CSV")
        print("7- Exit menu")

        try:
            choice = int(input("Choose an option (1-7): "))
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")
            continue

        if choice == 1:
            print(data.head())
        elif choice == 2:
            print(data.tail())
        elif choice == 3:
            print("\nAvailable columns:", list(data.columns))
            cols = input("Type the column names separated by commas: ")
            selected = [col.strip() for col in cols.split(',')]
            valid = [col for col in selected if col in data.columns]
            invalid = [col for col in selected if col not in data.columns]
            if valid:
                print(data[valid])
            if invalid:
                print(f"Invalid columns: {', '.join(invalid)}")
        elif choice == 4:
            try:
                price = float(input("Show rows where Close > "))
                print(data[data['Close'] > price])
            except ValueError:
                print("⚠️ Invalid number.")
        elif choice == 5:
            print(data.describe())
        elif choice == 6:
            filename = input("Enter filename (e.g., stock_data.csv): ")
            data.to_csv(filename)
            print(f"✅ Data exported to {filename}")
        elif choice == 7:
            print("🔚 Exiting menu.")
            break
        else:
            print("⚠️ Invalid option.")

    return data, symbol


def calcul_moving_average(data, symbol):
    # Προβολή Moving Averages
    df = data.reset_index()
    df.insert(loc=0, column='row_num', value=np.arange(len(df)))
    print("\n📊 Stock Data with Moving Averages and Row Number:\n")
    print(df)

    while True:
        try:
            avr = int(input("\nPress 1 to calculate a custom moving average, 0 to continue: "))
        except ValueError:
            print("⚠️ Invalid input.")
            continue

        if avr == 0:
            break

        try:
            days_avr = int(input("For how many days would you like to calculate the moving average? "))
            column_name = f"MA{days_avr}"
            data[column_name] = data['Close'].rolling(window=days_avr).mean()
            filtered = data[['Close', column_name]].dropna()

            print(f"\n{days_avr}-Day Moving Average for {symbol}")
            print(filtered)

            plt.figure(figsize=(12, 6))
            plt.plot(filtered.index, filtered['Close'], label='Closing Price', color='blue')
            plt.plot(filtered.index, filtered[column_name], label=f'{days_avr}-Day MA', color='orange', linestyle='--')
            plt.title(f"{symbol} - Closing Price and {days_avr}-Day Moving Average")
            plt.xlabel("Date")
            plt.ylabel("Price ($)")
            plt.legend()
            plt.grid()
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
            plt.show()

        except ValueError:
            print("⚠️ Invalid number.")


def info_sell_buy(data, symbol):
    buy_signals = []
    sell_signals = []
    position = False

    for i in range(len(data)):
        if data['MA20'].iloc[i] > data['MA50'].iloc[i] and not position:
            buy_signals.append(data['Close'].iloc[i])
            sell_signals.append(None)
            position = True
        elif data['MA20'].iloc[i] < data['MA50'].iloc[i] and position:
            buy_signals.append(None)
            sell_signals.append(data['Close'].iloc[i])
            position = False
        else:
            buy_signals.append(None)
            sell_signals.append(None)

    data['Buy'] = buy_signals
    data['Sell'] = sell_signals

    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label='Closing Price', color='blue')
    plt.plot(data.index, data['MA20'], label='20-day MA', color='green', linestyle='--')
    plt.plot(data.index, data['MA50'], label='50-day MA', color='red', linestyle='--')
    plt.scatter(data.index, data['Buy'], label="Buy Signal", color='green', s=100)
    plt.scatter(data.index, data['Sell'], label="Sell Signal", color='red', s=100)
    plt.title(f"{symbol} Stock Price with Buy/Sell Signals")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid()
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()


def main():
    print("' Welcome to Stock Market 💻 Analyzer 📊' \n")
    data, symbol = search_info_stock()
    if data is not None and not data.empty:
        calcul_moving_average(data, symbol)
        info_sell_buy(data, symbol)
    else:
        print("❌ No valid data to proceed with analysis.")


if __name__ == '__main__':
    main()
