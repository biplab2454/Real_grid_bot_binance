from flask import Flask, render_template, request, jsonify, redirect
from config_manager import load_config, save_config
from binance_client import get_trading_pairs
from tasks import start_bot

app = Flask(__name__)

@app.route('/')
def index():
    config = load_config()
    pairs = get_trading_pairs() or ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Backup if API fails
    return render_template('dashboard.html', config=config, pairs=pairs)

@app.route('/start-bot', methods=['POST'])
def start():
    start_bot()
    return jsonify(status='Bot started.')

@app.route('/save-config', methods=['POST'])
def save():
    data = request.form.to_dict()
    save_config(data)
    return redirect('/')

@app.route('/config')
def config_json():
    return jsonify(load_config())

# ✅ Repaired Manual Grid Setup Route
@app.route('/manual_grid_setup', methods=['POST'])
def manual_grid_setup():
    data = request.json

    grid_levels = int(data.get("grid_levels", 10))
    min_price = float(data.get("min_price", 0))
    max_price = float(data.get("max_price", 0))
    step_size = float(data.get("step_size", 0))
    total_investment = float(data.get("total_investment", 1000))  # Default fallback

    grid_range = f"{min_price}-{max_price}"

    config = {
        "grid_levels": grid_levels,
        "grid_range": grid_range,
        "step_size": step_size,
        "mode": "Manual",
        "total_investment": total_investment
    }

    save_config(config)  # Optional: Save for persistence
    print("Manual grid setup triggered:", config)

    return jsonify(status="Manual grid setup done", config=config)

@app.route('/ai_grid_setup', methods=['POST'])
def ai_grid_setup():
    print("AI grid setup triggered.")
    return jsonify(status="AI grid setup done")

@app.route('/close-bot', methods=['POST'])
def close_bot():
    print("Bot stopped.")
    return jsonify(status="Bot stopped")

@app.route('/close_trade', methods=['POST'])
def