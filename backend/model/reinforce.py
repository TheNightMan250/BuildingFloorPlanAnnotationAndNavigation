import torch


class Reinforce:
    def __init__(self, predictor, lr=1e-4):
        self.predictor = predictor
        self.opt = torch.optim.Adam(self.predictor.parameters(), lr=lr)

    def apply(self, reward, actions, prediction_id):
        if self.predictor.prediction_id != prediction_id:
            return
        if len(actions) < 2:
            return
        feat = actions[-2:]
        from .network import encode_actions

        x = encode_actions(feat, max_len=2).flatten().unsqueeze(0)
        coords_pred, action_pred = self.predictor.net(x)
        # Simple reward nudging
        loss = -reward * (coords_pred.mean() + action_pred.mean())
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

