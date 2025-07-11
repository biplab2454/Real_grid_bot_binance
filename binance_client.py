from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()  # Optional: only needed for local testing

# Get keys from environment
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret)

def get_trading_pairs():
    try:
        exchange_info = client.get_exchange_info()
        return sorted([s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING'])
    except:
        return ['BTCUSDT', 'ETHUSDT']  # fallback