
const socket = io();
let playerSymbol = null;
let currentTurn = "X";

const board = document.getElementById("board");
const info = document.getElementById("info");

function createBoard() {
    board.innerHTML = "";
    for (let i = 0; i < 18; i++) {
        for (let j = 0; j < 18; j++) {
            const cell = document.createElement("div");
            cell.className = "cell";
            cell.dataset.row = i;
            cell.dataset.col = j;
            cell.addEventListener("click", handleClick);
            board.appendChild(cell);
        }
    }
}

function handleClick(e) {
    if (!playerSymbol) return;
    const row = e.target.dataset.row;
    const col = e.target.dataset.col;
    if (e.target.textContent !== "") return;
    if (playerSymbol !== currentTurn) return;

    socket.emit("move", { row: parseInt(row), col: parseInt(col), player: playerSymbol });
}

function resetBoard() {
    socket.emit("reset");
}

socket.on("player_assigned", symbol => {
    playerSymbol = symbol;
    info.textContent = `You are Player ${symbol}`;
});

socket.on("start_game", () => {
    info.textContent = "Game started!";
});

socket.on("update_cell", data => {
    const { row, col, player } = data;
    const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
    cell.textContent = player;
    currentTurn = player === "X" ? "O" : "X";
    if (playerSymbol === currentTurn) {
        info.textContent = "Your turn";
    } else {
        info.textContent = "Opponent's turn";
    }
});

socket.on("game_over", msg => {
    info.textContent = msg;
});

socket.on("reset_board", () => {
    createBoard();
    currentTurn = "X";
    info.textContent = `Game reset. You are Player ${playerSymbol}`;
});

createBoard();
socket.emit("join");
