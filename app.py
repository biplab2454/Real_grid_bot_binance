
from flask import Flask, render_template, request, redirect, jsonify
from config_manager import load_config, save_config
from binance_client import get_trading_pairs
from tasks import start_bot

app = Flask(__name__)

@app.route('/')
def index():
    config = load_config()
    pairs = get_trading_pairs()
    return render_template('dashboard.html', config=config, pairs=pairs)

@app.route('/start-bot', methods=['POST'])
def start():
    start_bot()
    return redirect('/')

@app.route('/save-config', methods=['POST'])
def save():
    data = request.form.to_dict()
    save_config(data)
    return redirect('/')

@app.route('/config')
def config_json():
    return jsonify(load_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
