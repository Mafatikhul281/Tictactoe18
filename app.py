from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

rooms = {}  # {room_name: [sid1, sid2]}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("create_room")
def create_room(data):
    room_name = data["room"]
    if room_name in rooms:
        emit("error", "Room sudah ada.")
        return
    join_room(room_name)
    rooms[room_name] = [request.sid]
    emit("room_created", room_name)
    update_room_list()

@socketio.on("join_room")
def join_room_event(data):
    room_name = data["room"]
    if room_name in rooms and len(rooms[room_name]) == 1:
        join_room(room_name)
        rooms[room_name].append(request.sid)
        emit("room_joined", room_name)
        socketio.emit("start_game", room=room_name)
        update_room_list()
    else:
        emit("error", "Room tidak tersedia atau sudah penuh.")

@socketio.on("disconnect")
def handle_disconnect():
    for room, players in list(rooms.items()):
        if request.sid in players:
            players.remove(request.sid)
            if not players:
                del rooms[room]
            update_room_list()
            break

def update_room_list():
    available_rooms = [room for room, p in rooms.items() if len(p) == 1]
    socketio.emit("room_list", available_rooms)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))