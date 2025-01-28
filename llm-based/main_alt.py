import json
import sys
import pandas as pd
from main import generate_random_x_y_n, LLMGrid, Person

def get_4_neighbors(x, y, grid):
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[ny][nx] is not None:
            yield grid[ny][nx]

class Agent(Person):
    def __init__(self, id, name, grp):
        self.name = name
        self.id = id
        self.grp = grp
    def __str__(self):
        return self.name

class AgentGrid(LLMGrid):
    def __init__(self, mode = "p0_gpt4omini", setting = "50per-favourable", dim = 15):
        allowed_modes = ["p0_gpt4omini", "p1_gpt4omini", "p0_gpt3.5_turbo", "p1_gpt3.5_turbo"]
        if mode not in allowed_modes:
            raise ValueError(f"Mode should be one of {allowed_modes}")
        score_file = f"data/exp1/{mode}.json"
        agent_file = "data/exp1/agents.json"
        with open(score_file, "r") as f:
            self.scores = json.load(f)
        with open(agent_file, "r") as f:
            agent_list = json.load(f)
        self.agents = [Agent(*agent) for agent in agent_list]
        self.width, self.height = [dim] * 2
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        positions = generate_random_x_y_n(self.width, self.height, len(self.agents))
        for agent, (x, y) in zip(self.agents, positions):
            agent.update_position(x, y)
            self.grid[y][x] = agent
        stats = pd.DataFrame(self.scores.items(), columns = ["id", "score"])["score"].describe().to_dict()
        per_n, condition = setting.split("-")
        per_n = int(per_n.split("per")[0])
        self.tau = per_n / 100
        if condition == "favourable":
            self.sigma = stats["50%"]
        elif condition == "somewhatfavourable":
            self.sigma = stats["25%"]
        elif condition == "veryfavourable":
            self.sigma = stats["75%"]
        else:
            raise ValueError("Invalid setting")
        self.graphs = {}
        self.group_params = ["grp"]
        for g in self.group_params:
            self.graphs[f"{g}_similarity"] = []

    def get_number_of_rounds_and_sim(self):
        return len(self.graphs["grp_similarity"]), self.graphs["grp_similarity"][-1]

class SimpleAgentGrid(AgentGrid):
    def get_neighbors(self, x, y):
        return list(get_4_neighbors(x, y, self.grid))

if __name__ == "__main__":
    mode, setting, dim, simple = sys.argv[1:]
    dim = int(dim)
    simple = simple == "simple"
    grid = SimpleAgentGrid(mode, setting, dim) if simple else AgentGrid(mode, setting, dim)
    label = f"{mode}_{setting}_{dim}_{simple}"
    grid.visualize(label, visualize_circle=True, custom_label="inital")
    grid.simulate_rounds(label, visualize_circle=True, score_label=None)
