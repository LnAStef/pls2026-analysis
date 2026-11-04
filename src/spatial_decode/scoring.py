
import pandas as pd
import random

template = pd.read_csv("/Users/vera/Desktop/results/composition.csv")
type(template["square_id"][3])

# creating mock data sets
letters = ("apple", "lemon", "cherry", "raspberry", "donkey")
composition_mock = pd.DataFrame(columns=["square_id", "cell_type", "n_transcripts"])
composition_mock_gt = pd.DataFrame(columns=["square_id", "cell_type", "n_transcripts"])
domain_mock = pd.DataFrame(columns=["square_id", "domain"])
domain_mock_gt = pd.DataFrame(columns=["square_id", "domain"])
    
    
for i in range(20):
    d = {"square_id": random.choice(letters), "cell_type": random.choice(letters), "n_transcripts": random.randint(0, 11)}
    composition_mock.loc[i] = d
    composition_mock_gt.loc[i] = d
        
    f = {"square_id": random.choice(letters), "domain": random.choice(letters)}
    domain_mock.loc[i] = f
    domain_mock_gt.loc[i] = f
    
'''
composition_mock = composition_mock.sort_values("square_id")
composition_mock_gt = composition_mock.sort_values("square_id")
domain_mock = domain_mock.sort_values("square_id")  
domain_mock_gt = domain_mock_gt.sort_values("square_id")  
 '''
    
print(composition_mock, composition_mock_gt)
print(domain_mock, domain_mock_gt)
    

# scoring


def scoring(df_an, df_gt):
    
    # setting up counters and data frames
    counter_pos = 0
    counter_neg = 0
    
    df_both = pd.DataFrame(columns = df_an.columns)
    df_unique = pd.DataFrame(columns = [*df_an.columns, "an_or_gt"])
    
    
    # checking the two data frames against each other
    
    for _index, row_an in df_an.iterrows():
        
        if (df_gt == row_an).all(axis = 1).any():
            counter_pos += 1
            df_both.loc[len(df_both)] = row_an
            
        else:
            counter_neg += 1
            x = "an"
            df_unique.loc[len(df_unique)] = [*row_an, x]
            
            
    for _index, row_gt in df_gt.iterrows():
        
        if (df_an != row_gt).all(axis = 1).any() and (df_unique.iloc[:, :-1] != row_gt).all(axis = 1).any():
            counter_neg += 1
            y = "gt"
            df_unique.loc[len(df_unique)] = [*row_gt, y]
            
    
    print(counter_neg, counter_pos)
    
    
    
    
scoring(composition_mock, composition_mock_gt)   
    
    
    
    ''''
    # sorting the data frames in the same way
    df_an = df_an.sort_values(by=df_an.columns[0])
    df_gt = df_gt.sort_values(by=df_gt.columns[0])
    
    # setting up counters
    counter_an = 0
    counter_gt = 0
    counter_pos = 0
    counter_neg = 0
    
    while counter_an < len(df_an.rows()):
        
        if df_an.rows[counter_an] == df_gt[counter_gt]:
            counter_pos += 1
            counter_an += 1
            counter_gt += 1
        
        elif df_an.instance(df_an.rows):
    
   
   
    
   
    
   
    
   
    
   
    
   
    for index, row_an in df_an.iterrows():
        for index, row_gt in df_gt.iterrows():
            if row_an["square_id"] == row_gt["square_id"] and row_an["cell_type"] == row_gt["cell_type"] and row_an["n_transcripts"] == row_gt["n_transcripts"]:
                counter += 1
                
            else:
                break
            
    print(counter)
                
        

scoring(composition_mock,composition_mock_gt)
    




 




# beide df gleich ordnen, durch beide durch iterieren, proportion ausrechnen




















# create a function that creates a mock data frame in a temporary path, use that to test the functions that compare

'''    



