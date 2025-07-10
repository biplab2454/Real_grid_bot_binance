import time
import threading
from binance_client import client
from config_manager import load_config
import math

class GridBot:
    def __init__(self):
        self.running = False
        self.active_orders = []
        self.last_price = None
        self.symbol = ""
        self.trailing_triggered = False
        self.trailing_time = None
        self.buy_paused = False

    def get_price(self, symbol):
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])

    def get_volatility_range(self, symbol):
        klines = client.get_klines(symbol=symbol, interval="1h", limit=20)
        prices = [float(k[2]) for k in klines] + [float(k[3]) for k in klines]
        return max(prices) * 0.98, min(prices) * 1.02

    def cancel_all_orders(self, symbol):
        open_orders = client.get_open_orders(symbol=symbol)
        for order in open_orders:
            client.cancel_order(symbol=symbol, orderId=order["orderId"])

    def place_grid_orders(self, symbol, lower_price, upper_price, levels, amount_per_order):
        grid_step = (upper_price - lower_price) / levels
        self.active_orders.clear()
        for i in range(levels):
            buy_price = lower_price + i * grid_step
            sell_price = buy_price + grid_step
            quantity = round(amount_per_order / buy_price, 6)
            try:
                buy = client.order_limit_buy(symbol=symbol, quantity=quantity, price=str(round(buy_price, 2)))
                sell = client.order_limit_sell(symbol=symbol, quantity=quantity, price=str(round(sell_price, 2)))
                self.active_orders.append((buy, sell))
            except Exception as e:
                print("Order placement error:", e)

    def profit_from_trade(self, buy_price, sell_price, quantity):
        return (sell_price - buy_price) * quantity

    def monitor_trades(self, config):
        self.symbol = config["symbol"]
        levels = config["grid_levels"]
        investment = config["total_investment"]
        trailing_pct = config["trailing_trigger_pct"] / 100
        pump_pct = config["pump_protection_pct"] / 100

        amount_per_order = investment / levels

        while self.running:
            try:
                current_price = self.get_price(self.symbol)
                if not self.last_price:
                    self.last_price = current_price

                change_pct = (current_price - self.last_price) / self.last_price

                if change_pct >= pump_pct:
                    print("Pump detected! Pausing buys.")
                    self.buy_paused = True
                else:
                    self.buy_paused = False

                if change_pct >= trailing_pct:
                    if not self.trailing_triggered:
                        self.trailing_triggered = True
                        self.trailing_time = time.time()
                    elif time.time() - self.trailing_time >= 120:
                        print("Trailing up triggered. Resetting grid.")
                        self.cancel_all_orders(self.symbol)
                        lower, upper = self.get_volatility_range(self.symbol)
                        self.place_grid_orders(self.symbol, lower, upper, levels, amount_per_order)
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
        lower, upper = self.get_volatility_range(config["symbol"])
        amount_per_order = config["total_investment"] / config["grid_levels"]
        self.place_grid_orders(config["symbol"], lower, upper, config["grid_levels"], amount_per_order)
        threading.Thread(target=self.monitor_trades, args=(config,), daemon=True).start()

    def stop(self):
        self.running = False
        self.cancel_all_orders(self.symbol)

bot_instance = GridBot()
