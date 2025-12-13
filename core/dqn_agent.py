import random
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
from .neural_q import NeuralQ


class DQNAgent:
    def __init__(self, input_dim=8, lr=1e-3, gamma=0.95, buffer_size=2000, batch_size=32, demo_mode=True):
        self.demo_mode = demo_mode
        self.input_dim = input_dim
        
        if demo_mode:
            print("[DEMO] DQN Agent running in demo mode - using stub predictions")
            self.device = "cpu"  # Force CPU for demo stability
            return
            
        # Original initialization for non-demo mode
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[DEMO] ML components initialized on {self.device}")
        
        try:
            self.q_net = NeuralQ(input_dim=input_dim).to(self.device)
            self.target_net = NeuralQ(input_dim=input_dim).to(self.device)
            self.target_net.load_state_dict(self.q_net.state_dict())
            self.opt = optim.Adam(self.q_net.parameters(), lr=lr)
            self.gamma = gamma
            self.buffer = deque(maxlen=buffer_size)
            self.batch_size = batch_size
            self.loss_fn = nn.MSELoss()
            self.epsilon = 0.2
            self.step_count = 0
            self.save_path = "model.pth"
            self.log_path = "training.log"
            self.autosave_every = 200
        except Exception as e:
            print(f"[DEMO] DQN initialization failed: {e}")
            self.demo_mode = True

    def act(self, state):
        if self.demo_mode:
            # Demo mode: return plausible actions without neural network
            import random
            if hasattr(state, 'cpu'):
                state = state.cpu()
            
            # Generate demo actions based on common patterns
            actions = [
                torch.tensor([50.0, 30.0]),  # Move right and down
                torch.tensor([-30.0, 40.0]), # Move left and down  
                torch.tensor([20.0, -20.0]), # Move right and up
            ]
            return actions[random.randint(0, len(actions)-1)]
        
        # Original neural network code
        if random.random() < self.epsilon:
            with torch.no_grad():
                rand = torch.randn(2, device=self.device)
                return rand
        with torch.no_grad():
            q = self.q_net(state.unsqueeze(0))
        return q.squeeze(0)

    def push(self, transition):
        if self.demo_mode:
            return  # Demo mode: no training
        self.buffer.append(transition)

    def update(self):
        if self.demo_mode:
            return None  # Demo mode: no training
        # Original training code
        if len(self.buffer) < self.batch_size:
            return None
        batch = random.sample(self.buffer, self.batch_size)
        states, actions, rewards, next_states = zip(*batch)
        states = torch.stack(states).to(self.device)
        actions = torch.stack(actions).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device).unsqueeze(1)
        next_states = torch.stack(next_states).to(self.device)

        q_values = self.q_net(states)
        q_value = (q_values * actions).sum(dim=1, keepdim=True)

        with torch.no_grad():
            next_q = self.target_net(next_states)
            next_best = next_q.norm(dim=1, keepdim=True)
            target = rewards + self.gamma * next_best

        loss = self.loss_fn(q_value, target)
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        self.step_count += 1
        if self.step_count % 20 == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())
        if self.step_count % self.autosave_every == 0:
            torch.save(self.q_net.state_dict(), self.save_path)
        self.log(loss.item(), rewards.mean().item())
        return loss.item()

    def log(self, loss, reward):
        if self.demo_mode:
            return  # Demo mode: no logging
        try:
            with open(self.log_path, "a") as f:
                f.write(f"{self.step_count},{loss:.4f},{reward:.3f}\n")
        except Exception:
            pass

    def load(self):
        if self.demo_mode:
            return  # Demo mode: no model loading
        try:
            self.q_net.load_state_dict(torch.load(self.save_path, map_location=self.device))
            self.target_net.load_state_dict(self.q_net.state_dict())
        except Exception:
            pass

