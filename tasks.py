
from threading import Thread
from grid_bot import run_grid_bot

def start_bot():
    thread = Thread(target=run_grid_bot)
    thread.start()
