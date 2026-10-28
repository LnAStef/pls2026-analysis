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
