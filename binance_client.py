
from binance.client import Client

client = Client(api_key='1Caz5wSZD7PdSjbGqofLpR3CUZ6sDw5Z178oXTggugoiKgsJ52Arez9JdgFOHVKa', api_secret='NGMnGvS1GeNcAOUcuFMKp7jquKzF4ToFGeh2kqNMN4DhmkGVvj7egOlapIHBEld2')

def get_trading_pairs():
    try:
        exchange_info = client.get_exchange_info()
        return sorted([s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING'])
    except:
        return ['BTCUSDT', 'ETHUSDT']
