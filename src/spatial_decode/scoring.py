
    ## libraries to import

import pandas as pd
import random
from collections import defaultdict
import numpy as np
from sklearn.metrics import adjusted_rand_score


    ## creating mock data sets for composition & domains

fruits = ("apple", "lemon", "orange", "banana", "grape", "persimmon")
djs = ("PENCIL", "A.N.I.", "Dasstudach", "POLTERGST", "IGDA", "Novah", "HOLY PRIEST", "Restricted", "Cera Khin", "Mr. Polska", "Samuel Moriero", "BEAUZ")
composition_mock = pd.DataFrame(columns=["square_id", "cell_type", "n_transcripts"])
composition_mock_gt = composition_mock.copy()
domain_mock = pd.DataFrame(columns=["square_id", "domain"])
domain_mock_gt = domain_mock.copy()
    
composition_rows = set()
domain_rows = []

    # composition
for i in range(len(djs)):

    while True:
        d = (random.choice(djs), random.choice(fruits), random.randint(0, 11))

        if d not in composition_rows:
            composition_rows.add(d)
            break

    composition_mock.loc[i] = d
    composition_mock_gt.loc[i] = d

    # domain
for el in djs:
    f = (el, random.choice(fruits))
    domain_rows.append(f)

domain_mock = pd.DataFrame(domain_rows)
domain_mock_gt = pd.DataFrame(domain_rows)


print(composition_mock, composition_mock_gt)
print(domain_mock, domain_mock_gt)
    

    ## RSME scoring
def scoring_RMSE(df_an, df_gt):

    # checking the DataFrame format
    if df_an.shape[1] != 3 or df_gt.shape[1] != 3:
        raise ValueError("DataFrames must both have 3 columns.")

    # setting up
    sum_sq_diff = 0
    n = 0
    gt_dict = defaultdict(list)
    an_dict = defaultdict(list)
    unique = []

    # creating dictionaries for both DataFrames
    for row_gt in df_gt.itertuples(index=False):
        key = (row_gt[0], row_gt[1])
        gt_dict[key].append(row_gt[2])

    for row_an in df_an.itertuples(index=False):
        key = (row_an[0], row_an[1])
        an_dict[key].append(row_an[2])

    # comparing matching combinations
    
    for key in set(an_dict):
        an_values = sorted(an_dict[key])
    for key in set(gt_dict):
        gt_values = sorted(gt_dict[key])

        # comparing individual values
    for key in an_dict:

        if key in gt_dict:
            
            for an, gt in zip(an_values, gt_values):
                diff = abs(an - gt)
                sum_sq_diff += diff**2
                n += 1
            
            # excess entries in df_an
            for value in an_dict[key][len(gt_dict[key]):]:
                unique.append((key, value))
                sum_sq_diff += value**2
                n += 1
                
        else:
            for value in an_dict[key]:
                unique.append((key, value))
                sum_sq_diff += value**2
                n += 1
    
    # excess entries in df_gt
    for key in gt_dict:
        for value in gt_dict[key][len(an_dict[key]):]:
            unique.append((key, value))
            sum_sq_diff += value**2
            n += 1

    # calculating RMSE
    if n == 0:
        return np.nan

    RMSE = np.sqrt(sum_sq_diff / n)

    print("Unique entries:", unique)
    print("RMSE:", RMSE)

    return RMSE


    ##known answer test
    # should return an empty list [] for unique and a RSME of 0
scoring_RMSE(composition_mock, composition_mock_gt)  
    # should return a ValueError because wrong number of columns
scoring_RMSE(domain_mock, domain_mock_gt)    
            
        
    ## ARI scoring

def scoring_ARI(df_an, df_gt):
    
    # checking the DataFrame format
    if df_an.shape[1] != 2 or df_gt.shape[1] != 2:
        raise ValueError("DataFrames must both have 2 columns.")
    
    # identifying the columns
    id_col_1 = df_an.columns[0]
    cluster_col_1 = df_an.columns[1]
    id_col_2 = df_gt.columns[0]
    cluster_col_2 = df_gt.columns[1]

    # renaming the columns
    file_an = df_an[[id_col_1, cluster_col_1]].copy()
    file_gt = df_gt[[id_col_2, cluster_col_2]].copy()
    file_an.columns = ["square_id", "domain_an"]
    file_gt.columns = ["square_id", "domain_gt"]

    # checking that there are no duplicates
    assert file_an["square_id"].is_unique, "Duplicate IDs in file 1"
    assert file_gt["square_id"].is_unique, "Duplicate IDs in file 2"
    
    # combining the two files using the square_id column as the matching column, keeping only IDs that appear in both df (inner), 
    # one_to_one = each ID exists at least once in both files
    merged = pd.merge(file_an, file_gt,on="square_id", how="inner", validate="one_to_one")
    
    # checking if number of rows is the same in all data frames & that there are no NaN
    assert len(merged) == len(file_an) == len(file_gt), "The files contain different IDs"
    assert merged["domain_an"].notna().all()
    assert merged["domain_gt"].notna().all()
    
    # calculating ARI
    ARI = adjusted_rand_score(merged["domain_an"], merged["domain_gt"])
    
    print("\nNumber of matched observations:", len(merged))
    print(len(domain_mock) == len(merged))
    print("Adjusted Rand Index:", ARI)
    
    
    ## known answer test
    # should return True and an ARI of 1
scoring_ARI(domain_mock, domain_mock_gt)  
    # should return a ValueError because wrong number of columns
scoring_ARI(composition_mock, composition_mock_gt)











