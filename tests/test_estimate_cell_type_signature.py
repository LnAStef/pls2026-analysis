# In the program estimate_cell_type_signatures.py: two reference data sets are loaded one containing cell types of each reference cell and on the number of transcripts per gene of each reference cell. The two data sets are merged and matrix with the mean expression profile generated. In this test should be evaluated if the programm generates the mean expression matrix based on a small data set.


import pandas as pd

# Table 1: transcript counts for 10 reference cells and 5 genes
transcripts = pd.DataFrame({
    "ref_cell": ["Cell1", "Cell2", "Cell3", "Cell4"],
    "Gene1": [12, 4, 0, 6],
    "Gene2": [0, 8, 2, 4]
})

# Table 2: the same 10 reference cells and their cell type
cell_types = pd.DataFrame({
    "ref_cell": ["Cell1", "Cell2", "Cell3", "Cell4"],
    "cell_type": ["TypeA", "TypeB", "TypeB", "TypeA"],
})

print(transcripts)
print(cell_types)

known_mean_expression = pd.DataFrame({
    "cell_type": ["TypeA", "TypeB"],
    "Gene1": [9.0, 2.0],
    "Gene2": [2.0, 5.0],
}).set_index("cell_type")


from src.spatial_decode.estimate_cell_type_signatures import load_reference_counts, load_reference_labels, cell_id_match, merge_counts_types, mean_expression_matrix 

counts = load_reference_counts(transcripts)
labels = load_reference_labels(cell_types)

cell_id_match(counts, labels)

merged = merge_counts_types(counts, labels)

matrixS = mean_expression_matrix(merged)

if matrixS.equals(known_mean_expression):
    print("Test passed") 
else:
    print("Test not passed - check functions again")