import random
import sys
import time
import os
import glob
import matplotlib.pyplot as plt

def generate_random_x_y_n(width, height, number_of):
    x_y_pairs = set()
    while len(x_y_pairs) < number_of:
        x_y_pairs.add((random.randint(0, width - 1), random.randint(0, height - 1)))
    return list(x_y_pairs)

def get_neighbors(x, y, grid):
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if 0 <= x + i < len(grid) and 0 <= y + j < len(grid[0]) and grid[y + j][x + i] is not None:
                if i != 0 or j != 0:
                    neighbors.append(grid[y + j][x + i])
    return neighbors

def plot_grid(grid, state_label, threshold):
    _, ax = plt.subplots()
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] is None:
                continue
            ## circle if not satisfied.
            flag_circle = False
            neighbors = get_neighbors(j, i, grid)
            if not grid[i][j].check_satisfaction(neighbors, threshold):
                flag_circle = True
            ## color based on chars, keep a palette of upto 8 colors, choose color based on index.
            color = ['r', 'b', 'g', 'c', 'm', 'y', 'k', 'w'][grid[i][j].chars]
            ax.text(j, -i, color, ha='center', va='center', fontsize=10, color = color)
            if flag_circle:
                circle = plt.Circle((j, -i), 0.3, color='green', fill=False)
                ax.add_artist(circle)
    
    ax.axis('off')
    ax.set_xlim(-0.5, len(grid[0]) - 0.5)
    ax.set_ylim(-len(grid) + 0.5, -0.5)
    ## add a title.
    # ax.set_title(state_label)
    ## add title at the bottom of the plot.
    ax.text(0.5, -len(grid) + 0.5, state_label, ha='center', va='center', fontsize=20, color = 'black')
    ## save as image.
    os.makedirs('outputs/images', exist_ok=True)
    plt.savefig(f'outputs/images/{state_label}.png')

class Agent:
    def __init__(self, x, y, chars):
        self.x, self.y, self.chars = x, y, chars
    def update_position(self, x, y):
        self.x, self.y = x, y
    def check_satisfaction(self, agents, threshold):
        total, similar = len(agents), sum([1 for agent in agents if agent.chars == self.chars])
        if total == 0:
            return False   
        return round(similar / total, 2) >= threshold


class Grid:
    def __init__(self, num_of_agents, num_of_cells, num_of_chars, threshold):
        self.threshold = threshold
        ## square root of the number of cells
        self.width, self.height = int(num_of_cells ** 0.5), int(num_of_cells ** 0.5)
        ## create agents with random positions and equidistributed chars.
        x_y_pos = generate_random_x_y_n(self.width, self.height, num_of_agents)
        self.agents = [(i, Agent(x_y_pos[i][0], x_y_pos[i][1], i % num_of_chars)) for i in range(num_of_agents)]
        ## create grid and place agents on it
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        for _, agent in self.agents:
            self.grid[agent.y][agent.x] = agent
        self.grid_states = {}

    def get_neighbors(self, x, y):
        return get_neighbors(x, y, self.grid)

    def simulate_round(self):
        unsatified_agents = []
        for _, agent in self.agents:
            ## get the Moore neighborhood of the agent
            neighbors = self.get_neighbors(agent.x, agent.y)
            ## check if the agent is satisfied
            if not agent.check_satisfaction(neighbors, self.threshold):
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

    def simulate_rounds(self):
        max_rounds = 100
        round = 0
        self.visualize(round)
        while self.simulate_round() > 0 and round < max_rounds:
            round += 1
            self.visualize(round)
            time.sleep(1)
        self.visualize("final") ## may or may not be equal to the last but one entry.
    
    def visualize(self, round):
        os.makedirs('outputs', exist_ok=True)
        self.grid_states[round] = [[self.grid[y][x] for x in range(self.width)] for y in range(self.height)]
        with open(f'outputs/grid_{round}.txt', 'w') as f:
            for row in self.grid:
                for cell in row:
                    if cell is None:
                        f.write('.')
                    else:
                        f.write(str(cell.chars))
                f.write('\n')

    def plot_progression(self):
        ## plot atmost 5 distinct states of the grid.
        state_len = len(self.grid_states)
        state_dict = {}
        state_dict["initial state"] = self.grid_states[0]
        state_dict["final state"] = self.grid_states["final"]
        ## get 3 equidistant states
        for i in range(1, 4):
            t = int(i * state_len / 4)
            if t not in self.grid_states:
                continue
            state_dict[f"round {t}"] = self.grid_states[t]
        ## plot the states
        for state_label, state in state_dict.items():
            plot_grid(state, state_label, self.threshold)

        ## plot the similarity percentage progression in the grid.
        similarity_per = []
        for i in range(len(self.grid_states)):
            if i not in self.grid_states:
                continue
            state = self.grid_states[i]
            total, similar = 0, 0
            for row in state:
                for cell in row:
                    if cell is None:
                        continue
                    neighbors = get_neighbors(cell.x, cell.y, state)
                    total += len(neighbors)
                    similar += sum([1 for agent in neighbors if agent.chars == cell.chars])
            similarity_per.append(round(similar / total, 2))
        ## save the similarity percentage progression as a plt file.
        ## new plot.
        plt.figure()
        plt.plot(range(len(similarity_per)), similarity_per)
        plt.xlabel('rounds')
        plt.ylabel('similarity percentage')
        plt.title('similarity percentage progression')
        plt.savefig('outputs/similarity_percentage.png')

        ## get the radius of different nuclei in the grid.
        radius_list = []
        ## get the connected components in the final_state grid.
        final_grid = self.grid_states["final"]
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        def dfs(x, y, flag_list, char_check):
            if x < 0 or x >= self.width or y < 0 or y >= self.height or visited[y][x] or final_grid[y][x] is None or final_grid[y][x].chars != char_check:
                return 0
            visited[y][x] = True
            flag_list.append((x, y))
            return 1 + sum([dfs(x + i, y + j, flag_list, char_check) for i in range(-1, 2) for j in range(-1, 2)])
        for i in range(self.height):
            for j in range(self.width):
                flag_list = []
                if not visited[i][j] and final_grid[i][j] is not None:
                    dfs(j, i, flag_list, final_grid[i][j].chars)
                ## get the diameter of the flag_list.
                if flag_list:
                    x_min, x_max, y_min, y_max = min([x for x, y in flag_list]), max([x for x, y in flag_list]), min([y for x, y in flag_list]), max([y for x, y in flag_list])
                    radius_list.append(max(x_max - x_min, y_max - y_min) // 2)
        ## plot all radius distribution without any binning.
        plt.figure()
        plt.hist(radius_list, bins = len(set(radius_list)))
        plt.xlabel('radius')
        plt.ylabel('frequency')
        plt.title('radius distribution')
        plt.savefig('outputs/radius_distribution.png')



if __name__ == "__main__":
    ## remove all the outputs from earlier.
    files = glob.glob("outputs/grid_*.txt")
    image_files = glob.glob("outputs/images/*.png")
    other_image_files = glob.glob("outputs/*.png")
    for f in [*files, *image_files, *other_image_files]:
        os.remove(f)
    num_of_agents, num_of_cells, num_of_chars, threshold = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    grid = Grid(num_of_agents, num_of_cells, num_of_chars, threshold)
    grid.simulate_rounds()
    ## Now, we create grid plot images.
    grid.plot_progression()
