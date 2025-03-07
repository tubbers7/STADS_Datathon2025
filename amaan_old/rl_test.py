import gymnasium as gym
from gymnasium import spaces
import numpy as np

class SimpleCorridor(gym.Env):
    """A simple corridor environment where the agent moves towards a goal."""

    def __init__(self, corridor_length=10):
        super(SimpleCorridor, self).__init__()
        self.corridor_length = corridor_length
        self.current_position = 0

        # Define action and observation space
        # They must be gymnasium.spaces objects
        self.action_space = spaces.Discrete(2)  # Two actions: move left or right
        self.observation_space = spaces.Discrete(corridor_length)  # Positions in the corridor

    def reset(self, seed=None, options=None):
        """Reset the environment to an initial state and return the initial observation."""
        super().reset(seed=seed)
        self.current_position = 0  # Start at the beginning of the corridor
        return self.current_position, {}

    def step(self, action):
        """Execute one time step within the environment."""
        if action == 0:  # Move left
            self.current_position = max(0, self.current_position - 1)
        elif action == 1:  # Move right
            self.current_position = min(self.corridor_length - 1, self.current_position + 1)

        # Check if the agent has reached the goal
        done = self.current_position == (self.corridor_length - 1)
        reward = 1 if done else -0.01  # Reward for reaching the goal, small penalty otherwise

        return self.current_position, reward, done, False, {}

    def render(self):
        """Render the environment."""
        print(f"Current position: {self.current_position}")

from gymnasium.envs.registration import register

register(
    id='SimpleCorridor-v0',
    entry_point='simple_corridor:SimpleCorridor',
    kwargs={'corridor_length': 10},  # Adjust as needed
)

# Create the environment
env = gym.make('SimpleCorridor-v0')

# Reset the environment to get the initial observation
observation, info = env.reset()

done = False
while not done:
    # Sample a random action
    action = env.action_space.sample()

    # Apply the action to the environment
    observation, reward, done, truncated, info = env.step(action)

    # Render the current state of the environment
    env.render()

# Close the environment
env.close()