# Updating ABMs with LLMs.

## Article.
- Refer [this notion article](https://phantom-pine-d78.notion.site/Updating-ABMs-with-LLMs-182e46ec019d8096b56fd04ce8dda39e).

## Prerequisites to run.
- `matplotlib(>3.10)`, `openai(>1.50)`, `numpy(>2.2)` and `pandas(>2.2)` with `python(>3.11)` installed in `venv`.
- minor versions of these packages should also work, no fancy util functions were used.

## Run:
Root/
├── classic/
│   ├── main.py
├── llm-based
│   ├── main.py
│   ├── main_alt.py

- `classic` contains the default implementation of schelling simulation.
- To run in `classic` mode, go to the folder, and run `python main.py {arg1} {arg2} {arg3} {arg4}` according to explanation provided in code.
- `llm-based` contains the experimental implementation.
- Before running, download and unzip the `data.zip` file from the `releases` section of the repo.
- Ensure the folder structure should look like this:

llm-based/
├── data/
├── main.py
├── main_alt.py

- Run `python main.py *args` for the first variant (with all parameters) and `python main_alt.py *args` for the second variant.
- Data can be replicated by running cells in `rough2.ipynb` for `exp0` and `rough3.ipynb` for `exp1`.
