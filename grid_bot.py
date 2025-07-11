import time import threading import os import math from binance_client import client from config_manager import load_config from ta.volatility import average_true_range, BollingerBands from ta.momentum import RSIIndicator from ta.trend import MACD import pandas as pd

class GridBot: def init(self): self.running = False self.active_orders = [] self.last_price = None self.symbol = "" self.trailing_triggered = False self.trailing_time = None self.buy_paused = False self.total_profit = 0 self.sell_history = []  # for profit tracking

def get_price(self, symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])

def get_klines_df(self, symbol, interval="1h", limit=50):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_volume',
        'taker_buy_quote_volume', 'ignore'
    ])
    df = df.astype(float)
    return df

def get_smart_grid_range(self, symbol):
    df = self.get_klines_df(symbol)
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    lower = bb.bollinger_l().iloc[-1]
    upper = bb.bollinger_h().iloc[-1]
    return lower, upper

def cancel_all_orders(self, symbol):
    open_orders = client.get_open_orders(symbol=symbol)
    for order in open_orders:
        client.cancel_order(symbol=symbol, orderId=order["orderId"])

def place_grid_orders(self, symbol, lower_price, upper_price, levels, capital_list):
    grid_step = (upper_price - lower_price) / levels
    self.active_orders.clear()
    for i in range(levels):
        buy_price = lower_price + i * grid_step
        sell_price = buy_price + grid_step
        capital = capital_list[i]
        quantity = round(capital / buy_price, 6)
        try:
            buy = client.order_limit_buy(symbol=symbol, quantity=quantity, price=str(round(buy_price, 2)))
            sell = client.order_limit_sell(symbol=symbol, quantity=quantity, price=str(round(sell_price, 2)))
            self.active_orders.append((buy, sell))
        except Exception as e:
            print("Order placement error:", e)

def compute_capital_allocation(self, total, levels):
    weights = [i + 1 for i in range(levels)]  # cost averaging
    total_weight = sum(weights)
    return [(w / total_weight) * total for w in weights]

def track_profit(self):
    for _, sell_order in self.active_orders:
        try:
            order = client.get_order(symbol=self.symbol, orderId=sell_order["orderId"])
            if order["status"] == "FILLED":
                filled_qty = float(order["executedQty"])
                sell_price = float(order["price"])
                buy_price = float([b["price"] for b, s in self.active_orders if s["orderId"] == order["orderId"]][0])
                profit = self.profit_from_trade(float(buy_price), sell_price, filled_qty)
                self.total_profit += profit
                self.sell_history.append(order["orderId"])
        except:
            continue

def profit_from_trade(self, buy_price, sell_price, quantity):
    return (sell_price - buy_price) * quantity

def use_recovery_signals(self):
    df = self.get_klines_df(self.symbol, interval="15m", limit=50)
    rsi = RSIIndicator(close=df['close']).rsi().iloc[-1]
    macd = MACD(close=df['close']).macd_diff().iloc[-1]
    volume_spike = df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1]
    return rsi < 30 and macd > 0 and volume_spike

def monitor_trades(self, config):
    self.symbol = config["symbol"]
    levels = config["grid_levels"]
    investment = config["total_investment"]
    trailing_pct = config["trailing_trigger_pct"] / 100
    pump_pct = config["pump_protection_pct"] / 100
    capital_list = self.compute_capital_allocation(investment, levels)

    while self.running:
        try:
            current_price = self.get_price(self.symbol)
            self.track_profit()

            if self.total_profit >= 0.3 * investment:
                print("🎯 Target profit hit. Resetting grid.")
                self.cancel_all_orders(self.symbol)
                lower, upper = self.get_smart_grid_range(self.symbol)
                self.place_grid_orders(self.symbol, lower, upper, levels, capital_list)
                self.total_profit = 0

            if not self.last_price:
                self.last_price = current_price

            change_pct = (current_price - self.last_price) / self.last_price

            if change_pct >= pump_pct:
                print("🚨 Pump detected! Pausing buys.")
                self.buy_paused = True
            else:
                self.buy_paused = False

            if change_pct >= trailing_pct:
                if not self.trailing_triggered:
                    self.trailing_triggered = True
                    self.trailing_time = time.time()
                elif time.time() - self.trailing_time >= 120:
                    print("📈 Trailing up triggered. Resetting grid.")
                    self.cancel_all_orders(self.symbol)
                    lower, upper = self.get_smart_grid_range(self.symbol)
                    self.place_grid_orders(self.symbol, lower, upper, levels, capital_list)
                    self.last_price = current_price
                    self.trailing_triggered = False
            else:
                self.trailing_triggered = False

        except Exception as e:
            print("Monitoring error:", e)

        time.sleep(10)

def start(self):
    config = load_config()
    self.running = True
    self.symbol = config["symbol"]
    levels = config["grid_levels"]
    investment = config["total_investment"]
    capital_list = self.compute_capital_allocation(investment, levels)
    lower, upper = self.get_smart_grid_range(self.symbol)
    self.place_grid_orders(self.symbol, lower, upper, levels, capital_list)
    threading.Thread(target=self.monitor_trades, args=(config,), daemon=True).start()

def stop(self):
    self.running = False
    self.cancel_all_orders(self.symbol)

bot_instance = GridBot()

