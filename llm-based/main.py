import random
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt

compat_str = "CompatibilityScore"

def generate_random_x_y_n(width, height, number_of):
    x_y_pairs = [(num % width, num // width) for num in random.sample(range(width * height), number_of)]
    return list(x_y_pairs)

def get_neighbors(x, y, grid):
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if 0 <= x + i < len(grid) and 0 <= y + j < len(grid[0]) and grid[y + j][x + i] is not None:
                if i != 0 or j != 0:
                    neighbors.append(grid[y + j][x + i])
    return neighbors

class Person:
    def __init__(self, **kwargs):
        ## assign all args to self.
        for key, value in kwargs.items():
            setattr(self, key, value)
    def __str__(self):
        return f"""
            {self.name} is a {self.occupation} who is {self.age} years old.
            They have an annual income of {self.income}
            They are quite interested in {self.hobbies}
        """
    def update_position(self, x, y):
        self.x, self.y = x, y
    def check_satisfaction(self, agent_sims, tau, sigma):
        ### tau -> fraction of agents, sigma => lower bound of acceptable similarity.        
        total, similar = len(agent_sims), sum([1 for agent_score in agent_sims if int(agent_score) >= sigma])
        if total == 0:
            return False
        return similar / total >= tau
    def check_if_same(self, neighbors, group_param):
        return len([n for n in neighbors if getattr(n, group_param) == getattr(self, group_param)]) > 0

class USPerson(Person):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.income = str(self.income) + " USD"

class IndiaPerson(Person):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.income = str(self.income) + " INR"

class LLMGrid:
    def __init__(self, mode = "india", setting = "50per-favorable"):
        if mode not in ["india", "us"]:
            raise ValueError("Mode should be either 'india' or 'us'")
        score_file = f"data/exp0/{mode}/scores.json"
        agent_file = f"data/exp0/{mode}/agents.json"
        with open(score_file, "r") as f:
            self.scores = json.load(f)
        with open(agent_file, "r") as f:
            self.agents = json.load(f)
        self.agents = [IndiaPerson(**agent) if mode == "india" else USPerson(**agent) for agent in self.agents]
        
        ## Fixed dims.
        self.width, self.height = 28, 28
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        ## set them randomly.
        agent_positions = generate_random_x_y_n(self.width, self.height, len(self.agents))
        for i, agent in enumerate(self.agents):
            agent.update_position(*agent_positions[i])
            self.grid[agent.y][agent.x] = agent
        
        all_scores = pd.DataFrame(self.scores).T
        all_scores[compat_str] = all_scores[compat_str].astype(float)
        stats = all_scores[compat_str].describe().to_dict()
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
        self.group_params = ["age_group", "income_group", "hobbies_group", "occupation_group", "name_group"]
        for g in self.group_params:
            self.graphs[f"{g}_similarity"] = []

    def get_neighbors(self, x, y):
        return get_neighbors(x, y, self.grid)

    def simulate_round(self, score_label = compat_str):
        unsatified_agents = []
        for agent in self.agents:
            ## get the Moore neighborhood of the agent
            neighbors = self.get_neighbors(agent.x, agent.y)
            if score_label == None:
                neighbor_sims = [self.scores[f"score_{agent.id}_{neighbor.id}"] for neighbor in neighbors]
            else:
                neighbor_sims = [self.scores[f"score_{agent.id}_{neighbor.id}"][score_label] for neighbor in neighbors]
            ## check if the agent is satisfied
            if not agent.check_satisfaction(neighbor_sims, self.tau, self.sigma):
                unsatified_agents.append(agent)
        
        ## get unoccupied cells
        unoccupied_cells = [(x, y) for y in range(self.height) for x in range(self.width) if self.grid[y][x] is None]

        ## put unsatisfied agents in unoccupied cells
        for agent in unsatified_agents:
            if unoccupied_cells:
                x, y = unoccupied_cells.pop(random.randint(0, len(unoccupied_cells) - 1))
                self.grid[agent.y][agent.x] = None
                self.grid[y][x] = agent
                agent.update_position(x, y)
            else:
                break
        
        return len(unsatified_agents)
    
    def analyze(self):
        ## get similarity% for each group_param.
        for g in self.group_params:
            total_similarity = 0
            for agent in self.agents:
                neighbours = self.get_neighbors(agent.x, agent.y)
                if len(neighbours) == 0:
                    continue
                similarity = len([n for n in neighbours if getattr(n, g) == getattr(agent, g)]) / len(neighbours)
                total_similarity += similarity
            self.graphs[f"{g}_similarity"].append(total_similarity / len(self.agents))

    def simulate_rounds(self, state_label, visualize_circle = False, score_label = compat_str, plot = True, grid_vis = True, max_rounds = 100):
        round = 0
        self.analyze()
        while self.simulate_round(score_label) > 0 and round < max_rounds:
            round += 1
            self.analyze()
        if plot:
            self.plot(state_label)
        if grid_vis:
            self.visualize(state_label, visualize_circle)

    def plot(self, state_label):
        plt.figure()
        for g in self.group_params:
            plt.plot(range(len(self.graphs[f"{g}_similarity"])), self.graphs[f"{g}_similarity"], label=g)
            ## x and y labels.
            plt.xlabel("Round")
            plt.ylabel(f"{g} Similarity %")
        plt.legend()
        ## save the plot.
        os.makedirs(f'outputs/images/{state_label}', exist_ok=True)
        plt.savefig(f"outputs/images/{state_label}/similarity_plots.png")
        plt.close()
    
    def visualize(self, state_label, visualize_circle = False, custom_label = None):
        ## for each group_param, we have a separate final grid to visualize.
        for grp in self.group_params:
            plt.figure()
            all_uniques = list(set([getattr(agent, grp) for agent in self.agents]))
            _, ax = plt.subplots()
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j] is None:
                        continue
                    ## circle if not satisfied.
                    agent = self.grid[i][j]
                    flag_circle = False
                    if visualize_circle:
                        neighbors = self.get_neighbors(agent.x, agent.y)
                        if not agent.check_if_same(neighbors, grp):
                            flag_circle = True
                    ## color based on chars, keep a palette of upto 8 colors, choose color based on index in all_uniques.
                    val = getattr(self.grid[i][j], grp)
                    try:
                        color = ['r', 'b', 'w', 'c', 'm', 'y', 'k', 'g'][all_uniques.index(val)]
                    except:
                        print(f"Error: {val} not found in {all_uniques}")
                        color = 'black'
                    abbr = val[:2]
                    ax.text(j, -i, abbr, ha='center', va='center', fontsize=10, color = color)
                    if flag_circle:
                        circle = plt.Circle((j, -i), 0.3, color='green', fill=False)
                        ax.add_artist(circle)
            
            ax.axis('off')
            ax.set_xlim(-0.5, len(self.grid[0]) - 0.5)
            ax.set_ylim(-len(self.grid) + 0.5, -0.5)
            ## add a title.
            # ax.set_title(state_label)
            ## add title at the bottom of the plot.
            ax.text(0.5, -len(self.grid) + 0.5, grp, ha='center', va='center', fontsize=20, color = 'black')
            ## save as image.
            os.makedirs(f'outputs/images/{state_label}', exist_ok=True)
            if custom_label:
                plt.savefig(f'outputs/images/{state_label}/{custom_label}.png')
            else:
                plt.savefig(f'outputs/images/{state_label}/{grp}.png')
            plt.close()

if __name__ == "__main__":
    mode, setting = sys.argv[1], sys.argv[2]
    llm = LLMGrid(mode, setting)
    llm.simulate_rounds(f"{mode}_{setting}")