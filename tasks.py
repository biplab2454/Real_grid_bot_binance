
from threading import Thread
from grid_bot import bot_instance

def start_bot():
    thread = Thread(target=run_grid_bot)
    thread.start()
