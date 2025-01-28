from main_alt import AgentGrid, Agent
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind, gaussian_kde, entropy, t

def get_two_sample_ttest(data1, data2):
    _, p_value = ttest_ind(data1, data2, equal_var=False)
    return p_value

def get_kl_divergence(data1, data2):
    kde_data1 = gaussian_kde(data1)
    kde_data2 = gaussian_kde(data2)
    x = np.linspace(0, 1, 1000)
    pdf1 = kde_data1(x)
    pdf2 = kde_data2(x)
    pdf1 = pdf1 / np.sum(pdf1)
    pdf2 = pdf2 / np.sum(pdf2)
    return entropy(pdf1, pdf2)

def get_p_value_that_expectation_is_point5(data):
    x_bar = np.mean(data)
    s = np.std(data, ddof=1)
    n = len(data)

    t_stat = (x_bar - 0.5) / (s / np.sqrt(n))

    p_value =  2 * (1 - t.cdf(t_stat, n - 1))
    return p_value


class RandomAgent(Agent):
    def __init__(self, agent):
        super().__init__(agent.id, agent.name, agent.grp)
        self.x = agent.x
        self.y = agent.y

    def check_satisfaction(self, agent_sims, tau, sigma):
        if len(agent_sims) == 0:
            return False
        return np.random.choice([True, False])

class RandomGrid(AgentGrid):
    def __init__(self, mode, setting, dim):
        super().__init__(mode, setting, dim)
        self.agents = [RandomAgent(agent) for agent in self.agents]



if __name__ == "__main__":
    ## A: All modes, settings and dims.
    # modes = ["p0_gpt4omini", "p1_gpt4omini", "p0_gpt3.5_turbo", "p1_gpt3.5_turbo"]
    # setting_conditions = ["favourable", "somewhatfavourable", "veryfavourable"]
    # setting_pers = [25, 40, 50, 60, 75]
    # dims = [15, 20, 30]
    # simple_values = [True, False]
    # for per in setting_pers:
    #     for cond in setting_conditions:
    #         for mode in modes:
    #             for simple in simple_values:
    #                 for dim in dims:
    #                     label = f"{mode}_{per}per-{cond}_{simple}_{dim}"
    #                     grid = SimpleAgentGrid(mode, f"{per}per-{cond}", dim) if simple else AgentGrid(mode, f"{per}per-{cond}", dim)
    #                     grid.visualize(label, visualize_circle=True, custom_label="initial")
    #                     grid.simulate_rounds(label, visualize_circle=True, score_label=None)

    ## B: Three curated experiments.
    modes = ["p0_gpt4omini", "p1_gpt4omini", "p0_gpt3.5_turbo", "p1_gpt3.5_turbo"]
    exps = [
        {"per": 40, "cond": "favourable", "dim": 15},
        {"per": 50, "cond": "veryfavourable", "dim": 30},
        {"per": 60, "cond": "somewhatfavourable", "dim": 20},
    ]    

    for exp in exps:
        obs_dict = {}
        for mode in modes:
            obs_dict[mode] = []
            label = f"curated_{mode}_{exp['per']}per-{exp['cond']}_{exp['dim']}"
            for i in range(100):
                grid = AgentGrid(mode, f"{exp['per']}per-{exp['cond']}", exp['dim'])
                grid.simulate_rounds(label, visualize_circle=True, score_label=None, grid_vis = False, plot = True if i == 0 else False, max_rounds = 2000)
                nr, sim = grid.get_number_of_rounds_and_sim()
                obs_dict[mode].append((nr, sim))
        random_grid = RandomGrid("p0_gpt4omini", "40per-favourable", exp["dim"])
        random_dis = []
        for _ in range(100):
            random_grid.simulate_rounds("random", visualize_circle=True, score_label=None, plot=False, grid_vis = False, max_rounds = 2000)
            nr, sim = random_grid.get_number_of_rounds_and_sim()
            random_dis.append((nr, sim))

        ## compare the observed and random data.
        with open("logs_run_main_alt.txt", "a") as f:
            f.write(f"Exp: {exp}, Random Mean: {np.mean([sim for _, sim in random_dis])}\n")
        for mode in modes:
            obs_data = [sim for _, sim in obs_dict[mode]]
            random_data = [sim for _, sim in random_dis]
            p_value = get_two_sample_ttest(obs_data, random_data)
            kl_div = get_kl_divergence(obs_data, random_data)
            p_value_e = get_p_value_that_expectation_is_point5(obs_data)
            # print(f"Exp: {exp}, Mode: {mode}, p-value: {p_value}, kl-divergence: {kl_div}")
            with open("logs_run_main_alt.txt", "a") as f:
                f.write(f"Exp: {exp}, Mode: {mode}, mean: {np.mean(obs_data)}, p-value: {p_value}, kl-divergence: {kl_div}, p-value-e: {p_value_e}\n")