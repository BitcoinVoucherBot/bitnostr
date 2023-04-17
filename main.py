#!/usr/bin/env python3

import time
import logging
import threading
import redis
from src.utils import Utils
from src.settings import Settings
from src.bot import Bot

utils = Utils()
nb = Bot()
settings = Settings()

redis_host = 'redis' if utils.is_running_in_docker() else '127.0.0.1'
print("Redis host: ", redis_host)
r = redis.Redis(host=redis_host, port=6379, db=0)
pubsub = None

def start_bot():
    print("Starting bot")
    
    try:
        relays = None
        nb.connect_relays(relays=relays)

        while True:
            nb.update()
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Shutting down")
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        print("Attempting to disconnect")
        nb.disconnect_relays()
        print("Disconnected!")

def subscribe_to_redis():
    pubsub = r.pubsub()
    pubsub.subscribe('order_complete')
    pubsub.subscribe('order_contact')

    print("Subscribed to Redis: ", redis_host)

    for message in pubsub.listen():
        if message['type'] == 'message':
            channel = message['channel'].decode('utf-8')
            if channel == 'order_complete':
                nb.order_complete(message['data'])
            elif channel == 'order_contact':
                nb.order_contact(message['data'])
    
if __name__ == "__main__":
    # Global setting
    logging.basicConfig(level="ERROR")

    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    redis_thread = threading.Thread(target=subscribe_to_redis)
    redis_thread.start() 

    if not utils.is_running_in_docker():
        from wsgi import server as wsgi_server
        wsgi_server.run(host='0.0.0.0', port=8080, debug=False)
