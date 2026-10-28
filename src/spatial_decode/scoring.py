#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 10:47:35 2026

@author: vera
"""

import pandas as pd


# importing the ground truth
def import_gt(path):
    gt_composition = pd.read_csv(path + "/composition.csv")
    gt_domains = pd.read_csv(path + "/domains.csv")
    return gt_composition, gt_domains


gt_composition, gt_domains = import_gt(
    "/Users/vera/Desktop/unibas/modules/programming for life sciences/pls2026-analysis/reference_dataset/dataset/ground_truth"
)
print(gt_composition, gt_domains)


# importing the results of the analysis
def import_an (path):
    an_composition = pd.read_csv(path + "/composition.csv")
    an_domains = pd.read_csv(path + "/domains.csv")
    return an_composition, an_domains

an_composition, an_domains = import_an("/Users/vera/Desktop/results")
print(an_composition, an_domains)


# comparing line by line
for _index_an, row_an in an_composition.iterrows():
    for _index_gt, row_gt in gt_composition.iterrows():
   
        #print(row_an["square_id"], row_gt["square_id"])
    
        if row_an["square_id"] == row_gt["square_id"]:
            print (row_an["square_id"], row_gt["square_id"])
            break
       # else:
            #print("FALSE")
            #break

# seeing if its "in there"
x=0

for _index_an, row_an in an_composition.iterrows():
    
    if row_an["square_id"] in gt_composition["square_id"].values:
        x = x+1

  
    else:
        print("f")
        
print(x)





















    



# gt duplizieren erstmal, dann kleine .csv files generierem lassen oder selbst schreiben