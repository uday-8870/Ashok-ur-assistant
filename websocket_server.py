from bottle import Bottle, static_file, run
from bottle_websocket import GeventWebSocketServer, websocket
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Bottle()

@app.route('/')
def index():
    return static_file('index.html', root='./web')

@app.route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./web')

@app.route('/websocket', apply=[websocket])
def echo(ws):
    logger.info('WebSocket connection opened')
    try:
        while True:
            msg = ws.receive()
            if msg is not None:
                logger.info(f'Received message: {msg}')
                ws.send(f"Echo: {msg}")
            else:
                logger.info('WebSocket connection closed')
                break
    except Exception as e:
        logger.error(f'Error during WebSocket communication: {e}')
    finally:
        ws.close()

if __name__ == "__main__":
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8080))
    run(app, host=host, port=port, server=GeventWebSocketServer)
