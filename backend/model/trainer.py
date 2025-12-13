import torch
import torch.nn as nn
import torch.optim as optim
from .network import encode_actions


class OnlineTrainer:
    def __init__(self, predictor, store, lr=1e-3, seq_len=20):
        self.predictor = predictor
        self.store = store
        self.seq_len = seq_len
        self.opt = optim.Adam(self.predictor.parameters(), lr=lr)
        self.loss_coord = nn.MSELoss()
        self.loss_action = nn.CrossEntropyLoss()

    def sample(self, batch_size=8):
        data = self.store.get_last(batch_size + 1)
        if len(data) < 2:
            return None
        x = []
        y_coords = []
        y_action = []
        for i in range(len(data) - 1):
            hist = data[: i + 1]
            target = data[i + 1]
            feat = encode_actions(hist, self.seq_len).flatten()
            x.append(feat)
            coords = target.get("coords", [])
            if coords:
                xs = [p[0] for p in coords]
                ys = [p[1] for p in coords]
                cx = sum(xs) / len(xs)
                cy = sum(ys) / len(ys)
            else:
                cx = cy = 0.0
            y_coords.append([cx, cy])
            y_action.append(0 if target["action"] == "place_room" else 1)
        return torch.stack(x), torch.tensor(y_coords, dtype=torch.float32), torch.tensor(y_action)

    def train_step(self):
        batch = self.sample()
        if batch is None:
            return
        x, y_coords, y_action = batch
        coords_pred, action_pred = self.predictor.net(x)
        loss_c = self.loss_coord(coords_pred, y_coords)
        loss_a = self.loss_action(action_pred, y_action)
        loss = loss_c + loss_a
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

