import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np

class QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 32)
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class QLearningAgent:
    def __init__(self, state_size=3, action_size=3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = QNetwork(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        
        self.gamma = 0.95
        self.epsilon = 0.2
        self.action_size = action_size

    def choose_action(self, state, actions):
        # Convert state tuple to tensor
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        if random.random() < self.epsilon:
            return random.choice(actions)

        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
            action_idx = torch.argmax(q_values).item()
            return actions[action_idx]

    def update(self, state, action_name, reward, next_state, actions):
        # We need action_idx from action_name
        action_idx = actions.index(action_name)
        
        state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        next_state_t = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)
        reward_t = torch.FloatTensor([reward]).to(self.device)

        # Current Q value
        current_q = self.policy_net(state_t)[0][action_idx]

        # Target Q value
        with torch.no_grad():
            max_next_q = torch.max(self.policy_net(next_state_t)).item()
            target_q = reward_t + self.gamma * max_next_q

        # Optimize
        loss = self.criterion(current_q, torch.tensor(target_q).to(self.device))
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def save_q_table(self, path="model.pth"):
        torch.save(self.policy_net.state_dict(), path)
        print(f"PyTorch model saved to {path}")

    def load_q_table(self, path="model.pth"):
        import os
        if os.path.exists(path):
            self.policy_net.load_state_dict(torch.load(path, map_location=self.device))
            self.policy_net.eval()
            print(f"PyTorch model loaded from {path}")
        else:
            print("No saved model found, starting fresh.")
