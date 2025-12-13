from core.dqn_agent import DQNAgent
from core.state_encoder import encode_state


class RLPipeline:
    def __init__(self, agent: DQNAgent):
        self.agent = agent

    def step(self, last_center, prev_center, reward, next_center, avg_angle=0.0, pattern_count=0, grid_w=1.0, grid_h=1.0):
        state = encode_state(last_center, prev_center, avg_angle=avg_angle, pattern_count=pattern_count,
                             grid_w=grid_w, grid_h=grid_h, device=self.agent.device)
        next_state = encode_state(next_center, last_center, avg_angle=avg_angle, pattern_count=pattern_count,
                                  grid_w=grid_w, grid_h=grid_h, device=self.agent.device)
        action_vec = (next_state[:2] - state[:2]).detach()
        self.agent.push((state.detach(), action_vec.detach(), reward, next_state.detach()))
        loss = self.agent.update()
        return loss

