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

#777
@socketio.on("join_room")
def handle_join(data):
    room = data["room"]
    if room not in rooms or len(rooms[room]["players"]) >= 2:
        emit("error", "Room tidak tersedia")
        return
    join_room(room)
    rooms[room]["players"].append(request.sid)
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
        if check_winner(board, i, j, game["turn"]):
            socketio.emit("game_over", {"winner": game["turn"]}, room=room)
            del rooms[room]
        else:
            game["turn"] = "O" if game["turn"] == "X" else "X"
            socketio.emit("update_board", {"board": board, "nextTurn": game["turn"]}, room=room)

@socketio.on("surrender")
def handle_surrender(data):
    room = data["room"]
    symbol = data["symbol"]
    winner = "O" if symbol == "X" else "X"
    socketio.emit("game_over", {"winner": winner}, room=room)
    if room in rooms:
        del rooms[room]

def check_winner(board, row, col, symbol):
    def count(dx, dy):
        count = 0
        x, y = row + dx, col + dy
        while 0 <= x < 18 and 0 <= y < 18 and board[x][y] == symbol:
            count += 1
            x += dx
            y += dy
        return count

    directions = [(0,1), (1,0), (1,1), (1,-1)]
    for dx, dy in directions:
        total = 1 + count(dx, dy) + count(-dx, -dy)
        if total >= 5:
            return True
    return False

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
