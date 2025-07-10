
from threading import Thread
from grid_bot import bot_instance

def start_bot():
    thread = Thread(target=bot_instance.start)
    thread.start()