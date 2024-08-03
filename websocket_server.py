from bottle import Bottle, static_file, run
from bottle_websocket import GeventWebSocketServer, websocket

app = Bottle()

@app.route('/')
def index():
    return static_file('index.html', root='./web')

@app.route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./web')

@app.route('/websocket', apply=[websocket])
def echo(ws):
    while True:
        msg = ws.receive()
        if msg is not None:
            ws.send(f"Echo: {msg}")
        else:
            break

if __name__ == "__main__":
    run(app, host='localhost', port=8080, server=GeventWebSocketServer)
