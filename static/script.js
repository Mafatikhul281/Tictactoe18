const socket = io();
let roomName = "";
let playerName = "";
let playerSymbol = "";
let isMyTurn = false;
let board = Array(18).fill(null).map(() => Array(18).fill(""));

function saveName() {
  const nameInput = document.getElementById("playerName").value.trim();
  if (!nameInput) return alert("Masukkan nama kamu!");
  playerName = nameInput;
  document.getElementById("profileSection").style.display = "none";
  document.getElementById("roomSection").style.display = "block";
  socket.emit("request_rooms");
}

function createRoom() {
  const input = document.getElementById("roomInput").value.trim();
  if (!input) return alert("Masukkan nama room!");
  roomName = input;
  socket.emit("create_room", { room: roomName, name: playerName });
}

function joinRoom(name) {
  roomName = name;
  socket.emit("join_room", { room: roomName, name: playerName });
}

function startGame() {
  socket.emit("start_game", { room: roomName });
}

socket.on("room_created", (room) => {
  document.getElementById("roomSection").style.display = "none";
  document.getElementById("lobbySection").style.display = "block";
  document.getElementById("lobbyRoomName").innerText = room;
});

socket.on("room_joined", (room) => {
  document.getElementById("roomSection").style.display = "none";
  document.getElementById("lobbySection").style.display = "block";
  document.getElementById("lobbyRoomName").innerText = room;
});

socket.on("update_player_list", (players) => {
  const list = document.getElementById("playerList");
  list.innerHTML = "";
  players.forEach(p => {
    const li = document.createElement("li");
    li.textContent = p;
    list.appendChild(li);
  });
});

socket.on("game_started", (data) => {
  document.getElementById("lobbySection").style.display = "none";
  document.getElementById("gameSection").style.display = "block";
  isMyTurn = (data.starter === playerName);
  playerSymbol = data.symbol;
  alert("Game dimulai! Kamu adalah '" + playerSymbol + "'. " + (isMyTurn ? "Giliran kamu duluan." : "Tunggu giliran lawan."));
});

socket.on("room_list", (rooms) => {
  const div = document.getElementById("joinableRooms");
  div.innerHTML = "<p>Room Tersedia:</p>";
  rooms.forEach(r => {
    const btn = document.createElement("button");
    btn.textContent = "Gabung ke " + r;
    btn.onclick = () => joinRoom(r);
    div.appendChild(btn);
  });
});