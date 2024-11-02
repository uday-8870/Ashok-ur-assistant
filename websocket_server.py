import bottle
from bottle import Bottle, static_file, run
import logging
from socketio import SocketIO, WSGIApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Bottle()

@app.route('/')
def index():
    return static_file('index.html', root='./web')

@app.route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./web')

@app.route('/websocket')
def echo():
    sio = SocketIO(app)

    @sio.event
    def message(data):
        logger.info(f'Received message: {data}')
        sio.emit('echo', f"Echo: {data}")

    return sio

if __name__ == "__main__":
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8080))

    run(app, host=host, port=port)
