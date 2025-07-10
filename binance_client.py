
from binance.client import Client

client = Client(api_key='', api_secret='')

def get_trading_pairs():
    try:
        exchange_info = client.get_exchange_info()
        return sorted([s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING'])
    except:
        return ['BTCUSDT', 'ETHUSDT']
