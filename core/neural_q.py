import torch
import torch.nn as nn
import torch.nn.functional as F


class NeuralQ(nn.Module):
    def __init__(self, input_dim=8, hidden=64):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.fc3 = nn.Linear(hidden, 2)  # direction vector (dx, dy)

    def forward(self, x):
        h = F.relu(self.fc1(x))
        h = F.relu(self.fc2(h))
        return torch.tanh(self.fc3(h))  # dx, dy in [-1,1]

