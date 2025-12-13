import torch
import torch.nn as nn
import torch.nn.functional as F
import uuid


def encode_actions(actions, max_len=20):
    seq = actions[-max_len:]
    out = []
    for a in seq:
        t = 0 if a["action"] == "place_room" else 1
        coords = a.get("coords", [])
        if coords:
            xs = [p[0] for p in coords]
            ys = [p[1] for p in coords]
            cx = sum(xs) / len(xs)
            cy = sum(ys) / len(ys)
        else:
            cx = cy = 0.0
        out.append([cx, cy, t])
    while len(out) < max_len:
        out.insert(0, [0.0, 0.0, 0.0])
    return torch.tensor(out, dtype=torch.float32)


class Net(nn.Module):
    def __init__(self, seq_len=20, hidden=64):
        super().__init__()
        inp = seq_len * 3
        self.fc1 = nn.Linear(inp, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.out_coords = nn.Linear(hidden, 2)
        self.out_action = nn.Linear(hidden, 2)

    def forward(self, x):
        h = F.relu(self.fc1(x))
        h = F.relu(self.fc2(h))
        coords = torch.sigmoid(self.out_coords(h))
        action = torch.softmax(self.out_action(h), dim=-1)
        return coords, action


class Predictor:
    def __init__(self, seq_len=20, device="cpu"):
        self.seq_len = seq_len
        self.device = device
        self.net = Net(seq_len).to(device)
        self.prediction_id = None

    def predict(self, actions):
        x = encode_actions(actions, self.seq_len).flatten().unsqueeze(0).to(self.device)
        with torch.no_grad():
            coords, action = self.net(x)
        coords = coords.squeeze(0).cpu().tolist()
        action_probs = action.squeeze(0).cpu().tolist()
        action_type = "place_room" if action_probs[0] >= action_probs[1] else "pathway_segment"
        self.prediction_id = str(uuid.uuid4())
        return {
            "prediction_id": self.prediction_id,
            "predicted_action": action_type,
            "predicted_coords": coords,
            "confidence": max(action_probs),
        }

    def parameters(self):
        return self.net.parameters()

