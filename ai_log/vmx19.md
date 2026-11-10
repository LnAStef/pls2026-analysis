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


## 03/11/2026

- **Prompt / ask:** < Ideas for how to compare the two data frames with each other. >
        

- **What it produced:** < A general workflow on how the problem could be approached:
    1 Data preparation
    Ignore DataFrame indices, standardize data types and handle missing values.
    
    
    2 Group by square_id
    Compare corresponding groups in both DataFrames.
    
    
    3 Match individual records
    Use a composite key if possible, otherwise find the best row-to-row correspondence within each group.
    
    
    4 Compare individual columns
    Use exact comparisons for categorical data and tolerances or normalized errors for numerical data.
    
    
    5 Calculate metrics
    Calculate record-level accuracy, column-level similarity, and numerical similarity.
    
    
    6 Calculate final score
    Combine the metrics using weights that reflect the importance of each column.>


- **How you checked it:** < Since its not code, no check is really necessary or possible. >


- **What was wrong:** < nothing found. >


- **Decision:** < accepted, I take the ideas into consideration on how to move forward. >


## 03/11/2026

- **Prompt / ask:** < Would a sound workflow be to sort the two df in the same way, iterate through both of them 
comparing line by line, skipping over anything that is different (recorded in a counter # of rows that are different and the same)
 & then calculate the proportion of what is the same? Or do you see any problem with that? >
        

- **What it produced:** < Confirmation that this might be a good idea and a warning about accidentally skipping lines. >


- **How you checked it:** < Since its not code, no check is really necessary or possible. >


- **What was wrong:** < nothing found. >


- **Decision:** < accepted, I take the warning into consideration on how to move forward. >


## 04/11/2026

- **Prompt / ask:** < In the context of this problem, what is a command I can use to check whether the current row is also present 
in the other df? Something like .isinstance but not for a class but an element. >
        

- **What it produced:** < That what I am essentially looking for is .isin(). But for this project something else would work better since 
.isin() only checks single elements while I want to check a whole row:
 row_exists = (df_gt == row_an).all(axis=1).any() >


- **How you checked it:** < I implemeted into my code in an if condition to see if it works. >


- **What was wrong:** < nothing found. >


- **Decision:** < accepted, I use the line of code moving forward. >


## 04/11/2026

- **Prompt / ask:** < The easiest way to add new rows (+ an element in a column not in the row) to a new data frame. >
        

- **What it produced:** < df_unique.loc[len(df_unique)] = [*row_an, match_value] >


- **How you checked it:** < I implemeted into my code in an if condition to see if it works. >


- **What was wrong:** < nothing found. >


- **Decision:** < accepted, I use the line of code moving forward. >


## 10/11/2026

- **Prompt / ask:** < How can I make this code run faster for large data frames while still keeping the basic structure I came up with more or less?
    def scoring_RMSE(df_an, df_gt):
        sum_diff = 0
        for _index, row_an in df_an.iterrows():
            for _ind, row_gt in df_gt.iterrows():
                if (row_an["square_id"] == row_gt["square_id"] and row_an["cell_type"] == row_gt["cell_type"]):
                    diff = abs(row_an["n_transcripts"]-row_gt["n_transcripts"])
                    sum_diff += diff
                    print(_index, _ind) >
        

- **What it produced:** < 2 ways: use .intertuple() instead and create a dictioary first instead of looping through the data frames every time. >


- **How you checked it:** < Known - answer test with a mock data frame. >


- **What was wrong:** < nothing wrong per se but continued editing it until it fit my needs exactly. >


- **Decision:** < accepted, I use the piece of code to move forward. >


## 10/11/2026

- **Prompt / ask:** < What is code I can use to calculate the ARI between two data frames? I also gave it the domains.csv file as an example of 
what I want to compare. I asked to explain what it codes exactly. >
        

- **What it produced:** < A code to calculate the ARI. >


- **How you checked it:** < Known - answer test with a mock data frame. >


- **What was wrong:** < nothing wrong per se but continued editing it until it fit my needs exactly. It produced a very specific code only useable for this one type of .csv file.  
I continued working on it until it was useable for more general data frames with the same structure. >


- **Decision:** < accepted, I use the piece of code to move forward. >
