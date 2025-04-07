const socket = io();
let roomName = "";
let playerSymbol = "";
let board = Array(18).fill(null).map(() => Array(18).fill(""));
let isMyTurn = false;

function createRoom() {
  const input = document.getElementById("roomInput").value.trim();
  if (!input) return alert("Masukkan nama room!");
  roomName = input;
  socket.emit("create_room", { room: roomName });
}

function joinRoom(name) {
  roomName = name;
  socket.emit("join_room", { room: roomName });
}

socket.on("room_created", (room) => {
  console.log("Room dibuat:", room);
});

socket.on("room_joined", (room) => {
  console.log("Berhasil join:", room);
});

socket.on("start_game", () => {
  playerSymbol = "X";
  socket.emit("get_symbol", { room: roomName });
  document.getElementById("gameBoard").innerHTML = "";
  renderBoard();
});

socket.on("assign_symbol", (symbol) => {
  playerSymbol = symbol;
  isMyTurn = symbol === "X";
  renderBoard();
});

socket.on("update_board", ({ board: newBoard, nextTurn }) => {
  board = newBoard;
  isMyTurn = playerSymbol === nextTurn;
  renderBoard();
});

socket.on("room_list", (roomList) => {
  const listEl = document.getElementById("roomList");
  listEl.innerHTML = "";
  roomList.forEach(room => {
    const btn = document.createElement("button");
    btn.textContent = `Gabung ${room}`;
    btn.onclick = () => joinRoom(room);
    listEl.appendChild(btn);
    listEl.appendChild(document.createElement("br"));
  });
});

socket.on("error", (msg) => {
  alert(msg);
});

function renderBoard() {
  const boardDiv = document.getElementById("gameBoard");
  boardDiv.innerHTML = "";
  const table = document.createElement("table");
  table.style.borderCollapse = "collapse";
  table.style.margin = "auto";

  for (let i = 0; i < 18; i++) {
    const row = document.createElement("tr");
    for (let j = 0; j < 18; j++) {
      const cell = document.createElement("td");
      cell.textContent = board[i][j];
      cell.style.width = "25px";
      cell.style.height = "25px";
      cell.style.border = "1px solid #000";
      cell.style.textAlign = "center";
      cell.style.cursor = "pointer";
      cell.style.fontSize = "18px";
      cell.onclick = () => handleClick(i, j);
      row.appendChild(cell);
    }
    table.appendChild(row);
  }

  const turnInfo = document.createElement("p");
  turnInfo.textContent = isMyTurn ? "Giliran kamu" : "Menunggu lawan...";
  boardDiv.appendChild(turnInfo);
  boardDiv.appendChild(table);
}

function handleClick(i, j) {
  if (!isMyTurn || board[i][j] !== "") return;
  socket.emit("make_move", { room: roomName, row: i, col: j });
}