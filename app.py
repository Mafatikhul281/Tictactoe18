from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
rooms = {}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    emit("room_list", list(rooms.keys()))

@socketio.on("request_rooms")
def handle_request_rooms():
    emit("room_list", list(rooms.keys()))

@socketio.on("create_room")
def handle_create(data):
    room = data["room"]
    name = data["name"]
    if room in rooms:
        emit("error", "Room sudah ada")
        return
    join_room(room)
    rooms[room] = {
        "players": {request.sid: name},
        "board": [["" for _ in range(18)] for _ in range(18)],
    }
    emit("room_created", room)
    emit("room_list", list(rooms.keys()), broadcast=True)
    update_player_list(room)

@socketio.on("join_room")
def handle_join(data):
    room = data["room"]
    name = data["name"]
    if room not in rooms:
        emit("error", "Room tidak ditemukan")
        return
    join_room(room)
    rooms[room]["players"][request.sid] = name
    emit("room_joined", room)
    update_player_list(room)

def update_player_list(room):
    names = list(rooms[room]["players"].values())
    emit("update_player_list", names, room=room)

@socketio.on("start_game")
def handle_start_game(data):
    room = data["room"]
    if room not in rooms or len(rooms[room]["players"]) < 2:
        emit("error", "Minimal 2 pemain untuk mulai")
        return
    sids = list(rooms[room]["players"].keys())
    random.shuffle(sids)
    starter_sid = sids[0]
    other_sid = sids[1]
    starter_name = rooms[room]["players"][starter_sid]
    other_name = rooms[room]["players"][other_sid]
    socketio.emit("game_started", {"starter": starter_name, "symbol": "X"}, room=starter_sid)
    socketio.emit("game_started", {"starter": starter_name, "symbol": "O"}, room=other_sid)

if __name__ == "__main__":
    socketio.run(app, debug=True)