
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import eventlet
from flask import request
import os

app = Flask(__name__)
socketio = SocketIO(app)

ROOM = "main_room"
players = []
current_turn = "X"
grid = [["" for _ in range(18)] for _ in range(18)]

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("join")
def handle_join():
    global players
    if len(players) < 2:
        players.append(request.sid)
        join_room(ROOM)
        player_symbol = "X" if len(players) == 1 else "O"
        emit("player_assigned", player_symbol, room=request.sid)
        if len(players) == 2:
            socketio.emit("start_game", room=ROOM)

@socketio.on("move")
def handle_move(data):
    global current_turn, grid
    row, col = data["row"], data["col"]
    player = data["player"]

    if grid[row][col] == "" and player == current_turn:
        grid[row][col] = player
        socketio.emit("update_cell", {"row": row, "col": col, "player": player}, room=ROOM)
        
        if check_win(row, col, player):
            socketio.emit("game_over", f"{player} wins!", room=ROOM)
        else:
            current_turn = "O" if current_turn == "X" else "X"

@socketio.on("reset")
def handle_reset():
    global grid, current_turn
    grid = [["" for _ in range(18)] for _ in range(18)]
    current_turn = "X"
    socketio.emit("reset_board", room=ROOM)

def check_win(row, col, player):
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dx, dy in directions:
        count = 1
        for i in range(1, 5):
            r, c = row + i*dx, col + i*dy
            if r < 0 or r >= 18 or c < 0 or c >= 18 or grid[r][c] != player: break
            count += 1
        for i in range(1, 5):
            r, c = row - i*dx, col - i*dy
            if r < 0 or r >= 18 or c < 0 or c >= 18 or grid[r][c] != player: break
            count += 1
        if count >= 5:
            return True
    return False

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))