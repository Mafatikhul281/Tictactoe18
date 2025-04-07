from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    emit("room_list", list(rooms.keys()))

@socketio.on("create_room")
def handle_create(data):
    room = data["room"]
    if room in rooms:
        emit("error", "Room sudah ada")
        return
    join_room(room)
    rooms[room] = {
        "players": [request.sid],
        "board": [["" for _ in range(18)] for _ in range(18)],
        "turn": "X"
    }
    emit("room_created", room)
    emit("room_list", list(rooms.keys()), broadcast=True)

@socketio.on("join_room")
def handle_join(data):
    room = data["room"]
    if room not in rooms or len(rooms[room]["players"]) >= 2:
        emit("error", "Room tidak tersedia")
        return
    join_room(room)
    rooms[room]["players"].append(request.sid)

    # Acak urutan pemain (penentu siapa X dan siapa O)
    random.shuffle(rooms[room]["players"])
    rooms[room]["turn"] = "X"

    emit("room_joined", room)
    socketio.emit("start_game", room=room)

@socketio.on("get_symbol")
def assign_symbol(data):
    room = data["room"]
    if request.sid == rooms[room]["players"][0]:
        emit("assign_symbol", "X")
    else:
        emit("assign_symbol", "O")

@socketio.on("make_move")
def handle_move(data):
    room = data["room"]
    i, j = data["row"], data["col"]
    game = rooms.get(room)
    if not game:
        return
    board = game["board"]
    if board[i][j] == "":
        board[i][j] = game["turn"]
        game["turn"] = "O" if game["turn"] == "X" else "X"
        socketio.emit("update_board", {"board": board, "nextTurn": game["turn"]}, room=room)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)