const img = document.getElementById("floorImage");
const drawCanvas = document.getElementById("drawCanvas");
const ghostCanvas = document.getElementById("ghostCanvas");
const fileInput = document.getElementById("fileInput");
const statusEl = document.getElementById("status");
const toolRoom = document.getElementById("tool-room");
const toolPath = document.getElementById("tool-path");

let tool = "room";
let drawing = false;
let points = [];
let actions = [];

toolRoom.onclick = () => { tool = "room"; toolRoom.classList.add("active"); toolPath.classList.remove("active"); };
toolPath.onclick = () => { tool = "path"; toolPath.classList.add("active"); toolRoom.classList.remove("active"); };

fileInput.onchange = e => {
  const file = e.target.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  img.src = url;
  img.onload = () => resizeCanvases();
};

function resizeCanvases() {
  const w = img.naturalWidth || img.width;
  const h = img.naturalHeight || img.height;
  [drawCanvas, ghostCanvas].forEach(c => { c.width = w; c.height = h; });
}

function sendEvent(action, coords) {
  const body = { action, coords, timestamp: Date.now() / 1000 };
  actions.push(body);
  fetch("http://localhost:8000/api/event", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}

function requestPrediction() {
  fetch("http://localhost:8000/api/predict").then(r => r.json()).then(drawGhost);
}

function drawGhost(pred) {
  const ctx = ghostCanvas.getContext("2d");
  ctx.clearRect(0, 0, ghostCanvas.width, ghostCanvas.height);
  if (!pred || !pred.predicted_coords) return;
  const [x, y] = pred.predicted_coords;
  ctx.strokeStyle = "rgba(0,200,255,0.5)";
  ctx.fillStyle = "rgba(0,200,255,0.15)";
  if (pred.predicted_action === "place_room") {
    ctx.beginPath();
    ctx.rect(x * ghostCanvas.width - 30, y * ghostCanvas.height - 30, 60, 60);
    ctx.fill();
    ctx.stroke();
  } else {
    ctx.beginPath();
    ctx.arc(x * ghostCanvas.width, y * ghostCanvas.height, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }
  statusEl.textContent = `Suggest: ${pred.predicted_action} (conf ${pred.confidence.toFixed(2)})`;
  ghostCanvas.dataset.predictionId = pred.prediction_id;
}

drawCanvas.onmousedown = e => {
  drawing = true;
  points = [];
  addPoint(e);
};

drawCanvas.onmousemove = e => {
  if (!drawing) return;
  addPoint(e);
  renderDrawing();
};

drawCanvas.onmouseup = () => {
  drawing = false;
  finalize();
};

drawCanvas.onmouseleave = () => { if (drawing) { drawing = false; finalize(); } };

function addPoint(e) {
  const rect = drawCanvas.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width;
  const y = (e.clientY - rect.top) / rect.height;
  points.push([x, y]);
}

function renderDrawing() {
  const ctx = drawCanvas.getContext("2d");
  ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
  ctx.strokeStyle = tool === "room" ? "#0f0" : "#ff0";
  ctx.lineWidth = 2;
  ctx.beginPath();
  points.forEach((p, i) => {
    const x = p[0] * drawCanvas.width;
    const y = p[1] * drawCanvas.height;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  if (tool === "room" && points.length >= 2) {
    const [x0, y0] = [points[0][0] * drawCanvas.width, points[0][1] * drawCanvas.height];
    const [x1, y1] = [points[points.length - 1][0] * drawCanvas.width, points[points.length - 1][1] * drawCanvas.height];
    ctx.rect(Math.min(x0, x1), Math.min(y0, y1), Math.abs(x1 - x0), Math.abs(y1 - y0));
  }
  ctx.stroke();
}

function finalize() {
  if (!points.length) return;
  const action = tool === "room" ? "place_room" : "pathway_segment";
  sendEvent(action, points);
  renderDrawing();
  drawCanvas.getContext("2d").clearRect(0, 0, drawCanvas.width, drawCanvas.height);
  requestPrediction();
}

ghostCanvas.onclick = () => {
  const predId = ghostCanvas.dataset.predictionId;
  if (!predId) return;
  fetch("http://localhost:8000/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prediction_id: predId, reward: 1 })
  });
  ghostCanvas.getContext("2d").clearRect(0, 0, ghostCanvas.width, ghostCanvas.height);
  requestPrediction();
};

window.onload = () => {
  toolRoom.classList.add("active");
  requestPrediction();
};

