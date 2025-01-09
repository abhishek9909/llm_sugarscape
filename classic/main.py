import random
import sys
import time
import os

def generate_random_x_y(width, height):
    return random.randint(0, width - 1), random.randint(0, height - 1)

class Agent:
    def __init__(self, x, y, chars):
        self.x, self.y, self.chars = x, y, chars
    def update_position(self, x, y):
        self.x, self.y = x, y
    def check_satisfaction(self, agents, threshold):
        total, similar = len(agents), sum([1 for agent in agents if agent.chars == self.chars])   
        return total == 0 or round(similar / total, 2) >= threshold


class Grid:
    def __init__(self, num_of_agents, num_of_cells, num_of_chars, threshold):
        self.threshold = threshold
        ## square root of the number of cells
        self.width, self.height = int(num_of_cells ** 0.5), int(num_of_cells ** 0.5)
        ## create agents with random positions and equidistributed chars.
        self.agents = [(i, Agent(*generate_random_x_y(self.width, self.height), i % num_of_chars)) for i in range(num_of_agents)]
        ## create grid and place agents on it
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        for i, agent in self.agents:
            self.grid[agent.y][agent.x] = agent

    def get_neighbors(self, x, y):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= x + i < self.width and 0 <= y + j < self.height and self.grid[y + j][x + i] is not None:
                    if i != 0 or j != 0:
                        neighbors.append(self.grid[y + j][x + i])
        return neighbors

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
        round = 1
        self.visualize(round)
        while self.simulate_round() > 0:
            self.visualize(round)
            round += 1
            time.sleep(1)
    
    def visualize(self, round):
        os.makedirs('outputs', exist_ok=True)
        print(f'Round: {round}')
        for row in self.grid:
            for cell in row:
                if cell is None:
                    print('.', end=' ')
                else:
                    print(cell.chars, end=' ')
            print()
        ## outputs the grid to a file
        with open(f'outputs/grid_{round}.txt', 'w') as f:
            for row in self.grid:
                for cell in row:
                    if cell is None:
                        f.write('.')
                    else:
                        f.write(str(cell.chars))
                f.write('\n')

if __name__ == "__main__":
    num_of_agents, num_of_cells, num_of_chars, threshold = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    grid = Grid(num_of_agents, num_of_cells, num_of_chars, threshold)
    grid.simulate_rounds()