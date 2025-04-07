const socket = io();
let roomName = "";

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
  alert("Game dimulai di room: " + roomName);
  // Mulai logika game-mu di sini
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