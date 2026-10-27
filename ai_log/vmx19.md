#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 11:48:09 2026

@author: vera
"""

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

## 27/10/2026

- **Prompt / ask:** < Wrote a piece of code by hannd to check whether an element from one pd.df is also in another. Tried using "in" but did not work. I asked
ChatGPT why & how to fix it.
code I wrote:
for index_an, row_an in an_composition.iterrows():
    if row_an["square_id"] in gt_composition["square_id"]:
        print("t")
    else:
        print("f") >
        

- **What it produced:** < Use gt_composition["square_id"].values instead of only gt_composition["square_id"] or use .isin(). >


- **How you checked it:** < For trial purposes my df that I compare is just a duplicate of the groundtruth itself. So I know that they contain the exact same
amount of rows. I implemented a count where it did +1 everytime the element was in both df. In the end the value of the count was the same as number of rows in both df. >


- **What was wrong:** < nothing found. >


- **Decision:** < accepted, problem was solved. >








