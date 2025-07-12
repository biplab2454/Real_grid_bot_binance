from flask import Flask, render_template, request, jsonify, redirect from config_manager import load_config, save_config from binance_client import get_trading_pairs from tasks import start_bot

app = Flask(name)

@app.route('/') def index(): config = load_config() pairs = get_trading_pairs() return render_template('dashboard.html', config=config, pairs=pairs)

@app.route('/start-bot', methods=['POST']) def start(): start_bot() return jsonify(status='Bot started.')

@app.route('/save-config', methods=['POST']) def save(): data = request.form.to_dict() save_config(data) return redirect('/')

@app.route('/config') def config_json(): return jsonify(load_config())

@app.route('/manual_grid_setup', methods=['POST']) def manual_grid_setup(): print("Manual grid setup triggered.") return jsonify(status="Manual grid setup done")

@app.route('/ai_grid_setup', methods=['POST']) def ai_grid_setup(): print("AI grid setup triggered.") return jsonify(status="AI grid setup done")

@app.route('/close-bot', methods=['POST']) def close_bot(): print("Bot stopped.") return jsonify(status="Bot stopped")

@app.route('/close_trade', methods=['POST']) def close_trade(): print("Trade closed.") return jsonify(status="Trade closed")

@app.route('/set_pair', methods=['POST']) def set_pair(): pair = request.json.get("pair") print(f"Pair set to {pair}") return jsonify(status=f"Pair set to {pair}")

@app.route('/status') def status(): # Dummy example values, integrate your actual logic here return jsonify(total_balance=1200.50, recent_profit=123.45, bot_status="Running")

if name == 'main': app.run(host='0.0.0.0', port=8000)

