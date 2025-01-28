from main import LLMGrid

if __name__ == "__main__":
    modes = ["india", "us"]
    setting_conditions = ["favourable", "somewhatfavourable", "veryfavourable"]
    setting_pers = [60, 75] ## 25, 40, 50.
    for per in setting_pers:
        for cond in setting_conditions:
            for mode in modes:
                grid = LLMGrid(mode, f"{per}per-{cond}")
                grid.simulate_rounds(f"{mode}_{per}per-{cond}")