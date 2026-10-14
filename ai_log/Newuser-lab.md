# AI + verification logs

**One file per person.** Name it after your GitHub account: `ai_log/<your-github-username>.md`.

The repository is shared with your group; this log is not. Keeping separate files means
you never merge anybody else's notes, and it is obvious who wrote what — the commits
touching `ai_log/<your-github-username>.md` should be authored by you.

Copy the block below into your own file and delete nothing else from this directory.

---

## <date> — <what you were building>

- **Prompt / ask:** <what you asked, or "wrote by hand">
- **What it produced:** <a line or two>
- **How you checked it:** <the specific check you ran — not "I read it">
- **What was wrong:** <bugs, hallucinations, or "nothing found">
- **Decision:** <accepted / edited / rejected — and why>

---

Record your one or two most significant AI uses each week — the ones where verification
actually mattered. Not every keystroke.

## Week04: 10.10.2026 - Estimate cell-type signatures

- **Prompt (duck.ai):** I have two csv files. One with cell_id and genes and one with cell_id and cell_type. I need a matrix S with mean expression of of each gene of each cell_type.
- **What it produced:**

import pandas as pd

expression = pd.read_csv("expression.csv")  # cell_id, gene1, gene2, ...
types = pd.read_csv("cell_types.csv")       # cell_id, cell_type

merged = expression.merge(types, on="cell_id", how="inner")

S = merged.groupby("cell_type").mean(numeric_only=True)
S = S.drop(columns=["cell_id"], errors="ignore")  # if cell_id was read as numeric

S.to_csv("mean_expression_by_cell_type.csv")

- **Check:** I wrote a two little data.frames corresponding the structure of reference_counts.csv and reference_labels.csv and run the proposed script on this data. I checked the results by hand. 
- **What was wrong:** The mean values of my test data were right. 
- **Decision:** I took the code and adapted it in order to have functions and to get the resulting matrix S with genes in rows and cell types in columns. With this code it is vice versa but I was not defining it in my prompt.


